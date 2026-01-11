import uuid
import asyncio
import yaml
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, status, BackgroundTasks

from ..models import Task, TaskCreate, TaskSummary, ExecutionState, TaskStatus, CellExecutionState, ExecutionLog
from ..store import store
from ..storage import get_testcase_content, save_testcase
from ...agent.forge_agent import ForgeAgent

router = APIRouter(tags=["tasks"])


@router.get("/tasks", response_model=List[TaskSummary])
async def list_tasks(skip: int = 0, limit: int = 100):
    """
    List all tasks.
    """
    tasks = store.list_tasks(skip, limit)
    return [
        TaskSummary(
            id=t.id,
            name=t.name,
            status=t.status,
            created_at=t.created_at
        ) for t in tasks
    ]


@router.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(task_in: TaskCreate):
    """
    Create a new task with YAML test case definition.
    """
    task_id = str(uuid.uuid4())
    now = datetime.now()
    
    yaml_content = task_in.yaml_content
    if task_in.testcase_file:
        content = get_testcase_content(task_in.testcase_file)
        if not content:
            raise HTTPException(status_code=400, detail=f"Testcase file '{task_in.testcase_file}' not found")
        yaml_content = content
    elif yaml_content:
        # Save custom content to file for persistence/reference
        try:
            filename = f"custom_{task_id}.yaml"
            save_testcase(filename, yaml_content)
        except Exception as e:
            # Log error but continue since we have the content in memory
            print(f"Failed to save testcase file: {e}")
    
    if not yaml_content:
         raise HTTPException(status_code=400, detail="Either yaml_content or testcase_file must be provided")

    task = Task(
        id=task_id,
        name=task_in.name,
        description=task_in.description,
        yaml_content=yaml_content,
        status=TaskStatus.PENDING,
        created_at=now,
        updated_at=now
    )
    
    store.create_task(task)
    return task


@router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """
    Get task details by ID.
    """
    task = store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str):
    """
    Delete a task.
    """
    if not store.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")


async def _run_task_background(task_id: str):
    """
    Background task to execute ForgeAgent.
    """
    store.update_status(task_id, TaskStatus.RUNNING)
    store.append_log(task_id, "INFO", "Starting ForgeAgent session...")
    
    # 1. Initialize Session
    try:
        session = store.create_session(task_id)
        store.append_log(task_id, "INFO", "Jupyter session started.")
    except Exception as e:
        store.append_log(task_id, "ERROR", f"Failed to start session: {e}")
        store.update_status(task_id, TaskStatus.FAILED)
        return

    # 2. Parse Testcase
    task = store.get_task(task_id)
    if not task.yaml_content:
         store.append_log(task_id, "ERROR", "No YAML content found.")
         store.update_status(task_id, TaskStatus.FAILED)
         return
         
    try:
        testcase = yaml.safe_load(task.yaml_content)
        steps = [step["content"] for step in testcase.get("steps", [])]
        
        # Inject context if available
        if steps:
            context_str = f"Context: {testcase.get('description', '')}\n"
            steps[0] = f"{context_str}Step 1: {steps[0]}"
            
        store.append_log(task_id, "INFO", f"Loaded {len(steps)} steps from testcase.")
    except Exception as e:
        store.append_log(task_id, "ERROR", f"Failed to parse YAML: {e}")
        store.update_status(task_id, TaskStatus.FAILED)
        return

    # 3. Initialize Browser (based on env)
    env = testcase.get("test-env", {})
    base_url = env.get("base_url", "https://www.baidu.com")
    headless = env.get("headless", False)
    
    init_code = f"""
from playwright.async_api import async_playwright
playwright = await async_playwright().start()
browser = await playwright.chromium.launch(headless={headless})
context = await browser.new_context(base_url="{base_url}")
page = await context.new_page()
"""
    try:
        store.append_log(task_id, "INFO", "Initializing browser environment...")
        await session.add_cell(init_code)
        store.append_log(task_id, "INFO", "Browser initialized.")
    except Exception as e:
        store.append_log(task_id, "ERROR", f"Failed to initialize browser: {e}")
        store.update_status(task_id, TaskStatus.FAILED)
        return

    # 4. Run Agent
    try:
        store.append_log(task_id, "INFO", "Launching ForgeAgent...")
        agent = ForgeAgent(task_id)
        await agent.run(steps)
        store.append_log(task_id, "INFO", "Agent execution completed successfully.")
        store.update_status(task_id, TaskStatus.COMPLETED)
    except Exception as e:
        store.append_log(task_id, "ERROR", f"Agent execution failed: {e}")
        store.update_status(task_id, TaskStatus.FAILED)


@router.post("/tasks/{task_id}/start", status_code=status.HTTP_202_ACCEPTED)
async def start_task(task_id: str, background_tasks: BackgroundTasks):
    """
    Start task execution.
    """
    task = store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    background_tasks.add_task(_run_task_background, task_id)
    return {"status": "accepted"}


@router.get("/tasks/{task_id}/execution", response_model=ExecutionState)
async def get_task_execution(task_id: str):
    """
    Get current execution state (logs, cells) for a task.
    """
    task = store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    exec_state = store.get_execution_state(task_id) or {}
    
    # Get live cells from session if available
    session = store.get_session(task_id)
    cells = []
    if session:
        notebook_state = session.get_state()
        cells = [
            CellExecutionState(
                id=c.id,
                status=c.status,
                code=c.source,
                output=str(c.outputs) if c.outputs else None
            ) for c in notebook_state.cells
        ]
    else:
        # Fallback to stored execution state (e.g. if session closed)
        cells = [CellExecutionState(**cell) for cell in exec_state.get("cells", [])]

    return ExecutionState(
        task_id=task_id,
        status=task.status,
        logs=[ExecutionLog(**log) for log in exec_state.get("logs", [])],
        cells=cells
    )

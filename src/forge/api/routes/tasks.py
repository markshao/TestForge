import uuid
import asyncio
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, status, BackgroundTasks

from ..models import Task, TaskCreate, TaskSummary, ExecutionState, TaskStatus, CellExecutionState, ExecutionLog
from ..store import store

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
    
    task = Task(
        id=task_id,
        name=task_in.name,
        description=task_in.description,
        yaml_content=task_in.yaml_content,
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
    Background task to simulate execution.
    In the future, this will use the actual runtime.
    """
    store.update_status(task_id, TaskStatus.RUNNING)
    store.append_log(task_id, "INFO", "Starting session...")
    
    # Simulate some startup delay
    await asyncio.sleep(1)
    store.append_log(task_id, "INFO", "Browser launched (chromium)")
    
    # Mock cells based on some hardcoded logic for now
    # Since we haven't implemented the full YAML -> Code parser yet
    mock_cells = [
        {
            "id": "cell-1",
            "status": "success",
            "code": "from playwright.async_api import async_playwright\np = await async_playwright().start()",
            "output": "Browser launched successfully."
        },
        {
            "id": "cell-2",
            "status": "running",
            "code": "await page.goto('https://www.google.com')",
            "output": None
        }
    ]
    store.update_cells(task_id, mock_cells)
    
    await asyncio.sleep(2)
    store.append_log(task_id, "INFO", "Navigating to target URL...")
    
    # Update cell 2 to success
    mock_cells[1]["status"] = "success"
    mock_cells[1]["output"] = "Navigated to https://www.google.com"
    store.update_cells(task_id, mock_cells)
    
    store.append_log(task_id, "INFO", "Task completed successfully")
    store.update_status(task_id, TaskStatus.COMPLETED)


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
        
    exec_state = store.get_execution_state(task_id)
    
    return ExecutionState(
        task_id=task_id,
        status=task.status,
        logs=[ExecutionLog(**log) for log in exec_state.get("logs", [])],
        cells=[CellExecutionState(**cell) for cell in exec_state.get("cells", [])]
    )

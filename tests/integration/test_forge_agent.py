import pytest
import pytest_asyncio
import asyncio
import yaml
import os
from src.forge.api.store import store
from src.forge.api.models import Task, TaskStatus
from src.forge.agent.forge_agent import ForgeAgent
from src.forge.agent.tools import run_playwright_code, RunPlaywrightCodeToolInput
from datetime import datetime
from loguru import logger

@pytest_asyncio.fixture
async def active_session():
    task_id = "test-forge-agent-baidu"
    
    # Setup
    task = Task(
        id=task_id, 
        name="Test Forge Agent", 
        status=TaskStatus.RUNNING, 
        yaml_content="", 
        created_at=datetime.now(), 
        updated_at=datetime.now()
    )
    store.create_task(task)
    session = store.create_session(task_id)
    
    # Read testenv from YAML
    yaml_path = os.path.join(os.path.dirname(__file__), "../../examples/testcases/baidu_search.yaml")
    yaml_path = os.path.abspath(yaml_path)
    
    if not os.path.exists(yaml_path):
        pytest.fail(f"YAML file not found at {yaml_path}")
        
    with open(yaml_path, "r") as f:
        testcase = yaml.safe_load(f)
    
    env = testcase.get("test-env", {})
    base_url = env.get("base_url", "https://www.baidu.com")
    headless = env.get("headless", False)
    
    # Init browser with env config
    init_code = f"""
from playwright.async_api import async_playwright
playwright = await async_playwright().start()
browser = await playwright.chromium.launch(headless={headless})
context = await browser.new_context(base_url="{base_url}")
page = await context.new_page()
await page.goto("{base_url}")
"""
    await session.add_cell(init_code)
    
    yield task_id, testcase
    
    # Teardown
    store.delete_task(task_id)

def _log_steps(steps):
    logger.info(f"Loaded {len(steps)} steps from baidu_search.yaml")
    for i, s in enumerate(steps, 1):
        logger.info(f"Step {i}: {s}")

@pytest.mark.asyncio
async def test_forge_agent_baidu_flow(active_session):
    """
    Test that ForgeAgent can execute a multi-step plan on Baidu using the example YAML.
    """
    task_id, testcase = active_session
    
    # Initialize ForgeAgent
    try:
        agent = ForgeAgent(task_id)
    except Exception as e:
        pytest.skip(f"Skipping test due to agent initialization failure: {e}")

    steps = [step["content"] for step in testcase["steps"]]
    
    _log_steps(steps)
    
    print(f"\nExecuting plan with {len(steps)} steps...")
    
    try:
        # Prepend context to the first step or handle it in the agent
        # For now, let's make the goal more specific by adding context
        context_str = f"Context: {testcase.get('description', '')}\n"
        steps_with_context = steps.copy()
        steps_with_context[0] = f"{context_str}Step 1: {steps[0]}"
        
        result = await agent.run(steps_with_context)
        print(f"Agent execution finished.")
    except Exception as e:
        pytest.fail(f"Agent failed to execute plan: {e}")

    # Verify results
    await asyncio.sleep(2) # Wait for results to load
    
    # Check page title
    verify_code = "await page.title()"
    tool_result = await run_playwright_code(RunPlaywrightCodeToolInput(code=verify_code), task_id)
    
    print(f"Page title: {tool_result.stdout}")
    assert tool_result.success
    # Title should contain 'Playwright' (as per the yaml content)
    assert "Playwright" in tool_result.stdout or "Playwright" in str(tool_result.result)

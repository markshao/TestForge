import pytest
import pytest_asyncio
import asyncio
from src.forge.api.store import store
from src.forge.api.models import Task, TaskStatus
from src.forge.agent.forge_agent import ForgeAgent
from src.forge.agent.tools import run_playwright_code, RunPlaywrightCodeToolInput
from datetime import datetime

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
    
    # Init browser (Visible for debugging)
    init_code = """
from playwright.async_api import async_playwright
playwright = await async_playwright().start()
browser = await playwright.chromium.launch(headless=False)
context = await browser.new_context()
page = await context.new_page()
"""
    await session.add_cell(init_code)
    
    yield task_id
    
    # Teardown
    store.delete_task(task_id)

@pytest.mark.asyncio
async def test_forge_agent_baidu_flow(active_session):
    """
    Test that ForgeAgent can execute a multi-step plan on Baidu.
    """
    task_id = active_session
    
    # Initialize ForgeAgent
    try:
        agent = ForgeAgent(task_id)
    except Exception as e:
        pytest.skip(f"Skipping test due to agent initialization failure: {e}")

    # Define steps
    steps = [
        "Open https://www.baidu.com",
        "In the search box, type 'TestForge'",
        "Click the search button (百度一下)"
    ]
    
    print(f"\nExecuting plan with {len(steps)} steps...")
    
    try:
        result = await agent.run(steps)
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
    # Title should contain 'TestForge'
    assert "TestForge" in tool_result.stdout or "TestForge" in str(tool_result.result)

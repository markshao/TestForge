import pytest
import pytest_asyncio
import asyncio
from src.forge.api.store import store
from src.forge.api.models import Task, TaskStatus
from src.forge.agent.automation_agent import AutomationAgent
from src.forge.agent.tools import run_playwright_code, RunPlaywrightCodeToolInput
from datetime import datetime
import os

@pytest_asyncio.fixture
async def active_session():
    task_id = "test-automation-agent-baidu"
    
    # Setup
    task = Task(
        id=task_id, 
        name="Test Automation Agent", 
        status=TaskStatus.RUNNING, 
        yaml_content="", 
        created_at=datetime.now(), 
        updated_at=datetime.now()
    )
    store.create_task(task)
    session = store.create_session(task_id)
    
    # Init browser
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
async def test_automation_agent_baidu_search(active_session):
    """
    Test that the AutomationAgent can search for '拼多多' on Baidu.
    This test requires a valid OpenAI API key.
    """
    task_id = active_session
    
    # Pre-condition: Go to Baidu
    await run_playwright_code(RunPlaywrightCodeToolInput(code="await page.goto('https://www.baidu.com')"), task_id)
    
    # Initialize Agent
    # Note: This requires OPENAI_API_KEY to be set in .env or environment
    try:
        agent = AutomationAgent(task_id)
    except Exception as e:
        pytest.skip(f"Skipping test due to agent initialization failure (likely missing API key): {e}")

    step = "在搜索框输入'拼多多'，然后点击搜索按钮"
    
    print(f"\nExecuting step: {step}")
    try:
        result = await agent.run_step(step)
        print(f"Agent execution result: {result}")
    except Exception as e:
        pytest.fail(f"Agent failed to execute step: {e}")

    # Verify results
    # Check if page title contains '拼多多'
    verify_code = "await page.title()"
    tool_result = await run_playwright_code(RunPlaywrightCodeToolInput(code=verify_code), task_id)
    
    print(f"Page title after execution: {tool_result.stdout}")
    
    # Baidu search results usually have the query in the title, e.g., "拼多多_百度搜索"
    # But checking if url contains key words or if title contains it is good enough.
    assert tool_result.success
    # We assert loosely because the agent might take time or behave slightly differently
    # But if it succeeded, the title should likely change from "百度一下，你就知道" to something else.
    assert "拼多多" in tool_result.stdout or "拼多多" in str(tool_result.result)
    
    # Wait to see the result
    await asyncio.sleep(2)

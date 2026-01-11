import pytest
import pytest_asyncio
import asyncio
from src.forge.api.store import store
from src.forge.api.models import Task, TaskStatus
from src.forge.agent.tools import get_page_content, run_playwright_code, GetPageContentToolInput, RunPlaywrightCodeToolInput
from datetime import datetime

@pytest_asyncio.fixture
async def active_session():
    task_id = "test-task-1"
    
    # Setup
    task = Task(
        id=task_id, 
        name="Test Task", 
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
browser = await playwright.chromium.launch(headless=True)
context = await browser.new_context()
page = await context.new_page()
"""
    await session.add_cell(init_code)
    
    yield task_id
    
    # Teardown
    store.delete_task(task_id)

@pytest.mark.asyncio
async def test_run_playwright_code(active_session):
    task_id = active_session
    
    # Navigate to example.com
    code = "await page.goto('https://example.com')"
    result = await run_playwright_code(RunPlaywrightCodeToolInput(code=code), task_id)
    assert result.success is True
    
    # Get title
    code = "await page.title()"
    result = await run_playwright_code(RunPlaywrightCodeToolInput(code=code), task_id)
    assert result.success is True
    assert "Example Domain" in result.stdout or "Example Domain" in str(result.result)

@pytest.mark.asyncio
async def test_get_page_content(active_session):
    task_id = active_session
    
    # Set simple content
    html = """
    <html>
        <body>
            <div id="container">
                <h1>Hello World</h1>
                <button id="btn-submit" class="primary">Submit</button>
                <div style="display:none">Hidden</div>
            </div>
        </body>
    </html>
    """
    # Use setContent
    code = f"await page.set_content('''{html}''')"
    await run_playwright_code(RunPlaywrightCodeToolInput(code=code), task_id)
    
    # Get content
    result = await get_page_content(GetPageContentToolInput(), task_id)
    
    assert result.success is True
    dom = result.result
    
    # Verify structure
    print(f"DOM: {dom}")
    
    # Should contain body -> container -> h1/button
    # And NOT contain hidden div
    
    # Helper to find node
    def find_node(node, tag, attrs=None):
        if isinstance(node, str):
            return None
            
        if node.get('tag') == tag:
            match = True
            if attrs:
                for k, v in attrs.items():
                    if node.get(k) != v:
                        match = False
                        break
            if match: return node
        
        if 'children' in node:
            for child in node['children']:
                found = find_node(child, tag, attrs)
                if found: return found
        return None

    assert find_node(dom, 'h1') is not None
    assert find_node(dom, 'button', {'id': 'btn-submit'}) is not None
    
    # Verify text content
    # Note: My traverse function puts text in children? No, wait.
    # traverse(node) returns string if TEXT_NODE.
    # So children can be strings.
    
    h1 = find_node(dom, 'h1')
    assert "Hello World" in h1['children']
    
    # Verify hidden element is NOT present
    # We can check if "Hidden" text exists in the dump
    import json
    assert "Hidden" not in json.dumps(dom)

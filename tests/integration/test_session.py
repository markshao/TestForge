import pytest
import os
import nbformat
from forge.runtime.session import JupyterNotebookSession

@pytest.fixture
def session():
    s = JupyterNotebookSession()
    s.start()
    yield s
    s.stop()

@pytest.mark.asyncio
async def test_session_playwright_flow(session):
    # Step 1: Start Browser
    res1 = await session.add_cell("""
from playwright.async_api import async_playwright
p = await async_playwright().start()
browser = await p.chromium.launch(headless=False)
page = await browser.new_page()
    """)
    assert res1.is_success

    # Step 2: Goto Page
    res2 = await session.add_cell("""
await page.goto("https://example.com")
    """)
    assert res2.is_success

    # Step 3: Check Title
    res3 = await session.add_cell("await page.title()")
    assert res3.is_success
    assert "Example Domain" in res3.text_result or "'Example Domain'" in res3.text_result

    # Step 4: Verify Notebook Structure
    nb = session.get_notebook_json()
    assert len(nb['cells']) == 3
    assert nb['cells'][2]['source'] == "await page.title()"
    assert nb['cells'][2]['outputs'][0]['output_type'] == "execute_result"

    # Step 5: Save and Verify File
    session.save("test_output.ipynb")
    assert os.path.exists("test_output.ipynb")
    
    # Clean up
    await session.add_cell("await browser.close(); await p.stop()")
    os.remove("test_output.ipynb")

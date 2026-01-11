import pytest
import os
from forge.runtime.kernel import JupyterKernel

@pytest.fixture
def kernel():
    k = JupyterKernel()
    k.start()
    yield k
    k.stop()

def test_kernel_execution_simple_math(kernel):
    result = kernel.execute("1 + 1")
    assert result.is_success
    assert result.text_result == "2"

def test_playwright_scenario(kernel):
    # Step 1: Import and Start Playwright (Async)
    # Note: IPython kernel supports top-level await by default
    setup_code = """
from playwright.async_api import async_playwright
p = await async_playwright().start()
browser = await p.chromium.launch(headless=False)
page = await browser.new_page()
    """
    result = kernel.execute(setup_code)
    assert result.is_success, f"Setup failed: {result.error}"

    # Step 2: Navigate to Example.com
    nav_code = """
await page.goto("https://example.com")
print(f"Navigated to {page.url}")
    """
    result = kernel.execute(nav_code)
    assert result.is_success, f"Navigation failed: {result.error}"
    assert "Navigated to https://example.com" in result.stdout

    # Step 3: Get Title
    title_code = "await page.title()"
    result = kernel.execute(title_code)
    assert result.is_success
    assert "Example Domain" in result.text_result or "'Example Domain'" in result.text_result

    # Step 4: Cleanup
    cleanup_code = """
await browser.close()
await p.stop()
    """
    result = kernel.execute(cleanup_code)
    assert result.is_success

@pytest.mark.asyncio
async def test_async_execution(kernel):
    result = await kernel.aexecute("import time; time.sleep(0.1); print('async')")
    assert result.is_success
    assert "async" in result.stdout

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
import json
import base64
import os
from datetime import datetime

from ..api.store import store


class ToolResult(BaseModel):
    """
    Standard result format for all tool executions.
    """
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    stdout: Optional[str] = None
    artifacts: Optional[Dict[str, str]] = None  # Paths to screenshots, files, etc.


class GetPageContentToolInput(BaseModel):
    """
    Input schema for GetPageContentTool.
    """
    include_attributes: List[str] = Field(
        default=["id", "name", "class", "role", "aria-label", "placeholder", "type", "href", "value", "data-testid"],
        description="List of HTML attributes to include in the output element tree."
    )
    max_length: int = Field(
        default=50000,
        description="Maximum length of the returned content to prevent context overflow."
    )


async def get_page_content(
    input_data: GetPageContentToolInput,
    task_id: str
) -> ToolResult:
    """
    Extracts a simplified, LLM-friendly representation of the current page's DOM.
    """
    session = store.get_session(task_id)
    if not session:
        return ToolResult(success=False, error=f"No active session found for task {task_id}")

    # Python script to inject into the browser to extract the DOM
    # This script traverses the DOM and builds a simplified JSON structure
    # filtering out invisible elements and irrelevant attributes.
    script = """
async def extract_dom():
    try:
        # Check if page is available
        if 'page' not in locals() and 'page' not in globals():
            return {"error": "Page object not found in scope"}
            
        handle = await page.evaluate_handle('''
            () => {
                const importantAttributes = %s;
                
                function isVisible(element) {
                    if (!element) return false;
                    const style = window.getComputedStyle(element);
                    return style.display !== 'none' && 
                           style.visibility !== 'hidden' && 
                           style.opacity !== '0' &&
                           element.offsetWidth > 0 && 
                           element.offsetHeight > 0;
                }

                function traverse(node) {
                    if (node.nodeType === Node.TEXT_NODE) {
                        const text = node.textContent.trim();
                        return text ? text : null;
                    }

                    if (node.nodeType !== Node.ELEMENT_NODE) return null;

                    const element = node;
                    if (!isVisible(element)) return null;

                    const tagName = element.tagName.toLowerCase();
                    // Skip script, style, etc.
                    if (['script', 'style', 'noscript', 'meta', 'link'].includes(tagName)) return null;

                    const result = { tag: tagName };
                    
                    // Extract attributes
                    for (const attr of importantAttributes) {
                        if (element.hasAttribute(attr)) {
                            result[attr] = element.getAttribute(attr);
                        }
                    }
                    
                    // Specific handling for some elements
                    if (tagName === 'input' && element.value) {
                         result['value'] = element.value;
                    }

                    // Children
                    const children = [];
                    for (const child of element.childNodes) {
                        const childResult = traverse(child);
                        if (childResult) {
                            children.push(childResult);
                        }
                    }
                    
                    if (children.length > 0) {
                        result.children = children;
                    } else if (tagName === 'div' || tagName === 'span') {
                        // Filter out empty containers
                         // But keep if it has ID or meaningful attributes
                         if (Object.keys(result).length <= 1) return null;
                    }

                    return result;
                }

                return traverse(document.body);
            }
        ''')
        
        dom = await handle.json_value()
        import json
        print(json.dumps(dom))
        return dom
    except Exception as e:
        print(f"Error extracting DOM: {e}")
        return {"error": str(e)}

await extract_dom()
""" % (json.dumps(input_data.include_attributes))

    result = await session.add_cell(script)
    
    if not result.is_success:
        return ToolResult(
            success=False, 
            error=f"Runtime error: {result.error}",
            stdout=result.stdout
        )
    
    # Parse the output from stdout
    try:
        if result.stdout:
            # The last line should be the JSON
            lines = result.stdout.strip().split('\n')
            last_line = lines[-1]
            dom_data = json.loads(last_line)
            return ToolResult(success=True, result=dom_data, stdout=result.stdout)
        else:
             return ToolResult(success=False, error="No output received from DOM extraction", stdout=result.stdout)
    except json.JSONDecodeError:
        return ToolResult(
            success=False, 
            error="Failed to parse DOM JSON output", 
            stdout=result.stdout
        )


class RunPlaywrightCodeToolInput(BaseModel):
    """
    Input schema for RunPlaywrightCodeTool.
    """
    code: str = Field(
        ...,
        description="Python code to execute using Playwright. Use 'await page...' for interactions."
    )


async def run_playwright_code(
    input_data: RunPlaywrightCodeToolInput,
    task_id: str
) -> ToolResult:
    """
    Executes raw Playwright/Python code in the agent's session.
    """
    session = store.get_session(task_id)
    if not session:
        return ToolResult(success=False, error=f"No active session found for task {task_id}")

    # Wrap code to handle potential errors nicely? 
    # Or just let the session handle it.
    # We might want to ensure 'page' is available or import it?
    # The session is stateful, so imports should persist.
    
    result = await session.add_cell(input_data.code)
    
    if not result.is_success:
         return ToolResult(
            success=False, 
            error=str(result.error), # Convert error dict to string
            stdout=result.stdout
        )
        
    return ToolResult(
        success=True, 
        result=result.text_result, # Use text_result instead of result
        stdout=result.stdout
    )

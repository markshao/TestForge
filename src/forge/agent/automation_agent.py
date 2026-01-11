from typing import List, Dict, Any, Optional
from langchain_core.tools import StructuredTool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from ..llm import create_llm
from .tools import get_page_content, run_playwright_code, GetPageContentToolInput, RunPlaywrightCodeToolInput
from .prompts.automation import AUTOMATION_AGENT_SYSTEM_PROMPT

class AutomationAgent:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.llm = create_llm()
        self.tools = self._build_tools()
        
        # Create the ReAct agent using LangGraph
        # We pass the system prompt as the 'prompt' argument
        self.agent = create_react_agent(
            model=self.llm, 
            tools=self.tools, 
            prompt=AUTOMATION_AGENT_SYSTEM_PROMPT
        )

    def _build_tools(self) -> List[StructuredTool]:
        """
        Bind task_id to tools and wrap them as StructuredTool.
        """
        async def _get_page_content_wrapper(include_attributes: List[str] = None, max_length: int = 50000) -> str:
            """
            Get the current page content (DOM) as a simplified JSON tree.
            """
            input_data = GetPageContentToolInput(
                include_attributes=include_attributes or ["id", "name", "class", "role", "aria-label", "placeholder", "type", "href", "value", "data-testid"],
                max_length=max_length
            )
            result = await get_page_content(input_data, self.task_id)
            return result.model_dump_json()

        async def _run_playwright_code_wrapper(code: str) -> str:
            """
            Execute Python Playwright code.
            Example: await page.click('#submit-btn')
            """
            input_data = RunPlaywrightCodeToolInput(code=code)
            result = await run_playwright_code(input_data, self.task_id)
            return result.model_dump_json()

        return [
            StructuredTool.from_function(
                func=None,
                coroutine=_get_page_content_wrapper,
                name="get_page_content",
                description="Extracts the current page DOM to understand the UI structure. Returns JSON.",
                args_schema=GetPageContentToolInput
            ),
            StructuredTool.from_function(
                func=None,
                coroutine=_run_playwright_code_wrapper,
                name="run_playwright_code",
                description="Executes Playwright Python code to interact with the page. Returns execution result.",
                args_schema=RunPlaywrightCodeToolInput
            )
        ]

    async def run_step(self, step: str) -> Dict[str, Any]:
        """
        Execute a single automation step.
        """
        # invoke the graph
        inputs = {"messages": [HumanMessage(content=step)]}
        # We use ainvoke for async execution
        result = await self.agent.ainvoke(inputs)
        return result

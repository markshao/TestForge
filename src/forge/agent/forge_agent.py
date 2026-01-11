from typing import List, Dict, Any
from langchain_core.messages import HumanMessage
from deepagents import CompiledSubAgent, create_deep_agent
from loguru import logger

from ..llm import create_llm
from .automation_agent import AutomationAgent

class ForgeAgent:
    def __init__(self, task_id: str):
        """
        Initialize the ForgeAgent with a task_id.
        This agent uses a Planner-Agent architecture (via deepagents) to execute test steps.
        """
        self.task_id = task_id
        self.llm = create_llm()
        
        # Initialize the specialized Automation SubAgent
        self.automation_subagent = AutomationAgent(task_id)
        
        # Create the high-level Deep Agent (Planner + SubAgents)
        # The Planner will break down the user's request (test steps) into tasks
        # and delegate them to the appropriate subagent.
        self.agent = create_deep_agent(
            model=self.llm,
            subagents=[
                CompiledSubAgent(
                    name="automation_expert",
                    description="A specialized agent for executing browser automation steps on web pages. Capabilities include searching, clicking, typing, and extracting content.",
                    runnable=self.automation_subagent.agent
                )
            ]
        )

    async def run(self, steps: List[str]) -> Dict[str, Any]:
        """
        Run the agent with a list of test steps.
        
        Args:
            steps: A list of natural language strings describing the test steps.
                   Example: ["Open baidu.com", "Search for 'pinduoduo'"]
        
        Returns:
            The final state of the agent execution.
        """
        # 1. Construct the goal from steps
        goal_text = "Execute the following browser automation test plan strictly step-by-step:\n\n"
        for i, step in enumerate(steps, 1):
            goal_text += f"{i}. {step}\n"
        
        goal_text += "\nFor each step, verify the execution before moving to the next."

        logger.info(f"ForgeAgent [{self.task_id}] Goal constructed:\n{goal_text}")

        # 2. Invoke the Deep Agent
        # The agent will:
        # - Plan: Break down the goal into tasks (mapping to steps)
        # - Execute: Delegate each task to 'automation_expert'
        # - Verify: (Implicit in the ReAct loop of the subagent)
        
        inputs = {"messages": [HumanMessage(content=goal_text)]}
        
        logger.info(f"ForgeAgent [{self.task_id}] Starting DeepAgent execution...")

        # Use ainvoke to run the graph
        result = await self.agent.ainvoke(inputs)
        
        logger.info(f"ForgeAgent [{self.task_id}] Execution finished.")
        return result

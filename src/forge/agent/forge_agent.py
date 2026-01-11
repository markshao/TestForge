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

    async def run(self, steps: List[str], step_callback=None) -> Dict[str, Any]:
        """
        Run the agent with a list of test steps.
        
        Args:
            steps: A list of natural language strings describing the test steps.
            step_callback: Async callback function(index, step_content) called before each step.
        """
        # Since deepagents controls the loop, we can't easily hook into EXACT step boundaries 
        # unless we customize the graph or the subagent.
        # However, for this requirement, we can manually iterate steps and invoke the subagent directly
        # or use a simplified approach where ForgeAgent manages the loop instead of delegating planning to DeepAgent.
        # Given the requirement "ForgeAgent accepts steps and calls subagent", and we want explicit control over screenshots per step:
        
        # Let's iterate manually for precise control over screenshots and status updates
        logger.info(f"ForgeAgent [{self.task_id}] Starting Manual Execution Loop for {len(steps)} steps.")
        
        final_result = {}
        
        for i, step in enumerate(steps):
            logger.info(f"ForgeAgent [{self.task_id}] Executing Step {i+1}: {step}")
            
            # Notify start of step
            if step_callback:
                await step_callback(i, "running")
            
            try:
                # Direct invocation of subagent for the step
                # We wrap the step in a message
                step_input = {"messages": [HumanMessage(content=f"Execute this step: {step}")]}
                result = await self.automation_subagent.agent.ainvoke(step_input)
                final_result = result
                
                # Notify completion of step
                if step_callback:
                    await step_callback(i, "completed")
                    
            except Exception as e:
                logger.error(f"ForgeAgent [{self.task_id}] Step {i+1} failed: {e}")
                if step_callback:
                    await step_callback(i, "error")
                raise e

        logger.info(f"ForgeAgent [{self.task_id}] Execution finished.")
        return final_result

"""
Project Manager Agent - Coordinates the multi-agent workflow for blockchain analysis.
Acts as the supervisor agent that delegates tasks to specialized agents.
"""

from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from ..schemas.state import AnalysisState
from ..utils.agent_utils import create_handoff_tool, create_system_message
import logging

logger = logging.getLogger(__name__)


class ProjectManagerAgent:
    """
    Senior Project Manager specializing in blockchain analytics projects.
    Orchestrates workflow, manages crew progress, validates outputs.
    """

    def __init__(self, model_name: str = "gpt-4"):
        self.model = ChatOpenAI(model=model_name, temperature=0.1)
        self.name = "project_manager"

        # Create handoff tools for task delegation
        self.assign_to_revenue_agent = create_handoff_tool(
            agent_name="blockchain_revenue_agent",
            description="Assign blockchain revenue analysis tasks to the specialized agent."
        )

        self.assign_to_strategic_agent = create_handoff_tool(
            agent_name="strategic_editor_agent", 
            description="Assign strategic synthesis tasks to the strategic editor."
        )

        self.tools = [self.assign_to_revenue_agent, self.assign_to_strategic_agent]

        # Create the agent using LangGraph's prebuilt function
        self.agent = create_react_agent(
            model=self.model,
            tools=self.tools,
            prompt=self._get_system_prompt(),
            name=self.name
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the project manager agent"""
        return """You are a Senior Project Manager specializing in blockchain analytics projects.

RESPONSIBILITIES:
- Orchestrate the complete workflow for blockchain revenue analysis
- Delegate tasks to specialized agents in the correct order
- Validate that all required inputs are provided
- Ensure quality and completeness of outputs
- Coordinate between category analysis and contract analysis phases

WORKFLOW MANAGEMENT:
1. First, delegate category analysis for all blockchains to the blockchain_revenue_agent
2. Once category analysis is complete, delegate contract analysis to the blockchain_revenue_agent  
3. After both analyses are complete, delegate strategic synthesis to the strategic_editor_agent
4. Validate final outputs meet quality standards

DELEGATION RULES:
- Assign work to one agent at a time - do not call agents in parallel
- Provide clear, detailed task descriptions to each agent
- Include all necessary context and parameters
- Do not perform any technical analysis yourself - delegate to specialists
- Always validate inputs before delegation

You manage agents with different specializations:
- blockchain_revenue_agent: Handles all blockchain data analysis tasks
- strategic_editor_agent: Synthesizes analysis into strategic insights

Be systematic, thorough, and ensure all deliverables meet high standards."""

    def __call__(self, state: AnalysisState) -> Dict[str, Any]:
        """Execute the project manager logic"""
        try:
            logger.info("Project Manager: Starting workflow coordination")

            # Prepare input for the agent
            messages = [
                HumanMessage(content=f"""Please coordinate the blockchain analysis workflow:

Blockchains to analyze: {', '.join(state['blockchain_names'])}
Timeframe: {state['timeframe']}
Current task: {state.get('current_task', 'initial')}

Please delegate the appropriate tasks to the specialized agents following the workflow order.""")
            ]
           
            # Execute the agent
            response = self.agent.invoke({"messages": messages})
            # Update state
            updated_state = state.copy()
            updated_state["messages"] = response["messages"]

            # Only set to 'delegating' if current_task is not already a specific analysis task
            if state.get("current_task", "initial") == "delegating":
                # Already delegating, don't overwrite
                pass
            elif "analysis" in state.get("current_task", "") or "synthesis" in state.get("current_task", ""):
                # Already in a specific task, don't overwrite
                pass
            else:
                updated_state["current_task"] = "delegating"

            logger.info("Project Manager: Workflow coordination initiated")
            return updated_state

        except Exception as e:
            logger.error(f"Project Manager error: {str(e)}")
            updated_state = state.copy()
            updated_state["errors"].append(f"Project Manager: {str(e)}")
            return updated_state
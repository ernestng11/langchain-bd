"""
Main LangGraph orchestration system for the blockchain revenue analysis workflow.
Implements the multi-agent supervisor architecture with task delegation.
"""

from typing import Dict, Any, Literal
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent

from .agents.project_manager import ProjectManagerAgent
from .agents.blockchain_revenue_agent import BlockchainRevenueAgent  
from .agents.strategic_editor_agent import StrategicEditorAgent
from .schemas.state import AnalysisState
from .utils.agent_utils import validate_state_inputs, should_continue_analysis, create_error_state
import logging

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


class OnchainAnalysisWorkflow:
    """
    Multi-agent workflow for blockchain revenue analysis and competitive intelligence.
    Implements supervisor architecture with specialized agents.
    """

    def __init__(self, model_name: str = "gpt-4"):
        """
        Initialize the workflow with agents and graph structure.

        Args:
            model_name: LLM model to use for agents
        """
        self.model_name = model_name

        # Initialize agents
        self.project_manager = ProjectManagerAgent(model_name)
        self.blockchain_revenue_agent = BlockchainRevenueAgent(model_name)
        self.strategic_editor_agent = StrategicEditorAgent(model_name)

        # Build the workflow graph
        self.workflow = self._build_workflow()

        logger.info("OnchainAnalysisWorkflow initialized successfully")

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow structure"""

        # Create the state graph
        workflow = StateGraph(AnalysisState)

        # Add agent nodes
        workflow.add_node("project_manager", self._run_project_manager)
        workflow.add_node("blockchain_revenue_agent", self._run_blockchain_revenue_agent)
        workflow.add_node("strategic_editor_agent", self._run_strategic_editor_agent)
        workflow.add_node("validator", self._validate_inputs)

        # Set entry point
        workflow.add_edge(START, "validator")

        # Add conditional routing from validator
        workflow.add_conditional_edges(
            "validator",
            self._should_proceed_from_validation,
            {
                "proceed": "project_manager",
                "error": END
            }
        )

        # Add conditional routing from project manager
        workflow.add_conditional_edges(
            "project_manager", 
            self._route_from_project_manager,
            {
                "blockchain_revenue_agent": "blockchain_revenue_agent",
                "strategic_editor_agent": "strategic_editor_agent", 
                "end": END
            }
        )

        # Revenue agent routes back to project manager
        workflow.add_edge("blockchain_revenue_agent", "project_manager")

        # Strategic editor routes to end
        workflow.add_edge("strategic_editor_agent", END)

        return workflow

    def _run_project_manager(self, state: AnalysisState) -> AnalysisState:
        """Execute the project manager agent"""
        try:
            logger.info("Executing Project Manager")
            result = self.project_manager(state)
            logger.info("Project Manager completed successfully")
            return result
        except Exception as e:
            logger.error(f"Project Manager execution failed: {str(e)}")
            return create_error_state(state, str(e), "project_manager")

    def _run_blockchain_revenue_agent(self, state: AnalysisState) -> AnalysisState:
        """Execute the blockchain revenue agent"""
        try:
            logger.info("Executing Blockchain Revenue Agent")
            result = self.blockchain_revenue_agent(state)
            logger.info("Blockchain Revenue Agent completed successfully")
            return result
        except Exception as e:
            logger.error(f"Blockchain Revenue Agent execution failed: {str(e)}")
            return create_error_state(state, str(e), "blockchain_revenue_agent")

    def _run_strategic_editor_agent(self, state: AnalysisState) -> AnalysisState:
        """Execute the strategic editor agent"""
        try:
            logger.info("Executing Strategic Editor Agent")
            result = self.strategic_editor_agent(state)
            logger.info("Strategic Editor Agent completed successfully")
            return result
        except Exception as e:
            logger.error(f"Strategic Editor Agent execution failed: {str(e)}")
            return create_error_state(state, str(e), "strategic_editor_agent")

    def _validate_inputs(self, state: AnalysisState) -> AnalysisState:
        """Validate input parameters before processing"""
        logger.info("Validating input parameters")

        is_valid, errors = validate_state_inputs(state)

        if not is_valid:
            logger.error(f"Input validation failed: {errors}")
            error_state = create_error_state(state, f"Input validation failed: {', '.join(errors)}", "validator")
            return error_state

        # Initialize state fields if not present
        updated_state = state.copy()
        updated_state.setdefault("category_reports", [])
        updated_state.setdefault("contract_reports", [])
        updated_state.setdefault("strategic_synthesis", None)
        updated_state.setdefault("errors", [])
        updated_state.setdefault("messages", [])
        updated_state.setdefault("metadata", {})
        updated_state.setdefault("current_task", "validated")

        logger.info("Input validation passed")
        return updated_state

    def _should_proceed_from_validation(self, state: AnalysisState) -> Literal["proceed", "error"]:
        """Determine if workflow should proceed after validation"""
        if state.get("errors"):
            return "error"
        return "proceed"

    def _route_from_project_manager(self, state: AnalysisState) -> Literal["blockchain_revenue_agent", "strategic_editor_agent", "end"]:
        """Route from project manager based on current task state"""
        current_task = state.get("current_task", "")

        # Check for errors
        if state.get("errors"):
            logger.warning(f"Errors detected, ending workflow: {state['errors']}")
            return "end"

        # Check completion status
        has_category_reports = bool(state.get("category_reports"))
        has_contract_reports = bool(state.get("contract_reports"))
        has_synthesis = bool(state.get("strategic_synthesis"))

        # Route to strategic editor if both analyses are complete
        if has_category_reports and has_contract_reports and not has_synthesis:
            logger.info("Routing to Strategic Editor Agent for synthesis")
            return "strategic_editor_agent"

        # Route to blockchain revenue agent if analysis not complete
        if not has_category_reports or not has_contract_reports:
            logger.info("Routing to Blockchain Revenue Agent for analysis")
            return "blockchain_revenue_agent"

        # End if everything is complete
        if has_synthesis:
            logger.info("All analysis complete, ending workflow")
            return "end"

        # Default to blockchain revenue agent
        logger.info("Default routing to Blockchain Revenue Agent")
        return "blockchain_revenue_agent"

    def compile(self):
        """Compile the workflow for execution"""
        compiled_workflow = self.workflow.compile()
        logger.info("Workflow compiled successfully")
        return compiled_workflow

    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the complete workflow with input data.

        Args:
            input_data: Dictionary containing blockchain_names and timeframe

        Returns:
            Complete analysis results including all reports
        """
        try:
            logger.info(f"Starting workflow execution with input: {input_data}")

            # Create initial state
            initial_state = AnalysisState(
                blockchain_names=input_data.get("blockchain_names", []),
                timeframe=input_data.get("timeframe", "7d"),
                category_reports=[],
                contract_reports=[],
                strategic_synthesis=None,
                current_task="initial",
                errors=[],
                messages=[],
                metadata=input_data.get("metadata", {})
            )

            # Compile and execute workflow
            compiled_workflow = self.compile()
            result = compiled_workflow.invoke(initial_state)

            logger.info("Workflow execution completed successfully")
            return result

        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            return {
                "errors": [f"Workflow execution failed: {str(e)}"],
                "success": False
            }

    async def ainvoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asynchronously execute the complete workflow.

        Args:
            input_data: Dictionary containing blockchain_names and timeframe

        Returns:
            Complete analysis results including all reports
        """
        try:
            logger.info(f"Starting async workflow execution with input: {input_data}")

            # Create initial state
            initial_state = AnalysisState(
                blockchain_names=input_data.get("blockchain_names", []),
                timeframe=input_data.get("timeframe", "7d"),
                category_reports=[],
                contract_reports=[],
                strategic_synthesis=None,
                current_task="initial",
                errors=[],
                messages=[],
                metadata=input_data.get("metadata", {})
            )

            # Compile and execute workflow
            compiled_workflow = self.compile()
            result = await compiled_workflow.ainvoke(initial_state)

            logger.info("Async workflow execution completed successfully")
            return result

        except Exception as e:
            logger.error(f"Async workflow execution failed: {str(e)}")
            return {
                "errors": [f"Async workflow execution failed: {str(e)}"],
                "success": False
            }

    def stream(self, input_data: Dict[str, Any]):
        """
        Stream workflow execution for real-time updates.

        Args:
            input_data: Dictionary containing blockchain_names and timeframe

        Yields:
            Incremental workflow updates
        """
        try:
            logger.info(f"Starting streaming workflow execution with input: {input_data}")

            # Create initial state  
            initial_state = AnalysisState(
                blockchain_names=input_data.get("blockchain_names", []),
                timeframe=input_data.get("timeframe", "7d"),
                category_reports=[],
                contract_reports=[],
                strategic_synthesis=None,
                current_task="initial",
                errors=[],
                messages=[],
                metadata=input_data.get("metadata", {})
            )

            # Compile and stream workflow
            compiled_workflow = self.compile()

            for update in compiled_workflow.stream(initial_state):
                yield update

        except Exception as e:
            logger.error(f"Streaming workflow execution failed: {str(e)}")
            yield {
                "errors": [f"Streaming workflow execution failed: {str(e)}"],
                "success": False
            }

    def visualize(self) -> str:
        """
        Generate a visual representation of the workflow graph.

        Returns:
            Path to the generated graph image
        """
        try:
            compiled_workflow = self.compile()
            graph_image = compiled_workflow.get_graph().draw_mermaid_png()

            # Save the image
            image_path = "workflow_graph.png"
            with open(image_path, "wb") as f:
                f.write(graph_image)

            logger.info(f"Workflow graph saved to {image_path}")
            return image_path

        except Exception as e:
            logger.error(f"Graph visualization failed: {str(e)}")
            return None


# Factory function for easy workflow creation
def create_onchain_analysis_workflow(model_name: str = "gpt-4") -> OnchainAnalysisWorkflow:
    """
    Factory function to create and configure the onchain analysis workflow.

    Args:
        model_name: LLM model to use for agents

    Returns:
        Configured OnchainAnalysisWorkflow instance
    """
    return OnchainAnalysisWorkflow(model_name=model_name)


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create workflow
    workflow = create_onchain_analysis_workflow()

    # Example input
    test_input = {
        "blockchain_names": ["ethereum", "arbitrum"],
        "timeframe": "7d",
        "metadata": {
            "analysis_type": "competitive_intelligence",
            "requested_by": "strategy_team"
        }
    }

    # Execute workflow
    result = workflow.invoke(test_input)

    print("Workflow execution completed!")
    print(f"Errors: {result.get('errors', [])}")
    print(f"Strategic synthesis available: {bool(result.get('strategic_synthesis'))}")
"""
Utility functions for agent communication, handoffs, and system operations.
Implements the handoff mechanisms following LangGraph patterns.
"""

from typing import Annotated, Dict, Any, Callable
from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from ..schemas.state import AnalysisState
import logging

logger = logging.getLogger(__name__)


def create_handoff_tool(*, agent_name: str, description: str = None) -> Callable:
    """
    Create a handoff tool for agent-to-agent communication.

    Args:
        agent_name: Name of the target agent to hand off to
        description: Description of what this handoff tool does

    Returns:
        Tool function for handing off to the specified agent
    """
    name = f"transfer_to_{agent_name}"
    description = description or f"Transfer control to {agent_name}"

    @tool(name, description=description)
    def handoff_tool(
        task_description: Annotated[
            str,
            "Description of the task for the next agent, including all relevant context."
        ],
        state: Annotated[AnalysisState, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        """Execute handoff to target agent"""
        try:
            logger.info(f"Handing off to {agent_name}: {task_description}")

            # Create tool message for successful transfer
            tool_message = {
                "role": "tool",
                "content": f"Successfully transferred to {agent_name}",
                "name": name,
                "tool_call_id": tool_call_id,
            }

            # Create task message for the target agent
            task_message = HumanMessage(content=task_description)

            # Update state for handoff
            updated_state = state.copy()
            updated_state["messages"] = state.get("messages", []) + [tool_message]
            updated_state["current_task"] = f"handed_off_to_{agent_name}"

            return Command(
                goto=agent_name,
                update={**updated_state, "messages": [task_message]},
                graph=Command.PARENT,
            )

        except Exception as e:
            logger.error(f"Handoff error to {agent_name}: {str(e)}")
            error_message = {
                "role": "tool",
                "content": f"Error transferring to {agent_name}: {str(e)}",
                "name": name,
                "tool_call_id": tool_call_id,
            }

            updated_state = state.copy()
            updated_state["errors"] = state.get("errors", []) + [f"Handoff to {agent_name}: {str(e)}"]
            updated_state["messages"] = state.get("messages", []) + [error_message]

            return Command(
                goto=agent_name,
                update=updated_state,
                graph=Command.PARENT,
            )

    return handoff_tool


def create_system_message(role: str, capabilities: list, instructions: list) -> SystemMessage:
    """
    Create a standardized system message for agents.

    Args:
        role: The agent's role description
        capabilities: List of agent capabilities
        instructions: List of specific instructions

    Returns:
        SystemMessage object with formatted content
    """
    content = f"You are a {role}.\n\n"

    if capabilities:
        content += "CAPABILITIES:\n"
        for capability in capabilities:
            content += f"- {capability}\n"
        content += "\n"

    if instructions:
        content += "INSTRUCTIONS:\n"
        for instruction in instructions:
            content += f"- {instruction}\n"
        content += "\n"

    content += "Always respond professionally and focus on your specialized expertise."

    return SystemMessage(content=content)


def validate_state_inputs(state: AnalysisState) -> tuple[bool, list]:
    """
    Validate that the state has all required inputs for processing.

    Args:
        state: The analysis state to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Check required fields
    if not state.get("blockchain_names"):
        errors.append("blockchain_names is required")
    elif not isinstance(state["blockchain_names"], list) or len(state["blockchain_names"]) == 0:
        errors.append("blockchain_names must be a non-empty list")

    if not state.get("timeframe"):
        errors.append("timeframe is required")
    elif state["timeframe"] not in ["1d", "7d", "30d", "historical", "trend"]:
        errors.append("timeframe must be one of: 1d, 7d, 30d, historical, trend")

    # Validate blockchain names
    supported_blockchains = ['base', 'mantle', 'arbitrum', 'optimism']
    if state.get("blockchain_names"):
        for blockchain in state["blockchain_names"]:
            if blockchain.lower() not in supported_blockchains:
                errors.append(f"Unsupported blockchain: {blockchain}. Supported: {', '.join(supported_blockchains)}")

    return len(errors) == 0, errors


def format_agent_response(agent_name: str, success: bool, data: Any = None, error: str = None) -> Dict[str, Any]:
    """
    Format standardized agent response.

    Args:
        agent_name: Name of the responding agent
        success: Whether the operation was successful
        data: Response data (if successful)
        error: Error message (if unsuccessful)

    Returns:
        Formatted response dictionary
    """
    response = {
        "agent": agent_name,
        "success": success,
        "timestamp": logging.time.time()
    }

    if success and data is not None:
        response["data"] = data

    if not success and error:
        response["error"] = error

    return response


def extract_task_parameters(message_content: str) -> Dict[str, Any]:
    """
    Extract task parameters from message content.

    Args:
        message_content: The message content to parse

    Returns:
        Dictionary of extracted parameters
    """
    parameters = {}

    # Simple parameter extraction (can be enhanced with more sophisticated parsing)
    lines = message_content.split("\n")

    for line in lines:
        if "blockchains:" in line.lower() or "blockchain:" in line.lower():
            # Extract blockchain names
            parts = line.split(":")
            if len(parts) > 1:
                blockchain_text = parts[1].strip()
                blockchains = [b.strip() for b in blockchain_text.split(",")]
                parameters["blockchain_names"] = blockchains

        elif "timeframe:" in line.lower():
            # Extract timeframe
            parts = line.split(":")
            if len(parts) > 1:
                parameters["timeframe"] = parts[1].strip()

    return parameters


def create_error_state(state: AnalysisState, error: str, agent: str = "system") -> AnalysisState:
    """
    Create an error state with the given error message.

    Args:
        state: Current state
        error: Error message
        agent: Agent that encountered the error

    Returns:
        Updated state with error information
    """
    updated_state = state.copy()
    updated_state["errors"] = updated_state.get("errors", []) + [f"{agent}: {error}"]
    updated_state["current_task"] = "error"

    return updated_state


def should_continue_analysis(state: AnalysisState) -> bool:
    """
    Determine if analysis should continue based on current state.

    Args:
        state: Current analysis state

    Returns:
        True if analysis should continue, False if complete or error
    """
    # Stop if there are errors
    if state.get("errors"):
        return False

    # Stop if synthesis is complete
    if state.get("strategic_synthesis") is not None:
        return False

    # Continue if we haven't completed all phases
    current_task = state.get("current_task", "")

    if "complete" not in current_task:
        return True

    # Check if all required reports are present
    has_category_reports = bool(state.get("category_reports"))
    has_contract_reports = bool(state.get("contract_reports"))
    has_synthesis = bool(state.get("strategic_synthesis"))

    return not (has_category_reports and has_contract_reports and has_synthesis)


class AgentMetrics:
    """Simple metrics tracking for agent performance"""

    def __init__(self):
        self.metrics = {}

    def record_execution(self, agent_name: str, success: bool, duration: float):
        """Record agent execution metrics"""
        if agent_name not in self.metrics:
            self.metrics[agent_name] = {
                "executions": 0,
                "successes": 0,
                "total_duration": 0.0
            }

        self.metrics[agent_name]["executions"] += 1
        self.metrics[agent_name]["total_duration"] += duration

        if success:
            self.metrics[agent_name]["successes"] += 1

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        summary = {}

        for agent_name, metrics in self.metrics.items():
            summary[agent_name] = {
                "success_rate": metrics["successes"] / metrics["executions"] if metrics["executions"] > 0 else 0,
                "avg_duration": metrics["total_duration"] / metrics["executions"] if metrics["executions"] > 0 else 0,
                "total_executions": metrics["executions"]
            }

        return summary


# Global metrics instance
agent_metrics = AgentMetrics()
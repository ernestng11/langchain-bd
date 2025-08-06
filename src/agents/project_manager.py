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

    def analyze_trend_results(self, trend_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trend results to identify categories with significant changes"""
        try:
            logger.info("🧠 Project Manager: Analyzing trend results for significant changes")
            logger.info("=" * 50)
            
            combined_analysis = trend_analysis.get("combined_analysis", "")
            chronological_order = trend_analysis.get("chronological_order", [])
            
            logger.info(f"📊 Analyzing combined analysis for trends...")
            logger.info(f"⏰ Chronological order: {chronological_order}")
            
            # Use LLM to analyze the combined analysis and identify significant categories
            analysis_prompt = f"""Analyze this historical blockchain data analysis and identify categories with significant changes:

Chronological Order: {chronological_order}
Combined Analysis: {combined_analysis}

Identify categories that show:
1. Significant growth or decline trends
2. Major changes in market share

Return ONLY a JSON list of category names (e.g., ["defi", "social"]) that show significant changes and warrant contract analysis.
Focus on categories that have meaningful trends, not just noise."""

            response = self.model.invoke(analysis_prompt)
            
            # Parse the response to extract category names
            try:
                import json
                target_categories = json.loads(response.content.strip())
                if not isinstance(target_categories, list):
                    target_categories = ["defi"]  # Default fallback
            except:
                # Fallback parsing if JSON fails
                content = response.content.lower()
                target_categories = []
                if "defi" in content:
                    target_categories.append("defi")
                if "social" in content:
                    target_categories.append("social")
                if "nft" in content:
                    target_categories.append("nft")
                if "cefi" in content:
                    target_categories.append("cefi")
                if not target_categories:
                    target_categories = ["defi"]  # Default fallback

            insights = {
                "target_categories": target_categories,
                "analysis_reasoning": response.content,
                "chronological_order": chronological_order,
                "combined_analysis": combined_analysis
            }

            logger.info(f"🎯 Identified target categories: {target_categories}")
            logger.info(f"📝 Analysis reasoning: {response.content[:200]}...")
            logger.info("=" * 50)
            return insights

        except Exception as e:
            logger.error(f"Project Manager: Error analyzing trend results: {str(e)}")
            return {
                "target_categories": ["defi"],  # Default fallback
                "analysis_reasoning": f"Error in analysis: {str(e)}",
                "chronological_order": [],
                "combined_analysis": ""
            }

    def __call__(self, state: AnalysisState) -> Dict[str, Any]:
        """Execute the project manager logic"""
        try:
            logger.info("Project Manager: Starting workflow coordination")

                        # Check if we need to analyze trend results
            if state.get("growthepie_analysis") and not state.get("growthepie_insights"):
                logger.info("Project Manager: Analyzing trend results for target categories")
                trend_insights = self.analyze_trend_results(state["growthepie_analysis"])
                
                updated_state = state.copy()
                updated_state["growthepie_insights"] = trend_insights
                updated_state["target_categories"] = trend_insights["target_categories"]
                updated_state["current_task"] = "trend_analysis_analyzed"
                
                logger.info("Project Manager: Trend analysis completed, ready for targeted contract analysis")
                return updated_state

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
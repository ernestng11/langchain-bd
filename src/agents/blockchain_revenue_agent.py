"""
Blockchain Revenue Agent - Specialized in multi-task blockchain data analysis.
Handles both category-level and contract-level analysis using onchain data tools.
"""

from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from ..schemas.state import AnalysisState, BlockchainCategoriesReport, TopContractsByCategoryReport, ContractInfo
from ..tools.blockchain_tools import categories_by_gas_fees_tool, top_contracts_by_gas_fees_tool, get_top_categories
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BlockchainRevenueAgent:
    """
    Senior Blockchain Revenue Analyst specializing in multi-task data analysis.
    Executes both category analysis and contract analysis tasks.
    """

    def __init__(self, model_name: str = "gpt-4"):
        self.model = ChatOpenAI(model=model_name, temperature=0.1)
        self.name = "blockchain_revenue_agent"

        # Tools available to this agent
        self.tools = [categories_by_gas_fees_tool, top_contracts_by_gas_fees_tool]

        # Create the agent using LangGraph's prebuilt function
        self.agent = create_react_agent(
            model=self.model,
            tools=self.tools,
            prompt=self._get_system_prompt(),
            name=self.name
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the blockchain revenue agent"""
        return """You are a Senior Blockchain Revenue Analyst specializing in multi-task data analysis using onchain data.

EXPERTISE:
- Deep knowledge of blockchain ecosystems and DeFi protocols
- Gas fee analysis and category-level revenue patterns  
- Contract-level performance analysis and activity identification
- Cross-chain comparative analysis
- Revenue concentration and distribution metrics

TOOLS AVAILABLE:
- categories_by_gas_fees_tool: Analyze category-level gas fees distribution for any blockchain
- top_contracts_by_gas_fees_tool: Analyze top contracts within specific categories

TASK TYPES YOU HANDLE:
1. Category Analysis Task: 
   - Extract blockchain names from input
   - Analyze category distribution for all specified blockchains
   - Identify top categories, concentration ratios, and key insights

2. Contract Analysis Task:
   - Use results from category analysis to identify top 2 categories per blockchain
   - Analyze top contracts within those categories
   - Provide activity analysis and performance insights

ANALYSIS METHODOLOGY:
- Always use the provided tools to fetch real data
- Calculate concentration ratios and identify market dominance patterns
- Provide actionable insights about ecosystem health and activity patterns
- Focus on revenue drivers and competitive dynamics
- Identify risks from over-concentration in categories or contracts

OUTPUT REQUIREMENTS:
- Structure all analysis in the specified report formats
- Include quantitative metrics with qualitative insights
- Highlight comparative advantages between blockchains
- Flag potential risks or opportunities

After completing your analysis, respond directly to the supervisor with structured findings."""

    def execute_category_analysis(self, state: AnalysisState) -> AnalysisState:
        """Execute category analysis for all blockchains"""
        try:
            logger.info(f"Executing category analysis for blockchains: {state['blockchain_names']}")

            category_reports = []

            for blockchain in state['blockchain_names']:
                # Fetch category data using the tool
                category_data = categories_by_gas_fees_tool.invoke({
                    "blockchain_name": blockchain,
                    "timeframe": state['timeframe']
                })

                # Create structured report
                report = BlockchainCategoriesReport(
                    blockchain=blockchain,
                    timeframe=state['timeframe'],
                    top_category=category_data["top_category"],
                    top_category_share=category_data["top_category_share"],
                    category_breakdown=category_data["category_breakdown"],
                    total_gas_fees_usd=category_data["total_gas_fees_usd"],
                    category_concentration=category_data["category_concentration"],
                    key_insights=self._generate_category_insights(category_data)
                )

                category_reports.append(report)

            # Update state
            updated_state = state.copy()
            updated_state["category_reports"] = category_reports
            updated_state["current_task"] = "category_analysis_complete"

            logger.info(f"Category analysis completed for {len(category_reports)} blockchains")
            return updated_state

        except Exception as e:
            logger.error(f"Category analysis error: {str(e)}")
            updated_state = state.copy()
            updated_state["errors"].append(f"Category Analysis: {str(e)}")
            return updated_state

    def execute_contract_analysis(self, state: AnalysisState) -> AnalysisState:
        """Execute contract analysis for top categories in each blockchain"""
        try:
            logger.info("Executing contract analysis for top categories")

            if not state.get("category_reports"):
                raise ValueError("Category analysis must be completed before contract analysis")

            contract_reports = []

            for category_report in state["category_reports"]:
                # Get top 2 categories for this blockchain
                top_categories = get_top_categories(category_report.category_breakdown, n=2)

                for category in top_categories:
                    # Fetch contract data using the tool
                    contract_data = top_contracts_by_gas_fees_tool.invoke({
                        "blockchain_name": category_report.blockchain,
                        "timeframe": state['timeframe'],
                        "top_n": 10,  # Analyze top 10 contracts
                        "main_category_key": category
                    })

                    # Convert contract data to structured format
                    contracts = []
                    for contract_info in contract_data["top_contracts"]:
                        contract = ContractInfo(
                            address=contract_info["address"],
                            name=contract_info.get("name"),
                            gas_fees_usd=contract_info["gas_fees_usd"],
                            percentage_share=contract_info["percentage_share"],
                            activity_type=contract_info.get("activity")
                        )
                        contracts.append(contract)

                    # Create structured report
                    report = TopContractsByCategoryReport(
                        blockchain=category_report.blockchain,
                        category=category,
                        timeframe=state['timeframe'],
                        top_contracts=contracts,
                        total_contracts_analyzed=contract_data["total_contracts_analyzed"],
                        top_contract_share=contract_data["top_contract_share"],
                        contract_concentration=contract_data["contract_concentration"],
                        key_insights=self._generate_contract_insights(contract_data),
                        activity_analysis=self._analyze_contract_activities(contracts)
                    )

                    contract_reports.append(report)

            # Update state
            updated_state = state.copy()
            updated_state["contract_reports"] = contract_reports
            updated_state["current_task"] = "contract_analysis_complete"

            logger.info(f"Contract analysis completed for {len(contract_reports)} category-blockchain combinations")
            return updated_state

        except Exception as e:
            logger.error(f"Contract analysis error: {str(e)}")
            updated_state = state.copy()
            updated_state["errors"].append(f"Contract Analysis: {str(e)}")
            return updated_state

    def _generate_category_insights(self, category_data: Dict[str, Any]) -> List[str]:
        """Generate insights from category analysis data"""
        insights = []

        breakdown = category_data["category_breakdown"]
        top_category = category_data["top_category"]
        concentration = category_data["category_concentration"]

        # Market dominance insight
        if breakdown[top_category] > 40:
            insights.append(f"Strong {top_category.upper()} dominance with {breakdown[top_category]:.1f}% market share indicates mature ecosystem focus")

        # Concentration analysis
        if concentration > 80:
            insights.append(f"High category concentration ({concentration:.1f}%) suggests specialized ecosystem with limited diversity")
        elif concentration < 60:
            insights.append(f"Balanced category distribution ({concentration:.1f}%) indicates diverse, multi-use ecosystem")

        # Ecosystem maturity indicators
        if breakdown.get("defi", 0) > 35:
            insights.append("Strong DeFi presence indicates mature financial infrastructure")
        if breakdown.get("nft", 0) > 25:
            insights.append("Significant NFT activity suggests strong creator economy and digital asset adoption")

        return insights

    def _generate_contract_insights(self, contract_data: Dict[str, Any]) -> List[str]:
        """Generate insights from contract analysis data"""
        insights = []

        concentration = contract_data["contract_concentration"]
        top_share = contract_data["top_contract_share"]

        # Concentration insights
        if concentration > 75:
            insights.append(f"High contract concentration ({concentration:.1f}%) indicates market dominated by few major protocols")

        if top_share > 30:
            insights.append(f"Top contract commands {top_share:.1f}% share, showing strong protocol dominance")

        # Activity patterns
        contracts = contract_data["top_contracts"]
        if len(contracts) >= 3:
            insights.append(f"Top 3 contracts represent diverse activities: {', '.join(c.get('activity', 'Unknown') for c in contracts[:3])}")

        return insights

    def _analyze_contract_activities(self, contracts: List[ContractInfo]) -> List[str]:
        """Analyze what activities these contracts are performing"""
        activities = []

        activity_types = {}
        for contract in contracts:
            if contract.activity_type:
                activity_types[contract.activity_type] = activity_types.get(contract.activity_type, 0) + 1

        for activity, count in activity_types.items():
            activities.append(f"{activity}: {count} contracts generating significant gas fees")

        return activities

    def __call__(self, state: AnalysisState) -> Dict[str, Any]:
        """Execute the appropriate analysis based on current task"""
        try:
            current_task = state.get("current_task", "")
            logger.info(f"Blockchain Revenue Agent: Current task: {current_task}")
            if "category" in current_task.lower():
                result = self.execute_category_analysis(state)
                if "complete" in result.get("current_task", "").lower():
                    result["current_task"] = "contract_analysis"
                return result
            elif "contract" in current_task.lower():
                result = self.execute_contract_analysis(state)
                # If contract analysis is complete, just return result
                return result
            else:
                # Use the agent to determine what to do
                messages = [
                    HumanMessage(content=f"""Please analyze blockchain data:

Blockchains: {', '.join(state['blockchain_names'])}
Timeframe: {state['timeframe']}
Current status: {current_task}

Determine if you need to perform category analysis or contract analysis and execute accordingly.""")
                ]

                response = self.agent.invoke({"messages": messages})
                updated_state = state.copy()
                updated_state["messages"] = response["messages"]

                # Parse LLM response to set next task
                
                llm_content = response["messages"][-1].content.lower()
                logger.info(f"Blockchain Revenue Agent: LLM Response: {llm_content}")
                if "category" in llm_content:
                    updated_state["current_task"] = "category_analysis"
                elif "contract" in llm_content:
                    updated_state["current_task"] = "contract_analysis"
                else:
                    updated_state["current_task"] = "unknown"

                return updated_state

        except Exception as e:
            logger.error(f"Blockchain Revenue Agent error: {str(e)}")
            updated_state = state.copy()
            updated_state["errors"].append(f"Blockchain Revenue Agent: {str(e)}")
            return updated_state
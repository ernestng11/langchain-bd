"""
Blockchain Revenue Agent - Specialized in multi-task blockchain data analysis.
Handles both category-level and contract-level analysis using onchain data tools.
"""

from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from ..schemas.state import AnalysisState, BlockchainCategoriesReport, TopContractsByCategoryReport, ContractInfo
from ..tools.blockchain_tools import categories_by_gas_fees_tool, top_contracts_by_gas_fees_tool, get_latest_growthepie_datasets_tool, get_data_overview, get_combined_analysis, get_top_categories
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
   - Ignore 'unlabeled' category

2. Contract Analysis Task:
   - Use results from category analysis to identify top 3 categories per blockchain
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
            blockchain_names = state['blockchain_names']
            timeframe = state['timeframe']
            
            logger.info(f"💰 Starting Category Analysis")
            logger.info("=" * 50)
            logger.info(f"⛓️  Blockchains: {blockchain_names}")
            logger.info(f"⏰ Timeframe: {timeframe}")

            category_reports = []

            for blockchain in blockchain_names:
                # Use "7d" timeframe for blockchain analysis even when historical growthepie analysis is requested
                analysis_timeframe = "7d" if timeframe in ["historical", "trend"] else timeframe
                
                logger.info(f"📊 Analyzing {blockchain} (using {analysis_timeframe} timeframe)...")
                
                # Fetch category data using the tool
                category_data = categories_by_gas_fees_tool.invoke({
                    "blockchain_name": blockchain,
                    "timeframe": analysis_timeframe
                })

                # Check for errors in the response
                if category_data.get("error"):
                    error_msg = f"Error fetching data for {blockchain}: {category_data['error']}"
                    logger.error(f"❌ {error_msg}")
                    updated_state = state.copy()
                    updated_state["errors"].append(f"Category Analysis: {error_msg}")
                    return updated_state

                # Create structured report
                report = BlockchainCategoriesReport(
                    blockchain=blockchain,
                    timeframe=timeframe,
                    top_category=category_data["top_category"],
                    top_category_share=category_data["top_category_share"],
                    category_breakdown=category_data["category_breakdown"],
                    total_gas_fees_usd=category_data["total_gas_fees_usd"],
                    category_concentration=category_data["category_concentration"],
                    key_insights=self._generate_category_insights(category_data)
                )

                category_reports.append(report)
                logger.info(f"✅ {blockchain} category analysis completed")

            # Update state
            updated_state = state.copy()
            updated_state["category_reports"] = category_reports
            updated_state["current_task"] = "category_analysis_complete"

            logger.info(f"✅ Category analysis completed for {len(category_reports)} blockchains")
            logger.info("=" * 50)
            return updated_state

        except Exception as e:
            logger.error(f"Category analysis error: {str(e)}")
            updated_state = state.copy()
            updated_state["errors"].append(f"Category Analysis: {str(e)}")
            return updated_state

    def execute_contract_analysis(self, state: AnalysisState) -> AnalysisState:
        """Execute contract analysis for top categories in each blockchain"""
        try:
            logger.info(f"📄 Starting Contract Analysis")
            logger.info("=" * 50)

            # Check if we have target categories from trend analysis
            target_categories = state.get("target_categories")
            
            if not state.get("category_reports") and not target_categories:
                raise ValueError("Category analysis must be completed before contract analysis")

            contract_reports = []

            # If we have target categories from trend analysis, use those
            if target_categories:
                logger.info(f"🎯 Using target categories from trend analysis: {target_categories}")
                categories_to_analyze = target_categories
                blockchain_names = state.get("blockchain_names", [])
                
                logger.info(f"📊 Analyzing contracts for {len(blockchain_names)} blockchains × {len(categories_to_analyze)} categories")
                
                for blockchain in blockchain_names:
                    for category in categories_to_analyze:
                        # Use "7d" timeframe for blockchain analysis even when historical growthepie analysis is requested
                        analysis_timeframe = "7d" if state['timeframe'] in ["historical", "trend"] else state['timeframe']
                        
                        logger.info(f"🔍 Analyzing {category} contracts on {blockchain} (using {analysis_timeframe} timeframe)...")
                        
                        # Fetch contract data using the tool
                        contract_data = top_contracts_by_gas_fees_tool.invoke({
                            "blockchain_name": blockchain,
                            "timeframe": analysis_timeframe,
                            "top_n": 10,  # Analyze top 10 contracts
                            "main_category_key": category
                        })
                        
                        if contract_data.get("error"):
                            error_msg = f"Error fetching contract data for {blockchain}/{category}: {contract_data['error']}"
                            logger.error(f"❌ {error_msg}")
                            updated_state = state.copy()
                            updated_state["errors"].append(f"Contract Analysis: {error_msg}")
                            return updated_state
                        
                        contracts_found = len(contract_data.get("top_contracts", []))
                        logger.info(f"📋 Found {contracts_found} contracts for {category} on {blockchain}")
                        # print(contract_data["top_contracts"])
                        # Convert contract data to structured format
                        contracts = []
                        for contract_info in contract_data["top_contracts"]:
                            contract = ContractInfo(
                                address=contract_info["address"],
                                project_name=contract_info.get("project_name"),
                                name=contract_info.get("name"),
                                gas_fees_absolute_usd=contract_info["gas_fees_absolute_usd"],
                                main_category_key=contract_info["main_category_key"],
                                sub_category_key=contract_info.get("sub_category_key"),
                                chain=contract_info.get("chain"),
                                gas_fees_absolute_eth=contract_info.get("gas_fees_absolute_eth"),
                                txcount_absolute=contract_info.get("txcount_absolute")
                            )
                            contracts.append(contract)

                        # Create structured report
                        report = TopContractsByCategoryReport(
                            blockchain=blockchain,
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
                        logger.info(f"✅ {category} contract analysis completed for {blockchain}")
                
                logger.info(f"✅ Contract analysis completed for {len(contract_reports)} category-blockchain combinations")
                logger.info("=" * 50)
                
                # Update state
                updated_state = state.copy()
                updated_state["contract_reports"] = contract_reports
                updated_state["current_task"] = "contract_analysis_complete"
                return updated_state
                
            else:
                # Use original logic with category reports
                logger.info("📊 Using category reports to determine top categories...")
                for category_report in state["category_reports"]:
                    # Get top 2 categories for this blockchain
                    top_categories = get_top_categories(category_report.category_breakdown, n=2)
                    logger.info(f"🎯 Top categories for {category_report.blockchain}: {top_categories}")

                    for category in top_categories:
                        # Use "7d" timeframe for blockchain analysis even when historical growthepie analysis is requested
                        analysis_timeframe = "7d" if state['timeframe'] in ["historical", "trend"] else state['timeframe']
                        
                        # Fetch contract data using the tool
                        contract_data = top_contracts_by_gas_fees_tool.invoke({
                            "blockchain_name": category_report.blockchain,
                            "timeframe": analysis_timeframe,
                            "top_n": 10,  # Analyze top 10 contracts
                            "main_category_key": category
                        })
                        # print(contract_data["top_contracts"])
                        # Convert contract data to structured format
                        contracts = []
                        for contract_info in contract_data["top_contracts"]:
                            contract = ContractInfo(
                                address=contract_info["address"],
                                project_name=contract_info.get("project_name"),
                                name=contract_info.get("name"),
                                gas_fees_absolute_usd=contract_info["gas_fees_absolute_usd"],
                                main_category_key=contract_info["main_category_key"],
                                sub_category_key=contract_info.get("sub_category_key"),
                                chain=contract_info.get("chain"),
                                gas_fees_absolute_eth=contract_info.get("gas_fees_absolute_eth"),
                                txcount_absolute=contract_info.get("txcount_absolute")
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
                        logger.info(f"✅ {category} contract analysis completed for {category_report.blockchain}")

                # Update state
                updated_state = state.copy()
                updated_state["contract_reports"] = contract_reports
                updated_state["current_task"] = "contract_analysis_complete"

                logger.info(f"✅ Contract analysis completed for {len(contract_reports)} category-blockchain combinations")
                logger.info("=" * 50)
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
        # The activity_type field is no longer present, so this function will just return an empty list or a placeholder
        return []

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
                # logger.info(f"Blockchain Revenue Agent: LLM Response: {llm_content}")
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
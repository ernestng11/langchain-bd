"""
Growthepie Analysis Agent - Handles historical dataset analysis using cached data.
Performs 3-step analysis: get datasets → analyze each → combine results.
"""

from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from ..schemas.state import AnalysisState
from ..tools.blockchain_tools import get_latest_growthepie_datasets_tool, get_data_overview, get_combined_analysis
import logging

logger = logging.getLogger(__name__)


class TrendAnalysisAgent:
    """
    Specialized agent for analyzing historical blockchain datasets from GrowthePie cache.
    Performs chronological analysis of cached datasets to identify trends and patterns.
    """

    def __init__(self, model_name: str = "gpt-4"):
        self.model = ChatOpenAI(model=model_name, temperature=0.1)
        self.name = "trend_analysis_agent"

        # Tools available to this agent
        self.tools = [get_latest_growthepie_datasets_tool, get_data_overview, get_combined_analysis]

        # Create the agent using LangGraph's prebuilt function
        self.agent = create_react_agent(
            model=self.model,
            tools=self.tools,
            prompt=self._get_system_prompt(),
            name=self.name
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the trend analysis agent"""
        return """You are a Senior Blockchain Data Analyst specializing in historical dataset analysis using GrowthePie cached data.

EXPERTISE:
- Deep knowledge of blockchain ecosystems and historical data patterns
- Chronological analysis of cached datasets to identify trends
- Comparative analysis between time periods
- Trend identification and pattern recognition
- Historical performance analysis

TOOLS AVAILABLE:
- get_latest_growthepie_datasets_tool: Get the 2 latest datasets from the growthepie_cache directory
- get_data_overview: Analyze a single dataframe using LangChain's pandas dataframe agent
- get_combined_analysis: Synthesizes two individual dataset analyses into comparative insights

ANALYSIS METHODOLOGY:
1. **Dataset Retrieval**: Use get_latest_growthepie_datasets_tool() to fetch the 2 latest cached datasets
2. **Individual Analysis**: Call get_data_overview() for each dataframe individually with chronological context
3. **Combined Synthesis**: Use get_combined_analysis() to synthesize both analyses into comparative insights
4. **Trend Identification**: Identify patterns, changes, and trends between time periods

OUTPUT REQUIREMENTS:
- Structure analysis with chronological context (newer vs older datasets)
- Identify key trends and changes between time periods
- Provide actionable insights about ecosystem evolution
- Highlight significant changes in category performance
- Flag emerging patterns or declining trends

After completing your analysis, respond directly to the supervisor with structured findings."""

    def execute_trend_analysis(self, state: AnalysisState) -> AnalysisState:
        """Execute the complete 3-step trend analysis workflow"""
        try:
            logger.info("📊 Starting Trend Analysis Agent")
            logger.info("=" * 50)

            # Step 1: Get the datasets
            logger.info("📥 Step 1: Getting latest datasets...")
            datasets_result = get_latest_growthepie_datasets_tool.invoke({})
            
            if not datasets_result.get('success'):
                error_msg = f"Failed to get datasets: {datasets_result.get('error')}"
                logger.error(f"❌ {error_msg}")
                updated_state = state.copy()
                updated_state["errors"].append(f"Trend Analysis: {error_msg}")
                return updated_state

            datasets_loaded = datasets_result.get('datasets_loaded', 0)
            dataset_names = datasets_result.get('dataset_names', [])
            chronological_order = datasets_result.get('chronological_order', [])
            
            logger.info(f"✅ Found {datasets_loaded} datasets")
            logger.info(f"📁 Dataset names: {dataset_names}")
            logger.info(f"⏰ Chronological order: {chronological_order}")
            
            # Step 2: Analyze each dataframe individually
            dataframes = datasets_result.get('dataframes', [])
            dataframe_info = datasets_result.get('dataframe_info', [])
            individual_analyses = []
            individual_dataset_info = []
            
            logger.info(f"📊 Step 2: Analyzing {len(dataframes)} dataframes individually...")
            
            for i, (df, info) in enumerate(zip(dataframes, dataframe_info), 1):
                dataset_order = info.get('order', 'unknown')
                filename = info.get('filename', f'dataset_{i}.csv')
                rows = info.get('rows', 0)
                
                logger.info(f"🔍 Step 2.{i}: Analyzing dataframe {i} ({dataset_order} dataset)")
                logger.info(f"   📁 File: {filename}")
                logger.info(f"   📊 Rows: {rows}")
                
                # Create file path for the dataframe
                file_path = f"src/data/growthepie_cache/{filename}"
                
                analysis_result = get_data_overview.invoke({
                    "file_path": file_path,
                    "dataset_info": info
                })
                
                if analysis_result.get('success'):
                    logger.info(f"✅ Analysis {i} completed successfully!")
                    individual_analyses.append(analysis_result.get('analysis_result'))
                    individual_dataset_info.append(analysis_result.get('dataset_info'))
                else:
                    error_msg = f"Error in analysis {i}: {analysis_result.get('error')}"
                    logger.error(f"❌ {error_msg}")
                    updated_state = state.copy()
                    updated_state["errors"].append(f"Trend Analysis: {error_msg}")
                    return updated_state

            # Step 3: Combine analyses with chronological context
            logger.info(f"🔗 Step 3: Combining {len(individual_analyses)} analyses...")
            if len(individual_analyses) == 2:
                logger.info("📊 Combining individual analyses into comparative insights...")
                combined_result = get_combined_analysis.invoke({
                    "analysis_1": individual_analyses[0],
                    "analysis_2": individual_analyses[1],
                    "dataset_1_info": individual_dataset_info[0],
                    "dataset_2_info": individual_dataset_info[1]
                })
                
                if combined_result.get('success'):
                    logger.info("✅ Combined analysis completed successfully!")
                    logger.info("=" * 50)
                    
                    # Update state with results
                    updated_state = state.copy()
                    updated_state["growthepie_analysis"] = {
                        "individual_analyses": individual_analyses,
                        "combined_analysis": combined_result.get('combined_analysis'),
                        "dataset_info": individual_dataset_info,
                        "chronological_order": datasets_result.get('chronological_order'),
                        "success": True
                    }
                    updated_state["current_task"] = "trend_analysis_complete"
                    
                    return updated_state
                else:
                    error_msg = f"Error in combined analysis: {combined_result.get('error')}"
                    logger.error(f"❌ {error_msg}")
                    updated_state = state.copy()
                    updated_state["errors"].append(f"Trend Analysis: {error_msg}")
                    return updated_state
            else:
                error_msg = f"Expected 2 analyses, got {len(individual_analyses)}"
                logger.error(f"❌ {error_msg}")
                updated_state = state.copy()
                updated_state["errors"].append(f"Trend Analysis: {error_msg}")
                return updated_state

        except Exception as e:
            logger.error(f"Trend Analysis error: {str(e)}")
            updated_state = state.copy()
            updated_state["errors"].append(f"Trend Analysis: {str(e)}")
            return updated_state

    def __call__(self, state: AnalysisState) -> Dict[str, Any]:
        """Execute the trend analysis workflow"""
        try:
            logger.info("Trend Analysis Agent: Starting analysis")
            result = self.execute_trend_analysis(state)
            logger.info("Trend Analysis Agent: Analysis completed")
            return result
        except Exception as e:
            logger.error(f"Trend Analysis Agent error: {str(e)}")
            updated_state = state.copy()
            updated_state["errors"].append(f"Trend Analysis Agent: {str(e)}")
            return updated_state 
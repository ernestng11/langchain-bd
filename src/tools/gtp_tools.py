import json
import pandas as pd
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from crewai.tools import tool
from .category_perc import get_categories_by_gas_fees_share, get_available_blockchains
from .top_contracts_by_gas_fees import get_top_contracts_by_gas_fees, get_available_timeframes

class BlockchainCategoriesReport(BaseModel):
    """Report on categories by gas fees share for a target blockchain"""
    blockchain: str = Field(..., description="Blockchain network name")
    timeframe: str = Field(..., description="Data timeframe")
    top_category: str = Field(..., description="Category with highest gas fees share in the blockchain for the timeframe")
    top_category_share: float = Field(..., description="Gas fees share percentage of top category in the blockchain for the timeframe")
    category_breakdown: Dict[str, float] = Field(..., description="All categories with their gas fees shares in the blockchain for the timeframe")
    total_gas_fees_usd: float = Field(..., description="Total gas fees in USD for the timeframe")
    category_concentration: float = Field(..., description="Concentration ratio (top 3 categories share) in the blockchain for the timeframe")
    key_insights: List[str] = Field(..., description="Key insights about category distribution and trends in the blockchain for the timeframe")

class TopContractsByCategoryReport(BaseModel):
    """Report on top contracts by gas fees for a target blockchain and category"""
    blockchain: str = Field(..., description="Blockchain network name")
    category: str = Field(..., description="Category analyzed")
    timeframe: str = Field(..., description="Data timeframe")
    top_contracts: List[Dict[str, Any]] = Field(..., description="Top contracts with their gas fees data in the blockchain for the timeframe")
    total_contracts_analyzed: int = Field(..., description="Total number of contracts analyzed in the blockchain for the timeframe")
    top_contract_share: float = Field(..., description="Gas fees share of the top contract in the blockchain for the timeframe")
    contract_concentration: float = Field(..., description="Concentration ratio (top 5 contracts share) in the blockchain for the timeframe")
    key_insights: List[str] = Field(..., description="Key insights about contract performance and patterns in the blockchain for the timeframe")
    activity_analysis: List[str] = Field(..., description="Analysis of what activities these contracts might be performing to generate gas fees in their respective categories in the blockchain for the timeframe")

class StrategicSynthesisReport(BaseModel):
    """Strategic synthesis report combining analysis from multiple sources"""
    executive_summary: str = Field(..., description="Executive summary synthesizing key findings from both category and contract analysis reports")
    competitive_landscape_analysis: Dict[str, Any] = Field(..., description="Comparative analysis of blockchain performance across categories and contract activities, identifying competitive advantages and gaps")
    category_performance_insights: Dict[str, Any] = Field(..., description="Deep analysis of category distribution patterns, concentration ratios, and what they reveal about blockchain ecosystem maturity and user behavior")
    contract_activity_insights: Dict[str, Any] = Field(..., description="Analysis of top contract activities and what they indicate about blockchain usage patterns, developer activity, and ecosystem health")
    revenue_growth_hypotheses: List[str] = Field(..., description="Data-driven revenue growth hypotheses based on category performance, contract activities, and competitive positioning")
    strategic_recommendations: List[str] = Field(..., description="Strategic recommendations for competitive positioning, market entry, and revenue optimization based on category and contract analysis")
    risk_assessment: List[str] = Field(..., description="Risk assessment based on category concentration, contract dependency, and competitive landscape analysis")
    actionable_next_steps: List[str] = Field(..., description="Specific, data-backed actionable next steps for business development and competitive strategy")
    cross_blockchain_comparison: Dict[str, Any] = Field(..., description="Direct comparison of blockchain performance across categories and contract activities, highlighting relative strengths and weaknesses")

@tool("Get Categories by Gas Fees Share For A Target Blockchain")
def categories_by_gas_fees_tool(blockchain_name: str, timeframe: str = "7d") -> str:
    """
    Gets categories by gas fees share data for specified blockchain networks from GrowThePie.
    
    Supported blockchain names:
    - "mantle": For Mantle protocol data
    - "base": For Base protocol data
    - "arbitrum": For Arbitrum protocol data
    - "optimism": For Optimism protocol data
    - "unichain": For Unichain protocol data
    
    Supported timeframes:
    - "1d": 1 day data
    - "7d": 7 days data
    - "30d": 30 days data
    
    :param blockchain_name: str, name of the blockchain network
    :param timeframe: str, timeframe for the data ("1d", "7d", or "30d")
    :return: String representation of categories by gas fees share data
    """
    try:
        # Get available blockchains to validate input
        available_blockchains = get_available_blockchains(json_file_path="growthepie/inspect_blockspace.json")
        
        if blockchain_name.lower() not in [bc.lower() for bc in available_blockchains]:
            return f"Error: Blockchain '{blockchain_name}' not supported. Available blockchains: {', '.join(available_blockchains)}"
        
        # Validate timeframe
        valid_timeframes = ["1d", "7d", "30d"]
        if timeframe not in valid_timeframes:
            return f"Error: Timeframe '{timeframe}' not supported. Valid timeframes: {', '.join(valid_timeframes)}"
        
        # Get the data
        df = get_categories_by_gas_fees_share(blockchain_name.lower(), timeframe, json_file_path="growthepie/inspect_blockspace.json")
        
        # Convert DataFrame to readable string format for the agent
        summary = f"Categories by Gas Fees Share for {blockchain_name.title()} Blockchain ({timeframe}):\n"
        summary += f"Total categories: {len(df)}\n"
        summary += f"Columns: {', '.join(df.columns.tolist())}\n\n"
        summary += "Data:\n"
        summary += df.to_string(index=False)
        
        return summary
        
    except Exception as e:
        return f"Error retrieving data for {blockchain_name} ({timeframe}): {str(e)}"

@tool("Get Available Blockchains")
def available_blockchains_tool() -> str:
    """
    Gets list of available blockchain networks in the GrowThePie dataset.
    
    :return: String representation of available blockchain networks
    """
    try:
        blockchains = get_available_blockchains(json_file_path="growthepie/inspect_blockspace.json")
        summary = "Available blockchain networks in GrowThePie dataset:\n"
        summary += ", ".join(blockchains)
        return summary
    except Exception as e:
        return f"Error retrieving available blockchains: {str(e)}"

@tool("Get Top Contracts by Gas Fees For A Target Blockchain and Category")
def top_contracts_by_gas_fees_tool(blockchain_name: str, timeframe: str = "7d", top_n: int = 10, main_category_key: Optional[str] = None) -> str:
    """
    Gets top contracts by gas fees for specified blockchain networks from GrowThePie.
    
    Supported blockchain names:
    - "mantle": For Mantle protocol data
    - "base": For Base protocol data
    - "arbitrum": For Arbitrum protocol data
    - "optimism": For Optimism protocol data
    - "unichain": For Unichain protocol data
    
    Supported timeframes:
    - "7d": 7 days data
    - "30d": 30 days data
    - "90d": 90 days data
    - "180d": 180 days data
    - "365d": 365 days data
    - "max": Maximum available data
    

    
    :param blockchain_name: str, name of the blockchain network
    :param timeframe: str, timeframe for the data
    :param top_n: int, number of top contracts to return (default: 10)
    :param main_category_key: str, optional filter by main category
    :return: String representation of top contracts by gas fees data
    """
    try:
        # Get available blockchains to validate input
        available_blockchains = get_available_blockchains(json_file_path="growthepie/inspect_blockspace.json")
        
        if blockchain_name.lower() not in [bc.lower() for bc in available_blockchains]:
            return f"Error: Blockchain '{blockchain_name}' not supported. Available blockchains: {', '.join(available_blockchains)}"
        
        # Get available timeframes for validation
        available_timeframes = get_available_timeframes(blockchain_name.lower(), json_file_path="growthepie/inspect_blockspace.json")
        if timeframe not in available_timeframes:
            return f"Error: Timeframe '{timeframe}' not supported for {blockchain_name}. Available timeframes: {', '.join(available_timeframes)}"
        
        # Validate top_n
        if top_n <= 0 or top_n > 100:
            return f"Error: top_n must be between 1 and 100. Received: {top_n}"
        
        # Get the data
        df = get_top_contracts_by_gas_fees(blockchain_name.lower(), timeframe, top_n=top_n, main_category_key=main_category_key, json_file_path="growthepie/inspect_blockspace.json")
        
        if df.empty:
            category_info = f" and category '{main_category_key}'" if main_category_key else ""
            return f"No contracts found for {blockchain_name} ({timeframe}){category_info}"
        
        # Convert DataFrame to readable string format for the agent
        category_filter = f" (filtered by {main_category_key})" if main_category_key else ""
        summary = f"Top {top_n} Contracts by Gas Fees for {blockchain_name.title()} Blockchain ({timeframe}){category_filter}:\n"
        summary += f"Total contracts returned: {len(df)}\n"
        summary += f"Columns: {', '.join(df.columns.tolist())}\n\n"
        summary += "Data:\n"
        summary += df.to_string(index=False)
        
        return summary
        
    except Exception as e:
        return f"Error retrieving top contracts data for {blockchain_name} ({timeframe}): {str(e)}"

@tool("Get Available Timeframes")
def available_timeframes_tool(blockchain_name: str) -> str:
    """
    Gets list of available timeframes for a specific blockchain network in the GrowThePie dataset.
    
    :param blockchain_name: str, name of the blockchain network
    :return: String representation of available timeframes
    """
    try:
        # Get available blockchains to validate input
        available_blockchains = get_available_blockchains(json_file_path="growthepie/inspect_blockspace.json")
        
        if blockchain_name.lower() not in [bc.lower() for bc in available_blockchains]:
            return f"Error: Blockchain '{blockchain_name}' not supported. Available blockchains: {', '.join(available_blockchains)}"
        
        timeframes = get_available_timeframes(blockchain_name.lower(), json_file_path="growthepie/inspect_blockspace.json")
        summary = f"Available timeframes for {blockchain_name.title()} in GrowThePie dataset:\n"
        summary += ", ".join(timeframes)
        return summary
    except Exception as e:
        return f"Error retrieving available timeframes for {blockchain_name}: {str(e)}"


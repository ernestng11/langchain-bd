"""
State definitions for the blockchain revenue analysis system.
Defines the shared state structure used across all agents and tasks.
"""

from typing import TypedDict, List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class BlockchainCategoriesReport(BaseModel):
    """Report structure for category-level gas fees analysis"""
    blockchain: str = Field(description="Target blockchain network name")
    timeframe: str = Field(description="Analysis period (1d, 7d, 30d)")
    top_category: str = Field(description="Category with highest gas fees share")
    top_category_share: float = Field(description="Percentage share of top category")
    category_breakdown: Dict[str, float] = Field(
        description="Complete distribution across all categories"
    )
    total_gas_fees_usd: float = Field(description="Total gas fees in USD for the timeframe")
    category_concentration: float = Field(description="Concentration ratio of top 3 categories")
    key_insights: List[str] = Field(description="Analysis of category distribution patterns")
    generated_at: datetime = Field(default_factory=datetime.now)


class ContractInfo(BaseModel):
    """Individual contract information"""
    address: str
    project_name: Optional[str] = None
    name: Optional[str] = None
    gas_fees_absolute_usd: float
    main_category_key: str
    sub_category_key: Optional[str] = None
    gas_fees_absolute_eth: Optional[float] = None
    txcount_absolute: Optional[int] = None
    chain: Optional[str] = None


class TopContractsByCategoryReport(BaseModel):
    """Report structure for contract-level analysis within categories"""
    blockchain: str = Field(description="Target blockchain network name")
    category: str = Field(description="Specific category being analyzed")
    timeframe: str = Field(description="Analysis period")
    top_contracts: List[ContractInfo] = Field(description="List of top contracts with data")
    total_contracts_analyzed: int = Field(description="Number of contracts in analysis")
    top_contract_share: float = Field(description="Gas fees share of highest-earning contract")
    contract_concentration: float = Field(description="Concentration ratio of top 5 contracts")
    key_insights: List[str] = Field(description="Contract performance patterns")
    activity_analysis: List[str] = Field(description="Contract activities analysis")
    generated_at: datetime = Field(default_factory=datetime.now)


class StrategicSynthesisReport(BaseModel):
    """Comprehensive strategic analysis report"""
    executive_summary: str = Field(description="High-level synthesis of key findings")
    competitive_landscape_analysis: str = Field(description="Comparative blockchain performance")
    category_performance_insights: str = Field(description="Category distribution analysis")
    contract_activity_insights: str = Field(description="Contract activities analysis")
    revenue_growth_hypotheses: List[str] = Field(description="Data-driven growth hypotheses")
    strategic_recommendations: List[str] = Field(description="Competitive positioning recommendations")
    risk_assessment: str = Field(description="Risk analysis based on concentration")
    actionable_next_steps: List[str] = Field(description="Specific business development steps")
    cross_blockchain_comparison: str = Field(description="Direct blockchain comparison")
    generated_at: datetime = Field(default_factory=datetime.now)


class AnalysisState(TypedDict):
    """Main state structure for the multi-agent workflow"""
    # Input parameters
    blockchain_names: List[str]
    timeframe: str

    # Intermediate results
    category_reports: List[BlockchainCategoriesReport]
    contract_reports: List[TopContractsByCategoryReport]

    # Final output
    strategic_synthesis: Optional[StrategicSynthesisReport]

    # System state
    current_task: str
    errors: List[str]
    messages: List[Dict[str, Any]]
    metadata: Dict[str, Any]
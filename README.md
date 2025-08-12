# Onchain Tools - Agent-Task-Tool Architecture

## What It Is

A sophisticated multi-agent intelligence system that transforms raw blockchain data into strategic competitive insights. Built with LangGraph, it analyzes onchain metrics across multiple blockchains to identify revenue patterns, protocol dominance, and strategic opportunities in the blockchain ecosystem.

## Why It Works

**Data-Driven Intelligence**: Unlike traditional market analysis that relies on external reports, this system directly analyzes onchain data from GrowThePie and Dune Analytics, providing real-time, unfiltered insights into blockchain activity.

**Multi-Agent Specialization**: Each agent has specialized expertise - from historical trend analysis to strategic synthesis - ensuring comprehensive coverage of the blockchain landscape without human bias or oversight limitations.

**Competitive Advantage**: By identifying category concentration patterns, protocol dominance, and cross-blockchain opportunities, it reveals strategic insights that can inform investment decisions, partnership strategies, and ecosystem positioning.

## How It Works

**1. Data Ingestion & Processing**
- Connects to GrowThePie API for category-level gas fee distributions
- Integrates with Dune Analytics for contract-level performance data
- Processes historical datasets for trend analysis and pattern recognition

**2. Multi-Agent Analysis Pipeline**
- **Trend Analysis Agent**: Analyzes historical blockchain datasets to identify patterns over time
- **Blockchain Revenue Agent**: Examines current gas fee distributions across categories (DeFi, NFT, CeFi, etc.)
- **Contract Analysis**: Deep-dives into top-performing contracts within dominant categories
- **Strategic Editor**: Synthesizes all analysis into actionable competitive intelligence

**3. Strategic Output Generation**
- **Category Reports**: Reveals which blockchain ecosystems dominate specific categories
- **Contract Reports**: Identifies protocol concentration and market share patterns
- **Strategic Synthesis**: Provides executive summary, competitive landscape analysis, and actionable recommendations
- **Risk Assessment**: Highlights concentration risks and mitigation strategies

**4. Real-Time Execution**
- Streams analysis updates as they're processed
- Supports both historical trend analysis and current snapshot analysis
- Configurable timeframes (7d, 14d, historical) for different strategic needs

The system transforms complex blockchain data into clear strategic insights, enabling data-driven decision making in the rapidly evolving blockchain ecosystem.

## Overview

This project implements a **supervisor pattern** multi-agent system that analyzes blockchain ecosystems by examining:
- Category-level gas fee distributions across blockchains
- Contract-level performance within top categories  
- Strategic synthesis for competitive intelligence

## Architecture

### Agent-Task-Tool Relationships

```
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│ Project Manager │────│ Blockchain Revenue   │────│ Strategic Editor    │
│ Agent           │    │ Agent                │    │ Agent               │
├─────────────────┤    ├──────────────────────┤    ├─────────────────────┤
│ • Orchestrates  │    │ • Category Analysis  │    │ • Synthesis         │
│ • Delegates     │    │ • Contract Analysis  │    │ • Recommendations   │
│ • Validates     │    │ • Uses Tools         │    │ • Risk Assessment   │
└─────────────────┘    └──────────────────────┘    └─────────────────────┘
                                │
                                ▼
                       ┌──────────────────────┐
                       │ Trend Analysis       │
                       │ Agent                │
                       ├──────────────────────┤
                       │ • Historical Data    │
                       │ • Trend Analysis     │
                       │ • Pattern Recognition│
                       └──────────────────────┘
```

### Data Flow

1. **Input Processing**: User provides blockchain names and timeframe
2. **Trend Analysis** (Historical): Analyze historical datasets for patterns and trends
3. **Category Analysis**: Analyze gas fees distribution across categories (DeFi, NFT, etc.)
4. **Contract Analysis**: Deep-dive into top categories per blockchain
5. **Strategic Synthesis**: Generate competitive intelligence and recommendations

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd onchain_tools_agent_system

# Install dependencies
pip install -r requirements.txt

# Copy environment template and configure
cp .env.template .env
# Edit .env with your API keys
```

### Basic Usage

```python
from src.main_workflow import create_onchain_analysis_workflow

# Create workflow
workflow = create_onchain_analysis_workflow()

# Execute analysis
result = workflow.invoke({
    "blockchain_names": ["ethereum", "arbitrum", "polygon"],
    "timeframe": "7d"  # or "historical" for trend analysis
})

# Access results
strategic_report = result["strategic_synthesis"]
category_reports = result["category_reports"] 
contract_reports = result["contract_reports"]
trend_analysis = result.get("growthepie_analysis")  # Historical trend data
```

### Streaming Execution

```python
# Stream for real-time updates
for update in workflow.stream(input_data):
    print(f"Update: {update}")
```

## Project Structure

```
onchain_tools_agent_system/
├── src/
│   ├── agents/                 # Agent implementations
│   │   ├── project_manager.py        # Supervisor agent
│   │   ├── blockchain_revenue_agent.py   # Data analysis agent  
│   │   ├── growthepie_analysis_agent.py  # Trend analysis agent
│   │   └── strategic_editor_agent.py     # Synthesis agent
│   ├── tools/                  # Blockchain data tools
│   │   └── blockchain_tools.py       # GrowThePie & Dune tools
│   ├── schemas/               # Data models and state
│   │   └── state.py                  # State definitions
│   ├── utils/                 # Utilities
│   │   └── agent_utils.py            # Agent communication utils
│   └── main_workflow.py       # Main LangGraph workflow
├── tests/                     # Test suite
├── langgraph.json            # LangGraph configuration
├── requirements.txt          # Dependencies
├── .env.template            # Environment template
└── README.md               # This file
```

## Agent Specifications

### 1. Project Manager Agent
- **Role**: Senior Project Manager specializing in blockchain analytics
- **Responsibilities**: Orchestrates workflow, manages crew progress, validates outputs
- **Tools**: None (delegation-focused)

### 2. Blockchain Revenue Agent
- **Role**: Senior Blockchain Revenue Analyst 
- **Tools**:
  - `categories_by_gas_fees_tool`: Category-level analysis
  - `top_contracts_by_gas_fees_tool`: Contract-level analysis
- **Tasks**:
  - Category analysis for all blockchains
  - Contract analysis for top categories per blockchain

### 3. Trend Analysis Agent
- **Role**: Senior Blockchain Data Analyst specializing in historical trends
- **Tools**:
  - `get_latest_growthepie_datasets_tool`: Historical dataset retrieval
  - `get_data_overview`: Individual dataset analysis
  - `get_combined_analysis`: Comparative trend analysis
- **Tasks**:
  - Analyze historical blockchain datasets
  - Identify patterns and trends over time
  - Provide chronological insights for strategic decisions

### 4. Strategic Editor Agent
- **Role**: Chief Strategy Officer for competitive intelligence
- **Responsibilities**: Synthesizes analysis into strategic insights
- **Outputs**: Comprehensive strategic synthesis report

## Report Structures

### BlockchainCategoriesReport
- Blockchain-specific category distribution
- Gas fees breakdown by category (DeFi, NFT, CeFi, etc.)
- Concentration metrics and insights

### TopContractsByCategoryReport  
- Top contracts within specific categories
- Contract performance and activity analysis
- Protocol dominance patterns

### StrategicSynthesisReport
- Executive summary and competitive landscape
- Growth hypotheses and strategic recommendations
- Risk assessment and actionable next steps
- Historical trend analysis and pattern recognition

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here
GROWTHEPIE_API_KEY=your_growthepie_api_key_here  
DUNE_API_KEY=your_dune_api_key_here

# Optional
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
```

### LangGraph Configuration

The system uses `langgraph.json` for deployment configuration with LangGraph Platform.

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/agents/
pytest tests/tools/
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code  
flake8 src/ tests/

# Type checking
mypy src/
```

## Deployment

### LangGraph Platform

```bash
# Deploy to LangGraph Platform
langraph deploy

# Or use specific configuration
langraph deploy --config langgraph.json
```

### Local Development

```bash
# Run workflow locally
python -m src.main_workflow
```

## API Integration

### GrowThePie Integration
- Category-level gas fees data
- Blockchain ecosystem metrics
- Historical trend analysis
- Cached dataset analysis for chronological insights

### Dune Analytics Integration  
- Contract-level performance data
- Detailed protocol analytics
- Custom query capabilities

## Monitoring and Observability

- **LangSmith Integration**: Full tracing and debugging
- **Structured Logging**: JSON-formatted logs with context
- **Agent Metrics**: Performance tracking and success rates
- **Error Handling**: Comprehensive error capture and recovery

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following code standards
4. Add tests for new functionality
5. Submit a pull request

## License

This project is proprietary to MantleX Research Team.

## Support

For questions and support, contact the MantleX AI Research team.

## Sample Strategic Synthesis Output

```
executive_summary='Strategic analysis of 2 blockchain ecosystems reveals Ethereum as the market leader with $6,500,000 in gas fees over 7d. \n\nDEFI emerges as the dominant category across chains, indicating strong institutional adoption and mature financial infrastructure. Contract-level analysis shows varying degrees of protocol concentration, with implications for ecosystem resilience and competitive positioning.\n\nHistorical trend analysis reveals significant shifts in category dominance, with emerging patterns in social and DeFi categories. Key strategic opportunities exist in underserved categories and emerging protocols, while concentration risks require careful portfolio diversification strategies.'

competitive_landscape_analysis='Competitive landscape analysis:1. Ethereum: $6,500,000 total fees, defi dominance (45.2%), concentration ratio 81.1%2. Arbitrum: $6,500,000 total fees, defi dominance (52.1%), concentration ratio 86.0%Competitive insights:- Ethereum: DeFi specialist with strong financial infrastructur\n- Arbitrum: DeFi specialist with strong financial infrastructur\n'

category_performance_insights='Category performance reveals ecosystem maturity and specialization patterns:\n\n- DEFI: Average 48.7% across chains (max 52.1%)\n- NFT: Average 20.9% across chains (max 23.1%)\n- CEFI: Average 14.0% across chains (max 15.2%)\n- SOCIAL: Average 7.9% across chains (max 8.5%)\n- UTILITY: Average 5.6% across chains (max 6.2%)\n- TOKEN_TRANSFERS: Average 2.3% across chains (max 3.1%)\n- CROSS_CHAIN: Average 0.5% across chains (max 0.8%)\n- UNLABELED: Average 0.2% across chains (max 0.3%)\n\nStrategic implications:\n- DEFI dominance suggests mature market with established protocols\n'

contract_activity_insights='Contract activity analysis reveals protocol dominance and revenue patterns:\n\nProtocol concentration patterns:\n- High concentration (>75%): 4 category-blockchain combinations\n- Balanced distribution (≤60%): 0 category-blockchain combinations\n\nDominant protocols by category:\n- Contract_0 (arbitrum/defi): 43.8% market share\n- Contract_0 (arbitrum/nft): 43.8% market share\n- OpenSea (ethereum/nft): 42.8% market share\n- Uniswap V3 (ethereum/defi): 34.6% market share\n'

revenue_growth_hypotheses=[
    'Strong DeFi presence in ethereum, arbitrum indicates institutional adoption readiness and financial infrastructure maturity',
    'High protocol concentration suggests winner-take-all dynamics in certain categories, creating moat opportunities for dominant players'
]

strategic_recommendations=[
    'Consider ethereum for diversified market entry due to balanced ecosystem (81.1% concentration)',
    'Target cross_chain category on arbitrum (0.2% current share) for first-mover advantage',
    'Implement diversification strategies for exposure to ethereum, arbitrum due to high category concentration risk'
]

risk_assessment='Risk assessment identifies concentration and competitive threats:\nCategory concentration risks:\n- ethereum: 81.1% concentration in top 3 categories creates ecosystem vulnerability\n- arbitrum: 86.0% concentration in top 3 categories creates ecosystem vulnerability\n\nProtocol concentration risks:\n- ethereum/defi: 100.0% concentration in top contracts\n- ethereum/nft: 100.0% concentration in top contracts\n- arbitrum/defi: 100.0% concentration in top contracts\n- arbitrum/nft: 100.0% concentration in top contracts\n\nMitigation strategies:\n- Diversify across multiple blockchains and categories\n- Monitor protocol concentration trends for early warning signals\n- Maintain exposure to emerging protocols to capture growth opportunities\n'

actionable_next_steps=[
    'Implement continuous monitoring of gas fees and category distributions across analyzed blockchains',
    'Deep-dive analysis of ethereum ecosystem protocols for partnership opportunities',
    'Develop diversified portfolio allocation model based on category concentration analysis',
    'Competitive analysis of dominant protocols: OpenSea, Contract_0, Uniswap V3'
]

cross_blockchain_comparison='Cross-blockchain comparative analysis:\n\nRevenue performance ranking:\n1. Ethereum: $6,500,000\n2. Arbitrum: $6,500,000\n\nEcosystem specializations:\n- Ethereum: defi specialist (45.2%)\n- Arbitrum: defi specialist (52.1%)\n\nRisk-return profiles:\n- Ethereum: High concentration, specialized ecosystem\n- Arbitrum: High concentration, specialized ecosystem\n'

generated_at=datetime.datetime(2025, 7, 22, 17, 43, 6, 955410)
```
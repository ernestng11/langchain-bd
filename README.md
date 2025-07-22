# Onchain Tools - Agent-Task-Tool Architecture

A sophisticated multi-agent system built with LangGraph for blockchain revenue analysis and competitive intelligence using onchain data.

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
```

### Data Flow

1. **Input Processing**: User provides blockchain names and timeframe
2. **Category Analysis**: Analyze gas fees distribution across categories (DeFi, NFT, etc.)
3. **Contract Analysis**: Deep-dive into top 2 categories per blockchain
4. **Strategic Synthesis**: Generate competitive intelligence and recommendations

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
    "timeframe": "7d"
})

# Access results
strategic_report = result["strategic_synthesis"]
category_reports = result["category_reports"] 
contract_reports = result["contract_reports"]
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
  - Contract analysis for top 2 categories per blockchain

### 3. Strategic Editor Agent
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
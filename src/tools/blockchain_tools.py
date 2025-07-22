"""
Tools for interacting with blockchain data APIs (GrowThePie and Dune).
These tools provide the actual data fetching capabilities for the agents.
"""

from typing import Dict, List, Any, Optional
from langchain_core.tools import tool
import requests
import time
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Mock API responses for demonstration - replace with actual API calls
MOCK_CATEGORY_DATA = {
    "ethereum": {
        "defi": 45.2,
        "nft": 23.1,
        "cefi": 12.8,
        "social": 8.5,
        "utility": 6.2,
        "token_transfers": 3.1,
        "cross_chain": 0.8,
        "unlabeled": 0.3
    },
    "arbitrum": {
        "defi": 52.1,
        "nft": 18.7,
        "cefi": 15.2,
        "social": 7.3,
        "utility": 4.9,
        "token_transfers": 1.5,
        "cross_chain": 0.2,
        "unlabeled": 0.1
    },
    "polygon": {
        "defi": 38.9,
        "nft": 31.2,
        "cefi": 9.8,
        "social": 12.1,
        "utility": 5.7,
        "token_transfers": 2.0,
        "cross_chain": 0.2,
        "unlabeled": 0.1
    }
}

MOCK_CONTRACT_DATA = {
    ("ethereum", "defi"): [
        {"address": "0x1234...abcd", "name": "Uniswap V3", "gas_fees_usd": 2_450_000, "activity": "DEX Trading"},
        {"address": "0x5678...efgh", "name": "AAVE V3", "gas_fees_usd": 1_890_000, "activity": "Lending Protocol"},
        {"address": "0x9abc...ijkl", "name": "Curve Finance", "gas_fees_usd": 1_200_000, "activity": "Stableswap AMM"},
        {"address": "0xdef0...mnop", "name": "Compound V3", "gas_fees_usd": 890_000, "activity": "Lending Protocol"},
        {"address": "0x1111...qrst", "name": "Yearn Finance", "gas_fees_usd": 650_000, "activity": "Yield Farming"}
    ],
    ("ethereum", "nft"): [
        {"address": "0x2222...uvwx", "name": "OpenSea", "gas_fees_usd": 1_850_000, "activity": "NFT Marketplace"},
        {"address": "0x3333...yzab", "name": "LooksRare", "gas_fees_usd": 920_000, "activity": "NFT Marketplace"},
        {"address": "0x4444...cdef", "name": "Blur", "gas_fees_usd": 780_000, "activity": "NFT Marketplace"},
        {"address": "0x5555...ghij", "name": "Foundation", "gas_fees_usd": 450_000, "activity": "NFT Platform"},
        {"address": "0x6666...klmn", "name": "SuperRare", "gas_fees_usd": 320_000, "activity": "NFT Platform"}
    ]
}


@tool
def categories_by_gas_fees_tool(blockchain_name: str, timeframe: str) -> Dict[str, Any]:
    """
    Analyzes category-level gas fees distribution for a specific blockchain.

    Args:
        blockchain_name: Name of the blockchain (ethereum, arbitrum, polygon, etc.)
        timeframe: Analysis period (1d, 7d, 30d)

    Returns:
        Dictionary containing category distribution data and metadata
    """
    try:
        logger.info(f"Fetching category data for {blockchain_name} over {timeframe}")

        # Simulate API call delay
        time.sleep(0.5)

        # Get mock data (replace with actual GrowThePie API call)
        blockchain_lower = blockchain_name.lower()
        if blockchain_lower not in MOCK_CATEGORY_DATA:
            raise ValueError(f"Blockchain {blockchain_name} not supported")

        category_data = MOCK_CATEGORY_DATA[blockchain_lower].copy()

        # Calculate total gas fees (mock calculation)
        base_fees = {
            "1d": 1_000_000,
            "7d": 6_500_000, 
            "30d": 25_000_000
        }
        total_gas_fees = base_fees.get(timeframe, 1_000_000)

        # Calculate concentration ratio (top 3 categories)
        sorted_categories = sorted(category_data.items(), key=lambda x: x[1], reverse=True)
        top_3_concentration = sum([pct for _, pct in sorted_categories[:3]])

        result = {
            "blockchain": blockchain_name,
            "timeframe": timeframe,
            "category_breakdown": category_data,
            "total_gas_fees_usd": total_gas_fees,
            "top_category": sorted_categories[0][0],
            "top_category_share": sorted_categories[0][1],
            "category_concentration": top_3_concentration,
            "timestamp": datetime.now().isoformat(),
            "data_source": "GrowThePie API (Mock)"
        }

        logger.info(f"Successfully fetched category data for {blockchain_name}")
        return result

    except Exception as e:
        logger.error(f"Error fetching category data for {blockchain_name}: {str(e)}")
        raise


@tool
def top_contracts_by_gas_fees_tool(
    blockchain_name: str, 
    timeframe: str, 
    top_n: int, 
    main_category_key: str
) -> Dict[str, Any]:
    """
    Analyzes top contracts by gas fees within a specific category and blockchain.

    Args:
        blockchain_name: Name of the blockchain
        timeframe: Analysis period (1d, 7d, 30d)
        top_n: Number of top contracts to return
        main_category_key: Category to analyze (defi, nft, cefi, etc.)

    Returns:
        Dictionary containing top contracts data and analysis
    """
    try:
        logger.info(f"Fetching top contracts for {blockchain_name}/{main_category_key} over {timeframe}")

        # Simulate API call delay
        time.sleep(0.7)

        # Get mock data (replace with actual Dune Analytics API call)
        blockchain_lower = blockchain_name.lower()
        category_key = (blockchain_lower, main_category_key)

        if category_key not in MOCK_CONTRACT_DATA:
            # Generate mock data for unsupported combinations
            contracts_data = [
                {
                    "address": f"0x{i:04d}...mock",
                    "name": f"Contract_{i}",
                    "gas_fees_usd": 1_000_000 // (i + 1),
                    "activity": "Generic Activity"
                }
                for i in range(min(top_n, 5))
            ]
        else:
            contracts_data = MOCK_CONTRACT_DATA[category_key][:top_n]

        # Calculate total fees and percentages
        total_fees = sum(contract["gas_fees_usd"] for contract in contracts_data)

        # Add percentage share to each contract
        enhanced_contracts = []
        for contract in contracts_data:
            contract_copy = contract.copy()
            contract_copy["percentage_share"] = (contract["gas_fees_usd"] / total_fees) * 100
            enhanced_contracts.append(contract_copy)

        # Calculate concentration metrics
        top_contract_share = enhanced_contracts[0]["percentage_share"] if enhanced_contracts else 0
        top_5_concentration = sum(
            contract["percentage_share"] 
            for contract in enhanced_contracts[:5]
        )

        result = {
            "blockchain": blockchain_name,
            "category": main_category_key,
            "timeframe": timeframe,
            "top_contracts": enhanced_contracts,
            "total_contracts_analyzed": len(enhanced_contracts),
            "total_gas_fees_usd": total_fees,
            "top_contract_share": top_contract_share,
            "contract_concentration": top_5_concentration,
            "timestamp": datetime.now().isoformat(),
            "data_source": "Dune Analytics API (Mock)"
        }

        logger.info(f"Successfully fetched top contracts for {blockchain_name}/{main_category_key}")
        return result

    except Exception as e:
        logger.error(f"Error fetching contract data: {str(e)}")
        raise


# Additional utility functions for the tools
def validate_blockchain_name(blockchain_name: str) -> bool:
    """Validate if blockchain name is supported"""
    supported_chains = ["ethereum", "arbitrum", "polygon", "optimism", "base", "avalanche"]
    return blockchain_name.lower() in supported_chains


def validate_timeframe(timeframe: str) -> bool:
    """Validate if timeframe is supported"""
    supported_timeframes = ["1d", "7d", "30d"]
    return timeframe in supported_timeframes


def get_top_categories(category_data: Dict[str, float], n: int = 2) -> List[str]:
    """Get top N categories by gas fees percentage"""
    sorted_categories = sorted(category_data.items(), key=lambda x: x[1], reverse=True)
    return [category for category, _ in sorted_categories[:n]]
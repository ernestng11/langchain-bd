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
from .category_perc import get_categories_by_gas_fees_share, get_available_blockchains
from .top_contracts_by_gas_fees import get_top_contracts_by_gas_fees, get_available_timeframes

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


@tool("categories_by_gas_fees_tool")
def categories_by_gas_fees_tool(blockchain_name: str, timeframe: str = "7d") -> dict:
    """
    Gets categories by gas fees share data for specified blockchain networks from GrowThePie.
    Returns a dict with summary and data or error.
    """
    try:
        json_path = "src/data/inspect_blockspace.json"
        available_blockchains = get_available_blockchains(json_file_path=json_path)
        if blockchain_name.lower() not in [bc.lower() for bc in available_blockchains]:
            return {"error": f"Blockchain '{blockchain_name}' not supported.", "available_blockchains": available_blockchains}
        valid_timeframes = ["1d", "7d", "30d"]
        if timeframe not in valid_timeframes:
            return {"error": f"Timeframe '{timeframe}' not supported.", "valid_timeframes": valid_timeframes}
        df = get_categories_by_gas_fees_share(blockchain_name.lower(), timeframe, json_file_path=json_path)
        categories = df.to_dict(orient="records")
        # Compute summary fields
        if not categories:
            return {"error": "No category data found."}
        # Sort by gas_fees_share_usd descending
        sorted_cats = sorted(categories, key=lambda x: x.get("gas_fees_share_usd", 0), reverse=True)
        top_category = sorted_cats[0]["category"]
        top_category_share = sorted_cats[0]["gas_fees_share_usd"]
        category_breakdown = {cat["category"]: cat["gas_fees_share_usd"] for cat in categories}
        total_gas_fees_usd = sum(cat.get("gas_fees_usd_absolute", 0) for cat in categories)
        category_concentration = sum(cat.get("gas_fees_share_usd", 0) for cat in sorted_cats[:3])
        return {
            "blockchain": blockchain_name,
            "timeframe": timeframe,
            "top_category": top_category,
            "top_category_share": top_category_share,
            "category_breakdown": category_breakdown,
            "total_gas_fees_usd": total_gas_fees_usd,
            "category_concentration": category_concentration,
            "categories": categories,
            "columns": list(df.columns),
            "error": None
        }
    except Exception as e:
        return {"error": str(e)}

@tool("available_blockchains_tool")
def available_blockchains_tool() -> dict:
    """
    Gets list of available blockchain networks in the GrowThePie dataset.
    """
    try:
        json_path = "src/data/inspect_blockspace.json"
        blockchains = get_available_blockchains(json_file_path=json_path)
        return {"blockchains": blockchains, "error": None}
    except Exception as e:
        return {"error": str(e)}

@tool("top_contracts_by_gas_fees_tool")
def top_contracts_by_gas_fees_tool(blockchain_name: str, timeframe: str = "7d", top_n: int = 10, main_category_key: str = None) -> dict:
    """
    Gets top contracts by gas fees for specified blockchain networks from GrowThePie.
    Returns a dict with summary and data or error.
    """
    try:
        json_path = "src/data/inspect_blockspace.json"
        available_blockchains = get_available_blockchains(json_file_path=json_path)
        if blockchain_name.lower() not in [bc.lower() for bc in available_blockchains]:
            return {"error": f"Blockchain '{blockchain_name}' not supported.", "available_blockchains": available_blockchains}
        available_timeframes = get_available_timeframes(blockchain_name.lower(), json_file_path=json_path)
        if timeframe not in available_timeframes:
            return {"error": f"Timeframe '{timeframe}' not supported for {blockchain_name}.", "available_timeframes": available_timeframes}
        if top_n <= 0 or top_n > 100:
            return {"error": f"top_n must be between 1 and 100. Received: {top_n}"}
        df = get_top_contracts_by_gas_fees(blockchain_name.lower(), timeframe, top_n=top_n, main_category_key=main_category_key, json_file_path=json_path)
        contracts = df.to_dict(orient="records")
        if not contracts:
            return {"error": f"No contracts found for {blockchain_name} ({timeframe}){f' and category {main_category_key}' if main_category_key else ''}"}
        # Compute summary fields
        total_contracts_analyzed = len(contracts)
        total_gas_fees = sum(c.get("gas_fees_absolute_usd", 0) for c in contracts)
        if total_contracts_analyzed > 0 and total_gas_fees > 0:
            top_contract_share = (contracts[0]["gas_fees_absolute_usd"] / total_gas_fees) * 100
            contract_concentration = sum(c["gas_fees_absolute_usd"] for c in contracts[:5]) / total_gas_fees * 100
        else:
            top_contract_share = 0
            contract_concentration = 0
        return {
            "blockchain": blockchain_name,
            "timeframe": timeframe,
            "main_category_key": main_category_key,
            "top_contracts": contracts,
            "total_contracts_analyzed": total_contracts_analyzed,
            "top_contract_share": top_contract_share,
            "contract_concentration": contract_concentration,
            "columns": list(df.columns),
            "error": None
        }
    except Exception as e:
        return {"error": str(e)}

@tool("available_timeframes_tool")
def available_timeframes_tool(blockchain_name: str) -> dict:
    """
    Gets list of available timeframes for a specific blockchain network in the GrowThePie dataset.
    """
    try:
        json_path = "src/data/inspect_blockspace.json"
        available_blockchains = get_available_blockchains(json_file_path=json_path)
        if blockchain_name.lower() not in [bc.lower() for bc in available_blockchains]:
            return {"error": f"Blockchain '{blockchain_name}' not supported.", "available_blockchains": available_blockchains}
        timeframes = get_available_timeframes(blockchain_name.lower(), json_file_path=json_path)
        return {"blockchain": blockchain_name, "timeframes": timeframes, "error": None}
    except Exception as e:
        return {"error": str(e)}


# Additional utility functions for the tools
def validate_blockchain_name(blockchain_name: str) -> bool:
    """Validate if blockchain name is supported"""
    supported_chains = ['base', 'mantle', 'arbitrum', 'optimism']
    return blockchain_name.lower() in supported_chains


def validate_timeframe(timeframe: str) -> bool:
    """Validate if timeframe is supported"""
    supported_timeframes = ["1d", "7d", "30d"]
    return timeframe in supported_timeframes


def get_top_categories(category_data: Dict[str, float], n: int = 2) -> List[str]:
    """Get top N categories by gas fees percentage"""
    sorted_categories = sorted(category_data.items(), key=lambda x: x[1], reverse=True)
    return [category for category, _ in sorted_categories[:n]]
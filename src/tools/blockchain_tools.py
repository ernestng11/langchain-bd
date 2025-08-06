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
import os
import pandas as pd
from pathlib import Path
import re
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import DirectoryLoader, TextLoader
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
        json_path = "src/data/new_inspect_blockspace.json"
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

@tool("get_latest_growthepie_datasets_tool")
def get_latest_growthepie_datasets_tool() -> dict:
    """
    Gets the 2 latest datasets from the growthepie_cache directory using LLM to determine dates.
    Returns a dict with the loaded dataframes and metadata.
    """
    try:
        cache_dir = Path("src/data/growthepie_cache")
        
        if not cache_dir.exists():
            return {"error": f"Cache directory {cache_dir} does not exist."}
        
        # Get all CSV files using DirectoryLoader with TextLoader
        loader = DirectoryLoader(str(cache_dir), glob="*.csv", loader_cls=TextLoader)
        docs = loader.load()
        
        print(f"DEBUG: DirectoryLoader found {len(docs)} files")
        for doc in docs:
            print(f"DEBUG: File: {doc.metadata['source']}")
        
        if len(docs) < 2:
            return {"error": f"Not enough CSV files found. Found {len(docs)}, need at least 2."}
        
        # Extract filenames and use LLM to determine latest dates
        filenames = [doc.metadata["source"].split("/")[-1] for doc in docs]
        print(f"DEBUG: Extracted filenames: {filenames}")
        
        # Use LLM to identify the 2 latest files by date with chronological info
        llm = ChatOpenAI(temperature=0, model="gpt-4")
        
        date_analysis_prompt = f"""Analyze these CSV filenames and identify the 2 files with the latest dates:

Filenames: {filenames}

Extract the date information from each filename and return ONLY the 2 filenames with the most recent dates, in order from newest to oldest.

IMPORTANT: Return exactly 2 filenames, no more, no less.

Return format: filename1,filename2"""
        
        result = llm.invoke(date_analysis_prompt)
        response = result.content.strip()
        
        # Clean and parse the response
        latest_filenames = [f.strip() for f in response.split(",") if f.strip()]
        
        if len(latest_filenames) != 2:
            return {"error": f"LLM returned {len(latest_filenames)} files, expected 2. Response: {response}"}
        
        # Determine chronological order (older first, newer second)
        chronological_order = []
        for i, filename in enumerate(latest_filenames):
            filename = filename.strip()
            # Extract date info from filename (e.g., "mantle_7d_1" -> older, "mantle_7d_2" -> newer)
            if "_1" in filename:
                chronological_order.append({"filename": filename, "order": "older", "position": i})
            elif "_2" in filename:
                chronological_order.append({"filename": filename, "order": "newer", "position": i})
            else:
                chronological_order.append({"filename": filename, "order": "unknown", "position": i})
        
        # Load the identified files
        dataframes = []
        dataframe_names = []
        
        for i, filename in enumerate(latest_filenames, 1):
            file_path = cache_dir / filename.strip()
            
            if not file_path.exists():
                return {"error": f"File {filename} not found"}
            
            try:
                df = pd.read_csv(file_path)
                dataframes.append(df)
                dataframe_names.append(f"df{i}_{file_path.stem}")
                
                logger.info(f"Loaded dataset {i}: {file_path.stem} with {len(df)} rows")
                
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
                return {"error": f"Failed to read file {file_path}: {str(e)}"}
        
        return {
            "success": True,
            "datasets_loaded": len(dataframes),
            "dataset_names": dataframe_names,
            "dataframes": dataframes,
            "chronological_order": chronological_order,
            "dataframe_info": [
                {
                    "name": name,
                    "rows": len(df),
                    "columns": list(df.columns),
                    "filename": latest_filenames[i].strip(),
                    "order": chronological_order[i]["order"]
                }
                for i, (name, df) in enumerate(zip(dataframe_names, dataframes))
            ]
        }
        
    except Exception as e:
        logger.error(f"Error in get_latest_growthepie_datasets_tool: {e}")
        return {"error": f"Failed to get latest datasets: {str(e)}"}


@tool("get_data_overview")
def get_data_overview(file_path: str, dataset_info: dict = None) -> dict:
    """
    Analyzes a single dataframe using LangChain's pandas dataframe agent.
    Uses a fixed blockchain analysis prompt to provide insights.
    
    Args:
        file_path: Path to the CSV file to analyze
        dataset_info: Optional metadata about the dataset (filename, order, etc.)
    """
    try:
        # Load the dataframe from file
        dataframe = pd.read_csv(file_path)
        
        # Initialize the LLM for the agent
        llm = ChatOpenAI(temperature=0, model="gpt-4")
        
        # Enhanced analysis prompt with chronological context
        dataset_context = ""
        if dataset_info:
            dataset_context = f"\nThis dataset represents the {dataset_info.get('order', 'unknown')} time period (filename: {dataset_info.get('filename', 'unknown')})."
        
        fixed_analysis_prompt = f"""This dataframe is defined by the below columns.{dataset_context}

1. **category**: This column indicates the category or type of transaction. Examples include "defi" (decentralized finance), "unlabeled" (transactions that haven't been categorized), "cefi" (centralized finance), "utility", and "token_transfers".

2. **txcount_share**: This column represents the share or proportion of the total transaction count that each category accounts for. It is expressed as a decimal fraction of the total transactions.

3. **gas_fees_share_eth**: This column represents the share or proportion of the total gas fees, measured in Ethereum (ETH), that each category accounts for. It is expressed as a decimal fraction of the total gas fees in ETH.

4. **gas_fees_eth_absolute**: This column represents the absolute amount of gas fees, measured in Ethereum (ETH), that each category has incurred.

5. **gas_fees_share_usd**: This column represents the share or proportion of the total gas fees, measured in USD, that each category accounts for. It is expressed as a percentage of the total gas fees in USD.

6. **gas_fees_usd_absolute**: This column represents the absolute amount of gas fees, measured in USD, that each category has incurred.

7. **txcount_absolute**: This column likely represents the absolute number of transactions that fall under each category.

You are a blockchain data analyst expert in reading dataframes and crunching numbers.
Your task is to answer my question about the data. Always give your answer backed by actual numbers in the dataframe.

You MUST ignore the 'unlabeled' category.

My task to you is:
Give me a concise and factual report about each category and how they compare to each other."""
        
        # Create the agent with single dataframe
        agent = create_pandas_dataframe_agent(
            llm=llm,
            df=dataframe,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            allow_dangerous_code=True,
        )
        
        # Run the analysis
        logger.info("Running analysis with fixed blockchain data analysis prompt")
        result = agent.invoke(fixed_analysis_prompt)
        
        return {
            "success": True,
            "analysis_result": result.get('output', str(result)),
            "dataset_info": dataset_info or {}
        }
        
    except Exception as e:
        logger.error(f"Error in get_data_overview: {e}")
        return {"error": f"Failed to analyze dataset: {str(e)}"}


@tool("get_combined_analysis")
def get_combined_analysis(analysis_1: str, analysis_2: str, dataset_1_info: dict = None, dataset_2_info: dict = None) -> dict:
    """
    Combines two individual dataset analyses using LLM to provide comparative insights.
    
    Args:
        analysis_1: Analysis result from first dataset
        analysis_2: Analysis result from second dataset
        dataset_1_info: Metadata about first dataset (order, filename)
        dataset_2_info: Metadata about second dataset (order, filename)
    """
    try:
        # Initialize the LLM
        llm = ChatOpenAI(temperature=0, model="gpt-4")
        
        # Enhanced synthesis prompt with chronological context
        order_1 = dataset_1_info.get('order', 'unknown') if dataset_1_info else 'unknown'
        order_2 = dataset_2_info.get('order', 'unknown') if dataset_2_info else 'unknown'
        filename_1 = dataset_1_info.get('filename', 'unknown') if dataset_1_info else 'unknown'
        filename_2 = dataset_2_info.get('filename', 'unknown') if dataset_2_info else 'unknown'
        
        synthesis_prompt = f"""Below are two analyses of blockchain datasets in chronological order:

{order_1.upper()} DATASET ({filename_1}):
{analysis_1}

{order_2.upper()} DATASET ({filename_2}):
{analysis_2}

Provide a comprehensive comparative analysis that:
1. Identifies key differences between the two time periods
2. Highlights trends and patterns over time

Focus on meaningful changes in category performance, gas fees, and transaction patterns over the time period. Always remember to refer to the time period in your answer."""
        
        # Get combined analysis
        result = llm.invoke(synthesis_prompt)
        
        return {
            "success": True,
            "combined_analysis": result.content
        }
        
    except Exception as e:
        logger.error(f"Error in get_combined_analysis: {e}")
        return {"error": f"Failed to combine analyses: {str(e)}"}


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
import json
import pandas as pd
from typing import List, Dict, Optional

def get_top_contracts_by_gas_fees(
    blockchain_name: str, 
    timeframe: str, 
    json_file_path: str = "inspect_blockspace.json",
    top_n: int = 10,
    main_category_key: Optional[str] = None
) -> pd.DataFrame:
    """
    Get the top contracts by gas fees for a given blockchain and timeframe.
    
    Args:
        blockchain_name (str): Name of the blockchain (e.g., 'mantle', 'arbitrum', 'base')
        timeframe (str): Time period (e.g., '7d', '30d', '90d', '180d', '365d', 'max')
        json_file_path (str): Path to the blockspace JSON file
        top_n (int): Number of top contracts to return
        main_category_key (str, optional): Filter by main category (e.g., 'defi', 'nft', 'cefi', 'social', 'utility', 'token_transfers', 'cross_chain', 'unlabeled')
    
    Returns:
        pd.DataFrame: DataFrame with top contracts sorted by gas fees
    """
    
    # Load the JSON data
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    try:
        # Get all contracts data from all chains and timeframes
        all_contracts = []
        
        for chain_key, chain_data in data['data']['chains'].items():
            if 'overview' in chain_data and timeframe in chain_data['overview']:
                timeframe_data = chain_data['overview'][timeframe]
                
                # Look for contracts in each category
                for category_key, category_data in timeframe_data.items():
                    if category_key == 'types':
                        continue
                    
                    if 'contracts' in category_data:
                        contracts_data = category_data['contracts']
                        types = contracts_data['types']
                        data_rows = contracts_data['data']
                        
                        # Create DataFrame for this category
                        df = pd.DataFrame(data_rows, columns=types)
                        all_contracts.append(df)
        
        if not all_contracts:
            print(f"No contracts data found for timeframe '{timeframe}'")
            return pd.DataFrame()
        
        # Combine all contracts data
        combined_df = pd.concat(all_contracts, ignore_index=True)
        
        # Filter by blockchain name
        filtered_df = combined_df[combined_df['chain'] == blockchain_name]
        
        if filtered_df.empty:
            print(f"No contracts found for blockchain '{blockchain_name}' in timeframe '{timeframe}'")
            return pd.DataFrame()
        
        # Filter by main category if specified
        if main_category_key:
            filtered_df = filtered_df[filtered_df['main_category_key'] == main_category_key]
            
            if filtered_df.empty:
                print(f"No contracts found for blockchain '{blockchain_name}', timeframe '{timeframe}', and category '{main_category_key}'")
                return pd.DataFrame()
        
        # Sort by gas_fees_absolute_usd in descending order
        df_sorted = filtered_df.sort_values('gas_fees_absolute_usd', ascending=False)
        
        # Select top N contracts and format
        top_contracts = df_sorted.head(top_n).copy()
        top_contracts['gas_fees_absolute_usd'] = top_contracts['gas_fees_absolute_usd'].round(2)
        top_contracts['gas_fees_absolute_eth'] = top_contracts['gas_fees_absolute_eth'].round(6)
        
        result_df = top_contracts[['project_name', 'address', 'name', 'main_category_key', 'sub_category_key', 'chain', 'gas_fees_absolute_eth', 'txcount_absolute', 'gas_fees_absolute_usd']]
        return result_df
        
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()

def get_available_blockchains(json_file_path: str = "inspect_blockspace.json") -> List[str]:
    """Get list of available blockchains in the data."""
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    return list(data['data']['chains'].keys())

def get_available_timeframes(blockchain_name: str, json_file_path: str = "inspect_blockspace.json") -> List[str]:
    """Get list of available timeframes for a specific blockchain."""
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    try:
        return list(data['data']['chains'][blockchain_name]['overview'].keys())
    except KeyError:
        return []

# Example usage
if __name__ == "__main__":
    # Get available blockchains
    print("Available blockchains:")
    print(get_available_blockchains())
    
    top_contracts = get_top_contracts_by_gas_fees('base', '7d', top_n=20, main_category_key='cefi')
    print(top_contracts) 
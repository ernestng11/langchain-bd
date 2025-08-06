import json
import pandas as pd
from typing import List, Dict, Optional


def get_categories_by_gas_fees_share(blockchain_name, timeframe, json_file_path="inspect_blockspace.json"):
    with open(json_file_path) as f:
        data = json.load(f)
    overview = data['data']['chains'][blockchain_name]['overview']
    types = overview['types']
    categories = []
    for cat, val in overview[timeframe].items():
        if cat == 'types':
            continue
        if 'data' in val:
            d = val['data']
            category_data = {'category': cat}
            for i, col_name in enumerate(types):
                category_data[col_name] = d[i]
            categories.append(category_data)
    # Sort by gas_fees_share_usd descending
    df = pd.DataFrame(categories)
    df['gas_fees_share_usd'] = (df['gas_fees_share_usd'] * 100).round(2)
    return df.sort_values('gas_fees_share_usd', ascending=False).reset_index(drop=True)

def get_available_blockchains(json_file_path: str = "inspect_blockspace.json") -> List[str]:
    """Get list of available blockchains in the data."""
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    return list(data['data']['chains'].keys())

# # Example usage:
# if __name__ == "__main__":
#     print(get_available_blockchains(json_file_path='growthepie/inspect_blockspace.json'))

#     df = get_categories_by_gas_fees_share('base', '7d', json_file_path='growthepie/inspect_blockspace.json')
#     print(df)

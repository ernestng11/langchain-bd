#!/usr/bin/env python3
"""
Example usage of the get_latest_growthepie_datasets_tool with fixed prompt
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tools.blockchain_tools import get_latest_growthepie_datasets_tool

def example_usage():
    """Example usage of the pandas dataframe agent tool with fixed prompt"""
    
    print("=== Example Usage of Pandas Dataframe Agent Tool (Fixed Prompt) ===\n")
    
    print("The tool uses a fixed analysis prompt that provides:")
    print("- Detailed column definitions for blockchain data")
    print("- Instructions to ignore 'unlabeled' category")
    print("- Request for concise and factual report about each category")
    print("- Comparison analysis between categories\n")
    
    # Call the tool (no parameters needed since it uses fixed prompt)
    print("Running analysis...")
    result = get_latest_growthepie_datasets_tool.invoke({})
    
    if result.get('success'):
        print("✅ Analysis completed successfully!")
        print(f"Datasets loaded: {result.get('datasets_loaded')}")
        print(f"Dataset names: {result.get('dataset_names')}")
        
        print("\nDataframe Information:")
        for info in result.get('dataframe_info', []):
            print(f"  - {info['name']}: {info['rows']} rows, columns: {info['columns']}")
            print(f"    Filename: {info['filename']}")
        
        print(f"\nAnalysis Result:")
        print(f"{result.get('analysis_result', 'No result')}")
        
    else:
        print(f"❌ Error: {result.get('error')}")

if __name__ == "__main__":
    example_usage() 
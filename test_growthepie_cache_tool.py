#!/usr/bin/env python3
"""
Test script for the three-step growthepie analysis workflow with chronological ordering
"""

import sys
import os
import dotenv
dotenv.load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tools.blockchain_tools import get_latest_growthepie_datasets_tool, get_data_overview, get_combined_analysis

def test_growthepie_workflow():
    """Test the three-step growthepie analysis workflow with chronological ordering"""
    print("Testing three-step growthepie analysis workflow with chronological ordering...")
    
    # Step 1: Get the datasets
    print("\n1. Getting latest datasets...")
    datasets_result = get_latest_growthepie_datasets_tool.invoke({})
    
    if not datasets_result.get('success'):
        print(f"❌ Error getting datasets: {datasets_result.get('error')}")
        return
    
    print(f"✅ Found {datasets_result.get('datasets_loaded')} datasets")
    print(f"Dataset names: {datasets_result.get('dataset_names')}")
    print(f"Chronological order: {datasets_result.get('chronological_order')}")
    
    # Step 2: Analyze each dataframe individually with chronological context
    dataframes = datasets_result.get('dataframes', [])
    dataframe_info = datasets_result.get('dataframe_info', [])
    individual_analyses = []
    individual_dataset_info = []
    
    for i, (df, info) in enumerate(zip(dataframes, dataframe_info), 1):
        print(f"\n2.{i}. Analyzing dataframe {i} ({info.get('order', 'unknown')} dataset)...")
        # Create a temporary file path for the dataframe
        file_path = f"src/data/growthepie_cache/{info.get('filename', f'dataset_{i}.csv')}"
        analysis_result = get_data_overview.invoke({
            "file_path": file_path,
            "dataset_info": info
        })
        
        if analysis_result.get('success'):
            print(f"✅ Analysis {i} completed successfully!")
            individual_analyses.append(analysis_result.get('analysis_result'))
            individual_dataset_info.append(analysis_result.get('dataset_info'))
        else:
            print(f"❌ Error in analysis {i}: {analysis_result.get('error')}")
            return
    
    # Step 3: Combine analyses with chronological context
    print(f"\n3. Combining {len(individual_analyses)} analyses with chronological context...")
    if len(individual_analyses) == 2:
        combined_result = get_combined_analysis.invoke({
            "analysis_1": individual_analyses[0],
            "analysis_2": individual_analyses[1],
            "dataset_1_info": individual_dataset_info[0],
            "dataset_2_info": individual_dataset_info[1]
        })
        
        if combined_result.get('success'):
            print("✅ Combined analysis completed successfully!")
            print(f"\nCombined Analysis Result:")
            print(f"{combined_result.get('combined_analysis')}")
        else:
            print(f"❌ Error in combined analysis: {combined_result.get('error')}")
    else:
        print(f"❌ Expected 2 analyses, got {len(individual_analyses)}")

if __name__ == "__main__":
    test_growthepie_workflow() 
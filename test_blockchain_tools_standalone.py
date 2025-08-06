#!/usr/bin/env python3
"""
Standalone test script for blockchain tools.
Run this script to test categories_by_gas_fees_tool and top_contracts_by_gas_fees_tool functions.
"""

import sys
import os
import json
from typing import Dict, Any

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tools import blockchain_tools

def print_separator(title: str):
    """Print a formatted separator with title"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_result(result: Dict[str, Any], tool_name: str):
    """Print formatted result"""
    print(f"\n📊 {tool_name} Result:")
    print("-" * 40)
    
    if result.get("error"):
        print(f"❌ Error: {result['error']}")
        return
    
    # Print key information
    for key, value in result.items():
        if key == "error":
            continue
        elif key in ["categories", "top_contracts"]:
            print(f"📋 {key}: {len(value)} items")
            if value:
                print(f"   First item: {value[0]}")
        elif isinstance(value, dict):
            print(f"📊 {key}: {json.dumps(value, indent=2)}")
        else:
            print(f"📊 {key}: {value}")

def test_categories_by_gas_fees_tool():
    """Test the categories_by_gas_fees_tool function"""
    print_separator("Testing categories_by_gas_fees_tool")
    
    # Test cases
    test_cases = [
        {"blockchain_name": "mantle", "timeframe": "7d"},
        {"blockchain_name": "arbitrum", "timeframe": "1d"},
        {"blockchain_name": "base", "timeframe": "30d"},
        {"blockchain_name": "ethereum", "timeframe": "7d"},  # Should fail - not in dataset
        {"blockchain_name": "mantle", "timeframe": "invalid"},  # Should fail - invalid timeframe
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case}")
        try:
            result = blockchain_tools.categories_by_gas_fees_tool.invoke(test_case)
            print_result(result, f"categories_by_gas_fees_tool (Test {i})")
        except Exception as e:
            print(f"❌ Exception: {e}")

def test_top_contracts_by_gas_fees_tool():
    """Test the top_contracts_by_gas_fees_tool function"""
    print_separator("Testing top_contracts_by_gas_fees_tool")
    
    # Test cases
    test_cases = [
        {"blockchain_name": "mantle", "timeframe": "7d", "top_n": 5, "main_category_key": "defi"},
        {"blockchain_name": "arbitrum", "timeframe": "1d", "top_n": 3, "main_category_key": None},
        {"blockchain_name": "base", "timeframe": "30d", "top_n": 10, "main_category_key": "nft"},
        {"blockchain_name": "mantle", "timeframe": "7d", "top_n": 2, "main_category_key": "invalid_category"},
        {"blockchain_name": "ethereum", "timeframe": "7d", "top_n": 5},  # Should fail - not in dataset
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case}")
        try:
            result = blockchain_tools.top_contracts_by_gas_fees_tool.invoke(test_case)
            print_result(result, f"top_contracts_by_gas_fees_tool (Test {i})")
        except Exception as e:
            print(f"❌ Exception: {e}")

def test_available_blockchains_tool():
    """Test the available_blockchains_tool function"""
    print_separator("Testing available_blockchains_tool")
    
    try:
        result = blockchain_tools.available_blockchains_tool.invoke({})
        print_result(result, "available_blockchains_tool")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_available_timeframes_tool():
    """Test the available_timeframes_tool function"""
    print_separator("Testing available_timeframes_tool")
    
    test_blockchains = ["mantle", "arbitrum", "base", "ethereum"]
    
    for blockchain in test_blockchains:
        print(f"\n🧪 Testing timeframes for: {blockchain}")
        try:
            result = blockchain_tools.available_timeframes_tool.invoke({"blockchain_name": blockchain})
            print_result(result, f"available_timeframes_tool ({blockchain})")
        except Exception as e:
            print(f"❌ Exception: {e}")

def run_comprehensive_test():
    """Run all tests with comprehensive output"""
    print("🚀 Starting Comprehensive Blockchain Tools Test")
    print("=" * 60)
    
    try:
        # Test available blockchains first
        test_available_blockchains_tool()
        
        # Test available timeframes
        test_available_timeframes_tool()
        
        # Test main tools
        test_categories_by_gas_fees_tool()
        test_top_contracts_by_gas_fees_tool()
        
        print_separator("Test Summary")
        print("✅ All tests completed successfully!")
        print("\n💡 Tips:")
        print("   - Check the output above for any errors or unexpected results")
        print("   - Use the available_blockchains_tool to see supported networks")
        print("   - Use available_timeframes_tool to see supported timeframes")
        print("   - Modify test cases in this script to test different scenarios")
        
    except Exception as e:
        print(f"❌ Test suite failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_comprehensive_test() 
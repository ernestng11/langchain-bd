#!/usr/bin/env python3
"""
Quick test script for blockchain tools.
Simple and focused testing of the main functions.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tools import blockchain_tools

def quick_test():
    """Quick test of the main blockchain tools"""
    print("🚀 Quick Test of Blockchain Tools")
    print("=" * 50)
    
    # Test 1: Get available blockchains
    print("\n1️⃣ Testing available_blockchains_tool...")
    try:
        result = blockchain_tools.available_blockchains_tool.invoke({})
        if result.get("error"):
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Available blockchains: {result['blockchains']}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Test categories tool with first available blockchain
    print("\n2️⃣ Testing categories_by_gas_fees_tool...")
    try:
        # Use the first available blockchain
        blockchains = blockchain_tools.available_blockchains_tool.invoke({}).get("blockchains", [])
        if blockchains:
            blockchain = blockchains[0]
            result = blockchain_tools.categories_by_gas_fees_tool.invoke({
                "blockchain_name": blockchain,
                "timeframe": "7d"
            })
            if result.get("error"):
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Success! Found {len(result['categories'])} categories for {blockchain}")
                print(f"   Top category: {result['top_category']} ({result['top_category_share']:.2f}%)")
        else:
            print("❌ No blockchains available")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: Test contracts tool
    print("\n3️⃣ Testing top_contracts_by_gas_fees_tool...")
    try:
        blockchains = blockchain_tools.available_blockchains_tool.invoke({}).get("blockchains", [])
        if blockchains:
            blockchain = blockchains[0]
            result = blockchain_tools.top_contracts_by_gas_fees_tool.invoke({
                "blockchain_name": blockchain,
                "timeframe": "7d",
                "top_n": 3
            })
            if result.get("error"):
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Success! Found {len(result['top_contracts'])} contracts for {blockchain}")
                if result['top_contracts']:
                    first_contract = result['top_contracts'][0]
                    print(f"   Top contract: {first_contract.get('name', 'Unknown')}")
        else:
            print("❌ No blockchains available")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n✅ Quick test completed!")

if __name__ == "__main__":
    quick_test() 
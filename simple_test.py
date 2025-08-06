#!/usr/bin/env python3
"""
Simple test script for blockchain tools.
Run this from the project root directory.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import tools
from tools import blockchain_tools

def main():
    print("🚀 Testing Blockchain Tools")
    print("=" * 50)
    
    # Test 1: Available blockchains
    print("\n1️⃣ Testing available_blockchains_tool...")
    result = blockchain_tools.available_blockchains_tool.invoke({})
    if result.get("error"):
        print(f"❌ Error: {result['error']}")
        return
    else:
        print(f"✅ Available blockchains: {result['blockchains']}")
        available_blockchains = result['blockchains']
    
    if not available_blockchains:
        print("❌ No blockchains available")
        return
    
    # Test 2: Categories tool
    blockchain = available_blockchains[0]
    print(f"\n2️⃣ Testing categories_by_gas_fees_tool for {blockchain}...")
    result = blockchain_tools.categories_by_gas_fees_tool.invoke({
        "blockchain_name": blockchain,
        "timeframe": "7d"
    })
    
    if result.get("error"):
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Success! Found {len(result['categories'])} categories")
        print(f"   Top category: {result['top_category']} ({result['top_category_share']:.2f}%)")
    
    # Test 3: Contracts tool
    print(f"\n3️⃣ Testing top_contracts_by_gas_fees_tool for {blockchain}...")
    result = blockchain_tools.top_contracts_by_gas_fees_tool.invoke({
        "blockchain_name": blockchain,
        "timeframe": "7d",
        "top_n": 3
    })
    
    if result.get("error"):
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Success! Found {len(result['top_contracts'])} contracts")
        if result['top_contracts']:
            first_contract = result['top_contracts'][0]
            print(f"   Top contract: {first_contract.get('name', 'Unknown')}")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main() 
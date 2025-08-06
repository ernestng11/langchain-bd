from src.tools import blockchain_tools

def test_categories_by_gas_fees_tool():
    result = blockchain_tools.categories_by_gas_fees_tool.invoke({"blockchain_name": "mantle", "timeframe": "7d"})
    print("categories_by_gas_fees_tool result:", result)
    assert isinstance(result, dict)
    assert result["error"] is None
    assert "categories" in result
    assert isinstance(result["categories"], list)
    print("test_categories_by_gas_fees_tool passed.")

def test_available_blockchains_tool():
    result = blockchain_tools.available_blockchains_tool.invoke({})
    print("available_blockchains_tool result:", result)
    assert isinstance(result, dict)
    assert result["error"] is None
    assert "blockchains" in result
    assert isinstance(result["blockchains"], list)
    print("test_available_blockchains_tool passed.")

def test_top_contracts_by_gas_fees_tool():
    result = blockchain_tools.top_contracts_by_gas_fees_tool.invoke({
        "blockchain_name": "mantle",
        "timeframe": "7d",
        "top_n": 20,
        "main_category_key": "social"
    })
    print("top_contracts_by_gas_fees_tool result:", result)
    assert isinstance(result, dict)
    assert result["error"] is None
    assert "top_contracts" in result
    assert isinstance(result["top_contracts"], list)
    print("test_top_contracts_by_gas_fees_tool passed.")

def test_available_timeframes_tool():
    result = blockchain_tools.available_timeframes_tool.invoke({"blockchain_name": "mantle"})
    print("available_timeframes_tool result:", result)
    assert isinstance(result, dict)
    assert result["error"] is None
    assert "timeframes" in result
    assert isinstance(result["timeframes"], list)
    print("test_available_timeframes_tool passed.")

if __name__ == "__main__":
    test_categories_by_gas_fees_tool()
    test_available_blockchains_tool()
    test_top_contracts_by_gas_fees_tool()
    test_available_timeframes_tool()
    print("All tests passed.") 
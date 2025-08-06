#!/usr/bin/env python3
"""
Test script to verify the TrendAnalysisAgent renaming works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.growthepie_analysis_agent import TrendAnalysisAgent

def test_trend_analysis_agent():
    """Test that the TrendAnalysisAgent can be instantiated"""
    try:
        agent = TrendAnalysisAgent()
        print("✅ TrendAnalysisAgent imported and instantiated successfully")
        print(f"Agent name: {agent.name}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_trend_analysis_agent() 
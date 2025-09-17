#!/usr/bin/env python3
"""
Simple 7-Agent Trading Analysis Launcher
Runs the original simple 7-agent system
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def main():
    """Run simple 7-agent analysis"""
    print("🚀 Simple 7-Agent Trading Analysis")
    print("=" * 50)
    print("📊 Original system with 7 agents")
    print("⚡ Fast and straightforward analysis")
    print("=" * 50)
    
    try:
        from src.workflows.simple_7agent_workflow import run_simple_analysis
        
        # You can customize the stock and question here
        stock_symbol = "AAPL"
        question = "Should I buy stocks of Apple?"
        
        print(f"\n🎯 Analyzing: {stock_symbol}")
        print(f"❓ Question: {question}")
        print("\n🤖 Starting 7-agent discussion...")
        
        await run_simple_analysis(stock_symbol, question)
        
    except KeyboardInterrupt:
        print("\n\n❌ Analysis interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Make sure dependencies are installed: pip install -r requirements.txt")

if __name__ == "__main__":
    asyncio.run(main())
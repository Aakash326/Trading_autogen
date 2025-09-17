#!/usr/bin/env python3
"""
Enhanced 13-Agent Trading Analysis Launcher
Runs the new interactive 13-agent system with user input
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def main():
    """Run enhanced 13-agent interactive analysis"""
    print("🚀 Enhanced 13-Agent Trading Analysis")
    print("=" * 50)
    print("🤖 Interactive system with 13 agents")
    print("🎯 User-guided company and analysis selection")
    print("🌐 Real-time web research capabilities")
    print("=" * 50)
    
    try:
        from src.workflows.hybrid_team import run_interactive_hybrid_analysis
        
        print("\n🔄 Starting interactive session...")
        await run_interactive_hybrid_analysis()
        
    except KeyboardInterrupt:
        print("\n\n❌ Analysis interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Make sure dependencies are installed: pip install -r requirements.txt")

if __name__ == "__main__":
    asyncio.run(main())
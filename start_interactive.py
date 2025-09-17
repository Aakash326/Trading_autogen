#!/usr/bin/env python3
"""
Interactive Trading Analysis Console Application
Starts the workflow with user prompts for company and investment choice selection
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def main():
    """Main entry point for interactive analysis"""
    
    print("🎉 Welcome to Interactive Trading Analysis!")
    print("=" * 60)
    print("📊 13-Agent AI System for Comprehensive Stock Analysis")
    print("🤖 Enhanced with Compliance Officer Orchestration")
    print("🌐 Market Data Analyst with Real-time Web Research")
    print("=" * 60)
    
    try:
        # Import and run the interactive workflow
        from src.workflows.interactive_workflow import run_interactive_workflow
        
        print("\n🔄 Starting Interactive Session...")
        result = await run_interactive_workflow()
        
        if result:
            print("\n" + "=" * 80)
            print("📊 ANALYSIS COMPLETE")
            print("=" * 80)
            print(f"📈 Symbol: {result.get('symbol', 'N/A')}")
            print(f"✅ Status: {result.get('status', 'N/A')}")
            
            if 'analysis_duration_seconds' in result:
                print(f"⏱️ Duration: {result['analysis_duration_seconds']:.1f} seconds")
            
            if 'agent_participation' in result:
                agent_info = result['agent_participation']
                print(f"🤖 Total Agents: {agent_info.get('total_agents', 'N/A')}")
                print(f"🔧 AutoGen Agents: {len(agent_info.get('autogen_agents', []))}")
                print(f"⚙️ CrewAI Agents: {len(agent_info.get('crewai_agents', []))}")
            
            if 'workflow_phases' in result:
                phases = result['workflow_phases']
                final_rec = phases.get('phase_5_synthesis', {}).get('final_recommendation', 'N/A')
                print(f"💡 Final Recommendation: {final_rec}")
            
            # User context information
            if 'user_context' in result:
                user_info = result['user_context']
                if 'company_choice' in user_info:
                    company = user_info['company_choice']
                    print(f"🏢 Company: {company.get('name', 'N/A')} ({company.get('sector', 'N/A')})")
                
                if 'investment_choice' in user_info:
                    investment = user_info['investment_choice']
                    print(f"🎯 Analysis Type: {investment.get('title', 'N/A')}")
            
            print("=" * 80)
            print("✅ Analysis completed successfully!")
            
            # Ask if user wants to save results
            save_choice = input("\n💾 Save results to file? (y/n): ").strip().lower()
            if save_choice in ['y', 'yes']:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"analysis_results_{result.get('symbol', 'unknown')}_{timestamp}.json"
                
                try:
                    import json
                    with open(filename, 'w') as f:
                        json.dump(result, f, indent=2, default=str)
                    print(f"📄 Results saved to: {filename}")
                except Exception as e:
                    print(f"❌ Error saving file: {e}")
        else:
            print("\n❌ Analysis was not completed.")
            print("💡 Please try again or check your selections.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Interactive session interrupted by user.")
        print("Thanks for using the Trading Analysis System!")
    
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💡 Please check your configuration and try again.")
    
    finally:
        print("\n👋 Goodbye!")

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking system dependencies...")
    
    missing_deps = []
    
    try:
        import autogen_agentchat
        print("✅ AutoGen AgentChat")
    except ImportError:
        missing_deps.append("autogen-agentchat")
        print("❌ AutoGen AgentChat")
    
    try:
        import tavily
        print("✅ Tavily (Web Research)")
    except ImportError:
        missing_deps.append("tavily-python")
        print("❌ Tavily (Web Research)")
    
    try:
        import fastapi
        print("✅ FastAPI")
    except ImportError:
        missing_deps.append("fastapi")
        print("❌ FastAPI")
    
    try:
        import yfinance
        print("✅ YFinance (Market Data)")
    except ImportError:
        missing_deps.append("yfinance")
        print("❌ YFinance (Market Data)")
    
    try:
        import crewai
        print("⚠️ CrewAI (Optional - will use simulation mode)")
    except ImportError:
        print("⚠️ CrewAI (Optional - not installed)")
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("💡 Install with: pip install " + " ".join(missing_deps))
        return False
    
    print("\n✅ All core dependencies available!")
    return True

if __name__ == "__main__":
    print("🚀 Interactive Trading Analysis System")
    print("=" * 50)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again.")
        sys.exit(1)
    
    print("\n" + "🎯 STARTING INTERACTIVE MODE")
    print("=" * 50)
    
    # Run the interactive workflow
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
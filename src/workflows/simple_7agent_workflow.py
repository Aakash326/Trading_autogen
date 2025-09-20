"""
Simple 7-Agent Trading Workflow
Original simple system with 7 agents discussing stock analysis
"""

import asyncio
import os
import sys

# Add project root to Python path for direct execution
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.messages import TextMessage
# from autogen_agentchat.ui import Console  # Removed - using custom display

from src.agents.compilence_officer import compilence_officer
from src.agents.Risk_Manager import risk_manager
from src.agents.market_dataAnalyst import data_analyst
from src.agents.quantitative_analyst import quantitative_analysis
from src.agents.research_agent import create_organiser_agent
from src.agents.Strategy_devoloper import strategy_developer
from src.agents.report import report_agent

def create_simple_trading_team():
    """Create the simple 7-agent trading team"""
    print("🚀 Initializing Simple 7-Agent Trading Team...")
    
    # Create all 7 agents
    organiser_agent = create_organiser_agent()
    risk_manager_agent = risk_manager()
    data_analyst_agent = data_analyst()
    quantitative_analyst_agent = quantitative_analysis()
    strategy_developer_agent = strategy_developer()
    compliance_officer_agent = compilence_officer()
    report_agent_instance = report_agent()
    
    # Create the team
    team = RoundRobinGroupChat(
        participants=[
            organiser_agent,
            risk_manager_agent,
            data_analyst_agent,
            quantitative_analyst_agent,
            strategy_developer_agent,
            compliance_officer_agent,
            report_agent_instance
        ],
        termination_condition=TextMentionTermination("FINAL_ANALYSIS_COMPLETE"),
        max_turns=21  # 3 full rounds for all 7 agents
    )
    
    print(f"✅ Simple trading team created with 7 agents")
    return team

async def run_simple_analysis(stock_symbol="AAPL", question="Should I buy this stock?"):
    """Run simple 7-agent analysis"""
    print(f"📊 Starting Simple 7-Agent Analysis for {stock_symbol}")
    print("=" * 60)
    
    team = create_simple_trading_team()
    enhanced_question = f"""
{question} for stock symbol: {stock_symbol}

CRITICAL AGENT INSTRUCTIONS:
1. Each agent MUST provide detailed analysis in their specialty area
2. Wait for ALL 7 agents to contribute before any final decisions
3. Only the ReportAgent should use "FINAL_ANALYSIS_COMPLETE" after receiving input from all other agents
4. Provide specific data, numbers, and concrete recommendations
5. Do NOT use "STOP" or end discussion prematurely

REQUIRED AGENT PARTICIPATION ORDER:
- OrganiserAgent: Market data and initial assessment
- RiskManager: Risk analysis and portfolio impact  
- DataAnalyst: Fundamental analysis and financials
- QuantitativeAnalyst: Technical analysis and metrics
- StrategyDeveloper: Investment strategy and timing
- ComplianceOfficer: Regulatory and compliance review
- ReportAgent: FINAL synthesis after all others (use "FINAL_ANALYSIS_COMPLETE")

Proceed with comprehensive analysis.
"""
    
    task = TextMessage(
        content=enhanced_question,
        source='user'
    )
    
    print(f"🤖 7 agents discussing: {question} ({stock_symbol})")
    result_stream = team.run_stream(task=task)
    
    # Custom message display instead of Console
    message_count = 0
    async for message in result_stream:
        if hasattr(message, 'content') and hasattr(message, 'source'):
            message_count += 1
            source = getattr(message, 'source', 'Unknown')
            content = str(message.content)
            
            print(f"\n{'='*80}")
            print(f"📝 Message {message_count} from {source}")
            print(f"{'='*80}")
            print(content)
            
        # Stop after reasonable number of messages to prevent infinite loops
        if message_count >= 25:
            print(f"\n⏹️ Stopping after {message_count} messages (conversation limit reached)")
            break
    
    print(f"\n✅ Analysis complete! {message_count} agent messages exchanged.")

class InteractiveSelection:
    """Handles user interaction for company and investment choice selection"""
    
    def __init__(self):
        self.company_choices = {
            "1": {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
            "2": {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
            "3": {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology"},
            "4": {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Discretionary"},
            "5": {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Discretionary"},
            "6": {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology"},
            "7": {"symbol": "META", "name": "Meta Platforms Inc.", "sector": "Technology"},
            "8": {"symbol": "NFLX", "name": "Netflix Inc.", "sector": "Communication Services"},
            "9": {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financials"},
            "10": {"symbol": "V", "name": "Visa Inc.", "sector": "Financials"},
            "custom": {"symbol": "CUSTOM", "name": "Enter your own symbol", "sector": "Custom"}
        }
        
        self.investment_choices = {
            "1": {
                "type": "buying_decision",
                "title": "💰 Buying Decision",
                "description": "Should I buy this stock now? Complete investment analysis.",
                "question_template": "Should I buy {symbol} stock now? Provide a comprehensive investment analysis with buy/hold/sell recommendation."
            },
            "2": {
                "type": "selling_decision",
                "title": "💸 Selling Decision",
                "description": "Should I sell this stock now? Exit strategy analysis.",
                "question_template": "Should I sell {symbol} stock now? Analyze if this is a good time to exit my position and provide sell/hold recommendation."
            },
            "3": {
                "type": "health_check",
                "title": "🏥 General Health Check",
                "description": "Overall company and stock health assessment.",
                "question_template": "What is the overall health of {symbol}? Provide a comprehensive health assessment covering financials, performance, and outlook."
            },
            "4": {
                "type": "5day_outlook",
                "title": "📈 Next 5-Day Outlook",
                "description": "Short-term price movement and catalysts for next 5 days.",
                "question_template": "What is the 5-day outlook for {symbol}? Analyze short-term catalysts and expected price movement for the next week."
            },
            "5": {
                "type": "growth_potential",
                "title": "🚀 Growth Potential Analysis",
                "description": "Long-term growth prospects and investment potential.",
                "question_template": "What is the long-term growth potential of {symbol}? Analyze expansion opportunities, market trends, and future prospects."
            },
            "6": {
                "type": "risk_assessment",
                "title": "⚠️ Risk Assessment",
                "description": "Comprehensive risk analysis and downside protection.",
                "question_template": "What are the main risks of investing in {symbol}? Provide a detailed risk assessment covering market, financial, and operational risks."
            },
            "7": {
                "type": "sector_comparison",
                "title": "🏢 Sector Comparison",
                "description": "How does this company compare to its sector peers?",
                "question_template": "How does {symbol} compare to its sector peers? Analyze competitive positioning and relative performance."
            },
            "8": {
                "type": "earnings_forecast",
                "title": "📅 Earnings Forecast",
                "description": "Upcoming earnings analysis and price impact prediction.",
                "question_template": "How will upcoming earnings affect {symbol}? Analyze earnings expectations and potential market impact."
            }
        }
    
    def display_company_menu(self):
        """Display company selection menu"""
        print("\n" + "="*60)
        print("🏢 SELECT COMPANY FOR ANALYSIS")
        print("="*60)
        print("\n📈 Popular Companies:")
        
        for key, company in list(self.company_choices.items())[:-1]:  # Exclude 'custom'
            print(f"  {key:>2}. {company['symbol']:>6} - {company['name']}")
        
        print(f"\n🔍 Custom Option:")
        print(f"  custom. Enter your own stock symbol")
        print("\n" + "-"*60)
    
    def display_investment_menu(self):
        """Display investment choice menu"""
        print("\n" + "="*60)
        print("🎯 SELECT YOUR INVESTMENT QUESTION")
        print("="*60)
        
        for key, choice in self.investment_choices.items():
            print(f"\n{key}. {choice['title']}")
            print(f"   {choice['description']}")
        
        print("\n" + "-"*60)
    
    def get_company_selection(self):
        """Get company selection from user"""
        while True:
            self.display_company_menu()
            user_input = input("\n👉 Enter your choice (1-10 or 'custom'): ").strip().lower()
            
            if user_input in self.company_choices:
                if user_input == "custom":
                    symbol = input("📝 Enter stock symbol (e.g., AAPL): ").strip().upper()
                    if len(symbol) >= 1:
                        return {
                            "symbol": symbol,
                            "name": f"{symbol} (Custom)",
                            "sector": "User Selected"
                        }
                    else:
                        print("❌ Invalid symbol. Please try again.")
                        continue
                else:
                    return self.company_choices[user_input].copy()
            else:
                print("❌ Invalid choice. Please select a number from 1-10 or 'custom'.")
    
    def get_investment_choice(self, company_info):
        """Get investment choice from user"""
        while True:
            print(f"\n🏢 Selected Company: {company_info['symbol']} - {company_info['name']}")
            self.display_investment_menu()
            user_input = input("\n👉 Enter your choice (1-8): ").strip()
            
            if user_input in self.investment_choices:
                choice = self.investment_choices[user_input].copy()
                # Generate specific question
                choice["question"] = choice["question_template"].format(symbol=company_info["symbol"])
                return choice
            else:
                print("❌ Invalid choice. Please select a number from 1-8.")

async def run_interactive_simple_analysis():
    """Main function for interactive 7-agent analysis"""
    print("🎉 Welcome to Simple 7-Agent Trading Analysis!")
    print("=" * 60)
    print("🤖 Fast AI system with collaborative agent discussions")
    print("📊 Real-time stock analysis with 7 specialized agents")
    print("=" * 60)
    
    try:
        # Get user selections
        selector = InteractiveSelection()
        
        # Step 1: Company selection
        print("\n🔄 STEP 1: Company Selection")
        company_info = selector.get_company_selection()
        
        # Step 2: Investment focus selection
        print("\n🔄 STEP 2: Analysis Focus")
        investment_choice = selector.get_investment_choice(company_info)
        
        # Step 3: Confirmation
        print("\n" + "="*80)
        print("📋 ANALYSIS REQUEST SUMMARY")
        print("="*80)
        print(f"🏢 Company: {company_info['symbol']} - {company_info['name']}")
        print(f"🎯 Analysis: {investment_choice['title']}")
        print(f"❓ Question: {investment_choice['question']}")
        print("="*80)
        
        confirm = input("\n✅ Proceed with 7-agent analysis? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ Analysis cancelled.")
            return
        
        # Step 4: Run 7-agent analysis
        print("\n🚀 Starting Simple 7-Agent Analysis...")
        await run_simple_analysis(company_info["symbol"], investment_choice["question"])
        
        print("\n" + "="*80)
        print("📊 ANALYSIS COMPLETE")
        print("="*80)
        print("✅ 7-agent collaborative discussion finished!")
        print("📈 Review the agent conversations above for insights")
        
    except KeyboardInterrupt:
        print("\n❌ Analysis interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main function - runs interactive analysis"""
    await run_interactive_simple_analysis()

if __name__ == "__main__":
    asyncio.run(main())


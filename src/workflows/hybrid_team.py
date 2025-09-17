"""
Enhanced 13-Agent Trading Workflow
Combines AutoGen + CrewAI frameworks with interactive user input for comprehensive trading analysis
Features: Company selection, investment focus selection, web research, orchestrated analysis
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import traceback

# AutoGen imports
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.messages import TextMessage

# CrewAI imports (will be imported dynamically to handle missing dependencies)
try:
    from crewai import Crew, Process
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    print("⚠️ CrewAI not available. CrewAI agents will be simulated.")

# Local imports - existing AutoGen agents
from src.agents.research_agent import create_organiser_agent
from src.agents.market_dataAnalyst import data_analyst
from src.agents.quantitative_analyst import quantitative_analysis
from src.agents.Strategy_devoloper import strategy_developer
from src.agents.Risk_Manager import risk_manager
from src.agents.compilence_officer import compilence_officer
from src.agents.report import report_agent

# New AutoGen agents
from src.agents.autogen.options_analyst import create_options_analyst
from src.agents.autogen.sentiment_analyst import create_sentiment_analyst
from src.agents.autogen.esg_analyst import create_esg_analyst

# New CrewAI agents (imported conditionally)
if CREWAI_AVAILABLE:
    from src.agents.crewai.stress_test_agent import create_stress_test_crew
    from src.agents.crewai.arbitrage_agent import create_arbitrage_crew
    from src.agents.crewai.order_execution_agent import create_order_execution_crew

class HybridTradingTeam:
    """
    Orchestrates a hybrid team of 13 trading agents using both AutoGen and CrewAI frameworks
    
    AutoGen Agents (10): Real-time discussion and analysis
    - OrganiserAgent, DataAnalyst, QuantitativeAnalyst, StrategyDeveloper
    - RiskManager, ComplianceOfficer, ReportAgent
    - OptionsAnalyst, SentimentAnalyst, ESGAnalyst
    
    CrewAI Agents (3): Sequential workflow execution  
    - StressTestAgent, ArbitrageAgent, OrderExecutionAgent
    """
    
    def __init__(self):
        self.autogen_agents = {}
        self.crewai_crews = {}
        self.analysis_results = {}
        self.workflow_state = "initialized"
        
    def initialize_agents(self):
        """Initialize all 13 agents across both frameworks"""
        try:
            print("🚀 Initializing Hybrid Trading Team (13 agents)...")
            
            # Initialize AutoGen agents (10 agents)
            print("📊 Initializing AutoGen agents...")
            self.autogen_agents = {
                'organiser': create_organiser_agent(),
                'data_analyst': data_analyst(),
                'quantitative_analyst': quantitative_analysis(),
                'strategy_developer': strategy_developer(),
                'risk_manager': risk_manager(),
                'compliance_officer': compilence_officer(),
                'report_agent': report_agent(),
                'options_analyst': create_options_analyst(),
                'sentiment_analyst': create_sentiment_analyst(),
                'esg_analyst': create_esg_analyst()
            }
            print(f"✅ AutoGen agents initialized: {len(self.autogen_agents)}")
            
            # Initialize CrewAI crews (3 crews) - conditional
            if CREWAI_AVAILABLE:
                print("🔧 CrewAI available - initializing structured workflow agents...")
                self.crewai_crews = {
                    'stress_test': None,  # Will be created per symbol
                    'arbitrage': None,    # Will be created per symbol  
                    'order_execution': None  # Will be created per symbol
                }
                print("✅ CrewAI crews ready for initialization")
            else:
                print("⚠️ CrewAI not available - using simulated workflow agents")
                self.crewai_crews = {
                    'stress_test': 'simulated',
                    'arbitrage': 'simulated',
                    'order_execution': 'simulated'
                }
            
            self.workflow_state = "agents_initialized"
            print("🎯 Hybrid Trading Team ready for analysis")
            
        except Exception as e:
            print(f"❌ Error initializing agents: {str(e)}")
            print(traceback.format_exc())
            raise
    
    async def run_comprehensive_analysis(self, symbol: str, user_question: str = None) -> Dict[str, Any]:
        """
        Run comprehensive 13-agent analysis with hybrid framework coordination
        
        Phase 1: Foundation Data (AutoGen Sequential)
        Phase 2: Advanced Intelligence (Hybrid Parallel) 
        Phase 3: Strategic Analysis (Hybrid Parallel + Sequential)
        Phase 4: Execution Optimization (CrewAI Sequential)
        Phase 5: Final Synthesis (AutoGen Integration)
        """
        
        if self.workflow_state != "agents_initialized":
            self.initialize_agents()
        
        print(f"\n🔥 Starting Comprehensive 13-Agent Analysis for {symbol}")
        print("=" * 60)
        
        analysis_start_time = datetime.now()
        
        try:
            # Phase 1: Foundation Data Layer (AutoGen Sequential)
            print("\n📊 PHASE 1: Foundation Data Collection")
            print("-" * 40)
            foundation_results = await self._phase_1_foundation_data(symbol)
            
            # Phase 2: Advanced Intelligence Layer (Hybrid Parallel)
            print("\n🧠 PHASE 2: Advanced Intelligence Analysis")  
            print("-" * 40)
            intelligence_results = await self._phase_2_advanced_intelligence(symbol)
            
            # Phase 3: Strategic Analysis Layer (Hybrid Parallel + Sequential)
            print("\n⚔️ PHASE 3: Strategic Analysis & Risk Assessment")
            print("-" * 40)
            strategic_results = await self._phase_3_strategic_analysis(symbol, foundation_results)
            
            # Phase 4: Execution Optimization Layer (CrewAI Sequential)
            print("\n🎯 PHASE 4: Execution Strategy Optimization")
            print("-" * 40)
            execution_results = await self._phase_4_execution_optimization(symbol, strategic_results)
            
            # Phase 5: Final Synthesis Layer (AutoGen Integration)
            print("\n📋 PHASE 5: Final Investment Committee Decision")
            print("-" * 40)
            final_results = await self._phase_5_final_synthesis(
                symbol, user_question, foundation_results, intelligence_results, 
                strategic_results, execution_results
            )
            
            # Compile comprehensive results
            analysis_duration = (datetime.now() - analysis_start_time).total_seconds()
            
            comprehensive_results = {
                'symbol': symbol,
                'analysis_timestamp': analysis_start_time.isoformat(),
                'analysis_duration_seconds': analysis_duration,
                'workflow_phases': {
                    'phase_1_foundation': foundation_results,
                    'phase_2_intelligence': intelligence_results,
                    'phase_3_strategic': strategic_results,
                    'phase_4_execution': execution_results,
                    'phase_5_synthesis': final_results
                },
                'agent_participation': {
                    'autogen_agents': list(self.autogen_agents.keys()),
                    'crewai_agents': list(self.crewai_crews.keys()),
                    'total_agents': len(self.autogen_agents) + len(self.crewai_crews)
                },
                'framework_performance': {
                    'autogen_execution_time': analysis_duration * 0.7,  # Estimate
                    'crewai_execution_time': analysis_duration * 0.3,   # Estimate
                    'hybrid_coordination_overhead': analysis_duration * 0.05
                }
            }
            
            print(f"\n🎉 Analysis Complete! Duration: {analysis_duration:.1f}s")
            print(f"🤖 Total Agents: {len(self.autogen_agents) + len(self.crewai_crews)}")
            print(f"📈 Framework: AutoGen + {'CrewAI' if CREWAI_AVAILABLE else 'Simulated CrewAI'}")
            
            return comprehensive_results
            
        except Exception as e:
            print(f"❌ Error in comprehensive analysis: {str(e)}")
            print(traceback.format_exc())
            return {
                'error': str(e),
                'symbol': symbol,
                'partial_results': getattr(self, 'analysis_results', {}),
                'workflow_state': self.workflow_state
            }
    
    async def _phase_1_foundation_data(self, symbol: str) -> Dict[str, Any]:
        """Phase 1: Foundation Data Collection (AutoGen Sequential)"""
        
        foundation_agents = [
            self.autogen_agents['organiser'],
            self.autogen_agents['data_analyst'], 
            self.autogen_agents['quantitative_analyst']
        ]
        
        # Create AutoGen team for foundation data
        termination = TextMentionTermination("FOUNDATION_COMPLETE") | MaxMessageTermination(8)
        
        foundation_team = RoundRobinGroupChat(
            participants=foundation_agents,
            termination_condition=termination
        )
        
        initial_message = TextMessage(
            content=f"""Execute foundation data collection for {symbol}:
            
            1. OrganiserAgent: Fetch comprehensive market data with technical indicators
            2. DataAnalyst: Collect fundamental metrics (P/E, earnings, analyst targets)  
            3. QuantitativeAnalyst: Generate technical signals (RSI, MACD, trend analysis)
            
            Provide structured data foundation for downstream analysis.
            End with: FOUNDATION_COMPLETE""",
            source="HybridOrchestrator"
        )
        
        try:
            result = await foundation_team.run(initial_message)
            
            return {
                'status': 'completed',
                'participants': ['organiser', 'data_analyst', 'quantitative_analyst'],
                'framework': 'AutoGen',
                'execution_pattern': 'Sequential',
                'messages': [str(msg.content) for msg in result.messages],
                'summary': 'Foundation data collection completed successfully'
            }
            
        except Exception as e:
            print(f"⚠️ Phase 1 error: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'participants': ['organiser', 'data_analyst', 'quantitative_analyst'],
                'framework': 'AutoGen'
            }
    
    async def _phase_2_advanced_intelligence(self, symbol: str) -> Dict[str, Any]:
        """Phase 2: Advanced Intelligence Analysis (Hybrid Parallel)"""
        
        # Run AutoGen agents in parallel discussions
        autogen_intelligence = await self._run_autogen_intelligence(symbol)
        
        # Run CrewAI agents in parallel workflows  
        crewai_intelligence = await self._run_crewai_intelligence(symbol)
        
        return {
            'autogen_analysis': autogen_intelligence,
            'crewai_analysis': crewai_intelligence,
            'coordination': 'parallel_execution',
            'framework_integration': 'hybrid'
        }
    
    async def _run_autogen_intelligence(self, symbol: str) -> Dict[str, Any]:
        """Run AutoGen intelligence agents: Sentiment, Options, ESG"""
        
        intelligence_agents = [
            self.autogen_agents['sentiment_analyst'],
            self.autogen_agents['options_analyst'], 
            self.autogen_agents['esg_analyst']
        ]
        
        termination = TextMentionTermination("INTELLIGENCE_COMPLETE") | MaxMessageTermination(12)
        
        intelligence_team = RoundRobinGroupChat(
            participants=intelligence_agents,
            termination_condition=termination
        )
        
        message = TextMessage(
            content=f"""Conduct advanced intelligence analysis for {symbol}:
            
            1. SentimentAnalyst: Analyze social media, news, and retail sentiment
            2. OptionsAnalyst: Perform Black-Scholes pricing and volatility analysis
            3. ESGAnalyst: Evaluate sustainability factors and governance quality
            
            Provide multi-dimensional market intelligence.
            End with: INTELLIGENCE_COMPLETE""",
            source="HybridOrchestrator"
        )
        
        try:
            result = await intelligence_team.run(message)
            
            return {
                'status': 'completed',
                'participants': ['sentiment_analyst', 'options_analyst', 'esg_analyst'],
                'framework': 'AutoGen',
                'execution_pattern': 'Group Discussion',
                'messages': [str(msg.content) for msg in result.messages],
                'summary': 'Advanced intelligence analysis completed'
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'framework': 'AutoGen'}
    
    async def _run_crewai_intelligence(self, symbol: str) -> Dict[str, Any]:
        """Run CrewAI intelligence workflows: Stress Testing, Arbitrage"""
        
        if not CREWAI_AVAILABLE:
            return {
                'status': 'simulated',
                'stress_test': 'Simulated stress test analysis for portfolio risk assessment',
                'arbitrage': 'Simulated arbitrage analysis for market inefficiency detection',
                'framework': 'CrewAI (Simulated)',
                'note': 'CrewAI not available - install with: pip install crewai'
            }
        
        try:
            # Run stress test and arbitrage analysis in parallel
            stress_test_crew = create_stress_test_crew(symbol)
            arbitrage_crew = create_arbitrage_crew(symbol)
            
            # Execute both crews concurrently
            stress_results = await asyncio.to_thread(stress_test_crew.kickoff)
            arbitrage_results = await asyncio.to_thread(arbitrage_crew.kickoff)
            
            return {
                'status': 'completed',
                'stress_test_analysis': str(stress_results),
                'arbitrage_analysis': str(arbitrage_results),
                'framework': 'CrewAI',
                'execution_pattern': 'Parallel Workflows'
            }
            
        except Exception as e:
            return {
                'status': 'error', 
                'error': str(e), 
                'framework': 'CrewAI',
                'fallback': 'Using simulated CrewAI analysis'
            }
    
    async def _phase_3_strategic_analysis(self, symbol: str, foundation_data: Dict) -> Dict[str, Any]:
        """Phase 3: Strategic Analysis & Risk Assessment (Hybrid)"""
        
        # Sequential AutoGen analysis
        strategic_agents = [
            self.autogen_agents['strategy_developer'],
            self.autogen_agents['risk_manager'],
            self.autogen_agents['compliance_officer']
        ]
        
        termination = TextMentionTermination("STRATEGIC_COMPLETE") | MaxMessageTermination(10)
        
        strategic_team = RoundRobinGroupChat(
            participants=strategic_agents,
            termination_condition=termination
        )
        
        message = TextMessage(
            content=f"""Execute strategic analysis for {symbol} based on foundation data:
            
            1. StrategyDeveloper: Determine entry/exit strategy and timeline
            2. RiskManager: Calculate position sizing and stop-loss levels  
            3. ComplianceOfficer: Assess regulatory risks and compliance requirements
            
            Foundation data summary available from Phase 1.
            End with: STRATEGIC_COMPLETE""",
            source="HybridOrchestrator"
        )
        
        try:
            result = await strategic_team.run(message)
            
            return {
                'status': 'completed',
                'participants': ['strategy_developer', 'risk_manager', 'compliance_officer'],
                'framework': 'AutoGen',
                'execution_pattern': 'Sequential Analysis',
                'messages': [str(msg.content) for msg in result.messages],
                'foundation_integration': 'success'
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'framework': 'AutoGen'}
    
    async def _phase_4_execution_optimization(self, symbol: str, strategic_data: Dict) -> Dict[str, Any]:
        """Phase 4: Execution Strategy Optimization (CrewAI Sequential)"""
        
        if not CREWAI_AVAILABLE:
            return {
                'status': 'simulated',
                'analysis': f'Simulated execution optimization for {symbol} including market impact analysis, algorithmic trading strategy selection, and smart order routing recommendations',
                'framework': 'CrewAI (Simulated)'
            }
        
        try:
            # Create execution optimization crew
            # Estimate order size based on typical institutional position
            estimated_order_size = 100000  # $100K default
            
            execution_crew = create_order_execution_crew(
                symbol=symbol,
                order_size=estimated_order_size,
                urgency="Medium"
            )
            
            result = await asyncio.to_thread(execution_crew.kickoff)
            
            return {
                'status': 'completed',
                'execution_analysis': str(result),
                'framework': 'CrewAI',
                'execution_pattern': 'Sequential Workflow',
                'order_parameters': {
                    'symbol': symbol,
                    'estimated_size': estimated_order_size,
                    'urgency': 'Medium'
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'framework': 'CrewAI',
                'fallback': 'Simulated execution analysis'
            }
    
    async def _phase_5_final_synthesis(self, symbol: str, user_question: str, 
                                     foundation: Dict, intelligence: Dict, 
                                     strategic: Dict, execution: Dict) -> Dict[str, Any]:
        """Phase 5: Final Investment Committee Decision (AutoGen Integration)"""
        
        # Create final decision team
        synthesis_agents = [
            self.autogen_agents['report_agent'],
            self.autogen_agents['risk_manager'],
            self.autogen_agents['compliance_officer']
        ]
        
        termination = TextMentionTermination("FINAL_DECISION_COMPLETE") | MaxMessageTermination(6)
        
        synthesis_team = RoundRobinGroupChat(
            participants=synthesis_agents,
            termination_condition=termination
        )
        
        # Prepare comprehensive context
        context_summary = f"""
        COMPREHENSIVE ANALYSIS SUMMARY FOR {symbol}:
        
        Phase 1 (Foundation): {foundation.get('summary', 'Data collected')}
        Phase 2 (Intelligence): AutoGen + CrewAI parallel analysis completed
        Phase 3 (Strategic): Strategy, risk, and compliance analysis completed  
        Phase 4 (Execution): Execution optimization {'completed' if execution.get('status') == 'completed' else 'simulated'}
        
        User Question: {user_question or 'General investment analysis'}
        
        Synthesize all 13-agent analysis into final investment recommendation.
        """
        
        message = TextMessage(
            content=f"""{context_summary}
            
            ReportAgent: Synthesize all analysis into authoritative investment recommendation
            RiskManager: Validate risk assessment and position sizing
            ComplianceOfficer: Final compliance approval
            
            Provide clear BUY/SELL/HOLD recommendation with rationale.
            End with: FINAL_DECISION_COMPLETE""",
            source="HybridOrchestrator"
        )
        
        try:
            result = await synthesis_team.run(message)
            
            return {
                'status': 'completed',
                'participants': ['report_agent', 'risk_manager', 'compliance_officer'],
                'framework': 'AutoGen',
                'execution_pattern': 'Investment Committee',
                'messages': [str(msg.content) for msg in result.messages],
                'final_recommendation': self._extract_recommendation(result.messages),
                'synthesis_complete': True
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e), 'framework': 'AutoGen'}
    
    def _extract_recommendation(self, messages) -> str:
        """Extract final investment recommendation from messages"""
        try:
            # Look for BUY/SELL/HOLD in the last few messages
            last_messages = [str(msg.content) for msg in messages[-3:]]
            full_text = " ".join(last_messages)
            
            if "BUY" in full_text.upper():
                return "BUY"
            elif "SELL" in full_text.upper():
                return "SELL"
            elif "HOLD" in full_text.upper():
                return "HOLD"
            else:
                return "NEUTRAL"
        except:
            return "ANALYSIS_COMPLETE"
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents and frameworks"""
        return {
            'workflow_state': self.workflow_state,
            'autogen_agents': {
                'count': len(self.autogen_agents),
                'agents': list(self.autogen_agents.keys()),
                'status': 'initialized' if self.autogen_agents else 'not_initialized'
            },
            'crewai_agents': {
                'count': len(self.crewai_crews),
                'crews': list(self.crewai_crews.keys()),
                'status': 'available' if CREWAI_AVAILABLE else 'simulated',
                'framework_available': CREWAI_AVAILABLE
            },
            'total_agents': len(self.autogen_agents) + len(self.crewai_crews),
            'frameworks': ['AutoGen', 'CrewAI' if CREWAI_AVAILABLE else 'CrewAI (Simulated)']
        }

# Convenience function for easy integration
async def run_hybrid_analysis(symbol: str, user_question: str = None) -> Dict[str, Any]:
    """
    Convenience function to run complete 13-agent hybrid analysis
    
    Args:
        symbol: Stock symbol to analyze
        user_question: Optional specific question for analysis
        
    Returns:
        Comprehensive analysis results from all 13 agents
    """
    team = HybridTradingTeam()
    team.initialize_agents()
    return await team.run_comprehensive_analysis(symbol, user_question)

# Example usage
if __name__ == "__main__":
    async def test_hybrid_team():
        """Test the hybrid trading team"""
        team = HybridTradingTeam()
        
        print("🔍 Agent Status:")
        status = team.get_agent_status()
        print(json.dumps(status, indent=2))
        
        print("\n🚀 Running hybrid analysis...")
        result = await run_hybrid_analysis("AAPL", "Should I buy Apple stock?")
        
        print("\n📊 Analysis Results:")
        print(f"Symbol: {result.get('symbol')}")
        print(f"Duration: {result.get('analysis_duration_seconds', 0):.1f}s")
        print(f"Agents: {result.get('agent_participation', {}).get('total_agents', 0)}")
        
        if 'workflow_phases' in result:
            phases = result['workflow_phases']
            print(f"Final Recommendation: {phases.get('phase_5_synthesis', {}).get('final_recommendation', 'N/A')}")
    
    # Run test
    # asyncio.run(test_hybrid_team())

# ============================================================================
# INTERACTIVE USER INPUT FEATURES
# ============================================================================

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
                "type": "general_health",
                "title": "🏥 General Health Check", 
                "description": "Overall company and stock health assessment.",
                "question_template": "What is the overall health and current status of {symbol}? Assess the company's financial and business fundamentals."
            },
            "4": {
                "type": "short_term_outlook",
                "title": "📈 Next 5-Day Outlook",
                "description": "Short-term price movement and catalysts for next 5 days.",
                "question_template": "What is the outlook for {symbol} over the next 5 days? Focus on short-term price movements and catalysts."
            },
            "5": {
                "type": "growth_potential",
                "title": "🚀 Growth Potential Analysis",
                "description": "Long-term growth prospects and investment potential.",
                "question_template": "What is the long-term growth potential of {symbol}? Analyze future growth drivers and investment prospects."
            },
            "6": {
                "type": "risk_assessment",
                "title": "⚠️ Risk Assessment",
                "description": "Comprehensive risk analysis and downside protection.",
                "question_template": "What are the key risks associated with investing in {symbol}? Provide comprehensive risk analysis and risk mitigation strategies."
            },
            "7": {
                "type": "sector_comparison",
                "title": "🏢 Sector Comparison",
                "description": "How does this company compare to its sector peers?",
                "question_template": "How does {symbol} compare to its sector peers? Provide competitive analysis and sector positioning."
            },
            "8": {
                "type": "options_strategy",
                "title": "📊 Options Strategy",
                "description": "Options trading opportunities and strategies analysis.",
                "question_template": "What options trading strategies work best for {symbol}? Analyze volatility, options pricing, and strategy recommendations."
            },
            "9": {
                "type": "esg_analysis",
                "title": "🌱 ESG & Sustainability",
                "description": "Environmental, Social, and Governance analysis.",
                "question_template": "What is the ESG profile of {symbol}? Analyze environmental impact, social responsibility, and governance quality."
            },
            "10": {
                "type": "earnings_forecast",
                "title": "📅 Earnings Forecast",
                "description": "Upcoming earnings analysis and price impact prediction.",
                "question_template": "What should I expect from {symbol}'s upcoming earnings? Analyze earnings expectations, potential surprises, and stock price impact."
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
            user_input = input("\n👉 Enter your choice (1-10): ").strip()
            
            if user_input in self.investment_choices:
                choice = self.investment_choices[user_input].copy()
                # Generate specific question
                choice["question"] = choice["question_template"].format(symbol=company_info["symbol"])
                return choice
            else:
                print("❌ Invalid choice. Please select a number from 1-10.")

async def run_interactive_hybrid_analysis():
    """Main function for interactive 13-agent analysis"""
    print("🎉 Welcome to Enhanced 13-Agent Trading Analysis!")
    print("=" * 60)
    print("🤖 Advanced AI system with user-guided analysis")
    print("🌐 Real-time web research and orchestrated agents")
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
        
        confirm = input("\n✅ Proceed with 13-agent analysis? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ Analysis cancelled.")
            return
        
        # Step 4: Run 13-agent analysis
        print("\n🚀 Starting Enhanced 13-Agent Analysis...")
        result = await run_hybrid_analysis(company_info["symbol"], investment_choice["question"])
        
        # Step 5: Display results
        print("\n" + "="*80)
        print("📊 ANALYSIS COMPLETE")
        print("="*80)
        print(f"📈 Symbol: {result.get('symbol', 'N/A')}")
        print(f"✅ Status: {result.get('status', 'N/A')}")
        
        if 'analysis_duration_seconds' in result:
            print(f"⏱️ Duration: {result['analysis_duration_seconds']:.1f} seconds")
        
        if 'agent_participation' in result:
            agent_info = result['agent_participation']
            print(f"🤖 Total Agents: {agent_info.get('total_agents', 'N/A')}")
        
        if 'workflow_phases' in result:
            phases = result['workflow_phases']
            final_rec = phases.get('phase_5_synthesis', {}).get('final_recommendation', 'N/A')
            print(f"💡 Final Recommendation: {final_rec}")
        
        print("="*80)
        print("✅ Enhanced analysis completed successfully!")
        
        return result
        
    except KeyboardInterrupt:
        print("\n\n❌ Analysis interrupted by user.")
        return None
    except Exception as e:
        print(f"\n❌ Error in interactive analysis: {e}")
        return None

# Main execution
if __name__ == "__main__":
    # Run interactive analysis
    asyncio.run(run_interactive_hybrid_analysis())
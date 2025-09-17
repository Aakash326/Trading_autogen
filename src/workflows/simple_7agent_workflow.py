"""
Simple 7-Agent Trading Workflow
Original simple system with 7 agents discussing stock analysis
"""

import asyncio
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.ui import Console

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
        termination_condition=TextMentionTermination("STOP"),
        max_turns=8
    )
    
    print(f"✅ Simple trading team created with 7 agents")
    return team

async def run_simple_analysis(stock_symbol="AAPL", question="Should I buy this stock?"):
    """Run simple 7-agent analysis"""
    print(f"📊 Starting Simple 7-Agent Analysis for {stock_symbol}")
    print("=" * 60)
    
    team = create_simple_trading_team()
    task = TextMessage(
        content=f"{question} Stock symbol: {stock_symbol}",
        source='user'
    )
    
    print(f"🤖 7 agents discussing: {question} ({stock_symbol})")
    result_stream = team.run_stream(task=task)
    await Console(result_stream)

async def main():
    """Main function for simple workflow"""
    await run_simple_analysis("AAPL", "Should I buy stocks of Apple?")

if __name__ == "__main__":
    asyncio.run(main())


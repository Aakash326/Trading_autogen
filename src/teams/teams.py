import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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
from src.model.model import get_model_client

def trading_team():
    organiser_agent=create_organiser_agent()
    risk_manager_agent=risk_manager()
    data_analyst_agent=data_analyst()
    quantitative_analyst_agent=quantitative_analysis()
    strategy_developer_agent=strategy_developer()
    compilence_officer_agent=compilence_officer()
    report_agent_instance=report_agent()
    team=RoundRobinGroupChat(
        participants=[
            organiser_agent,
            risk_manager_agent,
            data_analyst_agent,
            quantitative_analyst_agent,
            strategy_developer_agent,
            compilence_officer_agent,
            report_agent_instance
        ],
        termination_condition=TextMentionTermination("STOP"),
        max_turns=8
    )
    return team

team=trading_team()
async def main():
    task = TextMessage(content="Should i buy stocks of Apple", source='user')
    result_stream = team.run_stream(task=task)
    await Console(result_stream)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


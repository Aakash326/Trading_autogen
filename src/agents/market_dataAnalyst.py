from autogen_agentchat.agents import AssistantAgent
from src.model.model import get_model_client
import os
import requests
from dotenv import load_dotenv
from typing import Annotated

model_client=get_model_client()

def data_analyst():
    data_analyst_agent=AssistantAgent(
        name="DataAnalyst",
        model_client=model_client,
        system_message="""Fetch fundamental data only (P/E, earnings date, analyst targets). 
No analysis, just data collection.
Output format: Key metrics in bullet points only.""",
        )
    return data_analyst_agent

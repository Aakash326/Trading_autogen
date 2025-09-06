from autogen_agentchat.agents import AssistantAgent
from src.model.model import get_model_client
import os
import requests
from dotenv import load_dotenv
from typing import Annotated

model_client=get_model_client()

def compilence_officer():
    compilence_officer_agent=AssistantAgent(
        name="ComplianceOfficer",
        model_client=model_client,
        system_message="""Identify top 2 risks only.
Output format: 'Key risks: 1. [risk], 2. [risk]'
No compliance explanations.""",
        )
    return compilence_officer_agent
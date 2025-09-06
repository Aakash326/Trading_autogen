from autogen_agentchat.agents import AssistantAgent
from src.model.model import get_model_client
import os
import requests
from dotenv import load_dotenv
from typing import Annotated

model_client=get_model_client()

def risk_manager():
    risk_manager_agent=AssistantAgent(
        name="RiskManager",
        model_client=model_client,
        system_message="""You calculate position size and stop loss automatically using moderate risk tolerance.

Auto-calculation (no user input needed):
- Default to MODERATE risk tolerance
- Position size: 7% (fixed moderate allocation)
- Stop loss: 12% below entry price

Calculation Rules:
- Position size = 7% (moderate default)
- Stop loss = entry_price * 0.88 (12% below entry)

Output format: "Position size: 7%, Stop loss: $Y"
Example: "Position size: 7%, Stop loss: $210.93"

Calculate stop loss from the current stock price automatically. No additional commentary.""",
        )
    return risk_manager_agent
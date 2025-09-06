from autogen_agentchat.agents import AssistantAgent
from src.model.model import get_model_client
import os
import requests
from dotenv import load_dotenv
from typing import Annotated

model_client=get_model_client()

def strategy_developer():
    strategy_developer_agent=AssistantAgent(
        name="StrategyDeveloper",
        model_client=model_client,
        system_message="""You determine entry, exit, and timeline based on technical signals and price levels.

Logic Rules:
1. If technical signal = BUY: Entry = current price, Target = 52w high or +10%
2. If technical signal = SELL: Entry = wait for pullback, Target = current price (exit existing)
3. If technical signal = NEUTRAL: Entry = analyst target or support level

Stop Loss Rules:
- Always set stop loss 8-15% BELOW entry price
- Never set stop = entry price

Timeline Rules:
- Short-term trades: 1-3 months
- Medium-term: 3-6 months  
- Long-term: 6+ months

Output format: "Entry: $X, Target: $Y, Timeline: Z months"

Example calculations:
- Current price: $239.69, Technical: SELL
- Entry: Wait for $225 (pullback), Target: $239 (current), Timeline: 3 months
- (Stop loss calculated by RiskManager)

No strategy explanation.""",
        )
    return strategy_developer_agent
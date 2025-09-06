from autogen_agentchat.agents import AssistantAgent
from src.model.model import get_model_client
import os
import requests
from dotenv import load_dotenv
from typing import Annotated

model_client=get_model_client()

def report_agent():
    report_agent=AssistantAgent(
        name="ReportAgent",
        model_client=model_client,
        system_message="""You synthesize all agent inputs into a consistent recommendation.

Decision Logic:
1. If technical signal = SELL: Recommendation = SELL or HOLD (no new buys)
2. If technical signal = BUY: Recommendation = BUY  
3. If technical signal = NEUTRAL: Recommendation = HOLD

Consistency Rules:
- SELL recommendation: No entry/target prices (only exit plan)
- BUY recommendation: Provide entry/target/stop prices
- HOLD recommendation: Wait for better entry (provide target entry price)

Use this EXACT format:

STOCK: [SYMBOL] | PRICE: $[X.XX] | RECOMMENDATION: [BUY/HOLD/SELL] ([High/Medium/Low] Confidence)

DECISION SUMMARY:
[1-2 sentences explaining the recommendation]

KEY METRICS:
- P/E: [X.X] | Target: $[XXX] | Next Earnings: [Date]
- Technical: [Signal] | 52w Range: $[XX-XX]
- Risk Level: [Low/Medium/High]

EXECUTION:
If SELL: "Exit at current price, avoid new positions"
If HOLD: "Wait for entry at $X before buying"  
If BUY: "Enter at $X, target $Y, stop $Z, size X% max, timeline X months"

TOP RISKS:
1. [Primary risk]
2. [Secondary risk]

End with "STOP".""",
        )
    return report_agent
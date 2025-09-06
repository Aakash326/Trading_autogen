"""
AutoGen Trading System - Standalone Version
Runs without AutoGen dependencies for testing and development
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import sys
import os
import asyncio
import json
from typing import Dict, Any
import uvicorn
from datetime import datetime
import time
import random

# Initialize FastAPI app
app = FastAPI(title="AutoGen Trading System", version="1.0.0")

# Data models
class StockAnalysisRequest(BaseModel):
    symbol: str
    question: str = "Should I buy stocks of this company?"

class AnalysisResponse(BaseModel):
    symbol: str
    timestamp: str
    analysis: str
    status: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    try:
        with open("index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("""
        <html>
            <head><title>AutoGen Trading System</title></head>
            <body>
                <h1>AutoGen Trading System</h1>
                <p>Frontend file not found. Please ensure index.html exists.</p>
            </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

async def simulate_trading_analysis(symbol: str):
    """Simulate the trading analysis process"""
    
    # Simulate different agents responding
    agents = [
        ("OrganiserAgent", f"{symbol} current price: $239.69, volume: 54,870,397"),
        ("RiskManager", "Position size: 7%, Stop loss: $210.93"),
        ("DataAnalyst", f"• P/E: 36.2\n• Target: $250.00\n• Next Earnings: 2024-01-25\n• 52W Range: $164.08-$237.49"),
        ("QuantitativeAnalyst", "Technical signal: BUY - RSI 28 (oversold), MACD bullish cross"),
        ("StrategyDeveloper", "Entry: $240.00, Target: $260.00, Timeline: 3 months"),
        ("ComplianceOfficer", "Key risks: 1. Market volatility ahead of earnings, 2. Tech sector rotation concerns"),
        ("ReportAgent", f"""STOCK: {symbol} | PRICE: $239.69 | RECOMMENDATION: BUY (High Confidence)

DECISION SUMMARY:
Strong technical signals with RSI oversold and MACD bullish crossover support entry.

KEY METRICS:
- P/E: 36.2 | Target: $250.00 | Next Earnings: 2024-01-25
- Technical: BUY | 52w Range: $164.08-$237.49
- Risk Level: Medium

EXECUTION:
Enter at $240.00, target $260.00, stop $210.93, size 7% max, timeline 3 months

TOP RISKS:
1. Market volatility ahead of earnings
2. Tech sector rotation concerns

STOP""")
    ]
    
    for agent_name, response in agents:
        yield {
            "agent": agent_name,
            "content": response,
            "timestamp": datetime.now().isoformat()
        }
        # Add random delay to simulate processing time
        await asyncio.sleep(random.uniform(2, 5))

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_stock(request: StockAnalysisRequest):
    """Analyze a stock using simulated trading analysis"""
    try:
        # Simulate analysis
        analysis_parts = []
        async for result in simulate_trading_analysis(request.symbol.upper()):
            analysis_parts.append(f"[{result['agent']}] {result['content']}")
        
        full_analysis = "\n\n".join(analysis_parts)
        
        return AnalysisResponse(
            symbol=request.symbol.upper(),
            timestamp=datetime.now().isoformat(),
            analysis=full_analysis,
            status="completed"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/analyze-stream/{symbol}")
async def analyze_stock_stream(symbol: str):
    """Stream simulated analysis results"""
    async def generate_stream():
        try:
            async for result in simulate_trading_analysis(symbol.upper()):
                data = {
                    "type": "message",
                    "content": f"[{result['agent']}] {result['content']}",
                    "timestamp": result['timestamp']
                }
                yield f"data: {json.dumps(data)}\n\n"
            
            # Send completion signal
            completion_data = {
                "type": "complete",
                "message": "Analysis completed",
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(completion_data)}\n\n"
            
        except Exception as e:
            error_data = {
                "type": "error",
                "message": f"Analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate_stream(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

@app.get("/popular-stocks")
async def get_popular_stocks():
    """Get list of popular stocks for quick selection"""
    popular_stocks = [
        {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology"}, 
        {"symbol": "MSFT", "name": "Microsoft Corp.", "sector": "Technology"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Discretionary"},
        {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Discretionary"},
        {"symbol": "NVDA", "name": "NVIDIA Corp.", "sector": "Technology"},
        {"symbol": "META", "name": "Meta Platforms Inc.", "sector": "Technology"},
        {"symbol": "NFLX", "name": "Netflix Inc.", "sector": "Communication Services"},
        {"symbol": "DIS", "name": "Walt Disney Co.", "sector": "Communication Services"},
        {"symbol": "PYPL", "name": "PayPal Holdings Inc.", "sector": "Financial Services"}
    ]
    return {"stocks": popular_stocks}

@app.get("/market-status")
async def get_market_status():
    """Get current market status"""
    now = datetime.now()
    # Simple market hours check (9:30 AM - 4:00 PM ET, Mon-Fri)
    weekday = now.weekday()  # 0 = Monday, 6 = Sunday
    hour = now.hour
    
    if weekday < 5 and 9 <= hour < 16:  # Simplified market hours
        status = "open"
    elif weekday < 5 and (hour == 9 or hour == 16):
        status = "pre_post"  # Pre-market or after-hours
    else:
        status = "closed"
    
    return {
        "status": status,
        "timestamp": now.isoformat(),
        "message": f"Market is currently {status}"
    }

if __name__ == "__main__":
    print("🤖 AutoGen Trading System - Standalone Mode")
    print("=" * 50)
    print("ℹ️  Running in simulation mode (no AutoGen required)")
    print("🌐 Open your browser to: http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "application_standalone:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )
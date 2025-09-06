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
import socket

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import AutoGen components
try:
    from src.teams.teams import trading_team
    from autogen_agentchat.messages import TextMessage
    AUTOGEN_AVAILABLE = True
    print("✅ AutoGen components loaded successfully")
except ImportError as e:
    print(f"⚠️  AutoGen not available: {e}")
    print("🔄 Falling back to simulation mode...")
    AUTOGEN_AVAILABLE = False
    
    # Create dummy functions for fallback
    def trading_team():
        return None
    
    class TextMessage:
        def __init__(self, content, source):
            self.content = content
            self.source = source

# Initialize FastAPI app
app = FastAPI(title="AutoGen Trading System", version="1.0.0")

# Create static directory if it doesn't exist and mount static files
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Data models
class StockAnalysisRequest(BaseModel):
    symbol: str
    question: str = "Should I buy stocks of this company?"

class AnalysisResponse(BaseModel):
    symbol: str
    timestamp: str
    analysis: str
    status: str

# Global team instance (if AutoGen is available)
team = trading_team() if AUTOGEN_AVAILABLE else None

async def simulate_trading_analysis(symbol: str):
    """Simulate the trading analysis process when AutoGen is not available"""
    import time
    import random
    
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

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_stock(request: StockAnalysisRequest):
    """Analyze a stock using the AutoGen trading team or simulation"""
    try:
        if AUTOGEN_AVAILABLE and team:
            # Use real AutoGen system
            task_content = f"{request.question} for {request.symbol.upper()}"
            task = TextMessage(content=task_content, source='user')
            
            # Run the analysis
            result_stream = team.run_stream(task=task)
            
            # Collect results from the stream
            analysis_parts = []
            async for message in result_stream:
                if hasattr(message, 'content'):
                    analysis_parts.append(str(message.content))
                elif hasattr(message, 'messages'):
                    for msg in message.messages:
                        if hasattr(msg, 'content'):
                            analysis_parts.append(str(msg.content))
            
            full_analysis = "\n\n".join(analysis_parts) if analysis_parts else "Analysis completed"
        else:
            # Use simulation mode
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
    """Stream real-time analysis results"""
    async def generate_stream():
        try:
            if AUTOGEN_AVAILABLE and team:
                # Use real AutoGen system
                task_content = f"Should I buy stocks of {symbol.upper()}?"
                task = TextMessage(content=task_content, source='user')
                
                result_stream = team.run_stream(task=task)
                
                async for message in result_stream:
                    if hasattr(message, 'content'):
                        data = {
                            "type": "message",
                            "content": str(message.content),
                            "timestamp": datetime.now().isoformat()
                        }
                        yield f"data: {json.dumps(data)}\n\n"
                    elif hasattr(message, 'messages'):
                        for msg in message.messages:
                            if hasattr(msg, 'content'):
                                data = {
                                    "type": "message", 
                                    "content": str(msg.content),
                                    "timestamp": datetime.now().isoformat()
                                }
                                yield f"data: {json.dumps(data)}\n\n"
            else:
                # Use simulation mode
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
    # This is a simplified version - in production, you'd use a proper market data API
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

def find_free_port(start_port=8000):
    """Find a free port starting from start_port"""
    port = start_port
    while port < start_port + 100:  # Try 100 ports
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            port += 1
    return None

if __name__ == "__main__":
    # Print startup message
    print("🤖 AutoGen Trading System")
    print("=" * 50)
    
    if AUTOGEN_AVAILABLE:
        print("✅ Running with FULL AutoGen multi-agent system")
        print("🧠 AI agents will provide real analysis")
    else:
        print("⚠️  Running in SIMULATION mode")
        print("🔄 Using simulated agent responses (AutoGen not available)")
    
    # Find a free port
    port = find_free_port(8000)
    if port is None:
        print("❌ Could not find a free port between 8000-8099")
        sys.exit(1)
    
    print(f"🌐 Starting server at: http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Run the FastAPI server
    uvicorn.run(
        "application:app",
        host="0.0.0.0", 
        port=port,
        reload=True,
        log_level="info"
    )
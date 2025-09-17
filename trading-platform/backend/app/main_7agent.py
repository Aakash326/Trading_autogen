"""
Real AI 7-Agent Trading Analysis Backend
FastAPI backend using the 7-agent AutoGen workflow for stock analysis
"""

import asyncio
import json
import logging
import uuid
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Import real AI agent workflows
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)
print(f"Added to path: {project_root}")

try:
    from src.workflows.simple_7agent_workflow import create_simple_trading_team, run_simple_analysis
    from autogen_agentchat.messages import TextMessage
    AI_AGENTS_AVAILABLE = True
    print("✅ Real 7-agent AI system successfully imported!")
except Exception as e:
    AI_AGENTS_AVAILABLE = False
    TextMessage = None
    print(f"❌ Failed to import 7-agent AI system: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state management
analysis_sessions: Dict[str, Dict[str, Any]] = {}
websocket_connections: Dict[str, WebSocket] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    if AI_AGENTS_AVAILABLE:
        logger.info("🚀 Real AI 7-Agent Trading Analysis Platform starting up...")
    else:
        logger.error("❌ AI Agent workflows not available - check imports")
        raise Exception("AI agents are required for this service")
    yield
    logger.info("🔄 7-Agent Trading Analysis Platform shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="7-Agent Trading Analysis API",
    description="Real AI trading analysis with 7-agent AutoGen workflows",
    version="3.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Stock(BaseModel):
    symbol: str
    name: str
    price: Optional[float] = None
    change: Optional[float] = None
    changePercent: Optional[float] = None
    marketCap: Optional[str] = None
    sector: Optional[str] = None

class StockQuote(BaseModel):
    symbol: str
    price: float
    change: float
    changePercent: float
    volume: int
    marketCap: str
    pe: Optional[float] = None
    dayRange: str
    weekRange52: str

class AnalysisType(BaseModel):
    id: str
    name: str
    description: str
    icon: str

class AnalysisRequest(BaseModel):
    stock_symbol: str
    analysis_type: str
    workflow_type: str

class AnalysisPhase(BaseModel):
    phase: str
    agent: str
    status: str
    content: Optional[str] = None
    timestamp: Optional[str] = None

class AnalysisResult(BaseModel):
    id: str
    stock_symbol: str
    analysis_type: str
    workflow_type: str
    status: str
    phases: List[AnalysisPhase]
    summary: Optional[str] = None
    recommendation: Optional[str] = None
    confidence_score: Optional[int] = None
    created_at: str
    completed_at: Optional[str] = None

# Static data
POPULAR_STOCKS = [
    {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
    {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
    {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology"},
    {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "E-commerce"},
    {"symbol": "TSLA", "name": "Tesla, Inc.", "sector": "Automotive"},
    {"symbol": "META", "name": "Meta Platforms Inc.", "sector": "Social Media"},
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology"},
    {"symbol": "NFLX", "name": "Netflix Inc.", "sector": "Entertainment"},
    {"symbol": "UBER", "name": "Uber Technologies Inc.", "sector": "Transportation"},
    {"symbol": "SPOT", "name": "Spotify Technology S.A.", "sector": "Entertainment"},
    {"symbol": "COIN", "name": "Coinbase Global Inc.", "sector": "Financial Services"},
    {"symbol": "SHOP", "name": "Shopify Inc.", "sector": "E-commerce"}
]

ANALYSIS_TYPES = [
    {"id": "buying", "name": "💰 Buying Decision", "description": "Should I buy this stock now? Complete investment analysis.", "icon": "💰"},
    {"id": "selling", "name": "💸 Selling Decision", "description": "Should I sell this stock now? Exit strategy analysis.", "icon": "💸"},
    {"id": "health", "name": "🏥 General Health Check", "description": "Overall company and stock health assessment.", "icon": "🏥"},
    {"id": "5day", "name": "📈 Next 5-Day Outlook", "description": "Short-term price movement and catalysts for next 5 days.", "icon": "📈"},
    {"id": "growth", "name": "🚀 Growth Potential Analysis", "description": "Long-term growth prospects and investment potential.", "icon": "🚀"},
    {"id": "risk", "name": "⚠️ Risk Assessment", "description": "Comprehensive risk analysis and downside protection.", "icon": "⚠️"},
    {"id": "sector", "name": "🏢 Sector Comparison", "description": "How does this company compare to its sector peers?", "icon": "🏢"},
    {"id": "options", "name": "📊 Options Strategy", "description": "Options trading opportunities and strategies analysis.", "icon": "📊"},
    {"id": "esg", "name": "🌱 ESG & Sustainability", "description": "Environmental, Social, and Governance analysis.", "icon": "🌱"},
    {"id": "earnings", "name": "📅 Earnings Forecast", "description": "Upcoming earnings analysis and price impact prediction.", "icon": "📅"}
]

def generate_analysis_id() -> str:
    """Generate unique analysis ID"""
    return str(uuid.uuid4())

async def send_websocket_update(analysis_id: str, message_type: str, data: Dict[str, Any]):
    """Send update via WebSocket if connected"""
    if analysis_id in websocket_connections:
        message = {
            "type": message_type,
            "analysis_id": analysis_id,
            "data": data
        }
        try:
            await websocket_connections[analysis_id].send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")
            websocket_connections.pop(analysis_id, None)

# API Routes
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0-7agent-ai",
        "service": "7-agent-trading-analysis",
        "ai_agents_available": AI_AGENTS_AVAILABLE,
        "agents_count": 7,
        "workflow_type": "7-agent"
    }

@app.get("/api/stocks")
async def get_stocks():
    """Get list of popular stocks"""
    return POPULAR_STOCKS

@app.get("/api/stocks/{symbol}/quote")
async def get_stock_quote(symbol: str):
    """Get real-time stock quote (mock implementation)"""
    # In production, this would fetch from a real data provider
    import random
    base_price = {"AAPL": 175, "MSFT": 330, "GOOGL": 140, "TSLA": 240}.get(symbol, 100)
    change = random.uniform(-5, 5)
    price = base_price + change
    
    return {
        "symbol": symbol,
        "price": round(price, 2),
        "change": round(change, 2),
        "changePercent": round((change / base_price) * 100, 2),
        "volume": random.randint(10000000, 50000000),
        "marketCap": f"${random.randint(100, 3000)}B",
        "pe": round(random.uniform(15, 35), 1),
        "dayRange": f"${round(price-5, 2)} - ${round(price+5, 2)}",
        "weekRange52": f"${round(price-50, 2)} - ${round(price+50, 2)}"
    }

@app.get("/api/stocks/search")
async def search_stocks(q: str):
    """Search stocks by query"""
    query = q.lower()
    results = [
        stock for stock in POPULAR_STOCKS
        if query in stock["symbol"].lower() or query in stock["name"].lower()
    ]
    return results

@app.get("/api/analysis-types")
async def get_analysis_types():
    """Get available analysis types"""
    return ANALYSIS_TYPES

@app.post("/api/analysis/start")
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start stock analysis"""
    if not AI_AGENTS_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI agents not available")
    
    analysis_id = generate_analysis_id()
    
    # Initialize analysis session
    analysis_sessions[analysis_id] = {
        "id": analysis_id,
        "stock_symbol": request.stock_symbol,
        "analysis_type": request.analysis_type,
        "workflow_type": request.workflow_type,
        "status": "pending",
        "phases": [],
        "created_at": datetime.now().isoformat()
    }
    
    # Start analysis in background
    background_tasks.add_task(run_real_7agent_analysis, analysis_id, request)
    
    return {"analysis_id": analysis_id}

@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get analysis status and results"""
    if analysis_id not in analysis_sessions:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_sessions[analysis_id]

@app.get("/api/analysis/history")
async def get_analysis_history():
    """Get analysis history"""
    return list(analysis_sessions.values())

@app.post("/api/analysis/{analysis_id}/cancel")
async def cancel_analysis(analysis_id: str):
    """Cancel analysis"""
    if analysis_id not in analysis_sessions:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    analysis_sessions[analysis_id]["status"] = "cancelled"
    return {"success": True}

async def run_real_7agent_analysis(analysis_id: str, request: AnalysisRequest):
    """Run real AI analysis workflow with 7 agents"""
    try:
        logger.info(f"Starting REAL 7-Agent AI analysis for {request.stock_symbol} - {request.analysis_type}")
        
        # Update status to running
        analysis_sessions[analysis_id]["status"] = "running"
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Initialization",
            "agent": "System",
            "status": "running",
            "content": f"Starting real 7-agent AI analysis for {request.stock_symbol}"
        })
        
        # Create analysis question based on type
        question_map = {
            "buying": f"Should I buy stocks of {request.stock_symbol}?",
            "selling": f"Should I sell my {request.stock_symbol} stocks now?", 
            "health": f"What is the overall health of {request.stock_symbol}?",
            "5day": f"What is the 5-day outlook for {request.stock_symbol}?",
            "growth": f"What is the long-term growth potential of {request.stock_symbol}?",
            "risk": f"What are the risks of investing in {request.stock_symbol}?",
            "sector": f"How does {request.stock_symbol} compare to its sector?",
            "options": f"What options strategies work for {request.stock_symbol}?",
            "esg": f"What is the ESG profile of {request.stock_symbol}?",
            "earnings": f"How will upcoming earnings affect {request.stock_symbol}?"
        }
        
        question = question_map.get(request.analysis_type, f"Should I invest in {request.stock_symbol}?")
        
        # Phase 1: Initialize 7-Agent AI Team
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Creating 7-Agent AI Team",
            "agent": "System",
            "status": "running",
            "content": "Initializing 7 specialized AI agents..."
        })
        
        # Create the real AI trading team
        team = create_simple_trading_team()
        
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Creating 7-Agent AI Team",
            "agent": "System", 
            "status": "completed",
            "content": "✅ 7-Agent AI team ready: OrganiserAgent, RiskManager, DataAnalyst, QuantitativeAnalyst, StrategyDeveloper, ComplianceOfficer, ReportAgent"
        })
        
        # Phase 2: Start AI Agent Collaboration
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "AI Agent Collaboration",
            "agent": "7-Agent Team",
            "status": "running", 
            "content": f"7 AI agents are analyzing {request.stock_symbol}. This may take 2-5 minutes..."
        })
        
        # Check if analysis was cancelled
        if analysis_sessions[analysis_id]["status"] == "cancelled":
            logger.info(f"Analysis {analysis_id} was cancelled")
            return
        
        # Execute the real AI analysis
        logger.info(f"🤖 Running REAL 7-agent AI analysis: {question}")
        
        # Create the task message
        task = TextMessage(
            content=f"{question} Stock symbol: {request.stock_symbol}",
            source='user'
        )
        
        # Use the streaming approach for real-time updates
        result_stream = team.run_stream(task=task)
        all_messages = []
        
        # Process the stream with timeout protection
        stream_timeout = 2400  # 40 minutes max for 7 agents
        start_time = asyncio.get_event_loop().time()
        
        try:
            async for message in result_stream:
                # Check timeout
                if asyncio.get_event_loop().time() - start_time > stream_timeout:
                    logger.warning("⏰ AI analysis timeout reached (40 minutes)")
                    break
                
                # Check for cancellation
                if analysis_sessions[analysis_id]["status"] == "cancelled":
                    logger.info(f"Analysis {analysis_id} was cancelled during processing")
                    return
                
                # Process different message types
                if hasattr(message, 'content') and message.content:
                    content_str = message.content if isinstance(message.content, str) else str(message.content)
                    source = getattr(message, 'source', 'Unknown')
                    
                    all_messages.append({
                        'source': source,
                        'content': content_str,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Send real-time updates of agent responses
                    await send_websocket_update(analysis_id, "agent_response", {
                        "agent": source,
                        "content": content_str[:200] + "..." if len(content_str) > 200 else content_str,
                        "full_content": content_str
                    })
                    
                    logger.info(f"📤 Agent {source}: {content_str[:100]}...")
                    
        except Exception as stream_error:
            logger.error(f"Error processing AI stream: {stream_error}")
            logger.error(traceback.format_exc())
        
        logger.info(f"✅ 7-Agent AI analysis stream completed with {len(all_messages)} agent responses")
        
        # Check if analysis was cancelled during AI processing
        if analysis_sessions[analysis_id]["status"] == "cancelled":
            logger.info(f"Analysis {analysis_id} was cancelled during AI processing")
            return
        
        # Phase 3: Extract Results from AI Analysis
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Processing AI Results",
            "agent": "System",
            "status": "running",
            "content": "Extracting insights from 7-agent AI discussions..."
        })
        
        # Process the real AI results
        if all_messages:
            # Get the final report (usually from ReportAgent)
            final_message = None
            report_messages = [msg for msg in all_messages if 'report' in msg.get('source', '').lower()]
            
            if report_messages:
                final_message = report_messages[-1]['content']
            else:
                # Fallback to last message
                final_message = all_messages[-1]['content']
            
            # Extract recommendation from AI response
            recommendation = "HOLD"  # Default
            confidence = 75  # Default
            
            content_upper = final_message.upper()
            
            # Look for clear recommendation signals
            if any(word in content_upper for word in ["STRONG BUY", "BUY RECOMMENDATION", "RECOMMEND BUYING"]):
                recommendation = "STRONG BUY"
                confidence = 85
            elif "BUY" in content_upper and "SELL" not in content_upper:
                recommendation = "BUY"
                confidence = 80
            elif any(word in content_upper for word in ["STRONG SELL", "SELL RECOMMENDATION", "RECOMMEND SELLING"]):
                recommendation = "STRONG SELL"
                confidence = 85
            elif "SELL" in content_upper and "BUY" not in content_upper:
                recommendation = "SELL"
                confidence = 80
            elif any(word in content_upper for word in ["HOLD", "WAIT", "NEUTRAL"]):
                recommendation = "HOLD"
                confidence = 75
            
            # Try to extract confidence score from AI response
            import re
            confidence_patterns = [
                r'confidence[:\s]+(\d+)%?',
                r'(\d+)%\s*confidence',
                r'conviction[:\s]+(\d+)',
                r'(\d+)/10'
            ]
            
            for pattern in confidence_patterns:
                confidence_match = re.search(pattern, final_message.lower())
                if confidence_match:
                    extracted_confidence = int(confidence_match.group(1))
                    if pattern.endswith('/10'):
                        confidence = min(95, extracted_confidence * 10)
                    else:
                        confidence = min(95, extracted_confidence)
                    break
            
            # Create comprehensive summary
            summary = f"✅ Real 7-Agent AI Analysis Complete for {request.stock_symbol}\n\n"
            summary += f"🎯 Recommendation: {recommendation} (Confidence: {confidence}%)\n\n"
            summary += f"📋 Analysis Type: {request.analysis_type.title()}\n"
            summary += f"🤖 AI Agents Consulted: 7 specialized agents\n"
            summary += f"📊 Question Analyzed: {question}\n\n"
            summary += "🔍 Key Insights from 7-Agent AI Analysis:\n"
            summary += final_message[:800] + ("..." if len(final_message) > 800 else "")
            
        else:
            # Should not happen with real AI
            summary = f"7-Agent AI analysis completed for {request.stock_symbol}, but no detailed response was generated."
            recommendation = "HOLD"
            confidence = 50
        
        # Phase 4: Complete Analysis
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Analysis Complete",
            "agent": "System",
            "status": "completed",
            "content": f"✅ Real 7-agent AI analysis finished. Recommendation: {recommendation}"
        })
        
        # Update final results with real AI data
        analysis_sessions[analysis_id].update({
            "status": "completed",
            "summary": summary,
            "recommendation": recommendation,
            "confidence_score": confidence,
            "completed_at": datetime.now().isoformat(),
            "ai_messages": all_messages[:20]  # Store last 20 AI responses
        })
        
        # Send completion message
        await send_websocket_update(analysis_id, "analysis_complete", analysis_sessions[analysis_id])
        
        logger.info(f"✅ REAL 7-Agent AI analysis completed for {analysis_id} - Recommendation: {recommendation} ({confidence}% confidence)")
        
    except Exception as e:
        logger.error(f"❌ Real 7-Agent AI analysis failed for {analysis_id}: {e}")
        logger.error(traceback.format_exc())
        analysis_sessions[analysis_id].update({
            "status": "error",
            "error": f"7-Agent AI Analysis Error: {str(e)}",
            "completed_at": datetime.now().isoformat()
        })
        await send_websocket_update(analysis_id, "error", {
            "message": f"7-Agent AI analysis failed: {str(e)}"
        })

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    client_id = str(uuid.uuid4())
    
    try:
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connected",
            "client_id": client_id,
            "message": "Connected to real 7-agent AI trading analysis platform"
        }))
        
        # Keep connection alive
        while True:
            try:
                message = await websocket.receive_text()
                data = json.loads(message)
                
                if data.get("type") == "subscribe" and "analysis_id" in data:
                    analysis_id = data["analysis_id"]
                    websocket_connections[analysis_id] = websocket
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "analysis_id": analysis_id
                    }))
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
                
    finally:
        # Clean up connections
        for analysis_id, ws in list(websocket_connections.items()):
            if ws == websocket:
                del websocket_connections[analysis_id]

if __name__ == "__main__":
    uvicorn.run(
        "main_7agent:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

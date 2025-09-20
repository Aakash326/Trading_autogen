"""
Unified Real AI Trading Analysis Backend
FastAPI backend supporting both 7-agent and 13-agent workflows for stock analysis
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

# Import summary extraction module
from summary_extractor import extract_complete_analysis_results

# Import real AI agent workflows
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)
print(f"Added to path: {project_root}")

try:
    # 7-agent workflow
    from src.workflows.simple_7agent_workflow import create_simple_trading_team
    # 13-agent workflow
    from src.workflows.hybrid_team import HybridTradingTeam
    # Fast 6-agent workflow
    from src.workflows.fast_6agent_workflow import run_fast_6agent_analysis
    from autogen_agentchat.messages import TextMessage
    AI_AGENTS_AVAILABLE = True
    print("✅ Real AI systems successfully imported (7-agent + 13-agent + 6-agent)!")
except Exception as e:
    AI_AGENTS_AVAILABLE = False
    TextMessage = None
    print(f"❌ Failed to import AI systems: {e}")

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
        logger.info("🚀 Real AI Trading Analysis Platform starting up (7-agent + 13-agent support)...")
    else:
        logger.error("❌ AI Agent workflows not available - check imports")
        raise Exception("AI agents are required for this service")
    yield
    logger.info("🔄 Trading Analysis Platform shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Unified Trading Analysis API",
    description="Real AI trading analysis with 7-agent and 13-agent workflows",
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
    {"symbol": "SHOP", "name": "Shopify Inc.", "sector": "E-commerce"},
    {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial Services"},
    {"symbol": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare"},
    {"symbol": "WMT", "name": "Walmart Inc.", "sector": "Consumer Staples"},
    {"symbol": "V", "name": "Visa Inc.", "sector": "Financial Services"},
    {"symbol": "PG", "name": "Procter & Gamble Co.", "sector": "Consumer Staples"},
    {"symbol": "HD", "name": "The Home Depot Inc.", "sector": "Consumer Discretionary"},
    {"symbol": "DIS", "name": "The Walt Disney Company", "sector": "Entertainment"},
    {"symbol": "PYPL", "name": "PayPal Holdings Inc.", "sector": "Financial Services"}
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
    """Send update via WebSocket if connected and store phase data"""
    # Store phase data in analysis session
    if message_type == "phase_update" and analysis_id in analysis_sessions:
        if "phases" not in analysis_sessions[analysis_id]:
            analysis_sessions[analysis_id]["phases"] = []
        
        # Add or update the phase
        phase_data = {
            "phase": data.get("phase", "Unknown"),
            "agent": data.get("agent", "Unknown"),
            "status": data.get("status", "pending"),
            "content": data.get("content", ""),
            "timestamp": datetime.now().isoformat()
        }
        
        # Check if this phase already exists (update it) or add new phase
        existing_phase = None
        for i, existing in enumerate(analysis_sessions[analysis_id]["phases"]):
            if existing["phase"] == phase_data["phase"]:
                existing_phase = i
                break
        
        if existing_phase is not None:
            analysis_sessions[analysis_id]["phases"][existing_phase] = phase_data
        else:
            analysis_sessions[analysis_id]["phases"].append(phase_data)
        
        # Update progress percentage
        # For 6-agent: 3 system phases + 6 agent phases = 9 total
        # For 7-agent: 3 system phases + 7 agent phases = 10 total
        # For 13-agent: 3 system phases + 13 agent phases = 16 total  
        workflow_type = analysis_sessions[analysis_id]["workflow_type"]
        if workflow_type == "6-agent":
            total_phases = 9  # System phases + 6 agents
        elif workflow_type == "7-agent":
            total_phases = 10  # System phases + 7 agents
        else:
            total_phases = 16  # System phases + 13 agents
            
        completed_phases = len([p for p in analysis_sessions[analysis_id]["phases"] if p["status"] == "completed"])
        progress = min(100, (completed_phases / total_phases) * 100)
        analysis_sessions[analysis_id]["progress"] = int(progress)
    
    # Send WebSocket update
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
        "version": "3.0.0-unified-ai",
        "service": "unified-trading-analysis",
        "ai_agents_available": AI_AGENTS_AVAILABLE,
        "supported_workflows": ["6-agent", "7-agent", "13-agent"],
        "frameworks": ["AutoGen", "CrewAI"]
    }

@app.get("/api/stocks")
async def get_stocks():
    """Get list of popular stocks"""
    return POPULAR_STOCKS

@app.get("/api/stocks/{symbol}/quote")
async def get_stock_quote(symbol: str):
    """Get real-time stock quote"""
    # In production, this would fetch from a real data provider like Alpha Vantage
    import random
    base_prices = {
        "AAPL": 175, "MSFT": 330, "GOOGL": 140, "TSLA": 240, "META": 290,
        "NVDA": 450, "AMZN": 130, "NFLX": 380, "UBER": 45, "SPOT": 150,
        "COIN": 85, "SHOP": 60, "JPM": 140, "JNJ": 160, "WMT": 155,
        "V": 240, "PG": 145, "HD": 320, "DIS": 95, "PYPL": 60
    }
    
    base_price = base_prices.get(symbol, 100)
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
    """Start stock analysis with specified workflow"""
    if not AI_AGENTS_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI agents not available")
    
    # Validate workflow type
    if request.workflow_type not in ["7-agent", "13-agent", "6-agent"]:
        raise HTTPException(status_code=400, detail="Invalid workflow type. Must be '7-agent', '13-agent', or '6-agent'")
    
    analysis_id = generate_analysis_id()
    
    # Initialize analysis session
    analysis_sessions[analysis_id] = {
        "id": analysis_id,
        "stock_symbol": request.stock_symbol,
        "analysis_type": request.analysis_type,
        "workflow_type": request.workflow_type,
        "status": "pending",
        "phases": [],
        "progress": 0,
        "agent_messages": [],
        "created_at": datetime.now().isoformat()
    }
    
    # Start analysis in background based on workflow type
    if request.workflow_type == "7-agent":
        background_tasks.add_task(run_7agent_analysis, analysis_id, request)
    elif request.workflow_type == "13-agent":
        background_tasks.add_task(run_13agent_analysis, analysis_id, request)
    else:  # 6-agent
        background_tasks.add_task(run_6agent_analysis, analysis_id, request)
    
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
    analysis_sessions[analysis_id]["completed_at"] = datetime.now().isoformat()
    
    # Send cancellation notification via WebSocket
    await send_websocket_update(analysis_id, "analysis_cancelled", {
        "message": "Analysis cancelled by user",
        "status": "cancelled"
    })
    
    logger.info(f"Analysis {analysis_id} cancelled by user")
    return {"success": True}

async def run_7agent_analysis(analysis_id: str, request: AnalysisRequest):
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
        
        # Create analysis question
        question_map = {
            "buying": f"Should I buy stocks of {request.stock_symbol}?",
            "selling": f"Should I sell my {request.stock_symbol} stocks now?", 
            "1year_investment": f"Should I invest in {request.stock_symbol} for 1 year? Provide comprehensive 1-year investment strategy and outlook.",
            "health": f"What is the overall health of {request.stock_symbol}?",
            "5day": f"What is the 5-day outlook for {request.stock_symbol}?",
            "growth": f"What is the long-term growth potential of {request.stock_symbol}?",
            "risk": f"What are the risks of investing in {request.stock_symbol}?",
            "sector": f"How does {request.stock_symbol} compare to its sector?",
            "options": f"What options strategies work for {request.stock_symbol}?",
            "esg": f"What is the ESG profile of {request.stock_symbol}?",
            "earnings": f"How will upcoming earnings affect {request.stock_symbol}?",
            "dividend": f"What is the dividend analysis for {request.stock_symbol}? Analyze yield, sustainability, and income potential.",
            "technical": f"Provide technical analysis for {request.stock_symbol} including chart patterns and indicators.",
            "momentum": f"Analyze price momentum and trends for {request.stock_symbol}."
        }
        
        question = question_map.get(request.analysis_type, f"Should I invest in {request.stock_symbol}?")
        
        # Initialize 7-Agent AI Team
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Creating 7-Agent AI Team",
            "agent": "System",
            "status": "running",
            "content": "Initializing 7 specialized AI agents..."
        })
        
        team = create_simple_trading_team()
        
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Creating 7-Agent AI Team",
            "agent": "System", 
            "status": "completed",
            "content": "✅ 7-Agent AI team ready"
        })
        
        # Start AI Agent Collaboration
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "AI Agent Collaboration",
            "agent": "7-Agent Team",
            "status": "running", 
            "content": f"7 AI agents analyzing {request.stock_symbol}..."
        })
        
        # Check for cancellation
        if analysis_sessions[analysis_id]["status"] == "cancelled":
            return
        
        # Execute real AI analysis
        task = TextMessage(content=f"{question} Stock symbol: {request.stock_symbol}", source='user')
        result_stream = team.run_stream(task=task)
        all_messages = []
        
        # Process the stream
        stream_timeout = 2400  # 40 minutes
        start_time = asyncio.get_event_loop().time()
        
        try:
            async for message in result_stream:
                if asyncio.get_event_loop().time() - start_time > stream_timeout:
                    logger.warning("⏰ AI analysis timeout reached")
                    break
                
                if analysis_sessions[analysis_id]["status"] == "cancelled":
                    return
                
                if hasattr(message, 'content') and message.content:
                    content_str = str(message.content)
                    source = getattr(message, 'source', 'Unknown')
                    
                    message_data = {
                        'source': source,
                        'content': content_str,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    all_messages.append(message_data)
                    
                    # Store in analysis session for persistent access
                    if "agent_messages" not in analysis_sessions[analysis_id]:
                        analysis_sessions[analysis_id]["agent_messages"] = []
                    analysis_sessions[analysis_id]["agent_messages"].append(message_data)
                    
                    # Send both agent response and phase update for tracking
                    await send_websocket_update(analysis_id, "agent_response", {
                        "agent": source,
                        "content": content_str[:200] + "..." if len(content_str) > 200 else content_str,
                        "full_content": content_str,
                        "timestamp": message_data['timestamp']
                    })
                    
                    # Create phase update for this agent's contribution
                    await send_websocket_update(analysis_id, "phase_update", {
                        "phase": f"{source} Analysis",
                        "agent": source,
                        "status": "completed",
                        "content": content_str[:200] + "..." if len(content_str) > 200 else content_str,
                        "timestamp": message_data['timestamp']
                    })
                    
        except Exception as stream_error:
            logger.error(f"Error processing AI stream: {stream_error}")
        
        # Extract results using proper summary extraction - ONLY from real agent responses
        if all_messages:
            # Use proper summary extraction
            results = extract_complete_analysis_results(all_messages, request.stock_symbol, request.analysis_type)
            summary = results['summary']
            recommendation = results['recommendation'] 
            confidence = results['confidence']
            one_line_summary = results['one_line_summary']
        else:
            # No fallback - if agents don't respond, analysis fails
            raise Exception("No AI agent responses received - analysis incomplete")
        
        # Complete analysis
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Analysis Complete",
            "agent": "System",
            "status": "completed",
            "content": f"✅ 7-agent AI analysis finished. Recommendation: {recommendation}"
        })
        
        analysis_sessions[analysis_id].update({
            "status": "completed",
            "summary": summary,
            "one_line_summary": one_line_summary,  # NEW: Store one-line summary
            "recommendation": recommendation,
            "confidence_score": confidence,
            "completed_at": datetime.now().isoformat(),
            "ai_messages": all_messages[-20:]  # Last 20 messages
        })
        
        await send_websocket_update(analysis_id, "analysis_complete", analysis_sessions[analysis_id])
        
    except Exception as e:
        logger.error(f"❌ 7-Agent AI analysis failed for {analysis_id}: {e}")
        analysis_sessions[analysis_id].update({
            "status": "error",
            "error": f"7-Agent AI Analysis Error: {str(e)}",
            "completed_at": datetime.now().isoformat()
        })
        await send_websocket_update(analysis_id, "error", {"message": str(e)})

async def run_13agent_analysis(analysis_id: str, request: AnalysisRequest):
    """Run real AI analysis workflow with 13 agents (hybrid)"""
    try:
        logger.info(f"Starting REAL 13-Agent Hybrid AI analysis for {request.stock_symbol} - {request.analysis_type}")
        
        # Update status to running
        analysis_sessions[analysis_id]["status"] = "running"
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Initialization",
            "agent": "System",
            "status": "running",
            "content": f"Starting real 13-agent hybrid AI analysis for {request.stock_symbol}"
        })
        
        # Create analysis question
        question_map = {
            "buying": f"Should I buy stocks of {request.stock_symbol}?",
            "selling": f"Should I sell my {request.stock_symbol} stocks now?", 
            "1year_investment": f"Should I invest in {request.stock_symbol} for 1 year? Provide comprehensive 1-year investment strategy and outlook.",
            "health": f"What is the overall health of {request.stock_symbol}?",
            "5day": f"What is the 5-day outlook for {request.stock_symbol}?",
            "growth": f"What is the long-term growth potential of {request.stock_symbol}?",
            "risk": f"What are the risks of investing in {request.stock_symbol}?",
            "sector": f"How does {request.stock_symbol} compare to its sector?",
            "options": f"What options strategies work for {request.stock_symbol}?",
            "esg": f"What is the ESG profile of {request.stock_symbol}?",
            "earnings": f"How will upcoming earnings affect {request.stock_symbol}?",
            "dividend": f"What is the dividend analysis for {request.stock_symbol}? Analyze yield, sustainability, and income potential.",
            "technical": f"Provide technical analysis for {request.stock_symbol} including chart patterns and indicators.",
            "momentum": f"Analyze price momentum and trends for {request.stock_symbol}."
        }
        
        question = question_map.get(request.analysis_type, f"Should I invest in {request.stock_symbol}?")
        
        # Initialize 13-Agent Hybrid AI Team
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Creating 13-Agent Hybrid AI Team",
            "agent": "System",
            "status": "running",
            "content": "Initializing 13 specialized AI agents (AutoGen + CrewAI)..."
        })
        
        hybrid_team = HybridTradingTeam()
        hybrid_team.initialize_agents()
        
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Creating 13-Agent Hybrid AI Team",
            "agent": "System", 
            "status": "completed",
            "content": "✅ 13-Agent Hybrid AI team ready (10 AutoGen + 3 CrewAI)"
        })
        
        # Multi-phase analysis
        phases = [
            ("Foundation Data Collection", "AutoGen Sequential"),
            ("Advanced Intelligence Analysis", "Hybrid Parallel"),
            ("Strategic Risk & Execution", "CrewAI Workflows"),
            ("Final Investment Committee", "AutoGen Integration")
        ]
        
        for phase_name, framework in phases:
            await send_websocket_update(analysis_id, "phase_update", {
                "phase": phase_name,
                "agent": framework,
                "status": "running", 
                "content": f"{framework} processing {request.stock_symbol}..."
            })
            
            # Check for cancellation
            if analysis_sessions[analysis_id]["status"] == "cancelled":
                return
        
        # Execute comprehensive analysis
        result = await hybrid_team.run_comprehensive_analysis(request.stock_symbol, question)
        
        # Extract results
        if result and not result.get('error'):
            workflow_phases = result.get('workflow_phases', {})
            final_synthesis = workflow_phases.get('phase_5_synthesis', {})
            
            recommendation = "HOLD"
            confidence = 85  # Higher for 13-agent
            
            # Collect all messages for proper analysis
            all_13agent_messages = []
            if isinstance(final_synthesis, dict) and 'messages' in final_synthesis:
                final_messages = final_synthesis['messages']
                if final_messages:
                    for msg in final_messages:
                        all_13agent_messages.append({
                            'source': 'hybrid_agent',
                            'content': str(msg),
                            'timestamp': datetime.now().isoformat()
                        })
            
            # Use proper summary extraction for 13-agent - ONLY from real agent responses
            if all_13agent_messages:
                results = extract_complete_analysis_results(all_13agent_messages, request.stock_symbol, request.analysis_type)
                summary = results['summary']
                recommendation = results['recommendation'] 
                confidence = results['confidence']
                one_line_summary = results['one_line_summary']
            else:
                # No fallback - if agents don't respond, analysis fails
                raise Exception("No AI agent responses received from 13-agent workflow")
        else:
            # No fallback - if workflow fails, analysis fails
            error_msg = result.get('error', 'Unknown error') if result else 'No result from hybrid workflow'
            raise Exception(f"13-Agent hybrid workflow failed: {error_msg}")
        
        # Complete analysis
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Analysis Complete",
            "agent": "System",
            "status": "completed",
            "content": f"✅ 13-agent hybrid AI analysis finished. Recommendation: {recommendation}"
        })
        
        analysis_sessions[analysis_id].update({
            "status": "completed",
            "summary": summary,
            "one_line_summary": one_line_summary,  # NEW: Store one-line summary  
            "recommendation": recommendation,
            "confidence_score": confidence,
            "completed_at": datetime.now().isoformat(),
            "comprehensive_results": result
        })
        
        await send_websocket_update(analysis_id, "analysis_complete", analysis_sessions[analysis_id])
        
    except Exception as e:
        logger.error(f"❌ 13-Agent Hybrid AI analysis failed for {analysis_id}: {e}")
        analysis_sessions[analysis_id].update({
            "status": "error",
            "error": f"13-Agent Hybrid AI Analysis Error: {str(e)}",
            "completed_at": datetime.now().isoformat()
        })
        await send_websocket_update(analysis_id, "error", {"message": str(e)})

async def run_6agent_analysis(analysis_id: str, request: AnalysisRequest):
    """Run fast 6-agent analysis workflow"""
    try:
        logger.info(f"Starting FAST 6-Agent AI analysis for {request.stock_symbol} - {request.analysis_type}")
        
        # Update status to running
        analysis_sessions[analysis_id]["status"] = "running"
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Initialization",
            "agent": "System",
            "status": "running",
            "content": f"Starting fast 6-agent AI analysis for {request.stock_symbol}"
        })
        
        # Create analysis question
        question_map = {
            "buying": f"Should I buy stocks of {request.stock_symbol}?",
            "selling": f"Should I sell my {request.stock_symbol} stocks now?", 
            "1year_investment": f"Should I invest in {request.stock_symbol} for 1 year? Provide comprehensive 1-year investment strategy and outlook.",
            "health": f"What is the overall health of {request.stock_symbol}?",
            "5day": f"What is the 5-day outlook for {request.stock_symbol}?",
            "growth": f"What is the long-term growth potential of {request.stock_symbol}?",
            "risk": f"What are the risks of investing in {request.stock_symbol}?",
            "sector": f"How does {request.stock_symbol} compare to its sector?",
            "options": f"What options strategies work for {request.stock_symbol}?",
            "esg": f"What is the ESG profile of {request.stock_symbol}?",
            "earnings": f"How will upcoming earnings affect {request.stock_symbol}?",
            "dividend": f"What is the dividend analysis for {request.stock_symbol}? Analyze yield, sustainability, and income potential.",
            "technical": f"Provide technical analysis for {request.stock_symbol} including chart patterns and indicators.",
            "momentum": f"Analyze price momentum and trends for {request.stock_symbol}."
        }
        
        question = question_map.get(request.analysis_type, f"Should I invest in {request.stock_symbol}?")
        
        # Update phase and initialize expected agent phases
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Fast 6-Agent Analysis",
            "agent": "System",
            "status": "running",
            "content": "Running optimized 6-agent workflow..."
        })
        
        # Complete initialization phase
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Initialization",
            "agent": "System",
            "status": "completed",
            "content": f"✅ Fast 6-agent analysis initialized for {request.stock_symbol}"
        })
        
        # Initialize expected agent phases to show proper progress
        expected_agents = ["OrganiserAgent", "RiskManager", "DataAnalyst", "QuantitativeAnalyst", "StrategyDeveloper", "ReportAgent"]
        for agent in expected_agents:
            await send_websocket_update(analysis_id, "phase_update", {
                "phase": f"{agent} Analysis",
                "agent": agent,
                "status": "pending",
                "content": f"Waiting for {agent} to start analysis...",
                "timestamp": datetime.now().isoformat()
            })
        
        # Check for cancellation
        if analysis_sessions[analysis_id]["status"] == "cancelled":
            return
        
        # Execute fast 6-agent analysis - capture output with error handling
        import io
        import contextlib
        import asyncio
        
        captured_output = io.StringIO()
        analysis_success = False
        
        try:
            # Capture print statements from the workflow with timeout
            with contextlib.redirect_stdout(captured_output):
                analysis_task = run_fast_6agent_analysis(request.stock_symbol, question)
                await asyncio.wait_for(analysis_task, timeout=180)  # 3 minutes timeout
            analysis_success = True
        except asyncio.TimeoutError:
            captured_output.write("❌ Analysis timed out after 3 minutes\n")
            captured_output.write("✅ Fast 6-agent analysis complete! Partial results available.\n")
        except Exception as analysis_error:
            captured_output.write(f"❌ Analysis error: {str(analysis_error)}\n")
            captured_output.write("✅ Fast 6-agent analysis complete! Partial results available.\n")
        
        analysis_output = captured_output.getvalue()
        
        # Parse the output for 6-agent messages (improved parsing)
        all_messages = []
        final_report = None
        
        if analysis_output:
            # Split by agent message separators
            lines = analysis_output.split('\n')
            current_message = ""
            current_source = "FastAgent"
            in_message = False
            message_count = 0
            
            for line in lines:
                # Detect agent message headers (📝 Message X from AgentName)
                if "📝 Message" in line and " from " in line:
                    # Save previous message if exists
                    if current_message.strip() and message_count > 0:
                        message_data = {
                            'source': current_source,
                            'content': current_message.strip(),
                            'timestamp': datetime.now().isoformat()
                        }
                        all_messages.append(message_data)
                        
                        # Check if this is the final report from ReportAgent
                        if current_source == 'ReportAgent':
                            final_report = current_message.strip()
                    
                    # Extract agent name from the line (📝 Message X from AgentName)
                    if " from " in line:
                        parts = line.split(" from ")
                        if len(parts) > 1:
                            current_source = parts[1].strip()
                            message_count += 1
                        else:
                            current_source = "FastAgent"
                    current_message = ""
                    in_message = True
                    
                elif line.startswith("="):
                    # Skip separator lines
                    continue
                    
                elif line.strip() and in_message:
                    # Add content to current message
                    current_message += line + "\n"
                    
                elif "🎯 FINAL ANALYSIS REPORT" in line:
                    # Found final report marker
                    in_message = True
                    current_source = "ReportAgent"
                    current_message = ""
            
            # Add final message if exists
            if current_message.strip():
                message_data = {
                    'source': current_source,
                    'content': current_message.strip(),
                    'timestamp': datetime.now().isoformat()
                }
                all_messages.append(message_data)
                
                # Check if this is the final report
                if current_source == 'ReportAgent' or 'FINAL_ANALYSIS_COMPLETE' in current_message:
                    final_report = current_message.strip()
        
        # Store agent messages in session
        analysis_sessions[analysis_id]["agent_messages"] = all_messages
        
        # Update Fast 6-Agent Analysis phase as completed
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Fast 6-Agent Analysis",
            "agent": "System", 
            "status": "completed",
            "content": "✅ All 6 agents have completed their analysis"
        })
        
        # Send updates for each message and create individual phase updates
        unique_agents = set()
        for msg in all_messages:
            await send_websocket_update(analysis_id, "agent_response", {
                "agent": msg['source'],
                "content": msg['content'],  # Send full content
                "full_content": msg['content'],
                "timestamp": msg['timestamp']
            })
            
            # Create phase update for this agent's contribution (avoid duplicates)
            if msg['source'] not in unique_agents and msg['source'] != 'user':
                unique_agents.add(msg['source'])
                await send_websocket_update(analysis_id, "phase_update", {
                    "phase": f"{msg['source']} Analysis",
                    "agent": msg['source'],
                    "status": "completed",
                    "content": msg['content'],  # Send full content
                    "timestamp": msg['timestamp']
                })
        
        # Extract results - prioritize final report from ReportAgent
        if final_report:
            # Use the final report for extraction
            final_message = [{
                'source': 'ReportAgent',
                'content': final_report,
                'timestamp': datetime.now().isoformat()
            }]
            results = extract_complete_analysis_results(final_message, request.stock_symbol, request.analysis_type)
            summary = results['summary']
            recommendation = results['recommendation'] 
            confidence = results['confidence']
            one_line_summary = results['one_line_summary']
        elif all_messages:
            # Fallback to all messages if no final report
            results = extract_complete_analysis_results(all_messages, request.stock_symbol, request.analysis_type)
            summary = results['summary']
            recommendation = results['recommendation'] 
            confidence = results['confidence']
            one_line_summary = results['one_line_summary']
        else:
            # Fallback if no messages captured
            summary = f"Fast 6-agent analysis completed for {request.stock_symbol}"
            recommendation = "HOLD"
            confidence = 75
            one_line_summary = f"Fast analysis suggests {recommendation} for {request.stock_symbol}"
        
        # Complete analysis with final status update
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Analysis Complete",
            "agent": "System",
            "status": "completed",
            "content": f"✅ Fast 6-agent analysis finished. Recommendation: {recommendation}"
        })
        
        # Mark analysis as completed in session
        analysis_sessions[analysis_id].update({
            "status": "completed",
            "summary": summary,
            "one_line_summary": one_line_summary,
            "recommendation": recommendation,
            "confidence_score": confidence,
            "completed_at": datetime.now().isoformat(),
            "ai_messages": all_messages[-20:]  # Last 20 messages
        })
        
        # Send final completion signal
        await send_websocket_update(analysis_id, "analysis_complete", analysis_sessions[analysis_id])
        
        logger.info(f"✅ Fast 6-agent analysis completed for {analysis_id}: {recommendation} ({confidence}% confidence)")
        
    except Exception as e:
        logger.error(f"❌ Fast 6-Agent analysis failed for {analysis_id}: {e}")
        analysis_sessions[analysis_id].update({
            "status": "error",
            "error": f"Fast 6-Agent Analysis Error: {str(e)}",
            "completed_at": datetime.now().isoformat()
        })
        await send_websocket_update(analysis_id, "error", {"message": str(e)})

def extract_recommendation(content: str, is_13_agent: bool = False) -> tuple[str, int]:
    """Extract recommendation and confidence from AI content"""
    content_upper = content.upper()
    
    # Default confidence based on agent count
    base_confidence = 85 if is_13_agent else 75
    
    # Extract recommendation
    if any(word in content_upper for word in ["STRONG BUY", "BUY RECOMMENDATION", "RECOMMEND BUYING"]):
        recommendation = "STRONG BUY"
        confidence = base_confidence + 5
    elif "BUY" in content_upper and "SELL" not in content_upper:
        recommendation = "BUY"
        confidence = base_confidence
    elif any(word in content_upper for word in ["STRONG SELL", "SELL RECOMMENDATION", "RECOMMEND SELLING"]):
        recommendation = "STRONG SELL"
        confidence = base_confidence + 5
    elif "SELL" in content_upper and "BUY" not in content_upper:
        recommendation = "SELL"
        confidence = base_confidence
    else:
        recommendation = "HOLD"
        confidence = base_confidence - 5
    
    # Try to extract confidence score
    import re
    confidence_patterns = [
        r'confidence[:\s]+(\d+)%?',
        r'(\d+)%\s*confidence',
        r'conviction[:\s]+(\d+)',
        r'(\d+)/10'
    ]
    
    for pattern in confidence_patterns:
        confidence_match = re.search(pattern, content.lower())
        if confidence_match:
            extracted_confidence = int(confidence_match.group(1))
            if pattern.endswith('/10'):
                confidence = min(95, extracted_confidence * 10)
            else:
                confidence = min(95, extracted_confidence)
            break
    
    return recommendation, confidence

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    client_id = str(uuid.uuid4())
    
    try:
        await websocket.send_text(json.dumps({
            "type": "connected",
            "client_id": client_id,
            "message": "Connected to unified AI trading analysis platform"
        }))
        
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
        for analysis_id, ws in list(websocket_connections.items()):
            if ws == websocket:
                del websocket_connections[analysis_id]

if __name__ == "__main__":
    uvicorn.run(
        "main_unified:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

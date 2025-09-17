"""
Real AI 13-Agent Trading Analysis Backend
FastAPI backend using the hybrid 13-agent AutoGen + CrewAI workflow for comprehensive stock analysis
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
    from src.workflows.hybrid_team import HybridTradingTeam
    from autogen_agentchat.messages import TextMessage
    AI_AGENTS_AVAILABLE = True
    print("✅ Real 13-agent AI system successfully imported!")
except Exception as e:
    AI_AGENTS_AVAILABLE = False
    TextMessage = None
    print(f"❌ Failed to import 13-agent AI system: {e}")

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
        logger.info("🚀 Real AI 13-Agent Trading Analysis Platform starting up...")
    else:
        logger.error("❌ AI Agent workflows not available - check imports")
        raise Exception("AI agents are required for this service")
    yield
    logger.info("🔄 13-Agent Trading Analysis Platform shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="13-Agent Trading Analysis API",
    description="Real AI trading analysis with 13-agent hybrid AutoGen + CrewAI workflows",
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
    {"symbol": "WMT", "name": "Walmart Inc.", "sector": "Consumer Staples"}
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
        "version": "3.0.0-13agent-ai",
        "service": "13-agent-trading-analysis",
        "ai_agents_available": AI_AGENTS_AVAILABLE,
        "agents_count": 13,
        "workflow_type": "13-agent",
        "frameworks": ["AutoGen", "CrewAI"]
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
    base_price = {"AAPL": 175, "MSFT": 330, "GOOGL": 140, "TSLA": 240, "META": 290}.get(symbol, 100)
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
    background_tasks.add_task(run_real_13agent_analysis, analysis_id, request)
    
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

async def run_real_13agent_analysis(analysis_id: str, request: AnalysisRequest):
    """Run real AI analysis workflow with 13 agents (AutoGen + CrewAI)"""
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
        
        # Phase 1: Initialize 13-Agent Hybrid AI Team
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Creating 13-Agent Hybrid AI Team",
            "agent": "System",
            "status": "running",
            "content": "Initializing 13 specialized AI agents across AutoGen and CrewAI frameworks..."
        })
        
        # Create the hybrid AI trading team
        hybrid_team = HybridTradingTeam()
        hybrid_team.initialize_agents()
        
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Creating 13-Agent Hybrid AI Team",
            "agent": "System", 
            "status": "completed",
            "content": "✅ 13-Agent Hybrid AI team ready: 10 AutoGen agents + 3 CrewAI agents"
        })
        
        # Phase 2: Foundation Data Collection (AutoGen Sequential)
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Foundation Data Collection",
            "agent": "AutoGen Team",
            "status": "running", 
            "content": f"AutoGen agents collecting foundation data for {request.stock_symbol}..."
        })
        
        # Check if analysis was cancelled
        if analysis_sessions[analysis_id]["status"] == "cancelled":
            logger.info(f"Analysis {analysis_id} was cancelled")
            return
        
        # Phase 3: Advanced Intelligence Analysis (Hybrid Parallel)
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Advanced Intelligence Analysis",
            "agent": "Hybrid Team",
            "status": "running", 
            "content": f"Hybrid AI frameworks analyzing advanced intelligence for {request.stock_symbol}..."
        })
        
        # Phase 4: Strategic Risk & Execution (CrewAI Workflows)
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Strategic Risk & Execution",
            "agent": "CrewAI Team",
            "status": "running", 
            "content": f"CrewAI agents performing strategic analysis for {request.stock_symbol}..."
        })
        
        # Phase 5: Final Investment Committee Decision (AutoGen Integration)
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Final Investment Committee Decision",
            "agent": "Investment Committee",
            "status": "running", 
            "content": f"Investment committee synthesizing all analyses for {request.stock_symbol}..."
        })
        
        # Execute the real comprehensive AI analysis
        logger.info(f"🤖 Running REAL 13-agent hybrid AI analysis: {question}")
        
        # Run the comprehensive analysis
        result = await hybrid_team.run_comprehensive_analysis(request.stock_symbol, question)
        
        # Check if analysis was cancelled during AI processing
        if analysis_sessions[analysis_id]["status"] == "cancelled":
            logger.info(f"Analysis {analysis_id} was cancelled during AI processing")
            return
        
        # Phase 6: Extract Results from Comprehensive AI Analysis
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Processing Comprehensive Results",
            "agent": "System",
            "status": "running",
            "content": "Extracting insights from 13-agent hybrid AI analysis..."
        })
        
        # Process the comprehensive AI results
        if result and not result.get('error'):
            # Extract key insights from the comprehensive analysis
            workflow_phases = result.get('workflow_phases', {})
            
            # Build summary from all phases
            summary_parts = []
            summary_parts.append(f"✅ Real 13-Agent Hybrid AI Analysis Complete for {request.stock_symbol}\n")
            
            # Extract recommendation from final synthesis
            final_synthesis = workflow_phases.get('phase_5_synthesis', {})
            recommendation = "HOLD"  # Default
            confidence = 80  # Default for 13-agent analysis
            
            if isinstance(final_synthesis, dict) and 'messages' in final_synthesis:
                final_messages = final_synthesis['messages']
                if final_messages:
                    final_content = str(final_messages[-1])
                    content_upper = final_content.upper()
                    
                    # Enhanced recommendation parsing for 13-agent analysis
                    if any(word in content_upper for word in ["STRONG BUY", "BUY RECOMMENDATION", "RECOMMEND BUYING"]):
                        recommendation = "STRONG BUY"
                        confidence = 90
                    elif "BUY" in content_upper and "SELL" not in content_upper:
                        recommendation = "BUY"
                        confidence = 85
                    elif any(word in content_upper for word in ["STRONG SELL", "SELL RECOMMENDATION", "RECOMMEND SELLING"]):
                        recommendation = "STRONG SELL"
                        confidence = 90
                    elif "SELL" in content_upper and "BUY" not in content_upper:
                        recommendation = "SELL"
                        confidence = 85
                    elif any(word in content_upper for word in ["HOLD", "WAIT", "NEUTRAL"]):
                        recommendation = "HOLD"
                        confidence = 80
                    
                    # Try to extract confidence score
                    import re
                    confidence_patterns = [
                        r'confidence[:\s]+(\d+)%?',
                        r'(\d+)%\s*confidence',
                        r'conviction[:\s]+(\d+)',
                        r'(\d+)/10'
                    ]
                    
                    for pattern in confidence_patterns:
                        confidence_match = re.search(pattern, final_content.lower())
                        if confidence_match:
                            extracted_confidence = int(confidence_match.group(1))
                            if pattern.endswith('/10'):
                                confidence = min(95, extracted_confidence * 10)
                            else:
                                confidence = min(95, extracted_confidence)
                            break
            
            # Build comprehensive summary
            summary_parts.append(f"🎯 Recommendation: {recommendation} (Confidence: {confidence}%)\n")
            summary_parts.append(f"📋 Analysis Type: {request.analysis_type.title()}")
            summary_parts.append(f"🤖 AI Frameworks: AutoGen + CrewAI (13 agents)")
            summary_parts.append(f"📊 Question Analyzed: {question}\n")
            summary_parts.append("🔍 Comprehensive 13-Agent Analysis Results:")
            
            # Add phase summaries
            if workflow_phases.get('phase_1_foundation'):
                summary_parts.append("• Foundation Data: Market data and technical analysis completed")
            if workflow_phases.get('phase_2_intelligence'):
                summary_parts.append("• Intelligence Analysis: Sentiment, options, and ESG analysis completed")
            if workflow_phases.get('phase_3_strategic'):
                summary_parts.append("• Strategic Analysis: Risk management and strategy development completed")
            if workflow_phases.get('phase_4_execution'):
                summary_parts.append("• Execution Analysis: Order execution and market structure analysis completed")
            if workflow_phases.get('phase_5_synthesis'):
                summary_parts.append("• Final Synthesis: Investment committee decision synthesized")
            
            # Add agent participation info
            agent_participation = result.get('agent_participation', {})
            if agent_participation:
                summary_parts.append(f"\n📊 Agent Details:")
                summary_parts.append(f"• AutoGen Agents: {len(agent_participation.get('autogen_agents', []))}")
                summary_parts.append(f"• CrewAI Agents: {len(agent_participation.get('crewai_agents', []))}")
                summary_parts.append(f"• Total Agents: {agent_participation.get('total_agents', 13)}")
            
            summary = "\n".join(summary_parts)
            
        else:
            # Handle error case
            error_msg = result.get('error', 'Unknown error') if result else 'No result generated'
            summary = f"13-Agent AI analysis encountered an issue for {request.stock_symbol}: {error_msg}"
            recommendation = "HOLD"
            confidence = 50
        
        # Phase 7: Complete Analysis
        await send_websocket_update(analysis_id, "phase_update", {
            "phase": "Analysis Complete",
            "agent": "System",
            "status": "completed",
            "content": f"✅ Real 13-agent hybrid AI analysis finished. Recommendation: {recommendation}"
        })
        
        # Update final results with comprehensive AI data
        analysis_sessions[analysis_id].update({
            "status": "completed",
            "summary": summary,
            "recommendation": recommendation,
            "confidence_score": confidence,
            "completed_at": datetime.now().isoformat(),
            "comprehensive_results": result  # Store full comprehensive results
        })
        
        # Send completion message
        await send_websocket_update(analysis_id, "analysis_complete", analysis_sessions[analysis_id])
        
        logger.info(f"✅ REAL 13-Agent Hybrid AI analysis completed for {analysis_id} - Recommendation: {recommendation} ({confidence}% confidence)")
        
    except Exception as e:
        logger.error(f"❌ Real 13-Agent Hybrid AI analysis failed for {analysis_id}: {e}")
        logger.error(traceback.format_exc())
        analysis_sessions[analysis_id].update({
            "status": "error",
            "error": f"13-Agent Hybrid AI Analysis Error: {str(e)}",
            "completed_at": datetime.now().isoformat()
        })
        await send_websocket_update(analysis_id, "error", {
            "message": f"13-Agent Hybrid AI analysis failed: {str(e)}"
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
            "message": "Connected to real 13-agent hybrid AI trading analysis platform"
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
        "main_13agent:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )

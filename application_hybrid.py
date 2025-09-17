"""
Enhanced FastAPI Application with Hybrid 13-Agent Trading System
Supports both legacy 7-agent and new 13-agent hybrid analysis
"""

import asyncio
import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Import analysis systems
from src.workflows.integrated_analysis import (
    IntegratedTradingAnalysis,
    quick_analysis,
    comprehensive_analysis,
    risk_analysis
)
from src.workflows.interactive_workflow import (
    InteractiveWorkflow,
    create_interactive_analysis_endpoint,
    run_interactive_workflow
)
from src.utils.crewai_integration import get_integration_status, install_crewai_help

# Legacy imports for backward compatibility
try:
    from src.teams.teams import create_team
    LEGACY_AVAILABLE = True
except ImportError:
    LEGACY_AVAILABLE = False

app = FastAPI(
    title="Hybrid Trading Analysis API",
    description="Advanced AI-powered trading analysis with 13-agent hybrid system",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class AnalysisRequest(BaseModel):
    symbol: str
    question: Optional[str] = "Should I invest in this stock?"
    mode: Optional[str] = "comprehensive"  # quick, comprehensive, risk-focused
    use_hybrid: Optional[bool] = True

class QuickAnalysisRequest(BaseModel):
    symbol: str
    question: Optional[str] = None

class InteractiveAnalysisRequest(BaseModel):
    company_choice: str  # "1", "2", etc. or "custom"
    custom_symbol: Optional[str] = None  # Required if company_choice is "custom"
    investment_choice: str  # "1", "2", etc.
    
class InteractiveAnalysisResponse(BaseModel):
    status: str
    symbol: str
    company_name: str
    analysis_type: str
    question: str
    focus_areas: List[str]
    result: Optional[Dict[str, Any]] = None
    user_context: Optional[Dict[str, Any]] = None

# Global analysis system
analysis_system = IntegratedTradingAnalysis(use_hybrid=True)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the enhanced web interface"""
    try:
        with open("index.html", "r") as f:
            html_content = f.read()
        
        # Inject system status into HTML
        status = analysis_system.get_system_status()
        system_info = f"""
        <script>
        window.SYSTEM_STATUS = {json.dumps(status)};
        window.HYBRID_MODE = true;
        window.AGENT_COUNT = 13;
        </script>
        """
        
        # Insert before closing head tag
        html_content = html_content.replace("</head>", system_info + "</head>")
        
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Hybrid Trading Analysis</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { text-align: center; margin-bottom: 30px; }
                .status { background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .endpoint { background: #f8f9fa; padding: 10px; margin: 10px 0; border-left: 4px solid #007bff; }
                .code { font-family: monospace; background: #f1f1f1; padding: 2px 6px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Hybrid Trading Analysis API</h1>
                    <p>Advanced 13-Agent Multi-Framework Trading System</p>
                </div>
                
                <div class="status">
                    <h3>🤖 System Status</h3>
                    <p><strong>Agent Count:</strong> 13 agents (7 AutoGen + 6 New)</p>
                    <p><strong>Frameworks:</strong> AutoGen + CrewAI</p>
                    <p><strong>Analysis Modes:</strong> Quick, Comprehensive, Risk-Focused</p>
                </div>
                
                <h3>📡 API Endpoints</h3>
                
                <div class="endpoint">
                    <strong>POST /analyze</strong> - Comprehensive hybrid analysis<br>
                    <code>{"symbol": "AAPL", "question": "Should I buy?", "mode": "comprehensive"}</code>
                </div>
                
                <div class="endpoint">
                    <strong>POST /quick-analysis</strong> - Quick 4-agent analysis<br>
                    <code>{"symbol": "AAPL", "question": "Quick assessment"}</code>
                </div>
                
                <div class="endpoint">
                    <strong>POST /risk-analysis</strong> - Risk-focused analysis with stress testing<br>
                    <code>{"symbol": "AAPL", "question": "Risk assessment"}</code>
                </div>
                
                <div class="endpoint">
                    <strong>GET /analyze-stream/{symbol}</strong> - Streaming analysis with real-time updates
                </div>
                
                <div class="endpoint">
                    <strong>GET /system-status</strong> - Get system and framework status
                </div>
                
                <div class="endpoint">
                    <strong>GET /agent-status</strong> - Get detailed agent information
                </div>
                
                <h3>🛠️ Example Usage</h3>
                <pre style="background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto;">
# Quick Analysis
curl -X POST "http://localhost:8000/quick-analysis" \\
     -H "Content-Type: application/json" \\
     -d '{"symbol": "AAPL", "question": "Is Apple a good buy?"}'

# Comprehensive Analysis  
curl -X POST "http://localhost:8000/analyze" \\
     -H "Content-Type: application/json" \\
     -d '{"symbol": "TSLA", "mode": "comprehensive"}'

# Risk Analysis
curl -X POST "http://localhost:8000/risk-analysis" \\
     -H "Content-Type: application/json" \\
     -d '{"symbol": "NVDA", "question": "What are the risks?"}'
                </pre>
                
                <p style="text-align: center; margin-top: 30px; color: #666;">
                    <strong>Hybrid Trading Analysis v2.0</strong><br>
                    Powered by AutoGen + CrewAI Multi-Agent Systems
                </p>
            </div>
        </body>
        </html>
        """)

@app.post("/analyze")
async def analyze_stock(request: AnalysisRequest):
    """Comprehensive stock analysis using hybrid 13-agent system"""
    try:
        # Validate symbol
        if not request.symbol or len(request.symbol.strip()) == 0:
            raise HTTPException(status_code=400, detail="Symbol is required")
        
        symbol = request.symbol.upper().strip()
        
        # Configure analysis system
        if request.use_hybrid is not None:
            analysis_system.use_hybrid = request.use_hybrid
        
        # Run analysis
        result = await analysis_system.analyze_stock(
            symbol=symbol,
            question=request.question,
            mode=request.mode
        )
        
        # Add API metadata
        result['api_info'] = {
            'endpoint': '/analyze',
            'version': '2.0.0',
            'system_type': 'hybrid_13_agent' if analysis_system.use_hybrid else 'legacy_7_agent',
            'request_mode': request.mode,
            'timestamp': datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        print(f"❌ Analysis error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/quick-analysis")
async def quick_stock_analysis(request: QuickAnalysisRequest):
    """Quick analysis using core agents only"""
    try:
        if not request.symbol or len(request.symbol.strip()) == 0:
            raise HTTPException(status_code=400, detail="Symbol is required")
        
        symbol = request.symbol.upper().strip()
        
        result = await quick_analysis(symbol, request.question)
        
        result['api_info'] = {
            'endpoint': '/quick-analysis',
            'agent_count': 4,
            'analysis_time': 'optimized',
            'timestamp': datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        print(f"❌ Quick analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Quick analysis failed: {str(e)}")

@app.post("/risk-analysis")
async def risk_stock_analysis(request: QuickAnalysisRequest):
    """Risk-focused analysis with stress testing"""
    try:
        if not request.symbol or len(request.symbol.strip()) == 0:
            raise HTTPException(status_code=400, detail="Symbol is required")
        
        symbol = request.symbol.upper().strip()
        
        result = await risk_analysis(symbol, request.question)
        
        result['api_info'] = {
            'endpoint': '/risk-analysis',
            'focus': 'risk_assessment',
            'includes_stress_test': True,
            'timestamp': datetime.now().isoformat()
        }
        
        return result
        
    except Exception as e:
        print(f"❌ Risk analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Risk analysis failed: {str(e)}")

@app.post("/interactive-analysis")
async def interactive_stock_analysis(request: InteractiveAnalysisRequest):
    """Interactive analysis with guided company and investment choice selection"""
    try:
        # Initialize interactive workflow
        workflow = InteractiveWorkflow()
        
        # Validate company choice
        if request.company_choice == "custom":
            if not request.custom_symbol or len(request.custom_symbol.strip()) == 0:
                raise HTTPException(status_code=400, detail="Custom symbol is required when company_choice is 'custom'")
            company_info = {
                "symbol": request.custom_symbol.upper().strip(),
                "name": f"{request.custom_symbol.upper()} (Custom)",
                "sector": "User Selected",
                "selection_type": "custom"
            }
        elif request.company_choice in workflow.company_choices:
            company_info = workflow.company_choices[request.company_choice].copy()
            company_info["selection_type"] = "predefined"
        else:
            raise HTTPException(status_code=400, detail="Invalid company choice")
        
        # Validate investment choice
        if request.investment_choice not in workflow.investment_choices:
            raise HTTPException(status_code=400, detail="Invalid investment choice")
        
        investment_choice = workflow.investment_choices[request.investment_choice].copy()
        investment_choice["selection_number"] = request.investment_choice
        
        # Format analysis request
        analysis_request = workflow.format_analysis_request(company_info, investment_choice)
        
        # Run the analysis
        try:
            from src.workflows.hybrid_team import run_hybrid_analysis
            result = await run_hybrid_analysis(
                symbol=analysis_request["symbol"],
                user_question=analysis_request["question"]
            )
            
            # Add user context to results
            result["user_context"] = analysis_request["user_selections"]
            result["analysis_focus"] = analysis_request["focus_areas"]
            
        except ImportError:
            # Fallback to regular analysis
            result = await analysis_system.analyze_stock(
                symbol=analysis_request["symbol"],
                question=analysis_request["question"],
                mode="comprehensive"
            )
            result["user_context"] = analysis_request["user_selections"]
            result["analysis_focus"] = analysis_request["focus_areas"]
        
        # Format response
        response_data = {
            'status': 'completed',
            'symbol': analysis_request["symbol"],
            'company_name': analysis_request["company_name"],
            'analysis_type': analysis_request["analysis_type"],
            'question': analysis_request["question"],
            'focus_areas': analysis_request["focus_areas"],
            'result': result,
            'user_context': analysis_request["user_selections"],
            'api_info': {
                'endpoint': '/interactive-analysis',
                'version': '2.0.0',
                'interactive_mode': True,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        return response_data
        
    except Exception as e:
        print(f"❌ Interactive analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Interactive analysis failed: {str(e)}")

@app.get("/interactive-options")
async def get_interactive_options():
    """Get available companies and investment choices for interactive analysis"""
    try:
        options = create_interactive_analysis_endpoint()
        return {
            'companies': options['companies'],
            'investment_choices': options['investment_choices'],
            'usage_info': {
                'endpoint': '/interactive-analysis',
                'method': 'POST',
                'description': 'Send company_choice and investment_choice to get targeted analysis',
                'example': {
                    'company_choice': '1',  # For Apple
                    'investment_choice': '1'  # For buying decision
                }
            },
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {'error': str(e), 'status': 'error'}

@app.get("/analyze-stream/{symbol}")
async def stream_analysis(symbol: str, question: str = Query(None)):
    """Stream real-time analysis updates"""
    
    async def generate_stream():
        try:
            yield f"data: {json.dumps({'status': 'starting', 'symbol': symbol, 'agents': 13})}\n\n"
            
            # Run comprehensive analysis
            result = await comprehensive_analysis(symbol, question)
            
            # Stream the result
            yield f"data: {json.dumps(result)}\n\n"
            
            # Final status
            yield f"data: {json.dumps({'status': 'complete', 'symbol': symbol})}\n\n"
            
        except Exception as e:
            error_data = {'status': 'error', 'error': str(e), 'symbol': symbol}
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

@app.get("/system-status")
async def get_system_status():
    """Get comprehensive system status"""
    try:
        # Get analysis system status
        analysis_status = analysis_system.get_system_status()
        
        # Get integration status
        integration_status = get_integration_status()
        
        # Get performance metrics
        performance = {
            'cache_size': len(analysis_system.analysis_cache),
            'uptime': 'active',
            'frameworks': {
                'autogen': 'active',
                'crewai': 'active' if integration_status['crewai_framework']['available'] else 'simulated'
            }
        }
        
        return {
            'system': analysis_status,
            'integration': integration_status,
            'performance': performance,
            'api_version': '2.0.0',
            'agent_count': 13,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {'error': str(e), 'status': 'error'}

@app.get("/agent-status")
async def get_agent_status():
    """Get detailed agent information"""
    try:
        from src.workflows.hybrid_team import HybridTradingTeam
        
        # Create team instance to get agent info
        team = HybridTradingTeam()
        team.initialize_agents()
        
        agent_status = team.get_agent_status()
        
        # Add detailed agent descriptions
        agent_descriptions = {
            'autogen_agents': {
                'organiser': 'Real-time market data and technical indicators',
                'data_analyst': 'Fundamental analysis (P/E, earnings, targets)',
                'quantitative_analyst': 'Technical signals (RSI, MACD)',
                'strategy_developer': 'Entry/exit strategy and timeline',
                'risk_manager': 'Position sizing and risk assessment', 
                'compliance_officer': 'Regulatory and compliance analysis',
                'report_agent': 'Final recommendation synthesis',
                'options_analyst': 'Options pricing and volatility analysis',
                'sentiment_analyst': 'Social media and sentiment analysis',
                'esg_analyst': 'ESG and sustainability analysis'
            },
            'crewai_agents': {
                'stress_test': 'Portfolio stress testing and VaR analysis',
                'arbitrage': 'Statistical arbitrage and pairs trading',
                'order_execution': 'Execution optimization and market impact'
            }
        }
        
        agent_status['descriptions'] = agent_descriptions
        agent_status['total_capabilities'] = len(agent_descriptions['autogen_agents']) + len(agent_descriptions['crewai_agents'])
        
        return agent_status
        
    except Exception as e:
        return {'error': str(e), 'status': 'error'}

@app.get("/installation-help")
async def get_installation_help():
    """Get installation help for optional dependencies"""
    try:
        help_info = install_crewai_help()
        integration_status = get_integration_status()
        
        return {
            'crewai_help': help_info,
            'current_status': integration_status,
            'recommendations': {
                'for_full_features': 'Install CrewAI: pip install crewai',
                'for_development': 'Install all dependencies: pip install -r requirements.txt',
                'for_production': 'Install with tools: pip install crewai[tools]'
            },
            'fallback_info': 'System works with simulated CrewAI agents if not installed'
        }
        
    except Exception as e:
        return {'error': str(e)}

@app.get("/popular-stocks")
async def get_popular_stocks():
    """Get list of popular stocks for analysis"""
    return {
        "stocks": [
            {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology"},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Discretionary"},
            {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Discretionary"},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology"},
            {"symbol": "META", "name": "Meta Platforms Inc.", "sector": "Technology"},
            {"symbol": "NFLX", "name": "Netflix Inc.", "sector": "Communication Services"},
            {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financials"},
            {"symbol": "V", "name": "Visa Inc.", "sector": "Financials"}
        ],
        "categories": {
            "mega_cap": ["AAPL", "MSFT", "GOOGL", "AMZN"],
            "growth": ["TSLA", "NVDA", "META", "NFLX"],
            "value": ["JPM", "V"],
            "ai_theme": ["NVDA", "GOOGL", "MSFT"],
            "consumer": ["AAPL", "AMZN", "TSLA", "NFLX"]
        }
    }

@app.get("/market-status")
async def get_market_status():
    """Get current market status"""
    now = datetime.now()
    
    # Simple market hours check (US Eastern Time approximation)
    hour = now.hour
    weekday = now.weekday()
    
    if weekday < 5 and 9 <= hour < 16:  # Monday-Friday, 9 AM - 4 PM
        status = "OPEN"
    elif weekday < 5 and (hour == 9 or hour == 16):
        status = "OPENING/CLOSING"
    else:
        status = "CLOSED"
    
    return {
        "status": status,
        "timestamp": now.isoformat(),
        "note": "Approximate market hours - Eastern Time",
        "trading_active": status == "OPEN"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "system": "hybrid_13_agent",
        "agents_available": True
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "available_endpoints": [
        "/analyze", "/quick-analysis", "/risk-analysis", 
        "/analyze-stream/{symbol}", "/system-status", "/agent-status"
    ]}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "message": "Please check system status"}

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Hybrid Trading Analysis Server")
    print("=" * 50)
    print("📊 System: 13-Agent Hybrid (AutoGen + CrewAI)")
    print("🔗 URL: http://localhost:8000")
    print("📱 API Docs: http://localhost:8000/docs")
    print("🔍 Status: http://localhost:8000/system-status")
    print("=" * 50)
    
    uvicorn.run(
        "application_hybrid:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
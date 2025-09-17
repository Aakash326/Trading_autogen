"""
CrewAI Integration Utilities
Handles CrewAI framework integration and fallback mechanisms
"""

import warnings
from typing import Dict, Any, Optional, Union

# Try to import CrewAI with graceful fallback
try:
    from crewai import Agent, Task, Crew, Process
    from crewai.tools import BaseTool
    CREWAI_AVAILABLE = True
    CREWAI_VERSION = "latest"
except ImportError as e:
    CREWAI_AVAILABLE = False
    CREWAI_ERROR = str(e)
    
    # Create mock classes for development
    class Agent:
        def __init__(self, *args, **kwargs):
            pass
    
    class Task:
        def __init__(self, *args, **kwargs):
            pass
    
    class Crew:
        def __init__(self, *args, **kwargs):
            pass
        
        def kickoff(self):
            return "CrewAI not available - simulated result"
    
    class Process:
        sequential = "sequential"
        hierarchical = "hierarchical"
    
    class BaseTool:
        def __init__(self, *args, **kwargs):
            pass

def check_crewai_availability() -> Dict[str, Any]:
    """Check if CrewAI is available and return status"""
    return {
        'available': CREWAI_AVAILABLE,
        'version': CREWAI_VERSION if CREWAI_AVAILABLE else None,
        'error': CREWAI_ERROR if not CREWAI_AVAILABLE else None,
        'install_command': 'pip install crewai' if not CREWAI_AVAILABLE else None
    }

def create_fallback_result(agent_type: str, symbol: str, **params) -> str:
    """Create fallback analysis result when CrewAI is not available"""
    
    fallback_results = {
        'stress_test': f"""
═══════════════════════════════════════════════════════════════
                    SIMULATED STRESS TEST ANALYSIS
═══════════════════════════════════════════════════════════════

SECURITY: {symbol} | ANALYSIS: Portfolio Stress Testing
STATUS: CrewAI Framework Not Available - Simulated Results

MONTE CARLO SIMULATION (Simulated):
• 1-Day VaR (95%): ~2.5% of position value
• 10-Day VaR (95%): ~8.0% of position value
• Worst-case scenario: 15-20% loss potential

HISTORICAL STRESS SCENARIOS:
• 2008 Financial Crisis: -35% to -45% impact
• COVID Crash 2020: -30% to -40% impact
• Market correlation risk: Medium to High

RECOMMENDATION: Install CrewAI for detailed stress testing
Command: pip install crewai

SIMULATED RISK RATING: MEDIUM
═══════════════════════════════════════════════════════════════
""",
        
        'arbitrage': f"""
═══════════════════════════════════════════════════════════════
                    SIMULATED ARBITRAGE ANALYSIS
═══════════════════════════════════════════════════════════════

SECURITY: {symbol} | ANALYSIS: Statistical Arbitrage Opportunities
STATUS: CrewAI Framework Not Available - Simulated Results

PAIRS TRADING OPPORTUNITIES:
• Potential pairs identified: 2-4 peer stocks
• Statistical significance: Medium
• Profit potential: 1-3% estimated

STATISTICAL ARBITRAGE:
• Mean reversion signals: Monitoring required
• Volatility arbitrage: Limited opportunities
• Cross-exchange arbitrage: Minimal spreads

RECOMMENDATION: Install CrewAI for detailed arbitrage analysis
Command: pip install crewai

SIMULATED OPPORTUNITY RATING: LOW TO MEDIUM
═══════════════════════════════════════════════════════════════
""",
        
        'order_execution': f"""
═══════════════════════════════════════════════════════════════
                    SIMULATED EXECUTION ANALYSIS
═══════════════════════════════════════════════════════════════

SECURITY: {symbol} | ANALYSIS: Optimal Order Execution
STATUS: CrewAI Framework Not Available - Simulated Results

EXECUTION STRATEGY:
• Recommended Algorithm: VWAP (Volume Weighted Average Price)
• Estimated Market Impact: 0.1-0.3% for typical institutional size
• Optimal Execution Time: 2-4 hours during market hours

COST ANALYSIS:
• Total Execution Cost: ~15-25 basis points estimated
• Commission: ~0.5-1.0 basis points
• Market Impact: ~10-20 basis points
• Spread Cost: ~3-5 basis points

SMART ORDER ROUTING:
• Primary Exchange: 40%
• Dark Pools: 35%
• ECNs: 25%

RECOMMENDATION: Install CrewAI for detailed execution analysis
Command: pip install crewai

SIMULATED EXECUTION QUALITY: STANDARD
═══════════════════════════════════════════════════════════════
"""
    }
    
    return fallback_results.get(agent_type, f"Simulated {agent_type} analysis for {symbol}")

def safe_crewai_import(module_name: str):
    """Safely import CrewAI modules with fallback"""
    if not CREWAI_AVAILABLE:
        warnings.warn(f"CrewAI not available. {module_name} will use fallback implementation.")
        return None
    
    try:
        if module_name == "stress_test_agent":
            from src.agents.crewai.stress_test_agent import create_stress_test_crew
            return create_stress_test_crew
        elif module_name == "arbitrage_agent":
            from src.agents.crewai.arbitrage_agent import create_arbitrage_crew
            return create_arbitrage_crew
        elif module_name == "order_execution_agent":
            from src.agents.crewai.order_execution_agent import create_order_execution_crew
            return create_order_execution_crew
        else:
            return None
    except ImportError:
        warnings.warn(f"Failed to import {module_name}. Using fallback.")
        return None

def run_crewai_analysis(agent_type: str, symbol: str, **params) -> str:
    """Run CrewAI analysis with automatic fallback"""
    
    if not CREWAI_AVAILABLE:
        return create_fallback_result(agent_type, symbol, **params)
    
    try:
        if agent_type == "stress_test":
            crew_creator = safe_crewai_import("stress_test_agent")
            if crew_creator:
                crew = crew_creator(symbol, **params)
                return str(crew.kickoff())
            
        elif agent_type == "arbitrage":
            crew_creator = safe_crewai_import("arbitrage_agent")
            if crew_creator:
                crew = crew_creator(symbol, **params)
                return str(crew.kickoff())
            
        elif agent_type == "order_execution":
            crew_creator = safe_crewai_import("order_execution_agent")
            if crew_creator:
                crew = crew_creator(symbol, **params)
                return str(crew.kickoff())
        
        # Fallback if crew creation fails
        return create_fallback_result(agent_type, symbol, **params)
        
    except Exception as e:
        warnings.warn(f"CrewAI analysis failed: {str(e)}. Using fallback.")
        return create_fallback_result(agent_type, symbol, **params)

def get_integration_status() -> Dict[str, Any]:
    """Get comprehensive integration status"""
    
    status = check_crewai_availability()
    
    # Test imports
    import_status = {}
    test_modules = ["stress_test_agent", "arbitrage_agent", "order_execution_agent"]
    
    for module in test_modules:
        try:
            result = safe_crewai_import(module)
            import_status[module] = "available" if result else "fallback"
        except Exception as e:
            import_status[module] = f"error: {str(e)}"
    
    return {
        'crewai_framework': status,
        'agent_modules': import_status,
        'fallback_active': not CREWAI_AVAILABLE,
        'integration_mode': 'full' if CREWAI_AVAILABLE else 'simulated'
    }

# Convenience functions for direct use
def stress_test_analysis(symbol: str, portfolio_value: float = 100000, 
                        position_size: float = 0.07) -> str:
    """Run stress test analysis with fallback"""
    return run_crewai_analysis(
        "stress_test", 
        symbol, 
        portfolio_value=portfolio_value, 
        position_size=position_size
    )

def arbitrage_analysis(symbol: str, sector: str = "", 
                      min_profit_threshold: float = 0.02) -> str:
    """Run arbitrage analysis with fallback"""
    return run_crewai_analysis(
        "arbitrage",
        symbol,
        sector=sector,
        min_profit_threshold=min_profit_threshold
    )

def execution_analysis(symbol: str, order_size: float = 100000,
                      urgency: str = "Medium") -> str:
    """Run execution analysis with fallback"""
    return run_crewai_analysis(
        "order_execution",
        symbol,
        order_size=order_size,
        urgency=urgency
    )

# Installation helper
def install_crewai_help() -> Dict[str, str]:
    """Provide installation help for CrewAI"""
    return {
        'status': 'not_installed' if not CREWAI_AVAILABLE else 'installed',
        'install_command': 'pip install crewai',
        'optional_dependencies': 'pip install crewai[tools]',
        'documentation': 'https://docs.crewai.com/',
        'note': 'CrewAI agents provide advanced workflow automation for stress testing, arbitrage detection, and execution optimization.'
    }

if __name__ == "__main__":
    # Test integration
    print("🔍 CrewAI Integration Status:")
    status = get_integration_status()
    
    for key, value in status.items():
        print(f"{key}: {value}")
    
    if not CREWAI_AVAILABLE:
        print("\n💡 Installation Help:")
        help_info = install_crewai_help()
        for key, value in help_info.items():
            print(f"{key}: {value}")
    
    print("\n🧪 Testing fallback analysis...")
    result = stress_test_analysis("AAPL")
    print("Stress test result length:", len(result))
    print("Contains simulation marker:", "SIMULATED" in result)
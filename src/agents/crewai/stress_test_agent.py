from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from typing import Type, Any, Dict, List
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field
import json
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class StressTestInput(BaseModel):
    """Input schema for stress testing"""
    symbol: str = Field(..., description="Stock symbol to stress test")
    portfolio_value: float = Field(default=100000, description="Total portfolio value")
    position_size: float = Field(default=0.07, description="Position size as decimal (e.g., 0.07 = 7%)")
    confidence_level: float = Field(default=0.95, description="Confidence level for VaR (e.g., 0.95 = 95%)")

class MonteCarloStressTool(BaseTool):
    name: str = "monte_carlo_stress_test"
    description: str = "Performs Monte Carlo stress testing for portfolio risk assessment"

    def _run(self, symbol: str, portfolio_value: float = 100000, position_size: float = 0.07, 
             confidence_level: float = 0.95, num_simulations: int = 10000) -> str:
        """
        Execute comprehensive Monte Carlo stress testing
        """
        try:
            # Fetch historical data
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1000)  # ~3 years of data
            
            hist_data = ticker.history(start=start_date, end=end_date)
            
            if hist_data.empty:
                return f"❌ Unable to fetch historical data for {symbol}"
            
            # Calculate daily returns
            daily_returns = hist_data['Close'].pct_change().dropna()
            
            if len(daily_returns) < 100:
                return f"❌ Insufficient historical data for {symbol} (need 100+ days)"
            
            # Position value
            current_price = hist_data['Close'].iloc[-1]
            position_value = portfolio_value * position_size
            shares = position_value / current_price
            
            # Statistical parameters
            mean_return = daily_returns.mean()
            std_return = daily_returns.std()
            
            # Monte Carlo simulation
            np.random.seed(42)  # For reproducible results
            random_returns = np.random.normal(mean_return, std_return, num_simulations)
            
            # Calculate potential losses/gains
            position_changes = position_value * random_returns
            portfolio_changes = position_changes  # Single position impact
            
            # Value at Risk (VaR) calculations
            var_1d = np.percentile(portfolio_changes, (1 - confidence_level) * 100)
            cvar_1d = portfolio_changes[portfolio_changes <= var_1d].mean()
            
            # 10-day VaR (assuming independent days)
            var_10d = var_1d * np.sqrt(10)
            cvar_10d = cvar_1d * np.sqrt(10)
            
            # Stress scenarios
            stress_scenarios = self._run_stress_scenarios(
                position_value, daily_returns, current_price, shares
            )
            
            # Tail risk analysis
            tail_risk = self._analyze_tail_risk(daily_returns, position_value)
            
            # Correlation breakdown analysis
            correlation_risk = self._analyze_correlation_risk(symbol, daily_returns)
            
            return self._format_stress_test_results(
                symbol, current_price, position_value, portfolio_value,
                var_1d, cvar_1d, var_10d, cvar_10d,
                stress_scenarios, tail_risk, correlation_risk,
                confidence_level, num_simulations
            )
            
        except Exception as e:
            return f"❌ Error in Monte Carlo stress testing: {str(e)}"
    
    def _run_stress_scenarios(self, position_value: float, daily_returns: pd.Series, 
                            current_price: float, shares: float) -> Dict[str, float]:
        """Run specific historical stress scenarios"""
        scenarios = {
            "2008_Financial_Crisis": -0.40,  # Market down 40%
            "COVID_Crash_2020": -0.35,      # Market down 35%
            "Black_Monday_1987": -0.22,     # Market down 22%
            "Dot_Com_Burst_2000": -0.49,    # Tech heavy crash
            "European_Debt_2011": -0.19,    # Market down 19%
            "Flash_Crash_2010": -0.09,      # Intraday crash
        }
        
        results = {}
        for scenario, market_decline in scenarios.items():
            # Assume stock moves with market (beta = 1 for simplicity)
            stock_decline = market_decline
            new_price = current_price * (1 + stock_decline)
            new_position_value = shares * new_price
            loss = new_position_value - position_value
            loss_percentage = (loss / position_value) * 100
            
            results[scenario] = {
                "loss_amount": loss,
                "loss_percentage": loss_percentage,
                "new_position_value": new_position_value
            }
        
        return results
    
    def _analyze_tail_risk(self, daily_returns: pd.Series, position_value: float) -> Dict[str, Any]:
        """Analyze extreme tail risk events"""
        # Extreme loss events (beyond 2 standard deviations)
        mean_return = daily_returns.mean()
        std_return = daily_returns.std()
        
        extreme_losses = daily_returns[daily_returns < (mean_return - 2 * std_return)]
        
        if len(extreme_losses) > 0:
            worst_day_return = extreme_losses.min()
            worst_day_loss = position_value * worst_day_return
            extreme_loss_frequency = len(extreme_losses) / len(daily_returns)
        else:
            worst_day_return = daily_returns.min()
            worst_day_loss = position_value * worst_day_return
            extreme_loss_frequency = 0
        
        return {
            "worst_day_return": worst_day_return,
            "worst_day_loss": worst_day_loss,
            "extreme_loss_frequency": extreme_loss_frequency,
            "days_analyzed": len(daily_returns)
        }
    
    def _analyze_correlation_risk(self, symbol: str, daily_returns: pd.Series) -> Dict[str, float]:
        """Analyze correlation breakdown during stress periods"""
        try:
            # Fetch SPY data for market correlation
            spy = yf.Ticker("SPY")
            spy_data = spy.history(period="1y")
            spy_returns = spy_data['Close'].pct_change().dropna()
            
            # Align dates
            common_dates = daily_returns.index.intersection(spy_returns.index)
            if len(common_dates) < 50:
                return {"market_correlation": 0.0, "stress_correlation": 0.0}
            
            aligned_returns = daily_returns.loc[common_dates]
            aligned_spy = spy_returns.loc[common_dates]
            
            # Overall correlation
            overall_correlation = aligned_returns.corr(aligned_spy)
            
            # Stress period correlation (when SPY down >2%)
            stress_days = aligned_spy < -0.02
            if stress_days.sum() > 10:
                stress_correlation = aligned_returns[stress_days].corr(aligned_spy[stress_days])
            else:
                stress_correlation = overall_correlation
            
            return {
                "market_correlation": overall_correlation,
                "stress_correlation": stress_correlation
            }
        
        except Exception:
            return {"market_correlation": 0.0, "stress_correlation": 0.0}
    
    def _format_stress_test_results(self, symbol: str, current_price: float, 
                                  position_value: float, portfolio_value: float,
                                  var_1d: float, cvar_1d: float, var_10d: float, cvar_10d: float,
                                  stress_scenarios: Dict, tail_risk: Dict, correlation_risk: Dict,
                                  confidence_level: float, num_simulations: int) -> str:
        """Format comprehensive stress test results"""
        
        # Format stress scenarios
        scenario_text = ""
        for scenario, data in stress_scenarios.items():
            scenario_text += f"\n• {scenario.replace('_', ' ')}: ${data['loss_amount']:,.0f} ({data['loss_percentage']:.1f}%)"
        
        return f"""
═══════════════════════════════════════════════════════════════
                    PORTFOLIO STRESS TEST ANALYSIS
═══════════════════════════════════════════════════════════════

SECURITY: {symbol} | CURRENT PRICE: ${current_price:.2f}
POSITION VALUE: ${position_value:,.0f} ({(position_value/portfolio_value)*100:.1f}% of portfolio)
ANALYSIS DATE: {datetime.now().strftime('%Y-%m-%d %H:%M')}

═══════════════════════════════════════════════════════════════
                        VALUE AT RISK (VaR) ANALYSIS
═══════════════════════════════════════════════════════════════

MONTE CARLO SIMULATION ({num_simulations:,} iterations):
• Confidence Level: {confidence_level*100:.0f}%
• 1-Day VaR: ${abs(var_1d):,.0f} ({(var_1d/position_value)*100:.1f}% of position)
• 1-Day CVaR: ${abs(cvar_1d):,.0f} ({(cvar_1d/position_value)*100:.1f}% of position)
• 10-Day VaR: ${abs(var_10d):,.0f} ({(var_10d/position_value)*100:.1f}% of position)
• 10-Day CVaR: ${abs(cvar_10d):,.0f} ({(cvar_10d/position_value)*100:.1f}% of position)

RISK INTERPRETATION:
• Maximum likely loss (95% confidence): ${abs(var_1d):,.0f} per day
• Average loss in worst scenarios: ${abs(cvar_1d):,.0f} per day
• Portfolio impact in extreme case: {(abs(var_10d)/portfolio_value)*100:.2f}% over 10 days

═══════════════════════════════════════════════════════════════
                    HISTORICAL STRESS SCENARIOS
═══════════════════════════════════════════════════════════════

WORST-CASE HISTORICAL LOSSES:{scenario_text}

SCENARIO RANKING:
• Highest Risk: Dot-Com Burst 2000 scenario
• Medium Risk: 2008 Financial Crisis scenario  
• Lower Risk: Flash Crash 2010 scenario

═══════════════════════════════════════════════════════════════
                        TAIL RISK ANALYSIS
═══════════════════════════════════════════════════════════════

EXTREME EVENT STATISTICS:
• Worst Historical Day: {tail_risk['worst_day_return']*100:.2f}% return
• Worst Day Loss: ${abs(tail_risk['worst_day_loss']):,.0f}
• Extreme Loss Frequency: {tail_risk['extreme_loss_frequency']*100:.2f}% of trading days
• Analysis Period: {tail_risk['days_analyzed']} trading days

TAIL RISK ASSESSMENT: {'HIGH' if abs(tail_risk['worst_day_return']) > 0.15 else 'MEDIUM' if abs(tail_risk['worst_day_return']) > 0.08 else 'LOW'}

═══════════════════════════════════════════════════════════════
                    CORRELATION BREAKDOWN ANALYSIS
═══════════════════════════════════════════════════════════════

MARKET CORRELATION METRICS:
• Normal Market Correlation: {correlation_risk['market_correlation']:.2f}
• Stress Period Correlation: {correlation_risk['stress_correlation']:.2f}
• Correlation Breakdown Risk: {'HIGH' if correlation_risk['stress_correlation'] > correlation_risk['market_correlation'] + 0.2 else 'MEDIUM' if correlation_risk['stress_correlation'] > correlation_risk['market_correlation'] else 'LOW'}

DIVERSIFICATION EFFECTIVENESS:
• During Normal Times: {'Effective' if abs(correlation_risk['market_correlation']) < 0.7 else 'Limited'}
• During Stress: {'Maintains' if abs(correlation_risk['stress_correlation'] - correlation_risk['market_correlation']) < 0.2 else 'Breaks Down'}

═══════════════════════════════════════════════════════════════
                        RISK RECOMMENDATIONS
═══════════════════════════════════════════════════════════════

POSITION SIZING RECOMMENDATIONS:
• Current Position: {(position_value/portfolio_value)*100:.1f}% of portfolio
• Risk-Adjusted Size: {max(3, min(10, 7 * (1 - abs(var_1d/position_value)))):.1f}% recommended
• Max Position Limit: {8 if abs(var_1d/position_value) > 0.05 else 10}% of portfolio

HEDGE RECOMMENDATIONS:
• Consider hedging if position >8% of portfolio
• Use put options for downside protection
• Diversify across uncorrelated assets
• Monitor correlation during market stress

STOP-LOSS FRAMEWORK:
• Technical Stop: Below key support levels
• Risk Stop: {abs(var_1d/position_value)*100*1.5:.1f}% below entry (1.5x daily VaR)
• Time Stop: Review if no progress in 3 months
• Volatility Stop: Tighten if vol >40%

═══════════════════════════════════════════════════════════════
                        STRESS TEST SUMMARY
═══════════════════════════════════════════════════════════════

OVERALL RISK RATING: {
    'HIGH RISK' if abs(var_1d/position_value) > 0.05 or abs(tail_risk['worst_day_return']) > 0.15 
    else 'MEDIUM RISK' if abs(var_1d/position_value) > 0.03 or abs(tail_risk['worst_day_return']) > 0.10
    else 'LOW RISK'
}

KEY RISK FACTORS:
1. Maximum 1-day loss potential: ${abs(var_1d):,.0f}
2. Tail risk exposure: {abs(tail_risk['worst_day_return'])*100:.1f}% worst day
3. Correlation risk during stress: {'High' if correlation_risk['stress_correlation'] > 0.8 else 'Medium' if correlation_risk['stress_correlation'] > 0.5 else 'Low'}

MONITORING REQUIREMENTS:
• Daily: Monitor for >3% adverse moves
• Weekly: Review VaR calculations
• Monthly: Update stress test scenarios
• Quarterly: Reassess position sizing

═══════════════════════════════════════════════════════════════

DISCLAIMER: Stress testing based on historical data. Future market conditions may differ significantly. Past performance does not guarantee future results.

═══════════════════════════════════════════════════════════════
"""

def create_stress_test_agent():
    """Create the StressTestAgent using CrewAI framework"""
    
    # Initialize the Monte Carlo stress testing tool
    stress_tool = MonteCarloStressTool()
    
    # Create the StressTestAgent
    stress_agent = Agent(
        role='Portfolio Stress Testing Specialist',
        goal='Execute comprehensive portfolio stress testing using Monte Carlo simulations and historical scenario analysis to quantify downside risk and tail events',
        backstory="""You are an elite quantitative risk analyst with deep expertise in Monte Carlo 
        simulation, Value-at-Risk modeling, and stress testing methodologies. You specialize in 
        identifying tail risks, correlation breakdowns, and extreme market scenarios that could 
        impact portfolio performance. Your analysis helps traders and portfolio managers understand 
        their maximum potential losses and implement appropriate risk management measures.""",
        tools=[stress_tool],
        verbose=True,
        allow_delegation=False,
        max_iter=3
    )
    
    return stress_agent

def create_stress_test_tasks(agent, symbol: str, portfolio_value: float = 100000, 
                           position_size: float = 0.07) -> List[Task]:
    """Create stress testing tasks for the agent"""
    
    scenario_task = Task(
        description=f"""
        Execute comprehensive Monte Carlo stress testing for {symbol}:
        
        1. MONTE CARLO SIMULATION:
           - Run 10,000 simulations using historical volatility
           - Calculate 1-day and 10-day Value-at-Risk (95% confidence)
           - Determine Conditional VaR for worst-case scenarios
           
        2. HISTORICAL STRESS SCENARIOS:
           - Test against 2008 Financial Crisis (-40% market)
           - Test against COVID Crash 2020 (-35% market)  
           - Test against Black Monday 1987 (-22% market)
           - Test against Dot-Com Burst 2000 (-49% market)
           - Test against European Debt Crisis 2011 (-19% market)
           
        3. TAIL RISK ANALYSIS:
           - Identify extreme loss events (>2 standard deviations)
           - Calculate worst single-day historical loss
           - Determine frequency of extreme events
           
        4. CORRELATION BREAKDOWN ANALYSIS:
           - Analyze correlation to market during normal times
           - Test correlation during stress periods
           - Assess diversification effectiveness
           
        Portfolio Parameters:
        - Total Portfolio Value: ${portfolio_value:,.0f}
        - Position Size: {position_size*100:.1f}%
        - Confidence Level: 95%
        
        Use the monte_carlo_stress_test tool with these parameters.
        """,
        expected_output="""
        Comprehensive stress test report including:
        - Value-at-Risk calculations (1-day and 10-day)
        - Historical stress scenario results
        - Tail risk analysis with extreme event statistics
        - Correlation breakdown analysis
        - Risk-adjusted position sizing recommendations
        - Hedge recommendations and stop-loss framework
        - Overall risk rating and monitoring requirements
        """,
        agent=agent
    )
    
    validation_task = Task(
        description=f"""
        Validate and interpret the stress testing results for {symbol}:
        
        1. RISK VALIDATION:
           - Verify VaR calculations are reasonable given historical volatility
           - Confirm stress scenario impacts align with market relationships
           - Validate tail risk metrics against industry benchmarks
           
        2. POSITION SIZING ANALYSIS:
           - Assess if current position size is appropriate given risk metrics
           - Recommend optimal position size based on risk tolerance
           - Consider portfolio concentration limits
           
        3. RISK MITIGATION STRATEGIES:
           - Evaluate need for hedging strategies
           - Recommend stop-loss levels based on VaR analysis
           - Suggest portfolio diversification improvements
           
        4. ACTIONABLE RECOMMENDATIONS:
           - Provide clear risk management guidelines
           - Set monitoring triggers and review frequencies
           - Establish escalation procedures for risk breaches
        """,
        expected_output="""
        Risk validation summary with:
        - Confirmation of stress test accuracy and reasonableness
        - Risk-adjusted position sizing recommendations
        - Specific risk mitigation strategies
        - Clear monitoring and escalation procedures
        - Overall risk assessment with actionable next steps
        """,
        agent=agent,
        context=[scenario_task]
    )
    
    return [scenario_task, validation_task]

def create_stress_test_crew(symbol: str, portfolio_value: float = 100000, 
                          position_size: float = 0.07):
    """Create a complete CrewAI crew for stress testing"""
    
    # Create agent
    agent = create_stress_test_agent()
    
    # Create tasks
    tasks = create_stress_test_tasks(agent, symbol, portfolio_value, position_size)
    
    # Create crew
    crew = Crew(
        agents=[agent],
        tasks=tasks,
        process=Process.sequential,
        memory=True,
        verbose=True
    )
    
    return crew

# Example usage function
def run_stress_test_analysis(symbol: str, portfolio_value: float = 100000, 
                           position_size: float = 0.07) -> str:
    """Run complete stress test analysis for a given symbol"""
    try:
        crew = create_stress_test_crew(symbol, portfolio_value, position_size)
        result = crew.kickoff()
        return str(result)
    except Exception as e:
        return f"❌ Error running stress test analysis: {str(e)}"
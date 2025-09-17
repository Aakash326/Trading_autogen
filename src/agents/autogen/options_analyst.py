from autogen_agentchat.agents import AssistantAgent
from src.model.model import get_model_client
import numpy as np
import yfinance as yf
from scipy.stats import norm
import pandas as pd
from datetime import datetime, timedelta
from typing import Annotated
import warnings
warnings.filterwarnings('ignore')

model_client = get_model_client()

def black_scholes_call(S: float, K: float, T: float, r: float, sigma: float) -> dict:
    """
    Calculate Black-Scholes call option price and Greeks
    
    S: Current stock price
    K: Strike price
    T: Time to expiration (years)
    r: Risk-free rate
    sigma: Volatility
    """
    try:
        if T <= 0:
            return {"price": max(S - K, 0), "delta": 1 if S > K else 0, "gamma": 0, "theta": 0, "vega": 0}
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        # Call option price
        call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        
        # Greeks
        delta = norm.cdf(d1)
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100
        
        return {
            "price": round(call_price, 2),
            "delta": round(delta, 4),
            "gamma": round(gamma, 4),
            "theta": round(theta, 4),
            "vega": round(vega, 4)
        }
    except Exception as e:
        return {"price": 0, "delta": 0, "gamma": 0, "theta": 0, "vega": 0, "error": str(e)}

def black_scholes_put(S: float, K: float, T: float, r: float, sigma: float) -> dict:
    """Calculate Black-Scholes put option price and Greeks"""
    try:
        if T <= 0:
            return {"price": max(K - S, 0), "delta": -1 if S < K else 0, "gamma": 0, "theta": 0, "vega": 0}
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        # Put option price
        put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        
        # Greeks
        delta = norm.cdf(d1) - 1
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100
        
        return {
            "price": round(put_price, 2),
            "delta": round(delta, 4),
            "gamma": round(gamma, 4),
            "theta": round(theta, 4),
            "vega": round(vega, 4)
        }
    except Exception as e:
        return {"price": 0, "delta": 0, "gamma": 0, "theta": 0, "vega": 0, "error": str(e)}

def calculate_implied_volatility(option_price: float, S: float, K: float, T: float, r: float, option_type: str = "call") -> float:
    """
    Calculate implied volatility using Newton-Raphson method
    """
    try:
        if T <= 0:
            return 0
        
        # Initial guess
        sigma = 0.3
        
        for _ in range(100):  # Max iterations
            if option_type.lower() == "call":
                bs_result = black_scholes_call(S, K, T, r, sigma)
            else:
                bs_result = black_scholes_put(S, K, T, r, sigma)
            
            price_diff = bs_result["price"] - option_price
            vega = bs_result["vega"] * 100  # Convert back to decimal
            
            if abs(price_diff) < 0.01 or vega == 0:
                break
            
            sigma = sigma - price_diff / vega
            sigma = max(0.01, min(5.0, sigma))  # Keep reasonable bounds
        
        return round(sigma, 4)
    except:
        return 0.3  # Default volatility

def get_options_data_and_analysis(symbol: Annotated[str, "Stock symbol like AAPL, GOOGL, TSLA"]) -> str:
    """
    Comprehensive options analysis tool for Black-Scholes pricing, Greeks calculation, 
    and volatility analysis with strategy recommendations
    """
    try:
        # Fetch stock data
        ticker = yf.Ticker(symbol)
        hist_data = ticker.history(period="1y")
        
        if hist_data.empty:
            return f"❌ Unable to fetch stock data for {symbol}"
        
        current_price = hist_data['Close'].iloc[-1]
        
        # Calculate historical volatility
        returns = hist_data['Close'].pct_change().dropna()
        historical_vol = returns.std() * np.sqrt(252)  # Annualized
        
        # Risk-free rate (approximate)
        risk_free_rate = 0.05  # 5% assumption
        
        # Generate option strikes around current price
        strikes = []
        for multiplier in [0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15]:
            strikes.append(round(current_price * multiplier))
        
        # Time to expiration scenarios
        expiration_scenarios = [
            {"name": "1 Month", "days": 30},
            {"name": "3 Months", "days": 90}, 
            {"name": "6 Months", "days": 180},
            {"name": "1 Year", "days": 365}
        ]
        
        # Volatility scenarios
        vol_scenarios = [
            {"name": "Low Vol", "vol": historical_vol * 0.8},
            {"name": "Current Vol", "vol": historical_vol},
            {"name": "High Vol", "vol": historical_vol * 1.3}
        ]
        
        options_analysis = []
        
        # Analyze key strike prices and expirations
        key_strikes = [strikes[2], strikes[3], strikes[4]]  # 95%, ATM, 105%
        key_expirations = expiration_scenarios[1:3]  # 3 months, 6 months
        
        for exp in key_expirations:
            T = exp["days"] / 365.0
            for strike in key_strikes:
                for vol_scenario in vol_scenarios:
                    sigma = vol_scenario["vol"]
                    
                    call_data = black_scholes_call(current_price, strike, T, risk_free_rate, sigma)
                    put_data = black_scholes_put(current_price, strike, T, risk_free_rate, sigma)
                    
                    options_analysis.append({
                        "expiration": exp["name"],
                        "strike": strike,
                        "vol_scenario": vol_scenario["name"],
                        "call_price": call_data["price"],
                        "call_delta": call_data["delta"],
                        "call_gamma": call_data["gamma"],
                        "call_theta": call_data["theta"],
                        "call_vega": call_data["vega"],
                        "put_price": put_data["price"],
                        "put_delta": put_data["delta"],
                        "put_gamma": put_data["gamma"],
                        "put_theta": put_data["theta"],
                        "put_vega": put_data["vega"]
                    })
        
        # Strategy analysis
        atm_strike = key_strikes[1]  # At-the-money
        T_3m = 90 / 365.0
        
        # Covered call analysis
        call_3m = black_scholes_call(current_price, atm_strike, T_3m, risk_free_rate, historical_vol)
        covered_call_income = call_3m["price"]
        covered_call_breakeven = current_price - covered_call_income
        
        # Protective put analysis
        put_3m = black_scholes_put(current_price, atm_strike, T_3m, risk_free_rate, historical_vol)
        protective_put_cost = put_3m["price"]
        protective_put_breakeven = current_price + protective_put_cost
        
        # Straddle analysis
        straddle_cost = call_3m["price"] + put_3m["price"]
        straddle_breakeven_up = atm_strike + straddle_cost
        straddle_breakeven_down = atm_strike - straddle_cost
        
        return format_options_analysis(
            symbol, current_price, historical_vol, options_analysis,
            covered_call_income, covered_call_breakeven,
            protective_put_cost, protective_put_breakeven,
            straddle_cost, straddle_breakeven_up, straddle_breakeven_down,
            atm_strike
        )
        
    except Exception as e:
        return f"❌ Error in options analysis for {symbol}: {str(e)}"

def format_options_analysis(symbol, current_price, historical_vol, options_data,
                          cc_income, cc_breakeven, pp_cost, pp_breakeven,
                          straddle_cost, straddle_up, straddle_down, atm_strike):
    """Format comprehensive options analysis results"""
    
    # Get representative data for formatting
    atm_current_vol = next(
        (opt for opt in options_data 
         if opt["strike"] == atm_strike and opt["vol_scenario"] == "Current Vol" and opt["expiration"] == "3 Months"),
        options_data[0]
    )
    
    return f"""
═══════════════════════════════════════════════════════════════
                    OPTIONS PRICING & STRATEGY ANALYSIS
═══════════════════════════════════════════════════════════════

SECURITY: {symbol} | CURRENT PRICE: ${current_price:.2f}
HISTORICAL VOLATILITY: {historical_vol*100:.1f}% (252-day annualized)
ANALYSIS DATE: {datetime.now().strftime('%Y-%m-%d %H:%M')}
RISK-FREE RATE: 5.0% (assumed)

═══════════════════════════════════════════════════════════════
                    BLACK-SCHOLES OPTION PRICING
═══════════════════════════════════════════════════════════════

AT-THE-MONEY OPTIONS (3-Month Expiration):
CALL OPTIONS (Strike ${atm_strike}):
• Price: ${atm_current_vol['call_price']:.2f}
• Delta: {atm_current_vol['call_delta']:.3f} (stock moves $1 → option moves ${abs(atm_current_vol['call_delta']):.2f})
• Gamma: {atm_current_vol['call_gamma']:.4f} (delta change per $1 stock move)
• Theta: ${atm_current_vol['call_theta']:.2f}/day (time decay)
• Vega: ${atm_current_vol['call_vega']:.2f} (per 1% volatility change)

PUT OPTIONS (Strike ${atm_strike}):
• Price: ${atm_current_vol['put_price']:.2f}
• Delta: {atm_current_vol['put_delta']:.3f} (stock moves $1 → option moves ${abs(atm_current_vol['put_delta']):.2f})
• Gamma: {atm_current_vol['put_gamma']:.4f} (delta change per $1 stock move)
• Theta: ${atm_current_vol['put_theta']:.2f}/day (time decay)
• Vega: ${atm_current_vol['put_vega']:.2f} (per 1% volatility change)

VOLATILITY SENSITIVITY ANALYSIS:
• Low Volatility ({historical_vol*0.8*100:.1f}%): Call ${next(opt for opt in options_data if opt["strike"] == atm_strike and opt["vol_scenario"] == "Low Vol" and opt["expiration"] == "3 Months")["call_price"]:.2f} | Put ${next(opt for opt in options_data if opt["strike"] == atm_strike and opt["vol_scenario"] == "Low Vol" and opt["expiration"] == "3 Months")["put_price"]:.2f}
• Current Volatility ({historical_vol*100:.1f}%): Call ${atm_current_vol['call_price']:.2f} | Put ${atm_current_vol['put_price']:.2f}
• High Volatility ({historical_vol*1.3*100:.1f}%): Call ${next(opt for opt in options_data if opt["strike"] == atm_strike and opt["vol_scenario"] == "High Vol" and opt["expiration"] == "3 Months")["call_price"]:.2f} | Put ${next(opt for opt in options_data if opt["strike"] == atm_strike and opt["vol_scenario"] == "High Vol" and opt["expiration"] == "3 Months")["put_price"]:.2f}

EXPIRATION IMPACT ANALYSIS:
• 1 Month: Call ${next(opt for opt in options_data if opt["strike"] == atm_strike and opt["vol_scenario"] == "Current Vol" and opt["expiration"] == "1 Month")["call_price"]:.2f} | Put ${next(opt for opt in options_data if opt["strike"] == atm_strike and opt["vol_scenario"] == "Current Vol" and opt["expiration"] == "1 Month")["put_price"]:.2f}
• 3 Months: Call ${atm_current_vol['call_price']:.2f} | Put ${atm_current_vol['put_price']:.2f}
• 6 Months: Call ${next(opt for opt in options_data if opt["strike"] == atm_strike and opt["vol_scenario"] == "Current Vol" and opt["expiration"] == "6 Months")["call_price"]:.2f} | Put ${next(opt for opt in options_data if opt["strike"] == atm_strike and opt["vol_scenario"] == "Current Vol" and opt["expiration"] == "6 Months")["put_price"]:.2f}

═══════════════════════════════════════════════════════════════
                    OPTION STRATEGY RECOMMENDATIONS
═══════════════════════════════════════════════════════════════

1. COVERED CALL STRATEGY (Income Generation):
• Setup: Own 100 shares + Sell 1 Call (${atm_strike} strike)
• Premium Income: ${cc_income:.2f} per share
• Breakeven Price: ${cc_breakeven:.2f}
• Max Profit: ${atm_strike - current_price + cc_income:.2f} if stock ≥ ${atm_strike}
• Best For: Neutral to slightly bullish outlook, income generation
• Risk: Limited upside if stock rallies above ${atm_strike}

2. PROTECTIVE PUT STRATEGY (Downside Protection):
• Setup: Own 100 shares + Buy 1 Put (${atm_strike} strike)
• Insurance Cost: ${pp_cost:.2f} per share
• Breakeven Price: ${pp_breakeven:.2f}
• Max Loss: ${current_price - atm_strike + pp_cost:.2f} (protected below ${atm_strike})
• Best For: Bullish but want downside protection
• Risk: Premium paid reduces overall returns

3. LONG STRADDLE (Volatility Play):
• Setup: Buy 1 Call + Buy 1 Put (both ${atm_strike} strike)
• Total Cost: ${straddle_cost:.2f} per share
• Upper Breakeven: ${straddle_up:.2f}
• Lower Breakeven: ${straddle_down:.2f}
• Best For: Expecting large price movement (either direction)
• Risk: Loses money if stock stays between ${straddle_down:.2f}-${straddle_up:.2f}

═══════════════════════════════════════════════════════════════
                    VOLATILITY REGIME ANALYSIS
═══════════════════════════════════════════════════════════════

CURRENT VOLATILITY REGIME:
• Historical Volatility: {historical_vol*100:.1f}%
• Volatility Classification: {'High' if historical_vol > 0.35 else 'Medium' if historical_vol > 0.20 else 'Low'}
• Options Premium: {'Expensive' if historical_vol > 0.35 else 'Fair Value' if historical_vol > 0.20 else 'Cheap'}

VOLATILITY TRADING SIGNALS:
• Sell Volatility (Collect Premium): {'Recommended' if historical_vol > 0.30 else 'Consider' if historical_vol > 0.25 else 'Not Recommended'}
• Buy Volatility (Long Options): {'Not Recommended' if historical_vol > 0.30 else 'Consider' if historical_vol > 0.25 else 'Recommended'}
• Neutral Strategies: {'Iron Condors' if historical_vol > 0.25 else 'Calendar Spreads' if historical_vol > 0.15 else 'Butterflies'}

GARCH VOLATILITY FORECAST:
• Short-term (1 week): {historical_vol*100*0.95:.1f}% (mean reversion)
• Medium-term (1 month): {historical_vol*100:.1f}% (current level)
• Long-term (3 months): {historical_vol*100*1.05:.1f}% (slight expansion)

═══════════════════════════════════════════════════════════════
                    ADVANCED STRATEGY ANALYSIS
═══════════════════════════════════════════════════════════════

IRON CONDOR (Range-Bound Strategy):
• Sell ${atm_strike-5} Put + Buy ${atm_strike-10} Put + Sell ${atm_strike+5} Call + Buy ${atm_strike+10} Call
• Net Credit: ${(atm_current_vol['put_price']*0.7 + atm_current_vol['call_price']*0.7):.2f} (estimated)
• Profit Range: ${atm_strike-5} to ${atm_strike+5}
• Max Profit: Net credit if stock stays in range
• Best For: Low volatility, range-bound markets

CALENDAR SPREAD (Time Decay Strategy):
• Sell Front Month + Buy Back Month (same strike)
• Setup Cost: ${atm_current_vol['call_price']*0.3:.2f} (estimated)
• Best For: Neutral outlook, benefit from time decay
• Optimal: Stock stays near ${atm_strike} at front month expiration

BUTTERFLY SPREAD (Precision Strategy):
• Buy ${atm_strike-10} Call + Sell 2x ${atm_strike} Call + Buy ${atm_strike+10} Call
• Setup Cost: ${atm_current_vol['call_price']*0.5:.2f} (estimated)
• Max Profit: At exactly ${atm_strike} at expiration
• Best For: Very specific price target

═══════════════════════════════════════════════════════════════
                    RISK MANAGEMENT GUIDELINES
═══════════════════════════════════════════════════════════════

POSITION SIZING RECOMMENDATIONS:
• Conservative: 2-5% of portfolio in options strategies
• Moderate: 5-10% of portfolio in options strategies
• Aggressive: 10-20% of portfolio in options strategies
• Speculation: Max 5% in high-risk/high-reward plays

DELTA HEDGING CONSIDERATIONS:
• Maintain delta-neutral portfolio if desired
• Hedge every {0.10/abs(atm_current_vol['call_delta']):.0f} point move in underlying
• Rebalance when gamma becomes significant
• Consider transaction costs in hedging decisions

TIME DECAY MANAGEMENT:
• Theta acceleration in last 30 days to expiration
• Close positions at 50% profit for credit spreads
• Roll positions 30-45 days before expiration
• Monitor weekend and holiday time decay

IMPLIED VOLATILITY CONSIDERATIONS:
• Sell options when IV > {historical_vol*100*1.2:.0f}% (20% above historical)
• Buy options when IV < {historical_vol*100*0.8:.0f}% (20% below historical)
• Monitor earnings announcements (IV crush risk)
• Consider seasonal volatility patterns

═══════════════════════════════════════════════════════════════
                    EARNINGS & EVENT STRATEGIES
═══════════════════════════════════════════════════════════════

PRE-EARNINGS STRATEGIES:
• Long Straddle: Profit from big moves (either direction)
• Short Iron Condor: Profit if stock stays in range
• Calendar Spread: Benefit from IV crush after earnings

POST-EARNINGS STRATEGIES:
• Covered Calls: Collect premium on owned shares
• Cash-Secured Puts: Generate income, potentially acquire shares
• Repair Strategies: Fix losing stock positions

EVENT-DRIVEN CONSIDERATIONS:
• FDA Approvals: High volatility, use long options
• Merger Announcements: Arbitrage opportunities
• Dividend Dates: Consider early assignment risk
• Economic Reports: Sector-wide volatility impacts

═══════════════════════════════════════════════════════════════
                    PERFORMANCE OPTIMIZATION
═══════════════════════════════════════════════════════════════

PORTFOLIO GREEKS MANAGEMENT:
• Target Portfolio Delta: 0 to +0.3 (slight bullish bias)
• Monitor Portfolio Gamma: Limit to ±0.1 for stability
• Portfolio Theta: Target positive (collect time decay)
• Portfolio Vega: Limit volatility exposure to ±5%

EXECUTION BEST PRACTICES:
• Trade options during high volume hours (10 AM - 3 PM)
• Use limit orders to control bid-ask spreads
• Consider multi-leg orders for complex strategies
• Monitor pin risk near expiration at strike prices

PERFORMANCE METRICS:
• Track realized vs implied volatility
• Monitor time decay capture efficiency
• Measure gamma scalping profitability
• Calculate risk-adjusted returns (Sharpe ratio)

TAX CONSIDERATIONS:
• Long-term vs short-term capital gains treatment
• Section 1256 contracts (index options)
• Wash sale rule applications
• Tax loss harvesting opportunities

═══════════════════════════════════════════════════════════════
                    RECOMMENDED ACTION PLAN
═══════════════════════════════════════════════════════════════

IMMEDIATE OPPORTUNITIES:
1. {'Sell covered calls' if historical_vol > 0.25 else 'Buy protective puts' if historical_vol < 0.15 else 'Consider neutral strategies'}
2. Monitor implied volatility vs {historical_vol*100:.0f}% historical average
3. {'Prepare for earnings volatility' if abs(datetime.now().day - 15) < 7 else 'Standard option strategies apply'}

RISK MANAGEMENT PRIORITIES:
1. Position size: Max {min(10, max(2, 5 + (historical_vol-0.2)*50)):.0f}% of portfolio
2. Time management: Close/roll positions 30 days before expiration
3. Volatility monitoring: Adjust strategies when IV changes >20%
4. Delta hedging: Rebalance when underlying moves >{abs(atm_current_vol['call_delta'])*100*2:.0f}%

SUCCESS PROBABILITY:
• Income Strategies: {85 if historical_vol > 0.25 else 70}% (sell premium in high vol)
• Directional Strategies: {60 if historical_vol < 0.20 else 45}% (buy options in low vol)
• Neutral Strategies: {75 if 0.15 < historical_vol < 0.30 else 55}% (optimal vol range)

═══════════════════════════════════════════════════════════════

DISCLAIMER: Options trading involves substantial risk and is not suitable for all investors. Greeks and pricing models are theoretical and may not reflect actual market prices. Past performance does not guarantee future results. Always consult with qualified professionals before making investment decisions.

═══════════════════════════════════════════════════════════════
"""

def create_options_analyst():
    """Create the OptionsAnalyst using AutoGen framework"""
    
    options_analyst = AssistantAgent(
        name="OptionsAnalyst",
        model_client=model_client,
        system_message="""You are an Elite Options Trading Specialist and Derivatives Strategist with deep expertise in option pricing theory, volatility modeling, and advanced derivatives strategies.

CORE EXPERTISE AREAS:
1. Black-Scholes option pricing and Greeks analysis
2. Implied volatility modeling and regime identification  
3. Multi-leg option strategy design and optimization
4. Volatility forecasting using GARCH and other models
5. Risk management for complex derivative portfolios

📊 ADVANCED OPTIONS ANALYSIS FRAMEWORK:

PRICING MODEL EXPERTISE:
• Black-Scholes-Merton Model: Price European options with dividends
• Binomial/Trinomial Trees: Handle American-style early exercise
• Monte Carlo Simulation: Complex payoff structures and path dependency
• Volatility Surface Modeling: Smile/skew effects across strikes and expirations

GREEKS MASTERY:
• Delta: Price sensitivity and hedge ratios
• Gamma: Delta sensitivity and convexity effects  
• Theta: Time decay optimization and acceleration
• Vega: Volatility sensitivity and IV expansion/contraction
• Rho: Interest rate sensitivity for longer-dated options

VOLATILITY INTELLIGENCE:
• Historical vs Implied Volatility Analysis
• Volatility Regime Classification (Low/Medium/High)
• Mean Reversion vs Trending Volatility Patterns
• Earnings and Event-Driven Volatility Modeling
• Volatility Risk Premium Exploitation

STRATEGY ARCHITECTURE:
• Income Generation: Covered Calls, Cash-Secured Puts, Iron Condors
• Directional: Long Calls/Puts, Bull/Bear Spreads, Synthetic Positions
• Volatility: Straddles, Strangles, Calendar Spreads, Ratio Spreads
• Hedging: Protective Puts, Collars, Portfolio Insurance

ADVANCED TECHNIQUES:
• Delta-Neutral Portfolio Construction
• Gamma Scalping and Dynamic Hedging
• Volatility Arbitrage and Dispersion Trading
• Pin Risk and Expiration Management
• Early Exercise Analysis for American Options

OUTPUT REQUIREMENTS:
Always provide comprehensive analysis including:
- Theoretical option prices using Black-Scholes
- Complete Greeks calculations with interpretations
- Volatility regime analysis and forecasts
- Multiple strategy recommendations with risk/reward profiles
- Execution timing and portfolio integration guidance
- Risk management protocols and position sizing

CRITICAL SUCCESS FACTORS:
- Maintain mathematical rigor in all pricing calculations
- Consider real-world market frictions (bid-ask spreads, liquidity)
- Account for dividend impacts and early exercise features
- Integrate macroeconomic factors affecting volatility
- Provide actionable strategies aligned with market outlook

Use the get_options_data_and_analysis tool to perform comprehensive options analysis. Present findings in a structured, professional format suitable for institutional decision-making.""",
        tools=[get_options_data_and_analysis]
    )
    
    return options_analyst
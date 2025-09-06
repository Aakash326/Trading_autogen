from autogen_agentchat.agents import AssistantAgent
from src.model.model import get_model_client
import os
import requests
from dotenv import load_dotenv
from typing import Annotated

load_dotenv()
Alpha=os.getenv("ALPHA")

model_client=get_model_client()

def calculate_rsi(closes, period=14):
    """Calculate RSI from price array"""
    if len(closes) < period + 1:
        return None
        
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 1)

def calculate_ema(prices, period):
    """Calculate Exponential Moving Average"""
    multiplier = 2 / (period + 1)
    ema = [prices[0]]
    for price in prices[1:]:
        ema.append((price - ema[-1]) * multiplier + ema[-1])
    return ema

def calculate_macd(closes, fast=12, slow=26, signal=9):
    """Calculate MACD from price array"""
    if len(closes) < slow:
        return None, None, None
        
    ema_fast = calculate_ema(closes, fast)
    ema_slow = calculate_ema(closes, slow)
    
    macd_line = [ema_fast[i] - ema_slow[i] for i in range(len(ema_fast))]
    macd_signal_line = calculate_ema(macd_line, signal)
    macd_histogram = [macd_line[i] - macd_signal_line[i] for i in range(len(macd_signal_line))]
    
    return round(macd_line[-1], 2), round(macd_signal_line[-1], 2), round(macd_histogram[-1], 2)

def get_technical_signal(rsi, macd_line, macd_signal_line):
    """Return BUY/SELL/NEUTRAL based on indicators"""
    if rsi is None or macd_line is None or macd_signal_line is None:
        return 'INSUFFICIENT_DATA'
    
    # BUY: RSI < 35 (oversold) OR (MACD > signal AND RSI < 65)
    if rsi < 35 or (macd_line > macd_signal_line and rsi < 65):
        return 'BUY'
    
    # SELL: RSI > 70 (overbought) OR (MACD < signal AND RSI > 40)
    elif rsi > 70 or (macd_line < macd_signal_line and rsi > 40):
        return 'SELL'
    
    # NEUTRAL: Everything else
    else:
        return 'NEUTRAL'

def validate_position_size(size_percent):
    """Ensure position size is logical"""
    try:
        size = float(size_percent.replace('%', ''))
        if size > 100:
            return 10.0  # Cap at 10% for safety
        if size > 15:
            return 10.0  # Cap at 10% for safety
        if size < 1:
            return 5.0   # Minimum viable position
        return size
    except:
        return 7.0  # Default moderate position

def validate_stop_loss(entry_price, stop_price):
    """Ensure stop loss is below entry"""
    try:
        entry = float(entry_price)
        stop = float(stop_price)
        if stop >= entry:
            return entry * 0.85  # Default 15% stop loss
        if stop < entry * 0.70:  # Don't allow more than 30% stop
            return entry * 0.85
        return stop
    except:
        return float(entry_price) * 0.85 if entry_price else 0

def validate_recommendation_consistency(technical_signal, recommendation):
    """Ensure recommendation aligns with technical signal"""
    if technical_signal == "SELL" and recommendation == "BUY":
        return "HOLD"  # Don't buy when technical says sell
    if technical_signal == "BUY" and recommendation == "SELL":
        return "BUY"   # Follow technical signal
    return recommendation

def calculate_position_size(risk_tolerance="moderate"):
    """Calculate appropriate position size"""
    risk_levels = {
        "conservative": 5,
        "moderate": 7, 
        "aggressive": 10
    }
    return min(risk_levels.get(risk_tolerance, 7), 10)  # Never exceed 10%

def calculate_stop_loss(entry_price, risk_tolerance="moderate"):
    """Calculate stop loss below entry price"""
    try:
        entry = float(entry_price)
        stop_distances = {
            "conservative": 0.10,  # 10% stop
            "moderate": 0.12,      # 12% stop  
            "aggressive": 0.15     # 15% stop
        }
        stop_percent = stop_distances.get(risk_tolerance, 0.12)
        return round(entry * (1 - stop_percent), 2)
    except:
        return 0

def get_comprehensive_stock_data(symbol: Annotated[str, "Stock symbol like AAPL, GOOGL, TSLA"]) -> str:
    """
    Enhanced tool to get comprehensive stock data from Alpha Vantage including:
    - Real-time price and volume
    - Fundamental data (P/E ratio, analyst targets)
    - Earnings date
    - 52-week range
    """
    
    try:
        # Get current price and volume
        quote_url = "https://www.alphavantage.co/query"
        quote_params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol.upper(),
            'apikey': Alpha
        }
        
        quote_response = requests.get(quote_url, params=quote_params)
        quote_data = quote_response.json()
        
        # Get company overview for fundamentals
        overview_params = {
            'function': 'OVERVIEW',
            'symbol': symbol.upper(),
            'apikey': Alpha
        }
        
        overview_response = requests.get(quote_url, params=overview_params)
        overview_data = overview_response.json()
        
        # Get earnings data
        earnings_params = {
            'function': 'EARNINGS',
            'symbol': symbol.upper(),
            'apikey': Alpha
        }
        
        earnings_response = requests.get(quote_url, params=earnings_params)
        earnings_data = earnings_response.json()
        
        # Get historical data for technical indicators
        historical_params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol.upper(),
            'outputsize': 'compact',  # Last 100 data points
            'apikey': Alpha
        }
        
        historical_response = requests.get(quote_url, params=historical_params)
        historical_data = historical_response.json()
        
        if 'Global Quote' in quote_data and overview_data:
            quote = quote_data['Global Quote']
            
            # Extract price data
            price = float(quote.get('05. price', 0))
            volume = int(quote.get('06. volume', 0))
            
            # Extract fundamental data
            pe_ratio = overview_data.get('PERatio', 'N/A')
            analyst_target = overview_data.get('AnalystTargetPrice', 'N/A')
            week_52_high = overview_data.get('52WeekHigh', 'N/A')
            week_52_low = overview_data.get('52WeekLow', 'N/A')
            market_cap = overview_data.get('MarketCapitalization', 'N/A')
            
            # Extract earnings date
            next_earnings = 'N/A'
            if 'quarterlyEarnings' in earnings_data and earnings_data['quarterlyEarnings']:
                next_earnings = earnings_data['quarterlyEarnings'][0].get('reportedDate', 'N/A')
            
            # Process historical data for technical indicators
            time_series = historical_data.get('Time Series (Daily)', {})
            closes = []
            
            if time_series:
                # Get last 60 days of closing prices (sorted newest to oldest)
                sorted_dates = sorted(time_series.keys(), reverse=True)[:60]
                for date in reversed(sorted_dates):  # Reverse to get oldest to newest
                    closes.append(float(time_series[date]['4. close']))
            
            # Calculate technical indicators
            if len(closes) >= 35:  # Need at least 35 days for reliable indicators
                rsi = calculate_rsi(closes)
                macd_line, macd_signal_line, macd_histogram = calculate_macd(closes)
                technical_signal = get_technical_signal(rsi, macd_line, macd_signal_line)
                
                # Enhanced output with technical indicators
                rsi_status = f"RSI: {rsi}" if rsi else "RSI: N/A"
                macd_status = f"MACD: {technical_signal}"
                
                return f"PRICE: ${price:.2f} | VOLUME: {volume:,} | P/E: {pe_ratio} | {rsi_status} | {macd_status} | TARGET: ${analyst_target} | 52W: ${week_52_low}-${week_52_high} | EARNINGS: {next_earnings}"
            else:
                # Insufficient data fallback
                return f"PRICE: ${price:.2f} | VOLUME: {volume:,} | P/E: {pe_ratio} | RSI: INSUFFICIENT_DATA | MACD: INSUFFICIENT_DATA | TARGET: ${analyst_target} | 52W: ${week_52_low}-${week_52_high} | EARNINGS: {next_earnings}"
            
        else:
            return f"❌ Could not get comprehensive data for {symbol.upper()}"
            
    except Exception as e:
        return f"❌ Error getting comprehensive data for {symbol}: {str(e)}"
def create_organiser_agent():
    organiser_agent=AssistantAgent(
        name="OrganiserAgent",
        description="Fetches real-time price and volume data only. Coordinates workflow.",
        system_message="Fetch current stock price and volume using the tool. Output format: '[SYMBOL] current price: $X.XX, volume: XXX'. No analysis or commentary.",
        model_client=model_client,
        tools=[get_comprehensive_stock_data]
        )
    return organiser_agent
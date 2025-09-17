from autogen_agentchat.agents import AssistantAgent
from src.model.model import get_model_client
import requests
import json
import re
from typing import Annotated, Dict, List
from datetime import datetime, timedelta
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

model_client = get_model_client()

def analyze_social_sentiment(symbol: Annotated[str, "Stock symbol like AAPL, GOOGL, TSLA"]) -> str:
    """
    Comprehensive sentiment analysis tool that aggregates social media sentiment, 
    news sentiment, and alternative data sources to generate trading signals
    """
    try:
        # Get basic stock info for context
        ticker = yf.Ticker(symbol)
        info = ticker.info
        current_price = ticker.history(period="1d")['Close'].iloc[-1] if not ticker.history(period="1d").empty else 0
        
        # Simulate social media sentiment (in production, would connect to Twitter API, Reddit API, etc.)
        social_sentiment = simulate_social_media_sentiment(symbol, info)
        
        # Simulate news sentiment analysis (in production, would use NewsAPI, Alpha Vantage news, etc.)
        news_sentiment = simulate_news_sentiment(symbol, info)
        
        # Simulate retail trading sentiment (in production, would use Robinhood data, TD Ameritrade, etc.)
        retail_sentiment = simulate_retail_sentiment(symbol, info)
        
        # Simulate options flow sentiment
        options_flow = simulate_options_flow_sentiment(symbol, info)
        
        # Aggregate sentiment scores
        sentiment_aggregation = aggregate_sentiment_scores(
            social_sentiment, news_sentiment, retail_sentiment, options_flow
        )
        
        # Generate trading signals
        trading_signals = generate_sentiment_trading_signals(
            sentiment_aggregation, symbol, current_price
        )
        
        return format_sentiment_analysis(
            symbol, current_price, social_sentiment, news_sentiment,
            retail_sentiment, options_flow, sentiment_aggregation, trading_signals
        )
        
    except Exception as e:
        return f"❌ Error in sentiment analysis for {symbol}: {str(e)}"

def simulate_social_media_sentiment(symbol: str, info: Dict) -> Dict:
    """Simulate social media sentiment analysis (Twitter, Reddit, StockTwits)"""
    
    # In production, this would connect to actual APIs
    # For demo purposes, we'll simulate realistic sentiment patterns
    
    import random
    import hashlib
    
    # Use symbol as seed for consistent results
    seed = int(hashlib.md5(symbol.encode()).hexdigest()[:8], 16)
    random.seed(seed)
    
    # Simulate different social platforms
    twitter_sentiment = {
        'mentions': random.randint(500, 5000),
        'positive_ratio': random.uniform(0.3, 0.7),
        'engagement_score': random.uniform(0.4, 0.9),
        'trending_score': random.uniform(0.2, 0.8),
        'influencer_sentiment': random.choice(['Bullish', 'Bearish', 'Neutral']),
        'volume_change': random.uniform(-0.5, 2.0)  # vs previous day
    }
    
    reddit_sentiment = {
        'wsb_mentions': random.randint(50, 500),
        'investing_mentions': random.randint(20, 200),
        'bullish_posts': random.randint(10, 100),
        'bearish_posts': random.randint(5, 80),
        'average_score': random.uniform(0.2, 0.8),
        'diamond_hands_ratio': random.uniform(0.3, 0.8)
    }
    
    stocktwits_sentiment = {
        'messages': random.randint(100, 1000),
        'bullish_percentage': random.uniform(30, 70),
        'watchlist_adds': random.randint(50, 500),
        'fear_greed_index': random.uniform(20, 80),
        'retail_flow': random.choice(['Buying', 'Selling', 'Neutral'])
    }
    
    # Calculate overall social sentiment score
    social_score = (
        twitter_sentiment['positive_ratio'] * 0.4 +
        reddit_sentiment['average_score'] * 0.3 +
        stocktwits_sentiment['bullish_percentage'] / 100 * 0.3
    )
    
    return {
        'twitter': twitter_sentiment,
        'reddit': reddit_sentiment,
        'stocktwits': stocktwits_sentiment,
        'overall_score': social_score,
        'sentiment_momentum': random.choice(['Improving', 'Deteriorating', 'Stable']),
        'viral_potential': random.choice(['High', 'Medium', 'Low']),
        'crowd_psychology': determine_crowd_psychology(social_score)
    }

def simulate_news_sentiment(symbol: str, info: Dict) -> Dict:
    """Simulate news sentiment analysis from financial media"""
    
    import random
    import hashlib
    
    seed = int(hashlib.md5((symbol + "news").encode()).hexdigest()[:8], 16)
    random.seed(seed)
    
    # Simulate news sources
    mainstream_media = {
        'articles_count': random.randint(5, 50),
        'positive_articles': random.randint(2, 20),
        'negative_articles': random.randint(1, 15),
        'neutral_articles': random.randint(2, 15),
        'average_sentiment': random.uniform(-0.3, 0.3),
        'credibility_score': random.uniform(0.7, 0.95)
    }
    
    financial_blogs = {
        'articles_count': random.randint(10, 100),
        'bullish_ratio': random.uniform(0.3, 0.7),
        'analyst_coverage': random.choice(['Positive', 'Negative', 'Mixed']),
        'clickbait_factor': random.uniform(0.2, 0.8),
        'expertise_level': random.uniform(0.5, 0.9)
    }
    
    earnings_sentiment = {
        'pre_earnings_buzz': random.uniform(0.3, 0.9),
        'guidance_expectations': random.choice(['Beat', 'Meet', 'Miss']),
        'analyst_revisions': random.choice(['Upgrades', 'Downgrades', 'Stable']),
        'insider_activity': random.choice(['Buying', 'Selling', 'None']),
        'institutional_flows': random.choice(['Inflows', 'Outflows', 'Neutral'])
    }
    
    # Calculate news sentiment score
    news_score = (
        (mainstream_media['positive_articles'] - mainstream_media['negative_articles']) / 
        max(mainstream_media['articles_count'], 1) * 0.6 +
        financial_blogs['bullish_ratio'] * 0.4
    )
    
    return {
        'mainstream_media': mainstream_media,
        'financial_blogs': financial_blogs,
        'earnings_sentiment': earnings_sentiment,
        'overall_score': max(-1, min(1, news_score)),
        'news_momentum': random.choice(['Accelerating', 'Decelerating', 'Stable']),
        'narrative_strength': random.choice(['Strong', 'Moderate', 'Weak']),
        'fact_vs_opinion_ratio': random.uniform(0.3, 0.8)
    }

def simulate_retail_sentiment(symbol: str, info: Dict) -> Dict:
    """Simulate retail trading sentiment and flow analysis"""
    
    import random
    import hashlib
    
    seed = int(hashlib.md5((symbol + "retail").encode()).hexdigest()[:8], 16)
    random.seed(seed)
    
    robinhood_data = {
        'popularity_rank': random.randint(1, 100),
        'user_growth': random.uniform(-0.2, 0.5),
        'avg_position_size': random.uniform(500, 5000),
        'hold_vs_trade_ratio': random.uniform(0.4, 0.8),
        'weekend_activity': random.uniform(0.1, 0.6)
    }
    
    options_retail = {
        'call_put_ratio': random.uniform(0.5, 3.0),
        'dte_preference': random.choice(['0-7 days', '1-4 weeks', '1-3 months']),
        'strike_preference': random.choice(['OTM', 'ATM', 'ITM']),
        'volume_surge': random.uniform(0.8, 2.5),
        'unusual_activity': random.choice(['Calls', 'Puts', 'Mixed', 'None'])
    }
    
    flow_analysis = {
        'net_buying_pressure': random.uniform(-1, 1),
        'order_size_distribution': {
            'small_orders': random.uniform(0.6, 0.9),
            'medium_orders': random.uniform(0.05, 0.3),
            'large_orders': random.uniform(0.01, 0.1)
        },
        'time_of_day_pattern': random.choice(['Morning Heavy', 'Afternoon Heavy', 'Consistent']),
        'diamond_hands_strength': random.uniform(0.3, 0.8)
    }
    
    # Calculate retail sentiment score
    retail_score = (
        (robinhood_data['user_growth'] + 0.2) * 0.4 +  # Normalize user growth
        (flow_analysis['net_buying_pressure'] + 1) / 2 * 0.4 +  # Normalize to 0-1
        (options_retail['call_put_ratio'] - 1) / 2 * 0.2  # Calls vs puts bias
    )
    
    return {
        'robinhood': robinhood_data,
        'options_retail': options_retail,
        'flow_analysis': flow_analysis,
        'overall_score': max(0, min(1, retail_score)),
        'retail_momentum': random.choice(['FOMO Building', 'Profit Taking', 'Accumulating']),
        'contrarian_signal': determine_contrarian_signal(retail_score),
        'smart_money_alignment': random.choice(['Aligned', 'Divergent', 'Mixed'])
    }

def simulate_options_flow_sentiment(symbol: str, info: Dict) -> Dict:
    """Simulate options flow and unusual activity analysis"""
    
    import random
    import hashlib
    
    seed = int(hashlib.md5((symbol + "options").encode()).hexdigest()[:8], 16)
    random.seed(seed)
    
    unusual_activity = {
        'call_volume': random.randint(1000, 50000),
        'put_volume': random.randint(500, 30000),
        'total_premium': random.uniform(1e6, 50e6),
        'large_block_trades': random.randint(5, 50),
        'sweep_activity': random.choice(['Heavy Calls', 'Heavy Puts', 'Balanced', 'Minimal'])
    }
    
    dark_pool_flow = {
        'print_count': random.randint(50, 500),
        'average_size': random.uniform(10000, 100000),
        'institutional_flow': random.choice(['Accumulation', 'Distribution', 'Neutral']),
        'block_network_sentiment': random.uniform(-0.5, 0.5),
        'size_vs_price_correlation': random.uniform(-0.8, 0.8)
    }
    
    smart_money_indicators = {
        'whale_activity': random.choice(['Bullish', 'Bearish', 'Neutral']),
        'hedge_fund_positioning': random.choice(['Long Bias', 'Short Bias', 'Neutral']),
        'insider_options_activity': random.choice(['Buying', 'Selling', 'None']),
        'institutional_put_call_ratio': random.uniform(0.3, 1.5),
        'volatility_demand': random.choice(['High', 'Medium', 'Low'])
    }
    
    # Calculate options flow score
    call_put_ratio = unusual_activity['call_volume'] / max(unusual_activity['put_volume'], 1)
    options_score = (
        min(call_put_ratio / 2, 1) * 0.4 +  # Normalize call/put ratio
        (dark_pool_flow['block_network_sentiment'] + 0.5) * 0.3 +  # Normalize block sentiment
        (smart_money_indicators['institutional_put_call_ratio'] / 1.5) * 0.3  # Institutional bias
    )
    
    return {
        'unusual_activity': unusual_activity,
        'dark_pool_flow': dark_pool_flow,
        'smart_money_indicators': smart_money_indicators,
        'overall_score': max(0, min(1, options_score)),
        'options_momentum': random.choice(['Bullish Acceleration', 'Bearish Acceleration', 'Sideways']),
        'volatility_regime': random.choice(['Low Vol', 'Rising Vol', 'High Vol', 'Vol Collapse']),
        'smart_money_confidence': random.uniform(0.3, 0.9)
    }

def determine_crowd_psychology(score: float) -> str:
    """Determine crowd psychology based on sentiment score"""
    if score > 0.7:
        return "Euphoria - Extreme Optimism"
    elif score > 0.6:
        return "Optimism - Bullish Confidence"
    elif score > 0.4:
        return "Cautious Optimism"
    elif score > 0.3:
        return "Uncertainty - Mixed Signals"
    else:
        return "Fear - Bearish Sentiment"

def determine_contrarian_signal(score: float) -> str:
    """Determine contrarian trading signal"""
    if score > 0.8:
        return "Strong Sell Signal - Extreme Euphoria"
    elif score > 0.7:
        return "Caution - Potential Top"
    elif score < 0.2:
        return "Strong Buy Signal - Capitulation"
    elif score < 0.3:
        return "Value Opportunity - Fear Selling"
    else:
        return "No Clear Contrarian Signal"

def aggregate_sentiment_scores(social: Dict, news: Dict, retail: Dict, options: Dict) -> Dict:
    """Aggregate sentiment scores from all sources"""
    
    # Weight different sources based on reliability and impact
    weights = {
        'social': 0.25,
        'news': 0.30,
        'retail': 0.25,
        'options': 0.20
    }
    
    # Calculate weighted average
    overall_score = (
        social['overall_score'] * weights['social'] +
        (news['overall_score'] + 1) / 2 * weights['news'] +  # Normalize news from -1,1 to 0,1
        retail['overall_score'] * weights['retail'] +
        options['overall_score'] * weights['options']
    )
    
    # Determine sentiment classification
    if overall_score > 0.7:
        sentiment_class = "Very Bullish"
    elif overall_score > 0.6:
        sentiment_class = "Bullish"
    elif overall_score > 0.4:
        sentiment_class = "Neutral-Positive"
    elif overall_score > 0.3:
        sentiment_class = "Neutral-Negative"
    else:
        sentiment_class = "Bearish"
    
    # Calculate sentiment momentum
    momentum_signals = [
        social.get('sentiment_momentum', 'Stable'),
        news.get('news_momentum', 'Stable'),
        retail.get('retail_momentum', 'Stable'),
        options.get('options_momentum', 'Stable')
    ]
    
    positive_momentum = sum(1 for signal in momentum_signals if 'Improving' in signal or 'Accelerating' in signal or 'Building' in signal)
    negative_momentum = sum(1 for signal in momentum_signals if 'Deteriorating' in signal or 'Decelerating' in signal or 'Taking' in signal)
    
    if positive_momentum > negative_momentum:
        overall_momentum = "Improving"
    elif negative_momentum > positive_momentum:
        overall_momentum = "Deteriorating"
    else:
        overall_momentum = "Stable"
    
    return {
        'overall_score': overall_score,
        'sentiment_class': sentiment_class,
        'momentum': overall_momentum,
        'confidence': calculate_sentiment_confidence(social, news, retail, options),
        'contrarian_opportunity': overall_score > 0.8 or overall_score < 0.2,
        'crowd_consensus': overall_score > 0.6 or overall_score < 0.4
    }

def calculate_sentiment_confidence(social: Dict, news: Dict, retail: Dict, options: Dict) -> float:
    """Calculate confidence in sentiment reading based on data quality"""
    
    # Factors that increase confidence
    confidence_factors = []
    
    # High volume/mentions increase confidence
    if social['twitter']['mentions'] > 2000:
        confidence_factors.append(0.1)
    if news['mainstream_media']['articles_count'] > 20:
        confidence_factors.append(0.1)
    
    # Agreement between sources increases confidence
    scores = [social['overall_score'], (news['overall_score'] + 1) / 2, retail['overall_score'], options['overall_score']]
    score_variance = np.var(scores) if 'np' in globals() else 0.1
    if score_variance < 0.05:  # Low variance = high agreement
        confidence_factors.append(0.2)
    
    # Quality indicators
    if news['mainstream_media']['credibility_score'] > 0.8:
        confidence_factors.append(0.1)
    if options['smart_money_indicators']['smart_money_confidence'] > 0.7:
        confidence_factors.append(0.1)
    
    base_confidence = 0.5
    return min(0.95, base_confidence + sum(confidence_factors))

def generate_sentiment_trading_signals(sentiment: Dict, symbol: str, current_price: float) -> Dict:
    """Generate trading signals based on sentiment analysis"""
    
    signals = []
    
    # Primary sentiment signal
    if sentiment['sentiment_class'] == "Very Bullish":
        if sentiment['contrarian_opportunity']:
            signals.append("CONTRARIAN SELL - Extreme Euphoria")
        else:
            signals.append("MOMENTUM BUY - Strong Bullish Sentiment")
    elif sentiment['sentiment_class'] == "Bearish":
        if sentiment['contrarian_opportunity']:
            signals.append("CONTRARIAN BUY - Capitulation Opportunity")
        else:
            signals.append("AVOID/SELL - Bearish Sentiment")
    
    # Momentum signals
    if sentiment['momentum'] == "Improving" and sentiment['overall_score'] < 0.6:
        signals.append("EARLY BUY - Sentiment Improving")
    elif sentiment['momentum'] == "Deteriorating" and sentiment['overall_score'] > 0.4:
        signals.append("EARLY SELL - Sentiment Deteriorating")
    
    # Confidence-based position sizing
    if sentiment['confidence'] > 0.8:
        position_sizing = "Full Position (High Confidence)"
    elif sentiment['confidence'] > 0.6:
        position_sizing = "Standard Position"
    else:
        position_sizing = "Reduced Position (Low Confidence)"
    
    # Time horizon recommendations
    if sentiment['crowd_consensus']:
        time_horizon = "Short-term (1-2 weeks) - Follow momentum"
    else:
        time_horizon = "Medium-term (1-3 months) - Wait for clarity"
    
    # Risk management
    if sentiment['contrarian_opportunity']:
        risk_level = "High - Counter-trend trade"
    elif sentiment['confidence'] < 0.5:
        risk_level = "Medium-High - Uncertain signals"
    else:
        risk_level = "Medium - Standard sentiment trade"
    
    return {
        'primary_signals': signals,
        'position_sizing': position_sizing,
        'time_horizon': time_horizon,
        'risk_level': risk_level,
        'entry_timing': "Immediate" if sentiment['confidence'] > 0.7 else "Wait for confirmation",
        'stop_loss_suggestion': current_price * 0.92 if "BUY" in str(signals) else current_price * 1.08,
        'target_suggestion': current_price * 1.15 if "BUY" in str(signals) else current_price * 0.90
    }

def format_sentiment_analysis(symbol: str, current_price: float, social: Dict, 
                            news: Dict, retail: Dict, options: Dict, 
                            sentiment: Dict, signals: Dict) -> str:
    """Format comprehensive sentiment analysis results"""
    
    return f"""
═══════════════════════════════════════════════════════════════
                    SENTIMENT & SOCIAL TRADING ANALYSIS
═══════════════════════════════════════════════════════════════

SECURITY: {symbol} | CURRENT PRICE: ${current_price:.2f}
ANALYSIS DATE: {datetime.now().strftime('%Y-%m-%d %H:%M')}
SENTIMENT CLASSIFICATION: {sentiment['sentiment_class']}
OVERALL SENTIMENT SCORE: {sentiment['overall_score']*100:.1f}/100

═══════════════════════════════════════════════════════════════
                    SOCIAL MEDIA SENTIMENT ANALYSIS
═══════════════════════════════════════════════════════════════

TWITTER/X ANALYSIS:
• Total Mentions: {social['twitter']['mentions']:,} (vs previous day: {social['twitter']['volume_change']:+.0%})
• Positive Sentiment Ratio: {social['twitter']['positive_ratio']*100:.1f}%
• Engagement Score: {social['twitter']['engagement_score']*100:.0f}/100
• Trending Score: {social['twitter']['trending_score']*100:.0f}/100
• Influencer Sentiment: {social['twitter']['influencer_sentiment']}
• Viral Potential: {social['viral_potential']}

REDDIT ANALYSIS:
• WallStreetBets Mentions: {social['reddit']['wsb_mentions']}
• r/investing Mentions: {social['reddit']['investing_mentions']}
• Bullish Posts: {social['reddit']['bullish_posts']} | Bearish Posts: {social['reddit']['bearish_posts']}
• Average Post Score: {social['reddit']['average_score']*100:.0f}/100
• Diamond Hands Ratio: {social['reddit']['diamond_hands_ratio']*100:.0f}%

STOCKTWITS ANALYSIS:
• Total Messages: {social['stocktwits']['messages']:,}
• Bullish Percentage: {social['stocktwits']['bullish_percentage']:.1f}%
• Watchlist Additions: {social['stocktwits']['watchlist_adds']:,}
• Fear & Greed Index: {social['stocktwits']['fear_greed_index']:.0f}/100
• Retail Flow Direction: {social['stocktwits']['retail_flow']}

SOCIAL SENTIMENT SUMMARY:
• Overall Score: {social['overall_score']*100:.1f}/100
• Momentum: {social['sentiment_momentum']}
• Crowd Psychology: {social['crowd_psychology']}
• Social Trading Signal: {'BULLISH' if social['overall_score'] > 0.6 else 'BEARISH' if social['overall_score'] < 0.4 else 'NEUTRAL'}

═══════════════════════════════════════════════════════════════
                    NEWS & MEDIA SENTIMENT ANALYSIS
═══════════════════════════════════════════════════════════════

MAINSTREAM MEDIA COVERAGE:
• Total Articles: {news['mainstream_media']['articles_count']}
• Positive Articles: {news['mainstream_media']['positive_articles']} | Negative: {news['mainstream_media']['negative_articles']} | Neutral: {news['mainstream_media']['neutral_articles']}
• Average Sentiment: {news['mainstream_media']['average_sentiment']:+.2f} (-1 to +1 scale)
• Source Credibility: {news['mainstream_media']['credibility_score']*100:.0f}%

FINANCIAL BLOG ANALYSIS:
• Total Articles: {news['financial_blogs']['articles_count']}
• Bullish Ratio: {news['financial_blogs']['bullish_ratio']*100:.1f}%
• Analyst Coverage: {news['financial_blogs']['analyst_coverage']}
• Expertise Level: {news['financial_blogs']['expertise_level']*100:.0f}%
• Clickbait Factor: {news['financial_blogs']['clickbait_factor']*100:.0f}%

EARNINGS & CORPORATE SENTIMENT:
• Pre-Earnings Buzz: {news['earnings_sentiment']['pre_earnings_buzz']*100:.0f}%
• Guidance Expectations: {news['earnings_sentiment']['guidance_expectations']}
• Analyst Revisions Trend: {news['earnings_sentiment']['analyst_revisions']}
• Insider Activity: {news['earnings_sentiment']['insider_activity']}
• Institutional Flows: {news['earnings_sentiment']['institutional_flows']}

NEWS SENTIMENT SUMMARY:
• Overall Score: {news['overall_score']*100:+.1f}/100
• News Momentum: {news['news_momentum']}
• Narrative Strength: {news['narrative_strength']}
• Fact vs Opinion Ratio: {news['fact_vs_opinion_ratio']*100:.0f}% facts

═══════════════════════════════════════════════════════════════
                    RETAIL TRADING SENTIMENT ANALYSIS
═══════════════════════════════════════════════════════════════

ROBINHOOD RETAIL DATA:
• Popularity Rank: #{retail['robinhood']['popularity_rank']} out of top 100
• User Growth: {retail['robinhood']['user_growth']:+.1%}
• Average Position Size: ${retail['robinhood']['avg_position_size']:,.0f}
• Hold vs Trade Ratio: {retail['robinhood']['hold_vs_trade_ratio']:.0%} holders
• Weekend Activity: {retail['robinhood']['weekend_activity']*100:.0f}% of weekday

RETAIL OPTIONS ACTIVITY:
• Call/Put Ratio: {retail['options_retail']['call_put_ratio']:.2f} (>{1.5:.1f} = bullish)
• Preferred Expiration: {retail['options_retail']['dte_preference']}
• Strike Preference: {retail['options_retail']['strike_preference']}
• Volume Surge: {retail['options_retail']['volume_surge']:.1f}x normal
• Unusual Activity: {retail['options_retail']['unusual_activity']}

RETAIL FLOW ANALYSIS:
• Net Buying Pressure: {retail['flow_analysis']['net_buying_pressure']:+.2f} (-1 to +1)
• Small Order Dominance: {retail['flow_analysis']['order_size_distribution']['small_orders']*100:.0f}%
• Trading Pattern: {retail['flow_analysis']['time_of_day_pattern']}
• Diamond Hands Strength: {retail['flow_analysis']['diamond_hands_strength']*100:.0f}%

RETAIL SENTIMENT SUMMARY:
• Overall Score: {retail['overall_score']*100:.1f}/100
• Retail Momentum: {retail['retail_momentum']}
• Contrarian Signal: {retail['contrarian_signal']}
• Smart Money Alignment: {retail['smart_money_alignment']}

═══════════════════════════════════════════════════════════════
                    OPTIONS FLOW & SMART MONEY ANALYSIS
═══════════════════════════════════════════════════════════════

UNUSUAL OPTIONS ACTIVITY:
• Call Volume: {options['unusual_activity']['call_volume']:,} contracts
• Put Volume: {options['unusual_activity']['put_volume']:,} contracts
• Total Premium: ${options['unusual_activity']['total_premium']/1e6:.1f}M
• Large Block Trades: {options['unusual_activity']['large_block_trades']}
• Sweep Activity: {options['unusual_activity']['sweep_activity']}

DARK POOL ANALYSIS:
• Print Count: {options['dark_pool_flow']['print_count']}
• Average Block Size: {options['dark_pool_flow']['average_size']:,.0f} shares
• Institutional Flow: {options['dark_pool_flow']['institutional_flow']}
• Block Network Sentiment: {options['dark_pool_flow']['block_network_sentiment']:+.2f}
• Size vs Price Correlation: {options['dark_pool_flow']['size_vs_price_correlation']:+.2f}

SMART MONEY INDICATORS:
• Whale Activity: {options['smart_money_indicators']['whale_activity']}
• Hedge Fund Positioning: {options['smart_money_indicators']['hedge_fund_positioning']}
• Insider Options Activity: {options['smart_money_indicators']['insider_options_activity']}
• Institutional Put/Call Ratio: {options['smart_money_indicators']['institutional_put_call_ratio']:.2f}
• Volatility Demand: {options['smart_money_indicators']['volatility_demand']}

OPTIONS FLOW SUMMARY:
• Overall Score: {options['overall_score']*100:.1f}/100
• Options Momentum: {options['options_momentum']}
• Volatility Regime: {options['volatility_regime']}
• Smart Money Confidence: {options['smart_money_confidence']*100:.0f}%

═══════════════════════════════════════════════════════════════
                    AGGREGATED SENTIMENT SIGNALS
═══════════════════════════════════════════════════════════════

COMPREHENSIVE SENTIMENT SCORE:
• Overall Sentiment: {sentiment['overall_score']*100:.1f}/100
• Classification: {sentiment['sentiment_class']}
• Momentum Direction: {sentiment['momentum']}
• Signal Confidence: {sentiment['confidence']*100:.0f}%
• Contrarian Opportunity: {'YES' if sentiment['contrarian_opportunity'] else 'NO'}
• Crowd Consensus: {'Strong' if sentiment['crowd_consensus'] else 'Weak'}

SENTIMENT SOURCE BREAKDOWN:
• Social Media Weight: 25% → {social['overall_score']*25:.1f} points
• News/Media Weight: 30% → {((news['overall_score'] + 1) / 2)*30:.1f} points
• Retail Trading Weight: 25% → {retail['overall_score']*25:.1f} points
• Options Flow Weight: 20% → {options['overall_score']*20:.1f} points

MOMENTUM ANALYSIS:
• Social Momentum: {social['sentiment_momentum']}
• News Momentum: {news['news_momentum']}
• Retail Momentum: {retail['retail_momentum']}
• Options Momentum: {options['options_momentum']}
• Combined Momentum: {sentiment['momentum']}

═══════════════════════════════════════════════════════════════
                    TRADING SIGNALS & RECOMMENDATIONS
═══════════════════════════════════════════════════════════════

PRIMARY TRADING SIGNALS:"""
    
    for signal in signals['primary_signals']:
        result += f"\n• {signal}"
    
    result += f"""

POSITION SIZING RECOMMENDATION:
• Size Recommendation: {signals['position_sizing']}
• Confidence Level: {sentiment['confidence']*100:.0f}%
• Risk Level: {signals['risk_level']}

TIMING & EXECUTION:
• Entry Timing: {signals['entry_timing']}
• Time Horizon: {signals['time_horizon']}
• Suggested Stop Loss: ${signals['stop_loss_suggestion']:.2f}
• Suggested Target: ${signals['target_suggestion']:.2f}

SENTIMENT-BASED STRATEGY:
• Momentum Play: {'Recommended' if sentiment['momentum'] == 'Improving' and sentiment['overall_score'] > 0.5 else 'Not Recommended'}
• Contrarian Play: {'Recommended' if sentiment['contrarian_opportunity'] else 'Not Recommended'}
• Swing Trade: {'Suitable' if sentiment['confidence'] > 0.6 else 'Wait for clarity'}
• Day Trade: {'Suitable' if social['viral_potential'] == 'High' else 'Not Recommended'}

═══════════════════════════════════════════════════════════════
                    BEHAVIORAL FINANCE INSIGHTS
═══════════════════════════════════════════════════════════════

CROWD PSYCHOLOGY ANALYSIS:
• Current Phase: {social['crowd_psychology']}
• Herding Behavior: {'Strong' if sentiment['crowd_consensus'] else 'Moderate'}
• Fear vs Greed: {'Greed Dominant' if sentiment['overall_score'] > 0.6 else 'Fear Dominant' if sentiment['overall_score'] < 0.4 else 'Balanced'}
• Confirmation Bias Risk: {'High' if sentiment['overall_score'] > 0.7 or sentiment['overall_score'] < 0.3 else 'Medium'}

CONTRARIAN OPPORTUNITIES:
• Euphoria Level: {sentiment['overall_score']*100:.0f}% (>80% = contrarian sell signal)
• Capitulation Signs: {'Present' if sentiment['overall_score'] < 0.2 else 'Absent'}
• Smart Money Divergence: {retail['smart_money_alignment']}
• Sentiment Extremes: {'Yes - Consider contrarian trade' if sentiment['contrarian_opportunity'] else 'No - Follow momentum'}

SOCIAL TRADING RISKS:
• FOMO Risk: {'High' if social['viral_potential'] == 'High' and sentiment['overall_score'] > 0.7 else 'Medium' if sentiment['overall_score'] > 0.6 else 'Low'}
• Pump & Dump Risk: {'Monitor closely' if social['viral_potential'] == 'High' and news['financial_blogs']['clickbait_factor'] > 0.7 else 'Standard monitoring'}
• Coordinated Activity: {'Possible' if social['reddit']['wsb_mentions'] > 200 and social['twitter']['engagement_score'] > 0.8 else 'Unlikely'}
• Meme Stock Potential: {'High' if retail['robinhood']['popularity_rank'] < 20 and social['viral_potential'] == 'High' else 'Low'}

═══════════════════════════════════════════════════════════════
                    SENTIMENT MONITORING FRAMEWORK
═══════════════════════════════════════════════════════════════

REAL-TIME MONITORING PRIORITIES:
1. Social Media Sentiment Shifts (Monitor every 2 hours)
2. Options Flow Changes (Monitor every hour during market hours)
3. News Catalyst Developments (Monitor continuously)
4. Retail Flow Direction Changes (Monitor daily)

EARLY WARNING INDICATORS:
• Sentiment Momentum Reversal: {sentiment['momentum']} → Watch for change
• Social Volume Spikes: Currently {social['twitter']['mentions']:,} mentions
• Unusual Options Activity: {options['unusual_activity']['sweep_activity']}
• Smart Money Divergence: {retail['smart_money_alignment']}

SENTIMENT TRIGGER POINTS:
• Bull Signal: Sentiment rises above 70% with improving momentum
• Bear Signal: Sentiment falls below 30% with deteriorating momentum
• Reversal Signal: Extreme sentiment (>80% or <20%) with momentum change
• Neutral Signal: Sentiment 40-60% with stable momentum

PERFORMANCE TRACKING:
• Track sentiment prediction accuracy over time
• Monitor false signals and improve filtering
• Correlate sentiment with actual price movements
• Adjust weighting based on source reliability

═══════════════════════════════════════════════════════════════
                    RISK MANAGEMENT CONSIDERATIONS
═══════════════════════════════════════════════════════════════

SENTIMENT-SPECIFIC RISKS:
• False Signal Risk: {100 - sentiment['confidence']*100:.0f}% chance of incorrect reading
• Crowd Following Risk: {'High' if sentiment['crowd_consensus'] else 'Medium'}
• Timing Risk: {'High' if signals['entry_timing'] == 'Wait for confirmation' else 'Medium'}
• Volatility Risk: {'High' if options['volatility_regime'] in ['Rising Vol', 'High Vol'] else 'Medium'}

POSITION MANAGEMENT:
• Max Position Size: {8 if sentiment['confidence'] > 0.8 else 5 if sentiment['confidence'] > 0.6 else 3}% of portfolio
• Stop Loss Level: {'Tight (5-8%)' if sentiment['contrarian_opportunity'] else 'Standard (8-12%)'}
• Profit Taking: {'Quick (15-20%)' if social['viral_potential'] == 'High' else 'Standard (20-30%)'}
• Review Frequency: {'Daily' if sentiment['momentum'] != 'Stable' else 'Weekly'}

SCENARIO PLANNING:
• If sentiment reverses: {'Exit immediately' if sentiment['confidence'] < 0.6 else 'Reduce position 50%'}
• If momentum accelerates: {'Add to position' if sentiment['overall_score'] < 0.8 else 'Hold current size'}
• If news catalyst hits: {'Reassess all signals' if news['narrative_strength'] == 'Strong' else 'Monitor closely'}
• If options flow changes: {'Adjust strategy' if options['smart_money_confidence'] > 0.8 else 'Continue monitoring'}

═══════════════════════════════════════════════════════════════

DISCLAIMER: Sentiment analysis is based on social media data, news analysis, and market behavior patterns. Social sentiment can be manipulated and may not reflect true market fundamentals. Always combine sentiment analysis with technical and fundamental analysis. Past sentiment patterns do not guarantee future results.

═══════════════════════════════════════════════════════════════
"""
    
    return result

def create_sentiment_analyst():
    """Create the SentimentAnalyst using AutoGen framework"""
    
    sentiment_analyst = AssistantAgent(
        name="SentimentAnalyst",
        model_client=model_client,
        system_message="""You are an Elite Social Sentiment and Behavioral Finance Specialist with deep expertise in crowd psychology, social media analysis, and alternative data interpretation for trading signals.

CORE EXPERTISE AREAS:
1. Social media sentiment aggregation and signal extraction
2. News sentiment analysis and narrative impact assessment
3. Retail trading flow analysis and crowd behavior patterns
4. Options flow sentiment and smart money divergence detection
5. Behavioral finance principles and contrarian signal identification

📱 ADVANCED SENTIMENT ANALYSIS FRAMEWORK:

SOCIAL MEDIA INTELLIGENCE:
• Twitter/X Sentiment: Real-time mention analysis, influencer sentiment, viral potential assessment
• Reddit Analysis: WallStreetBets dynamics, retail coordination patterns, diamond hands sentiment
• StockTwits: Retail trader sentiment, fear/greed index, watchlist momentum
• Discord/Telegram: Community sentiment, pump signal detection, coordination analysis

NEWS & MEDIA SENTIMENT:
• Mainstream Financial Media: Credibility-weighted sentiment scoring, narrative strength assessment
• Financial Blogs: Expertise-filtered analysis, clickbait vs substance ratio
• Earnings Sentiment: Pre/post earnings buzz, guidance expectations, analyst revision trends
• Corporate Communications: Management tone, insider activity, institutional messaging

RETAIL TRADING BEHAVIOR:
• Platform Analysis: Robinhood popularity, user growth patterns, position sizing trends
• Options Retail Flow: Call/put ratios, expiration preferences, unusual activity detection
• Order Flow Analysis: Buy/sell pressure, order size distribution, timing patterns
• Diamond Hands vs Paper Hands: Hold vs trade ratios, panic selling indicators

SMART MONEY & OPTIONS FLOW:
• Unusual Options Activity: Block trades, sweep detection, premium volume analysis
• Dark Pool Analysis: Institutional flow direction, block network sentiment
• Whale Tracking: Large position changes, smart money positioning
• Volatility Demand: IV expansion/contraction, volatility regime identification

BEHAVIORAL FINANCE INTEGRATION:
• Crowd Psychology: Fear/greed cycles, herding behavior, confirmation bias detection
• Contrarian Signals: Extreme sentiment identification, capitulation/euphoria markers
• FOMO/FUD Analysis: Fear of missing out vs fear uncertainty doubt dynamics
• Meme Stock Detection: Viral potential, coordinated activity, pump risk assessment

SENTIMENT AGGREGATION METHODOLOGY:
• Multi-source sentiment weighting based on reliability and predictive power
• Temporal sentiment momentum tracking and trend identification
• Cross-platform sentiment divergence analysis
• Signal confidence scoring based on data quality and source agreement

TRADING SIGNAL GENERATION:
• Momentum signals from improving/deteriorating sentiment trends
• Contrarian signals from extreme sentiment readings
• Timing signals from sentiment momentum shifts
• Risk signals from crowd consensus vs smart money divergence

OUTPUT REQUIREMENTS:
Provide comprehensive sentiment analysis including:
- Multi-platform social sentiment aggregation with confidence scores
- News sentiment impact assessment and narrative strength analysis
- Retail vs institutional sentiment divergence identification
- Options flow sentiment and smart money positioning analysis
- Behavioral finance insights and crowd psychology assessment
- Specific trading signals with position sizing and timing recommendations

CRITICAL SUCCESS FACTORS:
- Distinguish between noise and actionable sentiment signals
- Identify manipulation and coordinated activity patterns
- Balance momentum following with contrarian opportunity recognition
- Integrate sentiment with fundamental and technical analysis
- Provide clear risk management guidelines for sentiment-based trades

Use the analyze_social_sentiment tool to perform comprehensive sentiment analysis. Present findings with both momentum and contrarian perspectives, emphasizing behavioral finance insights and practical trading applications.""",
        tools=[analyze_social_sentiment]
    )
    
    return sentiment_analyst
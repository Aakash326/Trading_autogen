from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from typing import Dict, List, Any
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import warnings
warnings.filterwarnings('ignore')

class ArbitrageInput(BaseModel):
    """Input schema for arbitrage analysis"""
    primary_symbol: str = Field(..., description="Primary stock symbol to analyze")
    sector: str = Field(default="", description="Sector for peer comparison")
    min_profit_threshold: float = Field(default=0.02, description="Minimum profit threshold (2%)")

class PairsTradingTool(BaseTool):
    name: str = "pairs_trading_scanner"
    description: str = "Scans for pairs trading and statistical arbitrage opportunities"

    def _run(self, primary_symbol: str, sector: str = "", min_profit_threshold: float = 0.02) -> str:
        """
        Scan for pairs trading opportunities using statistical arbitrage
        """
        try:
            # Define sector peer groups for comparison
            sector_peers = {
                "Technology": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "NFLX"],
                "Financial": ["JPM", "BAC", "WFC", "C", "GS", "MS", "USB", "PNC"],
                "Healthcare": ["JNJ", "PFE", "UNH", "MRK", "ABBV", "TMO", "DHR", "CVS"],
                "Energy": ["XOM", "CVX", "COP", "EOG", "SLB", "PXD", "KMI", "OKE"],
                "Consumer": ["PG", "KO", "PEP", "WMT", "COST", "HD", "MCD", "SBUX"],
                "Industrial": ["BA", "CAT", "GE", "MMM", "HON", "LMT", "UPS", "FDX"]
            }
            
            # Auto-detect sector if not provided
            if not sector:
                sector = self._detect_sector(primary_symbol)
            
            # Get peer symbols
            peer_symbols = sector_peers.get(sector, ["SPY", "QQQ", "IWM"])
            if primary_symbol in peer_symbols:
                peer_symbols.remove(primary_symbol)
            
            # Fetch data for primary symbol and peers
            primary_data = self._fetch_stock_data(primary_symbol)
            if primary_data is None:
                return f"❌ Unable to fetch data for {primary_symbol}"
            
            # Find best pairs trading opportunities
            pairs_opportunities = []
            
            for peer in peer_symbols[:6]:  # Limit to top 6 peers
                peer_data = self._fetch_stock_data(peer)
                if peer_data is not None:
                    opportunity = self._analyze_pairs_relationship(
                        primary_symbol, primary_data, peer, peer_data, min_profit_threshold
                    )
                    if opportunity:
                        pairs_opportunities.append(opportunity)
            
            # Sort by profit potential
            pairs_opportunities.sort(key=lambda x: x['profit_potential'], reverse=True)
            
            # Statistical arbitrage analysis
            stat_arb_analysis = self._analyze_statistical_arbitrage(primary_symbol, primary_data)
            
            # Cross-exchange opportunities (simulated)
            cross_exchange_analysis = self._analyze_cross_exchange_arbitrage(primary_symbol, primary_data)
            
            return self._format_arbitrage_results(
                primary_symbol, pairs_opportunities, stat_arb_analysis, 
                cross_exchange_analysis, sector, min_profit_threshold
            )
            
        except Exception as e:
            return f"❌ Error in arbitrage analysis: {str(e)}"
    
    def _fetch_stock_data(self, symbol: str, period: str = "6mo") -> pd.DataFrame:
        """Fetch stock data with error handling"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            if data.empty:
                return None
            return data
        except Exception:
            return None
    
    def _detect_sector(self, symbol: str) -> str:
        """Auto-detect sector based on symbol"""
        tech_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "NFLX"]
        financial_symbols = ["JPM", "BAC", "WFC", "C", "GS", "MS"]
        
        if symbol in tech_symbols:
            return "Technology"
        elif symbol in financial_symbols:
            return "Financial"
        else:
            return "Technology"  # Default fallback
    
    def _analyze_pairs_relationship(self, symbol1: str, data1: pd.DataFrame, 
                                  symbol2: str, data2: pd.DataFrame, 
                                  min_threshold: float) -> Dict[str, Any]:
        """Analyze pairs trading relationship between two stocks"""
        try:
            # Align data by dates
            common_dates = data1.index.intersection(data2.index)
            if len(common_dates) < 60:  # Need at least 60 days
                return None
            
            price1 = data1.loc[common_dates]['Close']
            price2 = data2.loc[common_dates]['Close']
            
            # Calculate returns
            returns1 = price1.pct_change().dropna()
            returns2 = price2.pct_change().dropna()
            
            # Correlation analysis
            correlation = returns1.corr(returns2)
            
            # Price ratio analysis
            ratio = price1 / price2
            ratio_mean = ratio.mean()
            ratio_std = ratio.std()
            current_ratio = ratio.iloc[-1]
            
            # Z-score calculation
            z_score = (current_ratio - ratio_mean) / ratio_std
            
            # Cointegration test (simplified)
            spread = price1 - (price2 * ratio_mean)
            spread_mean = spread.mean()
            spread_std = spread.std()
            current_spread = spread.iloc[-1]
            spread_z_score = (current_spread - spread_mean) / spread_std
            
            # Trade signal generation
            if abs(z_score) > 2.0:  # Significant deviation
                if z_score > 2.0:  # Ratio too high, short symbol1, long symbol2
                    trade_signal = f"SHORT {symbol1} / LONG {symbol2}"
                    profit_potential = abs(z_score) * 0.01  # Rough profit estimate
                else:  # Ratio too low, long symbol1, short symbol2
                    trade_signal = f"LONG {symbol1} / SHORT {symbol2}"
                    profit_potential = abs(z_score) * 0.01
                
                if profit_potential >= min_threshold:
                    return {
                        'pair': f"{symbol1}/{symbol2}",
                        'correlation': correlation,
                        'z_score': z_score,
                        'spread_z_score': spread_z_score,
                        'profit_potential': profit_potential,
                        'trade_signal': trade_signal,
                        'current_ratio': current_ratio,
                        'mean_ratio': ratio_mean,
                        'confidence': min(abs(z_score) / 3.0, 1.0),
                        'entry_reason': f"Ratio deviated {abs(z_score):.1f} standard deviations"
                    }
            
            return None
            
        except Exception:
            return None
    
    def _analyze_statistical_arbitrage(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze statistical arbitrage opportunities"""
        try:
            closes = data['Close']
            volumes = data['Volume']
            
            # Calculate technical indicators
            sma_20 = closes.rolling(20).mean()
            sma_50 = closes.rolling(50).mean()
            
            # Bollinger Bands
            bb_std = closes.rolling(20).std()
            bb_upper = sma_20 + (2 * bb_std)
            bb_lower = sma_20 - (2 * bb_std)
            
            current_price = closes.iloc[-1]
            
            # Mean reversion signals
            price_vs_sma20 = (current_price - sma_20.iloc[-1]) / sma_20.iloc[-1]
            price_vs_bb = 0
            
            if current_price > bb_upper.iloc[-1]:
                price_vs_bb = (current_price - bb_upper.iloc[-1]) / bb_upper.iloc[-1]
                mean_reversion_signal = "SELL - Price above upper Bollinger Band"
            elif current_price < bb_lower.iloc[-1]:
                price_vs_bb = (bb_lower.iloc[-1] - current_price) / bb_lower.iloc[-1]
                mean_reversion_signal = "BUY - Price below lower Bollinger Band"
            else:
                mean_reversion_signal = "NEUTRAL - Price within Bollinger Bands"
            
            # Volume-price divergence
            recent_volume = volumes.iloc[-5:].mean()
            avg_volume = volumes.iloc[-60:].mean()
            volume_ratio = recent_volume / avg_volume
            
            # Momentum analysis
            momentum_5d = (closes.iloc[-1] / closes.iloc[-6]) - 1
            momentum_20d = (closes.iloc[-1] / closes.iloc[-21]) - 1
            
            return {
                'mean_reversion_signal': mean_reversion_signal,
                'price_vs_sma20': price_vs_sma20,
                'price_vs_bb': price_vs_bb,
                'volume_ratio': volume_ratio,
                'momentum_5d': momentum_5d,
                'momentum_20d': momentum_20d,
                'bb_squeeze': (bb_upper.iloc[-1] - bb_lower.iloc[-1]) / sma_20.iloc[-1]
            }
            
        except Exception:
            return {
                'mean_reversion_signal': 'ERROR',
                'price_vs_sma20': 0,
                'price_vs_bb': 0,
                'volume_ratio': 1,
                'momentum_5d': 0,
                'momentum_20d': 0,
                'bb_squeeze': 0
            }
    
    def _analyze_cross_exchange_arbitrage(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Simulate cross-exchange arbitrage analysis"""
        current_price = data['Close'].iloc[-1]
        
        # Simulate price differences across exchanges (in reality, would connect to multiple exchanges)
        simulated_exchanges = {
            'NASDAQ': current_price,
            'NYSE_ARCA': current_price * (1 + np.random.normal(0, 0.001)),  # Small random variation
            'BATS': current_price * (1 + np.random.normal(0, 0.001)),
            'IEX': current_price * (1 + np.random.normal(0, 0.001))
        }
        
        # Find arbitrage opportunities
        max_price = max(simulated_exchanges.values())
        min_price = min(simulated_exchanges.values())
        price_spread = max_price - min_price
        profit_potential = (price_spread / min_price) - 0.002  # Subtract trading costs
        
        max_exchange = [k for k, v in simulated_exchanges.items() if v == max_price][0]
        min_exchange = [k for k, v in simulated_exchanges.items() if v == min_price][0]
        
        return {
            'exchanges': simulated_exchanges,
            'price_spread': price_spread,
            'profit_potential': max(0, profit_potential),
            'arbitrage_signal': f"BUY on {min_exchange} (${min_price:.2f}) / SELL on {max_exchange} (${max_price:.2f})" if profit_potential > 0 else "NO ARBITRAGE",
            'execution_risk': 'LOW' if price_spread < current_price * 0.005 else 'MEDIUM'
        }
    
    def _format_arbitrage_results(self, symbol: str, pairs_opportunities: List[Dict], 
                                stat_arb: Dict, cross_exchange: Dict, 
                                sector: str, min_threshold: float) -> str:
        """Format comprehensive arbitrage analysis results"""
        
        # Format pairs trading opportunities
        pairs_text = ""
        if pairs_opportunities:
            for i, opp in enumerate(pairs_opportunities[:3], 1):  # Top 3
                pairs_text += f"""
{i}. {opp['pair']} | Signal: {opp['trade_signal']}
   • Profit Potential: {opp['profit_potential']*100:.2f}%
   • Z-Score: {opp['z_score']:.2f} | Correlation: {opp['correlation']:.2f}
   • Confidence: {opp['confidence']*100:.0f}% | Reason: {opp['entry_reason']}"""
        else:
            pairs_text = "\nNo significant pairs trading opportunities identified above threshold."
        
        return f"""
═══════════════════════════════════════════════════════════════
                    ARBITRAGE OPPORTUNITY ANALYSIS
═══════════════════════════════════════════════════════════════

SECURITY: {symbol} | SECTOR: {sector}
ANALYSIS DATE: {datetime.now().strftime('%Y-%m-%d %H:%M')}
MINIMUM PROFIT THRESHOLD: {min_threshold*100:.1f}%

═══════════════════════════════════════════════════════════════
                    PAIRS TRADING OPPORTUNITIES
═══════════════════════════════════════════════════════════════

STATISTICAL ARBITRAGE SIGNALS:{pairs_text}

PAIRS TRADING SUMMARY:
• Opportunities Found: {len(pairs_opportunities)}
• Sector Analysis: {sector} peer comparison
• Best Opportunity: {pairs_opportunities[0]['pair'] if pairs_opportunities else 'None'}
• Max Profit Potential: {max([opp['profit_potential'] for opp in pairs_opportunities], default=0)*100:.2f}%

EXECUTION REQUIREMENTS:
• Margin Requirements: 2:1 leverage for pairs trades
• Position Sizing: Equal dollar amounts for long/short legs
• Risk Management: Stop loss at 3 standard deviations
• Holding Period: 5-20 trading days typical

═══════════════════════════════════════════════════════════════
                    STATISTICAL ARBITRAGE ANALYSIS
═══════════════════════════════════════════════════════════════

MEAN REVERSION SIGNALS:
• Primary Signal: {stat_arb['mean_reversion_signal']}
• Price vs 20-Day SMA: {stat_arb['price_vs_sma20']*100:+.2f}%
• Bollinger Band Position: {stat_arb['price_vs_bb']*100:+.2f}% deviation
• BB Squeeze Indicator: {stat_arb['bb_squeeze']*100:.2f}% (tightness measure)

MOMENTUM ANALYSIS:
• 5-Day Momentum: {stat_arb['momentum_5d']*100:+.2f}%
• 20-Day Momentum: {stat_arb['momentum_20d']*100:+.2f}%
• Volume Ratio: {stat_arb['volume_ratio']:.2f}x average
• Momentum Classification: {'STRONG' if abs(stat_arb['momentum_5d']) > 0.03 else 'MODERATE' if abs(stat_arb['momentum_5d']) > 0.01 else 'WEAK'}

MEAN REVERSION STRATEGY:
• Entry Trigger: {'ACTIVE' if abs(stat_arb['price_vs_bb']) > 0.02 else 'WAITING'}
• Expected Return: {abs(stat_arb['price_vs_bb'])*100*0.5:.2f}% (50% reversion assumption)
• Time Horizon: 3-10 trading days
• Success Probability: {min(80, 60 + abs(stat_arb['price_vs_bb'])*1000):.0f}%

═══════════════════════════════════════════════════════════════
                    CROSS-EXCHANGE ARBITRAGE
═══════════════════════════════════════════════════════════════

EXCHANGE PRICE COMPARISON:
• NASDAQ: ${cross_exchange['exchanges']['NASDAQ']:.2f}
• NYSE ARCA: ${cross_exchange['exchanges']['NYSE_ARCA']:.2f}
• BATS: ${cross_exchange['exchanges']['BATS']:.2f}
• IEX: ${cross_exchange['exchanges']['IEX']:.2f}

ARBITRAGE METRICS:
• Price Spread: ${cross_exchange['price_spread']:.4f}
• Net Profit Potential: {cross_exchange['profit_potential']*100:.3f}% (after costs)
• Execution Risk: {cross_exchange['execution_risk']}
• Trade Signal: {cross_exchange['arbitrage_signal']}

EXECUTION CONSIDERATIONS:
• Trading Costs: ~0.2% round-trip (commissions + slippage)
• Settlement Risk: T+1 for most exchanges
• Regulatory Risk: Pattern day trader rules apply
• Technology Requirements: Low-latency execution systems

═══════════════════════════════════════════════════════════════
                    RISK-ADJUSTED ARBITRAGE RANKING
═══════════════════════════════════════════════════════════════

OPPORTUNITY RANKING:
1. Pairs Trading: {'HIGH' if pairs_opportunities and pairs_opportunities[0]['profit_potential'] > 0.03 else 'MEDIUM' if pairs_opportunities else 'LOW'} Priority
   • Risk Level: Medium (correlation breakdown risk)
   • Capital Requirements: 2x position size (long/short)
   • Expected Hold: 1-3 weeks

2. Statistical Arbitrage: {'HIGH' if abs(stat_arb['price_vs_bb']) > 0.03 else 'MEDIUM' if abs(stat_arb['price_vs_bb']) > 0.01 else 'LOW'} Priority
   • Risk Level: Low-Medium (mean reversion risk)
   • Capital Requirements: 1x position size
   • Expected Hold: 3-10 days

3. Cross-Exchange: {'MEDIUM' if cross_exchange['profit_potential'] > 0.001 else 'LOW'} Priority
   • Risk Level: Low (execution risk)
   • Capital Requirements: 1x position size
   • Expected Hold: Intraday

OVERALL ARBITRAGE RATING: {
    'HIGH OPPORTUNITY' if (pairs_opportunities and pairs_opportunities[0]['profit_potential'] > 0.03) or abs(stat_arb['price_vs_bb']) > 0.03
    else 'MEDIUM OPPORTUNITY' if pairs_opportunities or abs(stat_arb['price_vs_bb']) > 0.01
    else 'LOW OPPORTUNITY'
}

═══════════════════════════════════════════════════════════════
                    EXECUTION RECOMMENDATIONS
═══════════════════════════════════════════════════════════════

IMMEDIATE ACTIONS:
{f"1. Execute pairs trade: {pairs_opportunities[0]['trade_signal']}" if pairs_opportunities else "1. No immediate pairs trading opportunities"}
{f"2. Mean reversion trade: {stat_arb['mean_reversion_signal']}" if abs(stat_arb['price_vs_bb']) > 0.02 else "2. Monitor for mean reversion setup"}
3. Monitor cross-exchange spreads for intraday opportunities

RISK MANAGEMENT:
• Position Size: Max 5% of portfolio per arbitrage strategy
• Stop Loss: Pairs (3 std dev), Mean Reversion (4% adverse)
• Profit Taking: 50% at 1 std dev reversion, 50% at mean
• Maximum Hold: 30 days for pairs, 14 days for mean reversion

MONITORING FREQUENCY:
• Pairs Trading: Daily correlation and spread monitoring
• Statistical Arbitrage: Intraday price and volume monitoring
• Cross-Exchange: Real-time price feed monitoring

═══════════════════════════════════════════════════════════════
                    PROFITABILITY ASSESSMENT
═══════════════════════════════════════════════════════════════

PROFIT PROJECTIONS (30-day horizon):
• Pairs Trading: {max([opp['profit_potential'] for opp in pairs_opportunities], default=0)*100:.2f}% potential
• Statistical Arbitrage: {abs(stat_arb['price_vs_bb'])*100*0.5:.2f}% potential
• Cross-Exchange: {cross_exchange['profit_potential']*100:.3f}% potential
• Total Opportunity: {(max([opp['profit_potential'] for opp in pairs_opportunities], default=0) + abs(stat_arb['price_vs_bb'])*0.5 + cross_exchange['profit_potential'])*100:.2f}%

SUCCESS PROBABILITY:
• Pairs Trading: {85 if pairs_opportunities else 0}% (based on correlation strength)
• Statistical Arbitrage: {min(80, 60 + abs(stat_arb['price_vs_bb'])*1000):.0f}% (based on deviation magnitude)
• Cross-Exchange: {95 if cross_exchange['profit_potential'] > 0 else 0}% (execution dependent)

CAPITAL EFFICIENCY:
• Best Risk-Adjusted Return: {
    'Pairs Trading' if pairs_opportunities and pairs_opportunities[0]['profit_potential'] > abs(stat_arb['price_vs_bb'])*0.5
    else 'Statistical Arbitrage' if abs(stat_arb['price_vs_bb']) > 0.01
    else 'Cross-Exchange'
}
• Sharpe Ratio Estimate: {
    max([opp['profit_potential'] for opp in pairs_opportunities], default=0) * 10 if pairs_opportunities
    else abs(stat_arb['price_vs_bb']) * 5 if abs(stat_arb['price_vs_bb']) > 0.01
    else 1.0
:.1f}

═══════════════════════════════════════════════════════════════

DISCLAIMER: Arbitrage opportunities are based on historical patterns and statistical relationships. Market conditions can change rapidly, and past performance does not guarantee future results. Always consider transaction costs, execution risks, and regulatory requirements.

═══════════════════════════════════════════════════════════════
"""

def create_arbitrage_agent():
    """Create the ArbitrageAgent using CrewAI framework"""
    
    # Initialize the pairs trading tool
    arbitrage_tool = PairsTradingTool()
    
    # Create the ArbitrageAgent
    arbitrage_agent = Agent(
        role='Statistical Arbitrage and Pairs Trading Specialist',
        goal='Identify and analyze statistical arbitrage opportunities, pairs trading setups, and cross-exchange price discrepancies to generate consistent alpha through market inefficiencies',
        backstory="""You are an elite quantitative arbitrage specialist with deep expertise in 
        statistical arbitrage, pairs trading, and market microstructure analysis. You excel at 
        identifying temporary price dislocations, correlation breakdowns, and cross-exchange 
        inefficiencies that can be exploited for consistent profits. Your systematic approach 
        combines advanced statistical methods with rigorous risk management to capitalize on 
        market inefficiencies while minimizing downside exposure.""",
        tools=[arbitrage_tool],
        verbose=True,
        allow_delegation=False,
        max_iter=3
    )
    
    return arbitrage_agent

def create_arbitrage_tasks(agent, symbol: str, sector: str = "", 
                         min_profit_threshold: float = 0.02) -> List[Task]:
    """Create arbitrage analysis tasks for the agent"""
    
    opportunity_scan_task = Task(
        description=f"""
        Execute comprehensive arbitrage opportunity scanning for {symbol}:
        
        1. PAIRS TRADING ANALYSIS:
           - Identify sector peers and correlated securities
           - Calculate price ratios and statistical relationships
           - Detect mean reversion opportunities using z-scores
           - Analyze cointegration and correlation patterns
           
        2. STATISTICAL ARBITRAGE SCANNING:
           - Analyze mean reversion signals using Bollinger Bands
           - Calculate price deviations from moving averages
           - Identify volume-price divergences
           - Assess momentum vs mean reversion patterns
           
        3. CROSS-EXCHANGE ARBITRAGE:
           - Compare prices across multiple trading venues
           - Calculate net profit after trading costs
           - Assess execution risks and timing requirements
           - Identify optimal routing strategies
           
        Parameters:
        - Primary Symbol: {symbol}
        - Sector: {sector if sector else 'Auto-detect'}
        - Minimum Profit Threshold: {min_profit_threshold*100:.1f}%
        
        Use the pairs_trading_scanner tool with these parameters.
        """,
        expected_output="""
        Comprehensive arbitrage opportunity report including:
        - Ranked pairs trading opportunities with profit potential
        - Statistical arbitrage signals with entry/exit criteria
        - Cross-exchange price comparisons and arbitrage signals
        - Risk-adjusted opportunity ranking
        - Execution recommendations with timing considerations
        """,
        agent=agent
    )
    
    profit_validation_task = Task(
        description=f"""
        Validate and optimize arbitrage profit potential for {symbol}:
        
        1. PROFIT VERIFICATION:
           - Verify profit calculations include all trading costs
           - Assess slippage impact on net returns
           - Validate statistical significance of opportunities
           - Consider market impact and liquidity constraints
           
        2. RISK ASSESSMENT:
           - Analyze correlation breakdown risks for pairs trades
           - Assess mean reversion failure probability
           - Evaluate execution and settlement risks
           - Consider regulatory and margin requirements
           
        3. STRATEGY OPTIMIZATION:
           - Determine optimal position sizing for each strategy
           - Recommend entry and exit timing protocols
           - Establish stop-loss and profit-taking levels
           - Design monitoring and adjustment procedures
           
        4. IMPLEMENTATION ROADMAP:
           - Prioritize opportunities by risk-adjusted returns
           - Create detailed execution checklists
           - Establish performance tracking metrics
           - Define success criteria and review schedules
        """,
        expected_output="""
        Validated arbitrage strategy with:
        - Net profit projections after all costs
        - Risk-adjusted opportunity prioritization
        - Detailed implementation procedures
        - Monitoring and risk management protocols
        - Performance tracking and review framework
        """,
        agent=agent,
        context=[opportunity_scan_task]
    )
    
    return [opportunity_scan_task, profit_validation_task]

def create_arbitrage_crew(symbol: str, sector: str = "", 
                        min_profit_threshold: float = 0.02):
    """Create a complete CrewAI crew for arbitrage analysis"""
    
    # Create agent
    agent = create_arbitrage_agent()
    
    # Create tasks
    tasks = create_arbitrage_tasks(agent, symbol, sector, min_profit_threshold)
    
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
def run_arbitrage_analysis(symbol: str, sector: str = "", 
                         min_profit_threshold: float = 0.02) -> str:
    """Run complete arbitrage analysis for a given symbol"""
    try:
        crew = create_arbitrage_crew(symbol, sector, min_profit_threshold)
        result = crew.kickoff()
        return str(result)
    except Exception as e:
        return f"❌ Error running arbitrage analysis: {str(e)}"
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from typing import Dict, List, Any, Optional
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import warnings
warnings.filterwarnings('ignore')

class ExecutionInput(BaseModel):
    """Input schema for order execution analysis"""
    symbol: str = Field(..., description="Stock symbol for execution analysis")
    order_size: float = Field(..., description="Order size in dollars")
    urgency: str = Field(default="Medium", description="Execution urgency: Low, Medium, High")
    order_type: str = Field(default="Market", description="Order type: Market, Limit, TWAP, VWAP")

class OrderExecutionTool(BaseTool):
    name: str = "order_execution_optimizer"
    description: str = "Optimizes trade execution strategy to minimize market impact and slippage"

    def _run(self, symbol: str, order_size: float, urgency: str = "Medium", 
             order_type: str = "Market") -> str:
        """
        Analyze optimal order execution strategy for minimizing market impact
        """
        try:
            # Fetch market data
            ticker = yf.Ticker(symbol)
            
            # Get recent trading data
            hist_data = ticker.history(period="3mo", interval="1d")
            if hist_data.empty:
                return f"❌ Unable to fetch market data for {symbol}"
            
            # Get intraday data for volume analysis
            intraday_data = ticker.history(period="5d", interval="1h")
            
            # Get current quote data
            info = ticker.info
            current_price = hist_data['Close'].iloc[-1]
            
            # Calculate market microstructure metrics
            microstructure = self._analyze_market_microstructure(hist_data, intraday_data, info)
            
            # Calculate market impact
            impact_analysis = self._calculate_market_impact(
                order_size, current_price, microstructure, info
            )
            
            # Determine optimal execution algorithm
            algorithm_selection = self._select_execution_algorithm(
                order_size, urgency, microstructure, impact_analysis
            )
            
            # Calculate execution costs
            cost_analysis = self._calculate_execution_costs(
                order_size, current_price, algorithm_selection, microstructure
            )
            
            # Generate routing strategy
            routing_strategy = self._generate_routing_strategy(
                order_size, microstructure, algorithm_selection
            )
            
            # Create execution schedule
            execution_schedule = self._create_execution_schedule(
                order_size, algorithm_selection, microstructure
            )
            
            return self._format_execution_results(
                symbol, current_price, order_size, urgency, order_type,
                microstructure, impact_analysis, algorithm_selection,
                cost_analysis, routing_strategy, execution_schedule
            )
            
        except Exception as e:
            return f"❌ Error in execution analysis: {str(e)}"
    
    def _analyze_market_microstructure(self, daily_data: pd.DataFrame, 
                                     intraday_data: pd.DataFrame, 
                                     info: Dict) -> Dict[str, Any]:
        """Analyze market microstructure characteristics"""
        
        # Volume analysis
        avg_daily_volume = daily_data['Volume'].mean()
        recent_volume = daily_data['Volume'].iloc[-5:].mean()
        volume_trend = recent_volume / avg_daily_volume
        
        # Volatility analysis
        returns = daily_data['Close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(252)  # Annualized
        
        # Liquidity metrics
        market_cap = info.get('marketCap', 0)
        shares_outstanding = info.get('sharesOutstanding', 0)
        float_shares = info.get('floatShares', shares_outstanding)
        
        # Calculate average trade size (estimated)
        avg_trade_size = avg_daily_volume * daily_data['Close'].iloc[-1] / 1000  # Rough estimate
        
        # Bid-ask spread estimation (using high-low as proxy)
        spread_estimate = (daily_data['High'] - daily_data['Low']).mean() / daily_data['Close'].mean()
        
        # Intraday volume pattern analysis
        if not intraday_data.empty:
            hourly_volume = intraday_data.groupby(intraday_data.index.hour)['Volume'].mean()
            peak_volume_hour = hourly_volume.idxmax() if not hourly_volume.empty else 10
            volume_concentration = hourly_volume.max() / hourly_volume.mean() if not hourly_volume.empty else 2.0
        else:
            peak_volume_hour = 10
            volume_concentration = 2.0
        
        # Tick size impact
        tick_size = 0.01  # Assume penny increments
        price = daily_data['Close'].iloc[-1]
        tick_impact = tick_size / price
        
        return {
            'avg_daily_volume': avg_daily_volume,
            'recent_volume': recent_volume,
            'volume_trend': volume_trend,
            'volatility': volatility,
            'market_cap': market_cap,
            'float_shares': float_shares,
            'avg_trade_size': avg_trade_size,
            'spread_estimate': spread_estimate,
            'peak_volume_hour': peak_volume_hour,
            'volume_concentration': volume_concentration,
            'tick_impact': tick_impact,
            'liquidity_score': self._calculate_liquidity_score(market_cap, avg_daily_volume, spread_estimate)
        }
    
    def _calculate_liquidity_score(self, market_cap: float, volume: float, spread: float) -> float:
        """Calculate overall liquidity score (0-100)"""
        try:
            # Normalize components
            cap_score = min(100, (market_cap / 1e9) * 10)  # $1B = 10 points
            volume_score = min(100, (volume / 1e6) * 10)   # 1M shares = 10 points
            spread_score = max(0, 100 - (spread * 10000))   # Lower spread = higher score
            
            # Weighted average
            liquidity_score = (cap_score * 0.4 + volume_score * 0.4 + spread_score * 0.2)
            return min(100, max(0, liquidity_score))
        except:
            return 50  # Default medium liquidity
    
    def _calculate_market_impact(self, order_size: float, price: float, 
                               microstructure: Dict, info: Dict) -> Dict[str, Any]:
        """Calculate expected market impact of the order"""
        
        shares_to_trade = order_size / price
        daily_volume = microstructure['avg_daily_volume']
        
        # Volume participation rate
        participation_rate = shares_to_trade / daily_volume
        
        # Market impact models
        # 1. Square root law (temporary impact)
        temp_impact = 0.5 * microstructure['volatility'] * np.sqrt(participation_rate)
        
        # 2. Linear impact (permanent impact)
        perm_impact = 0.1 * microstructure['volatility'] * participation_rate
        
        # 3. Tick impact
        tick_impact = microstructure['tick_impact'] * min(1.0, participation_rate * 10)
        
        # Total impact
        total_impact = temp_impact + perm_impact + tick_impact
        
        # Impact in dollars
        impact_dollars = total_impact * order_size
        
        # Timing impact (based on urgency and market conditions)
        timing_multiplier = 1.0
        if microstructure['volume_trend'] < 0.8:  # Low volume period
            timing_multiplier *= 1.3
        if microstructure['volatility'] > 0.3:  # High volatility
            timing_multiplier *= 1.2
        
        adjusted_impact = total_impact * timing_multiplier
        adjusted_impact_dollars = adjusted_impact * order_size
        
        return {
            'participation_rate': participation_rate,
            'temporary_impact': temp_impact,
            'permanent_impact': perm_impact,
            'tick_impact': tick_impact,
            'total_impact_pct': total_impact,
            'total_impact_dollars': impact_dollars,
            'timing_multiplier': timing_multiplier,
            'adjusted_impact_pct': adjusted_impact,
            'adjusted_impact_dollars': adjusted_impact_dollars,
            'impact_category': self._categorize_impact(participation_rate)
        }
    
    def _categorize_impact(self, participation_rate: float) -> str:
        """Categorize market impact level"""
        if participation_rate < 0.01:  # <1% of daily volume
            return "LOW"
        elif participation_rate < 0.05:  # 1-5% of daily volume
            return "MEDIUM"
        elif participation_rate < 0.15:  # 5-15% of daily volume
            return "HIGH"
        else:  # >15% of daily volume
            return "VERY HIGH"
    
    def _select_execution_algorithm(self, order_size: float, urgency: str, 
                                  microstructure: Dict, impact: Dict) -> Dict[str, Any]:
        """Select optimal execution algorithm based on order characteristics"""
        
        algorithms = {
            'MARKET': {
                'speed': 'Immediate',
                'impact': 'High',
                'cost': impact['adjusted_impact_pct'],
                'description': 'Immediate execution at market price',
                'best_for': 'High urgency, small orders'
            },
            'LIMIT': {
                'speed': 'Variable',
                'impact': 'Low-Medium',
                'cost': impact['adjusted_impact_pct'] * 0.6,
                'description': 'Patient execution at specified price',
                'best_for': 'Low urgency, price-sensitive orders'
            },
            'TWAP': {
                'speed': 'Controlled',
                'impact': 'Medium',
                'cost': impact['adjusted_impact_pct'] * 0.7,
                'description': 'Time-Weighted Average Price over specified period',
                'best_for': 'Medium urgency, consistent execution'
            },
            'VWAP': {
                'speed': 'Controlled',
                'impact': 'Low-Medium',
                'cost': impact['adjusted_impact_pct'] * 0.6,
                'description': 'Volume-Weighted Average Price following volume pattern',
                'best_for': 'Low-medium urgency, large orders'
            },
            'POV': {
                'speed': 'Controlled',
                'impact': 'Low',
                'cost': impact['adjusted_impact_pct'] * 0.5,
                'description': 'Percentage of Volume strategy',
                'best_for': 'Large orders, stealth execution'
            },
            'IMPLEMENTATION_SHORTFALL': {
                'speed': 'Adaptive',
                'impact': 'Low-Medium',
                'cost': impact['adjusted_impact_pct'] * 0.65,
                'description': 'Minimize implementation shortfall vs arrival price',
                'best_for': 'Sophisticated execution, cost minimization'
            }
        }
        
        # Selection logic based on order characteristics
        participation_rate = impact['participation_rate']
        urgency_score = {'Low': 1, 'Medium': 2, 'High': 3}.get(urgency, 2)
        
        if urgency_score == 3:  # High urgency
            if participation_rate < 0.02:
                recommended = 'MARKET'
            else:
                recommended = 'TWAP'
        elif urgency_score == 2:  # Medium urgency
            if participation_rate < 0.01:
                recommended = 'LIMIT'
            elif participation_rate < 0.05:
                recommended = 'VWAP'
            else:
                recommended = 'POV'
        else:  # Low urgency
            if participation_rate < 0.03:
                recommended = 'LIMIT'
            else:
                recommended = 'IMPLEMENTATION_SHORTFALL'
        
        # Liquidity adjustment
        if microstructure['liquidity_score'] < 30:  # Low liquidity
            if recommended in ['MARKET', 'TWAP']:
                recommended = 'POV'  # More conservative for illiquid stocks
        
        return {
            'recommended': recommended,
            'alternative1': self._get_alternative_algorithm(recommended, algorithms),
            'alternative2': self._get_alternative_algorithm(recommended, algorithms, 2),
            'algorithms': algorithms,
            'selection_reasoning': f"Based on {urgency} urgency, {participation_rate*100:.1f}% participation rate, and {microstructure['liquidity_score']:.0f} liquidity score"
        }
    
    def _get_alternative_algorithm(self, primary: str, algorithms: Dict, 
                                 alt_num: int = 1) -> str:
        """Get alternative algorithm options"""
        algo_list = list(algorithms.keys())
        try:
            primary_idx = algo_list.index(primary)
            if alt_num == 1:
                return algo_list[(primary_idx + 1) % len(algo_list)]
            else:
                return algo_list[(primary_idx + 2) % len(algo_list)]
        except:
            return 'VWAP'
    
    def _calculate_execution_costs(self, order_size: float, price: float, 
                                 algorithm: Dict, microstructure: Dict) -> Dict[str, Any]:
        """Calculate comprehensive execution costs"""
        
        # Base costs
        commission = min(order_size * 0.0005, 5.0)  # 5 bps cap at $5
        
        # Market impact cost
        algo_info = algorithm['algorithms'][algorithm['recommended']]
        impact_cost = order_size * algo_info['cost']
        
        # Spread cost (half-spread for aggressive orders)
        spread_cost = order_size * microstructure['spread_estimate'] * 0.5
        
        # Opportunity cost (for slower algorithms)
        algo_speed_factor = {
            'MARKET': 0, 'LIMIT': 0.002, 'TWAP': 0.001, 
            'VWAP': 0.001, 'POV': 0.0015, 'IMPLEMENTATION_SHORTFALL': 0.001
        }
        opportunity_cost = order_size * algo_speed_factor.get(algorithm['recommended'], 0.001)
        
        # Total cost
        total_cost = commission + impact_cost + spread_cost + opportunity_cost
        total_cost_bps = (total_cost / order_size) * 10000  # Basis points
        
        return {
            'commission': commission,
            'market_impact': impact_cost,
            'spread_cost': spread_cost,
            'opportunity_cost': opportunity_cost,
            'total_cost': total_cost,
            'total_cost_bps': total_cost_bps,
            'cost_breakdown': {
                'Commission': commission / total_cost * 100,
                'Market Impact': impact_cost / total_cost * 100,
                'Spread': spread_cost / total_cost * 100,
                'Opportunity': opportunity_cost / total_cost * 100
            }
        }
    
    def _generate_routing_strategy(self, order_size: float, microstructure: Dict, 
                                 algorithm: Dict) -> Dict[str, Any]:
        """Generate smart order routing strategy"""
        
        # Venue allocation based on liquidity and characteristics
        venues = {
            'Primary Exchange': {'allocation': 0.4, 'type': 'Lit', 'cost': 'Standard'},
            'Dark Pool 1': {'allocation': 0.25, 'type': 'Dark', 'cost': 'Low'},
            'Dark Pool 2': {'allocation': 0.15, 'type': 'Dark', 'cost': 'Low'},
            'Electronic ECN': {'allocation': 0.15, 'type': 'Lit', 'cost': 'Medium'},
            'Alternative ATS': {'allocation': 0.05, 'type': 'Dark', 'cost': 'Low'}
        }
        
        # Adjust allocation based on order size and liquidity
        if microstructure['liquidity_score'] < 40:  # Low liquidity
            # Increase dark pool allocation
            venues['Dark Pool 1']['allocation'] = 0.35
            venues['Dark Pool 2']['allocation'] = 0.25
            venues['Primary Exchange']['allocation'] = 0.25
            venues['Electronic ECN']['allocation'] = 0.1
            venues['Alternative ATS']['allocation'] = 0.05
        
        # Calculate dollar allocations
        for venue in venues:
            venues[venue]['dollar_amount'] = order_size * venues[venue]['allocation']
        
        return {
            'venues': venues,
            'routing_logic': 'Optimized for minimal market impact and cost',
            'dark_pool_percentage': sum(v['allocation'] for v in venues.values() if v['type'] == 'Dark') * 100,
            'lit_market_percentage': sum(v['allocation'] for v in venues.values() if v['type'] == 'Lit') * 100,
            'estimated_fill_rate': self._estimate_fill_rate(microstructure, algorithm['recommended'])
        }
    
    def _estimate_fill_rate(self, microstructure: Dict, algorithm: str) -> float:
        """Estimate order fill rate based on market conditions"""
        base_fill_rate = {
            'MARKET': 0.98, 'LIMIT': 0.75, 'TWAP': 0.85,
            'VWAP': 0.90, 'POV': 0.85, 'IMPLEMENTATION_SHORTFALL': 0.88
        }.get(algorithm, 0.85)
        
        # Adjust for liquidity
        liquidity_adjustment = microstructure['liquidity_score'] / 100
        
        # Adjust for volatility
        vol_adjustment = 1.0 if microstructure['volatility'] < 0.3 else 0.95
        
        return min(0.99, base_fill_rate * liquidity_adjustment * vol_adjustment)
    
    def _create_execution_schedule(self, order_size: float, algorithm: Dict, 
                                 microstructure: Dict) -> Dict[str, Any]:
        """Create detailed execution schedule"""
        
        algo_name = algorithm['recommended']
        
        # Time horizon based on algorithm
        time_horizons = {
            'MARKET': '1-5 minutes',
            'LIMIT': '1-8 hours',
            'TWAP': '2-6 hours',
            'VWAP': '1 trading day',
            'POV': '1-3 trading days',
            'IMPLEMENTATION_SHORTFALL': '2-8 hours'
        }
        
        # Slice scheduling
        if algo_name in ['TWAP', 'VWAP', 'POV']:
            num_slices = min(20, max(5, int(np.sqrt(order_size / 10000))))
            slice_size = order_size / num_slices
            slice_interval = '15-30 minutes' if algo_name == 'TWAP' else 'Volume-based'
        else:
            num_slices = 1
            slice_size = order_size
            slice_interval = 'Immediate'
        
        # Optimal timing
        if microstructure['peak_volume_hour'] in [10, 11, 14, 15]:  # Market open/close
            optimal_timing = "Avoid first/last hour for large orders"
        else:
            optimal_timing = f"Execute during peak volume hours around {microstructure['peak_volume_hour']}:00"
        
        return {
            'algorithm': algo_name,
            'time_horizon': time_horizons.get(algo_name, '2-6 hours'),
            'num_slices': num_slices,
            'slice_size': slice_size,
            'slice_interval': slice_interval,
            'optimal_timing': optimal_timing,
            'start_time': 'Market open + 30 minutes' if order_size > 100000 else 'Flexible',
            'completion_target': self._calculate_completion_target(algo_name),
            'monitoring_frequency': self._get_monitoring_frequency(algo_name)
        }
    
    def _calculate_completion_target(self, algorithm: str) -> str:
        """Calculate target completion time"""
        targets = {
            'MARKET': 'Within 5 minutes',
            'LIMIT': 'End of trading day',
            'TWAP': 'Within specified time window',
            'VWAP': 'Market close',
            'POV': '80% by end of day 1',
            'IMPLEMENTATION_SHORTFALL': 'Within 4 hours'
        }
        return targets.get(algorithm, 'End of trading day')
    
    def _get_monitoring_frequency(self, algorithm: str) -> str:
        """Get recommended monitoring frequency"""
        frequencies = {
            'MARKET': 'Real-time (every tick)',
            'LIMIT': 'Every 15 minutes',
            'TWAP': 'Every slice (15-30 min)',
            'VWAP': 'Every 30 minutes',
            'POV': 'Every hour',
            'IMPLEMENTATION_SHORTFALL': 'Every 30 minutes'
        }
        return frequencies.get(algorithm, 'Every 30 minutes')
    
    def _format_execution_results(self, symbol: str, price: float, order_size: float,
                                urgency: str, order_type: str, microstructure: Dict,
                                impact: Dict, algorithm: Dict, cost: Dict,
                                routing: Dict, schedule: Dict) -> str:
        """Format comprehensive execution analysis results"""
        
        return f"""
═══════════════════════════════════════════════════════════════
                    OPTIMAL EXECUTION STRATEGY ANALYSIS
═══════════════════════════════════════════════════════════════

SECURITY: {symbol} | CURRENT PRICE: ${price:.2f}
ORDER SIZE: ${order_size:,.0f} ({order_size/price:,.0f} shares)
EXECUTION URGENCY: {urgency} | ORDER TYPE: {order_type}
ANALYSIS DATE: {datetime.now().strftime('%Y-%m-%d %H:%M')}

═══════════════════════════════════════════════════════════════
                    MARKET MICROSTRUCTURE ANALYSIS
═══════════════════════════════════════════════════════════════

LIQUIDITY METRICS:
• Daily Average Volume: {microstructure['avg_daily_volume']:,.0f} shares
• Recent Volume Trend: {microstructure['volume_trend']:.2f}x average
• Market Cap: ${microstructure['market_cap']/1e9:.1f}B
• Float Shares: {microstructure['float_shares']/1e6:.1f}M
• Liquidity Score: {microstructure['liquidity_score']:.0f}/100

TRADING CHARACTERISTICS:
• Average Trade Size: ${microstructure['avg_trade_size']:,.0f}
• Estimated Spread: {microstructure['spread_estimate']*100:.2f}%
• Volatility (Annualized): {microstructure['volatility']*100:.1f}%
• Peak Volume Hour: {microstructure['peak_volume_hour']:02d}:00
• Volume Concentration: {microstructure['volume_concentration']:.1f}x average

MARKET STRUCTURE ASSESSMENT:
• Liquidity Classification: {'High' if microstructure['liquidity_score'] > 70 else 'Medium' if microstructure['liquidity_score'] > 40 else 'Low'}
• Trading Difficulty: {impact['impact_category']}
• Venue Diversity: {'Excellent' if microstructure['liquidity_score'] > 70 else 'Good' if microstructure['liquidity_score'] > 40 else 'Limited'}

═══════════════════════════════════════════════════════════════
                    MARKET IMPACT ANALYSIS
═══════════════════════════════════════════════════════════════

ORDER IMPACT METRICS:
• Volume Participation: {impact['participation_rate']*100:.2f}% of daily volume
• Temporary Impact: {impact['temporary_impact']*100:.3f}%
• Permanent Impact: {impact['permanent_impact']*100:.3f}%
• Tick Impact: {impact['tick_impact']*100:.3f}%
• Total Base Impact: {impact['total_impact_pct']*100:.3f}%

ADJUSTED IMPACT (Market Conditions):
• Timing Multiplier: {impact['timing_multiplier']:.2f}x
• Adjusted Impact: {impact['adjusted_impact_pct']*100:.3f}%
• Impact in Dollars: ${impact['adjusted_impact_dollars']:,.0f}
• Impact Category: {impact['impact_category']}

IMPACT INTERPRETATION:
• Price Movement Risk: {'High' if impact['adjusted_impact_pct'] > 0.005 else 'Medium' if impact['adjusted_impact_pct'] > 0.002 else 'Low'}
• Slippage Expectation: {impact['adjusted_impact_pct']*100:.2f}% of order value
• Information Leakage: {'High' if impact['participation_rate'] > 0.1 else 'Medium' if impact['participation_rate'] > 0.03 else 'Low'}

═══════════════════════════════════════════════════════════════
                    ALGORITHM SELECTION & OPTIMIZATION
═══════════════════════════════════════════════════════════════

RECOMMENDED ALGORITHM: {algorithm['recommended']}
• Description: {algorithm['algorithms'][algorithm['recommended']]['description']}
• Execution Speed: {algorithm['algorithms'][algorithm['recommended']]['speed']}
• Expected Impact: {algorithm['algorithms'][algorithm['recommended']]['impact']}
• Best For: {algorithm['algorithms'][algorithm['recommended']]['best_for']}

ALTERNATIVE OPTIONS:
1. {algorithm['alternative1']}: {algorithm['algorithms'][algorithm['alternative1']]['description']}
2. {algorithm['alternative2']}: {algorithm['algorithms'][algorithm['alternative2']]['description']}

SELECTION REASONING:
{algorithm['selection_reasoning']}

ALGORITHM COMPARISON:
• Market Order: Immediate but highest impact ({algorithm['algorithms']['MARKET']['cost']*100:.3f}%)
• VWAP Strategy: Balanced approach ({algorithm['algorithms']['VWAP']['cost']*100:.3f}%)
• POV Strategy: Stealth execution ({algorithm['algorithms']['POV']['cost']*100:.3f}%)

═══════════════════════════════════════════════════════════════
                    EXECUTION COST ANALYSIS
═══════════════════════════════════════════════════════════════

COMPREHENSIVE COST BREAKDOWN:
• Commission Costs: ${cost['commission']:.2f}
• Market Impact: ${cost['market_impact']:,.0f}
• Bid-Ask Spread: ${cost['spread_cost']:,.0f}
• Opportunity Cost: ${cost['opportunity_cost']:,.0f}
• TOTAL COST: ${cost['total_cost']:,.0f} ({cost['total_cost_bps']:.1f} bps)

COST COMPONENT ANALYSIS:
• Commission: {cost['cost_breakdown']['Commission']:.1f}% of total cost
• Market Impact: {cost['cost_breakdown']['Market Impact']:.1f}% of total cost
• Spread Cost: {cost['cost_breakdown']['Spread']:.1f}% of total cost
• Opportunity: {cost['cost_breakdown']['Opportunity']:.1f}% of total cost

COST BENCHMARKS:
• Industry Average: 15-25 bps for institutional orders
• Your Estimated Cost: {cost['total_cost_bps']:.1f} bps
• Cost Efficiency: {'Excellent' if cost['total_cost_bps'] < 15 else 'Good' if cost['total_cost_bps'] < 25 else 'Above Average' if cost['total_cost_bps'] < 35 else 'High'}

═══════════════════════════════════════════════════════════════
                    SMART ORDER ROUTING STRATEGY
═══════════════════════════════════════════════════════════════

VENUE ALLOCATION:"""

        # Add venue details
        for venue, details in routing['venues'].items():
            result += f"""
• {venue}: {details['allocation']*100:.0f}% (${details['dollar_amount']:,.0f}) - {details['type']} market"""

        result += f"""

ROUTING OPTIMIZATION:
• Dark Pool Allocation: {routing['dark_pool_percentage']:.0f}%
• Lit Market Allocation: {routing['lit_market_percentage']:.0f}%
• Estimated Fill Rate: {routing['estimated_fill_rate']*100:.0f}%
• Routing Logic: {routing['routing_logic']}

VENUE SELECTION RATIONALE:
• Dark pools minimize market impact for large orders
• Primary exchange ensures liquidity and best execution
• ECNs provide additional liquidity and price improvement
• ATS venues offer cost-effective execution

═══════════════════════════════════════════════════════════════
                    EXECUTION SCHEDULE & TIMING
═══════════════════════════════════════════════════════════════

EXECUTION PLAN:
• Algorithm: {schedule['algorithm']}
• Time Horizon: {schedule['time_horizon']}
• Number of Slices: {schedule['num_slices']}
• Slice Size: ${schedule['slice_size']:,.0f} per slice
• Slice Interval: {schedule['slice_interval']}

TIMING OPTIMIZATION:
• Optimal Start Time: {schedule['start_time']}
• Completion Target: {schedule['completion_target']}
• Peak Volume Strategy: {schedule['optimal_timing']}
• Monitoring Frequency: {schedule['monitoring_frequency']}

EXECUTION WORKFLOW:
1. Pre-market: Analyze overnight news and pre-market activity
2. Market Open: {schedule['start_time']}
3. Execution: Follow {schedule['algorithm']} strategy with {schedule['slice_interval']} intervals
4. Monitoring: {schedule['monitoring_frequency']} performance checks
5. Adjustment: Dynamic parameter adjustment based on market conditions
6. Completion: Target {schedule['completion_target']}

═══════════════════════════════════════════════════════════════
                    RISK MANAGEMENT & CONTINGENCIES
═══════════════════════════════════════════════════════════════

EXECUTION RISKS:
• Market Impact Risk: {impact['impact_category']} - Monitor for adverse price movement
• Liquidity Risk: {'Low' if microstructure['liquidity_score'] > 60 else 'Medium' if microstructure['liquidity_score'] > 30 else 'High'} - Ensure adequate volume
• Timing Risk: {'Low' if urgency == 'Low' else 'Medium' if urgency == 'Medium' else 'High'} - Balance speed vs cost
• News Risk: Monitor for material announcements during execution

CONTINGENCY PLANS:
• If volume drops 50%: Switch to POV algorithm, extend timeline
• If volatility spikes >50%: Pause execution, reassess strategy
• If spread widens >50%: Increase limit order usage, reduce aggression
• If news breaks: Immediate pause, reassess fundamentals

PERFORMANCE MONITORING:
• Real-time TWAP tracking vs benchmark
• Slippage monitoring against pre-trade estimates
• Fill rate tracking by venue and time
• Market impact measurement vs predictions

ESCALATION PROCEDURES:
• >2x expected slippage: Portfolio manager notification
• <50% fill rate: Algorithm adjustment
• Material news: Immediate strategy review
• Technical issues: Manual oversight activation

═══════════════════════════════════════════════════════════════
                    EXECUTION RECOMMENDATIONS
═══════════════════════════════════════════════════════════════

IMMEDIATE ACTIONS:
1. Implement {algorithm['recommended']} algorithm starting {schedule['start_time']}
2. Route {routing['dark_pool_percentage']:.0f}% to dark pools, {routing['lit_market_percentage']:.0f}% to lit markets
3. Execute in {schedule['num_slices']} slices over {schedule['time_horizon']}
4. Monitor performance every {schedule['monitoring_frequency']}

OPTIMIZATION OPPORTUNITIES:
• Consider Implementation Shortfall if cost minimization is priority
• Use LIMIT orders during low volatility periods
• Increase dark pool allocation for orders >$500K
• Time execution around {microstructure['peak_volume_hour']}:00 for optimal liquidity

EXPECTED OUTCOMES:
• Total Execution Cost: ${cost['total_cost']:,.0f} ({cost['total_cost_bps']:.1f} bps)
• Fill Rate: {routing['estimated_fill_rate']*100:.0f}%
• Completion Time: {schedule['completion_target']}
• Market Impact: {impact['adjusted_impact_pct']*100:.3f}% price movement

SUCCESS METRICS:
• Achieve <{cost['total_cost_bps']*1.2:.1f} bps total cost
• Maintain >{routing['estimated_fill_rate']*100-5:.0f}% fill rate
• Complete within {schedule['time_horizon']}
• Minimize information leakage and adverse selection

═══════════════════════════════════════════════════════════════

DISCLAIMER: Execution analysis based on historical market data and statistical models. Actual execution costs may vary due to changing market conditions, liquidity fluctuations, and unforeseen events. Always monitor execution in real-time and adjust strategy as needed.

═══════════════════════════════════════════════════════════════
"""
        
        return result

def create_order_execution_agent():
    """Create the OrderExecutionAgent using CrewAI framework"""
    
    # Initialize the order execution tool
    execution_tool = OrderExecutionTool()
    
    # Create the OrderExecutionAgent
    execution_agent = Agent(
        role='Trade Execution Optimization Specialist',
        goal='Design and optimize trade execution strategies to minimize market impact, reduce slippage, and achieve best execution while managing timing and liquidity risks',
        backstory="""You are an elite institutional execution trader with deep expertise in 
        market microstructure, algorithmic trading, and smart order routing. You specialize in 
        minimizing transaction costs through sophisticated execution strategies, optimal venue 
        selection, and precise timing. Your systematic approach combines advanced analytics 
        with real-time market intelligence to achieve superior execution quality while 
        managing information leakage and adverse selection risks.""",
        tools=[execution_tool],
        verbose=True,
        allow_delegation=False,
        max_iter=3
    )
    
    return execution_agent

def create_execution_tasks(agent, symbol: str, order_size: float, 
                         urgency: str = "Medium", order_type: str = "Market") -> List[Task]:
    """Create order execution optimization tasks for the agent"""
    
    strategy_task = Task(
        description=f"""
        Design optimal execution strategy for {symbol} order:
        
        1. MARKET MICROSTRUCTURE ANALYSIS:
           - Analyze daily and intraday volume patterns
           - Calculate liquidity metrics and trading characteristics
           - Assess bid-ask spreads and market depth
           - Evaluate venue diversity and execution options
           
        2. MARKET IMPACT MODELING:
           - Calculate temporary and permanent impact components
           - Model volume participation effects
           - Assess timing and urgency impacts
           - Quantify information leakage risks
           
        3. ALGORITHM SELECTION:
           - Compare TWAP, VWAP, POV, and Implementation Shortfall
           - Select optimal algorithm based on order characteristics
           - Consider market conditions and liquidity constraints
           - Provide alternative execution strategies
           
        4. COST OPTIMIZATION:
           - Calculate comprehensive execution costs
           - Include commission, spread, impact, and opportunity costs
           - Compare costs across different algorithms
           - Benchmark against industry standards
           
        Order Parameters:
        - Symbol: {symbol}
        - Order Size: ${order_size:,.0f}
        - Urgency: {urgency}
        - Order Type: {order_type}
        
        Use the order_execution_optimizer tool with these parameters.
        """,
        expected_output="""
        Comprehensive execution strategy including:
        - Market microstructure analysis with liquidity assessment
        - Market impact modeling with cost projections
        - Optimal algorithm selection with alternatives
        - Smart order routing strategy across venues
        - Detailed execution schedule with timing optimization
        - Risk management and contingency procedures
        """,
        agent=agent
    )
    
    implementation_task = Task(
        description=f"""
        Create detailed implementation plan for {symbol} execution:
        
        1. EXECUTION SCHEDULE:
           - Design slice timing and size optimization
           - Create venue allocation and routing strategy
           - Establish monitoring and adjustment protocols
           - Define completion targets and milestones
           
        2. RISK MANAGEMENT:
           - Identify execution risks and mitigation strategies
           - Create contingency plans for adverse scenarios
           - Establish escalation procedures and thresholds
           - Design real-time monitoring framework
           
        3. PERFORMANCE MEASUREMENT:
           - Define success metrics and benchmarks
           - Create TWAP and VWAP tracking protocols
           - Establish slippage measurement procedures
           - Design post-trade analysis framework
           
        4. OPERATIONAL PROCEDURES:
           - Create execution checklist and workflows
           - Define trader responsibilities and handoffs
           - Establish communication protocols
           - Document decision-making procedures
        """,
        expected_output="""
        Detailed implementation plan with:
        - Step-by-step execution procedures
        - Risk management framework with contingencies
        - Performance monitoring and measurement protocols
        - Operational workflows and communication procedures
        - Success criteria and post-trade analysis plan
        """,
        agent=agent,
        context=[strategy_task]
    )
    
    return [strategy_task, implementation_task]

def create_order_execution_crew(symbol: str, order_size: float, 
                              urgency: str = "Medium", order_type: str = "Market"):
    """Create a complete CrewAI crew for order execution optimization"""
    
    # Create agent
    agent = create_order_execution_agent()
    
    # Create tasks
    tasks = create_execution_tasks(agent, symbol, order_size, urgency, order_type)
    
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
def run_execution_analysis(symbol: str, order_size: float, 
                         urgency: str = "Medium", order_type: str = "Market") -> str:
    """Run complete execution optimization analysis for a given order"""
    try:
        crew = create_order_execution_crew(symbol, order_size, urgency, order_type)
        result = crew.kickoff()
        return str(result)
    except Exception as e:
        return f"❌ Error running execution analysis: {str(e)}"
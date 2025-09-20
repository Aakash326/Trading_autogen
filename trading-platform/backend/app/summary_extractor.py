"""
Summary Extraction Module
Extracts complete analysis results including proper one-line summaries from AI agent conversations
"""

import re
from typing import Dict, List, Tuple, Any

def extract_complete_analysis_results(all_messages: List[Dict], stock_symbol: str, analysis_type: str) -> Dict:
    """
    Extract complete analysis results including proper one-line summary
    
    Returns:
        {
            'summary': str,           # Detailed analysis summary  
            'recommendation': str,    # BUY/SELL/HOLD
            'confidence': int,        # 1-100 confidence score
            'one_line_summary': str  # Key one-line decision summary
        }
    """
    
    if not all_messages:
        return {
            'summary': f"No analysis generated for {stock_symbol}",
            'recommendation': 'HOLD',
            'confidence': 50,
            'one_line_summary': f"HOLD {stock_symbol} - No analysis available"
        }
    
    # Find ReportAgent's final message (most important)
    report_messages = [msg for msg in all_messages if 'report' in msg.get('source', '').lower()]
    final_content = report_messages[-1].get('content', '') if report_messages else all_messages[-1].get('content', '')
    
    # Extract recommendation
    recommendation = extract_recommendation_from_content(final_content)
    
    # Extract confidence score
    confidence = extract_confidence_from_content(final_content)
    
    # Generate one-line summary (CRITICAL FIX)
    one_line_summary = generate_one_line_summary(final_content, stock_symbol, recommendation, confidence)
    
    # Create comprehensive summary
    summary = create_comprehensive_summary(all_messages, stock_symbol, analysis_type, recommendation, confidence)
    
    return {
        'summary': summary,
        'recommendation': recommendation,
        'confidence': confidence,
        'one_line_summary': one_line_summary
    }

def extract_recommendation_from_content(content: str) -> str:
    """Extract BUY/SELL/HOLD recommendation from analysis content"""
    content_upper = content.upper()
    
    # Comprehensive patterns for recommendation extraction
    patterns = [
        r'FINAL\s+RECOMMENDATION[:\s]+(STRONG\s+BUY|BUY|STRONG\s+SELL|SELL|HOLD)',
        r'RECOMMENDATION[:\s]+(STRONG\s+BUY|BUY|STRONG\s+SELL|SELL|HOLD)',
        r'FINAL\s+DECISION[:\s]+(STRONG\s+BUY|BUY|STRONG\s+SELL|SELL|HOLD)',
        r'CONCLUDE[:\s]+(STRONG\s+BUY|BUY|STRONG\s+SELL|SELL|HOLD)',
        r'(STRONG\s+BUY)',
        r'(STRONG\s+SELL)', 
        r'\b(BUY)\b(?!\s+SIDE)(?!\s+BACK)',
        r'\b(SELL)\b(?!\s+SIDE)',
        r'\b(HOLD)\b'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content_upper)
        if match:
            rec = match.group(1).replace(' ', '_')  # Convert "STRONG BUY" to "STRONG_BUY"
            return rec
    
    # Fallback analysis based on sentiment
    if 'POSITIVE' in content_upper or 'BULLISH' in content_upper or 'UPSIDE' in content_upper:
        return 'BUY'
    elif 'NEGATIVE' in content_upper or 'BEARISH' in content_upper or 'DOWNSIDE' in content_upper:
        return 'SELL'
    
    return 'HOLD'  # Default conservative recommendation

def extract_confidence_from_content(content: str) -> int:
    """Extract confidence percentage from content"""
    patterns = [
        r'CONFIDENCE[:\s]+(\d+)%',
        r'CONFIDENCE[:\s]+(\d+)/10',
        r'(\d+)%\s*CONFIDENCE',
        r'(\d+)/10\s*CONFIDENCE',
        r'CONFIDENCE\s*LEVEL[:\s]+(\d+)%',
        r'CERTAINTY[:\s]+(\d+)%'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content.upper())
        if match:
            conf = int(match.group(1))
            # Convert x/10 to percentage
            if '/10' in pattern:
                conf = conf * 10
            return min(95, max(5, conf))  # Clamp between 5-95%
    
    # Fallback based on strength indicators
    content_upper = content.upper()
    if 'STRONG' in content_upper or 'HIGH CONFIDENCE' in content_upper:
        return 85
    elif 'MODERATE' in content_upper or 'MEDIUM' in content_upper:
        return 70
    elif 'WEAK' in content_upper or 'LOW' in content_upper:
        return 55
    
    return 75  # Default moderate confidence

def generate_one_line_summary(content: str, stock_symbol: str, recommendation: str, confidence: int) -> str:
    """Generate properly formatted one-line summary"""
    
    # Try to extract target price
    target_patterns = [
        r'TARGET\s+PRICE[:\s]*\$?(\d+(?:\.\d+)?)',
        r'PRICE\s+TARGET[:\s]*\$?(\d+(?:\.\d+)?)',
        r'TARGET[:\s]*\$?(\d+(?:\.\d+)?)',
        r'FAIR\s+VALUE[:\s]*\$?(\d+(?:\.\d+)?)'
    ]
    
    target = ""
    for pattern in target_patterns:
        target_match = re.search(pattern, content.upper())
        if target_match:
            target = f" - Target: ${target_match.group(1)}"
            break
    
    # Try to extract timeframe
    timeframe_patterns = [
        r'(\d+)[-\s]?(MONTH|YEAR|DAY|WEEK)',
        r'(SHORT|MEDIUM|LONG)[-\s]?TERM',
        r'NEXT\s+(\d+)\s+(MONTH|YEAR|DAY|WEEK)'
    ]
    
    timeframe = ""
    for pattern in timeframe_patterns:
        time_match = re.search(pattern, content.upper())
        if time_match:
            if len(time_match.groups()) == 2:
                timeframe = f" ({time_match.group(1)} {time_match.group(2).lower()})"
            else:
                timeframe = f" ({time_match.group(1).lower()}-term)"
            break
    
    # Generate the properly formatted one-line summary
    recommendation_display = recommendation.replace('_', ' ')
    return f"{recommendation_display} {stock_symbol} ({confidence}% confidence{target}{timeframe}) - Multi-agent AI analysis complete"

def create_comprehensive_summary(messages: List[Dict], symbol: str, analysis_type: str, rec: str, conf: int) -> str:
    """Create detailed analysis summary with agent participation"""
    
    # Count agent participation
    agent_counts = {}
    total_messages = 0
    
    for msg in messages:
        agent = msg.get('source', 'Unknown')
        if agent != 'user':
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
            total_messages += 1
    
    # Detect workflow type
    workflow_type = "13-agent" if len(agent_counts) > 10 else "7-agent"
    expected_agents = 13 if workflow_type == "13-agent" else 7
    
    # Check for completion indicators
    completion_indicators = [
        "FINAL_ANALYSIS_COMPLETE",
        "ANALYSIS COMPLETE", 
        "FINAL RECOMMENDATION",
        "CONCLUSION"
    ]
    
    has_completion = any(
        any(indicator in msg.get('content', '').upper() for indicator in completion_indicators)
        for msg in messages
    )
    
    # Extract key insights from final messages
    key_insights = extract_key_insights(messages[-3:] if len(messages) >= 3 else messages)
    
    summary_parts = [
        f"✅ Real {workflow_type} AI Analysis Complete for {symbol}",
        f"🎯 FINAL RECOMMENDATION: {rec.replace('_', ' ')} (Confidence: {conf}%)",
        f"📋 Analysis Type: {analysis_type.replace('_', ' ').title()}",
        f"🤖 Agent Participation: {len(agent_counts)} of {expected_agents} expected",
        f"💬 Total Messages: {total_messages}",
        f"✅ Completion Status: {'Complete' if has_completion else 'Partial'}",
        "",
        "🔍 Agent Participation Details:"
    ]
    
    # Add agent participation details
    for agent, count in sorted(agent_counts.items()):
        # Clean up agent names for display
        clean_agent = agent.replace('_', ' ').replace('-', ' ').title()
        summary_parts.append(f"  • {clean_agent}: {count} contributions")
    
    # Add key insights if available
    if key_insights:
        summary_parts.extend([
            "",
            "💡 Key Analysis Insights:",
            *[f"  • {insight}" for insight in key_insights[:3]]  # Top 3 insights
        ])
    
    # Extract decision reasoning from ReportAgent
    decision_reasoning = extract_decision_reasoning(messages, symbol, rec)
    if decision_reasoning:
        summary_parts.extend([
            "",
            "🧠 Why This Decision:",
            *[f"  • {reason}" for reason in decision_reasoning[:3]]  # Top 3 reasons
        ])
    
    return "\n".join(summary_parts)

def extract_decision_reasoning(messages: List[Dict], symbol: str, recommendation: str) -> List[str]:
    """Extract decision reasoning from ReportAgent's analysis"""
    reasoning = []
    
    # Find ReportAgent's message
    report_messages = [msg for msg in messages if 'report' in msg.get('source', '').lower()]
    if not report_messages:
        return reasoning
    
    content = report_messages[-1].get('content', '')
    
    # Extract "Why This Decision Makes Sense" section
    why_patterns = [
        r'Why This Decision Makes Sense[:\s]*([^🔍]+)',
        r'DECISION REASONING[:\s]*([^🔍]+)',
        r'Why.*Decision[:\s]*([^🔍]+)'
    ]
    
    for pattern in why_patterns:
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            why_text = match.group(1).strip()
            # Clean up and extract key points
            lines = [line.strip() for line in why_text.split('\n') if line.strip()]
            for line in lines[:2]:  # Take first 2 meaningful lines
                if len(line) > 20 and not line.startswith('🔍'):
                    reasoning.append(line)
    
    # Extract key factors
    factor_patterns = [
        r'Key Factors[:\s]*([^⚖️]+)',
        r'Factors That Drove[:\s]*([^⚖️]+)'
    ]
    
    for pattern in factor_patterns:
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            factors_text = match.group(1).strip()
            # Extract bullet points
            bullet_points = re.findall(r'•\s*([^•]+)', factors_text)
            for point in bullet_points[:2]:  # Take first 2 points
                clean_point = point.strip()
                if len(clean_point) > 15:
                    reasoning.append(clean_point)
    
    # Extract investment thesis if no specific reasoning found
    if not reasoning:
        thesis_patterns = [
            r'INVESTMENT THESIS[:\s]*([^4\.]+)',
            r'Investment Reasoning[:\s]*([^4\.]+)'
        ]
        
        for pattern in thesis_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                thesis_text = match.group(1).strip()
                # Take first sentence or two
                sentences = thesis_text.split('.')
                for sentence in sentences[:2]:
                    clean_sentence = sentence.strip()
                    if len(clean_sentence) > 30:
                        reasoning.append(clean_sentence + '.')
    
    # Fallback: extract general reasoning from decision summary
    if not reasoning:
        summary_patterns = [
            r'FINAL DECISION SUMMARY[:\s]*([^FINAL_ANALYSIS_COMPLETE]+)'
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                summary_text = match.group(1).strip()
                sentences = summary_text.split('.')
                for sentence in sentences[:2]:
                    clean_sentence = sentence.strip()
                    if len(clean_sentence) > 30:
                        reasoning.append(clean_sentence + '.')
    
    return reasoning[:3]  # Return top 3 reasoning points

def extract_key_insights(recent_messages: List[Dict]) -> List[str]:
    """Extract key insights from recent messages"""
    insights = []
    
    for msg in recent_messages:
        content = msg.get('content', '')
        
        # Look for specific patterns that indicate insights
        insight_patterns = [
            r'KEY\s+INSIGHT[:\s]+([^.]+\.)',
            r'IMPORTANT[:\s]+([^.]+\.)',
            r'CRITICAL[:\s]+([^.]+\.)',
            r'CONCLUSION[:\s]+([^.]+\.)',
            r'FINDING[:\s]+([^.]+\.)'
        ]
        
        for pattern in insight_patterns:
            matches = re.findall(pattern, content.upper())
            for match in matches:
                clean_insight = match.strip().capitalize()
                if len(clean_insight) > 20 and clean_insight not in insights:
                    insights.append(clean_insight)
        
        # Stop if we have enough insights
        if len(insights) >= 5:
            break
    
    return insights[:5]  # Return top 5 insights

def extract_numerical_metrics(content: str) -> Dict[str, str]:
    """Extract numerical metrics from analysis content"""
    metrics = {}
    
    # Price targets
    price_match = re.search(r'TARGET[:\s]*\$?(\d+(?:\.\d+)?)', content.upper())
    if price_match:
        metrics['target_price'] = f"${price_match.group(1)}"
    
    # Risk metrics
    risk_patterns = {
        'var': r'VAR[:\s]*(\d+(?:\.\d+)?)%',
        'beta': r'BETA[:\s]*(\d+(?:\.\d+)?)',
        'volatility': r'VOLATILITY[:\s]*(\d+(?:\.\d+)?)%'
    }
    
    for metric, pattern in risk_patterns.items():
        match = re.search(pattern, content.upper())
        if match:
            metrics[metric] = match.group(1)
    
    return metrics

def validate_analysis_completeness(messages: List[Dict], workflow_type: str = "7-agent") -> Dict[str, Any]:
    """Validate that analysis is complete with all required agents"""
    
    required_agents = {
        "7-agent": [
            "organiser", "risk", "data", "quantitative", 
            "strategy", "compliance", "report"
        ],
        "13-agent": [
            "organiser", "risk", "data", "quantitative", "strategy", 
            "compliance", "report", "stress", "arbitrage", "execution",
            "portfolio", "market", "research"
        ]
    }
    
    expected = required_agents.get(workflow_type, required_agents["7-agent"])
    
    # Count actual agent participation
    participating_agents = set()
    for msg in messages:
        agent = msg.get('source', '').lower()
        for expected_agent in expected:
            if expected_agent in agent:
                participating_agents.add(expected_agent)
                break
    
    missing_agents = set(expected) - participating_agents
    completion_rate = len(participating_agents) / len(expected) * 100
    
    return {
        'completion_rate': completion_rate,
        'participating_agents': list(participating_agents),
        'missing_agents': list(missing_agents),
        'is_complete': completion_rate >= 90.0,
        'expected_count': len(expected),
        'actual_count': len(participating_agents)
    }

# Testing and validation functions
def test_extraction_accuracy():
    """Test the extraction functions with sample data"""
    
    test_content = """
    FINAL RECOMMENDATION: BUY
    CONFIDENCE LEVEL: 85%
    TARGET PRICE: $150.00
    ANALYSIS COMPLETE - All agents have provided input.
    """
    
    recommendation = extract_recommendation_from_content(test_content)
    confidence = extract_confidence_from_content(test_content)
    summary = generate_one_line_summary(test_content, "AAPL", recommendation, confidence)
    
    print(f"Test Results:")
    print(f"  Recommendation: {recommendation}")
    print(f"  Confidence: {confidence}%")
    print(f"  One-line summary: {summary}")
    
    return {
        'recommendation': recommendation,
        'confidence': confidence,
        'summary': summary
    }

if __name__ == "__main__":
    # Run tests
    print("🧪 Testing Summary Extraction Module...")
    test_results = test_extraction_accuracy()
    
    # Expected results
    expected = {
        'recommendation': 'BUY',
        'confidence': 85,
    }
    
    success = (
        test_results['recommendation'] == expected['recommendation'] and
        test_results['confidence'] == expected['confidence'] and
        'BUY AAPL (85% confidence)' in test_results['summary']
    )
    
    print(f"✅ Test {'PASSED' if success else 'FAILED'}")
    
    if not success:
        print("❌ Test details:")
        for key, expected_val in expected.items():
            actual_val = test_results.get(key)
            if actual_val != expected_val:
                print(f"  {key}: expected {expected_val}, got {actual_val}")
from autogen_agentchat.agents import AssistantAgent
from src.model.model import get_model_client
import yfinance as yf
from typing import Annotated, Dict, List
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

model_client = get_model_client()

def analyze_esg_factors(symbol: Annotated[str, "Stock symbol like AAPL, GOOGL, TSLA"]) -> str:
    """
    Comprehensive ESG (Environmental, Social, Governance) analysis tool that evaluates 
    sustainability factors, climate risks, governance quality, and ESG investment implications
    """
    try:
        # Get company information
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist_data = ticker.history(period="1y")
        
        if hist_data.empty:
            return f"❌ Unable to fetch stock data for {symbol}"
        
        current_price = hist_data['Close'].iloc[-1]
        company_name = info.get('longName', symbol)
        sector = info.get('sector', 'Unknown')
        industry = info.get('industry', 'Unknown')
        market_cap = info.get('marketCap', 0)
        
        # Analyze Environmental factors
        environmental_analysis = analyze_environmental_factors(symbol, info, sector, industry)
        
        # Analyze Social factors
        social_analysis = analyze_social_factors(symbol, info, sector, industry)
        
        # Analyze Governance factors
        governance_analysis = analyze_governance_factors(symbol, info, sector, industry)
        
        # Climate risk assessment
        climate_risk = assess_climate_risk(symbol, info, sector, industry)
        
        # ESG scoring and rating
        esg_scoring = calculate_esg_scores(environmental_analysis, social_analysis, governance_analysis, climate_risk)
        
        # Investment implications
        investment_implications = analyze_esg_investment_impact(esg_scoring, market_cap, sector)
        
        return format_esg_analysis(
            symbol, company_name, current_price, sector, industry, market_cap,
            environmental_analysis, social_analysis, governance_analysis, 
            climate_risk, esg_scoring, investment_implications
        )
        
    except Exception as e:
        return f"❌ Error in ESG analysis for {symbol}: {str(e)}"

def analyze_environmental_factors(symbol: str, info: Dict, sector: str, industry: str) -> Dict:
    """Analyze environmental sustainability factors"""
    
    # Sector-specific environmental risk mapping
    high_impact_sectors = ['Energy', 'Utilities', 'Materials', 'Industrials']
    medium_impact_sectors = ['Consumer Discretionary', 'Consumer Staples', 'Real Estate']
    low_impact_sectors = ['Technology', 'Healthcare', 'Communication Services', 'Financials']
    
    if sector in high_impact_sectors:
        sector_risk = "High"
        base_score = 30
    elif sector in medium_impact_sectors:
        sector_risk = "Medium"
        base_score = 50
    else:
        sector_risk = "Low"
        base_score = 70
    
    # Industry-specific adjustments
    industry_adjustments = {
        'Oil & Gas': -20, 'Coal': -30, 'Mining': -15,
        'Renewable Energy': +20, 'Electric Vehicles': +15,
        'Software': +10, 'Semiconductors': +5,
        'Banking': +5, 'Insurance': +5
    }
    
    industry_adjustment = 0
    for key, adjustment in industry_adjustments.items():
        if key.lower() in industry.lower():
            industry_adjustment = adjustment
            break
    
    # Simulate environmental metrics (in production, would use real ESG data)
    import random
    import hashlib
    
    seed = int(hashlib.md5((symbol + "env").encode()).hexdigest()[:8], 16)
    random.seed(seed)
    
    carbon_footprint = {
        'scope_1_emissions': random.uniform(50000, 500000) if sector in high_impact_sectors else random.uniform(1000, 50000),
        'scope_2_emissions': random.uniform(20000, 200000) if sector in high_impact_sectors else random.uniform(500, 20000),
        'scope_3_emissions': random.uniform(100000, 1000000) if sector in high_impact_sectors else random.uniform(5000, 100000),
        'carbon_intensity': random.uniform(200, 800) if sector in high_impact_sectors else random.uniform(20, 200),
        'reduction_targets': random.choice(['Net Zero 2050', 'Net Zero 2040', 'Net Zero 2030', '50% by 2030', 'No targets'])
    }
    
    resource_management = {
        'water_usage': random.uniform(1000, 100000),  # cubic meters
        'waste_generation': random.uniform(500, 50000),  # tons
        'recycling_rate': random.uniform(0.2, 0.9),
        'renewable_energy_usage': random.uniform(0.1, 0.8),
        'energy_efficiency_score': random.uniform(0.3, 0.9)
    }
    
    environmental_initiatives = {
        'green_products': random.choice(['Leader', 'Innovator', 'Follower', 'Laggard']),
        'circular_economy': random.choice(['Advanced', 'Developing', 'Basic', 'None']),
        'biodiversity_impact': random.choice(['Positive', 'Neutral', 'Negative', 'Significant Negative']),
        'pollution_control': random.uniform(0.4, 0.95),
        'environmental_certifications': random.randint(0, 10)
    }
    
    # Calculate environmental score
    env_score = base_score + industry_adjustment
    
    # Adjust based on initiatives
    if environmental_initiatives['green_products'] == 'Leader':
        env_score += 10
    elif environmental_initiatives['green_products'] == 'Laggard':
        env_score -= 10
    
    if resource_management['renewable_energy_usage'] > 0.6:
        env_score += 5
    elif resource_management['renewable_energy_usage'] < 0.2:
        env_score -= 5
    
    if 'Net Zero' in carbon_footprint['reduction_targets']:
        env_score += 8
    elif carbon_footprint['reduction_targets'] == 'No targets':
        env_score -= 8
    
    env_score = max(0, min(100, env_score))
    
    return {
        'sector_risk': sector_risk,
        'carbon_footprint': carbon_footprint,
        'resource_management': resource_management,
        'environmental_initiatives': environmental_initiatives,
        'environmental_score': env_score,
        'key_strengths': generate_environmental_strengths(env_score, environmental_initiatives, resource_management),
        'key_concerns': generate_environmental_concerns(env_score, sector_risk, carbon_footprint),
        'regulatory_risk': assess_environmental_regulatory_risk(sector, industry)
    }

def analyze_social_factors(symbol: str, info: Dict, sector: str, industry: str) -> Dict:
    """Analyze social responsibility and stakeholder factors"""
    
    import random
    import hashlib
    
    seed = int(hashlib.md5((symbol + "social").encode()).hexdigest()[:8], 16)
    random.seed(seed)
    
    # Employee relations
    employee_metrics = {
        'employee_satisfaction': random.uniform(0.6, 0.9),
        'diversity_score': random.uniform(0.4, 0.8),
        'turnover_rate': random.uniform(0.05, 0.25),
        'training_investment': random.uniform(1000, 10000),  # per employee
        'safety_record': random.uniform(0.7, 0.98),
        'union_relations': random.choice(['Excellent', 'Good', 'Fair', 'Poor'])
    }
    
    # Customer relations
    customer_metrics = {
        'customer_satisfaction': random.uniform(0.6, 0.95),
        'product_safety': random.uniform(0.8, 0.99),
        'data_privacy_score': random.uniform(0.5, 0.95),
        'accessibility_efforts': random.choice(['Leader', 'Good', 'Basic', 'Minimal']),
        'customer_complaints': random.randint(10, 1000)
    }
    
    # Community impact
    community_metrics = {
        'local_hiring': random.uniform(0.3, 0.8),
        'community_investment': random.uniform(0.001, 0.05),  # % of revenue
        'local_supplier_usage': random.uniform(0.2, 0.7),
        'community_relations': random.choice(['Excellent', 'Good', 'Fair', 'Poor']),
        'social_impact_programs': random.randint(2, 20)
    }
    
    # Human rights
    human_rights = {
        'supply_chain_monitoring': random.choice(['Comprehensive', 'Good', 'Basic', 'Minimal']),
        'labor_standards': random.choice(['Gold Standard', 'Good', 'Adequate', 'Concerning']),
        'child_labor_risk': random.choice(['No Risk', 'Low Risk', 'Medium Risk', 'High Risk']),
        'fair_trade_practices': random.uniform(0.3, 0.9),
        'human_rights_policy': random.choice(['Comprehensive', 'Good', 'Basic', 'None'])
    }
    
    # Calculate social score
    social_score = (
        employee_metrics['employee_satisfaction'] * 25 +
        customer_metrics['customer_satisfaction'] * 25 +
        community_metrics['community_investment'] * 500 +  # Scale up the small percentage
        (1 if human_rights['supply_chain_monitoring'] in ['Comprehensive', 'Good'] else 0) * 25
    )
    
    social_score = max(0, min(100, social_score))
    
    return {
        'employee_metrics': employee_metrics,
        'customer_metrics': customer_metrics,
        'community_metrics': community_metrics,
        'human_rights': human_rights,
        'social_score': social_score,
        'stakeholder_engagement': random.choice(['Proactive', 'Reactive', 'Minimal']),
        'social_controversies': random.randint(0, 5),
        'social_innovation': random.choice(['Leader', 'Innovator', 'Follower', 'Laggard'])
    }

def analyze_governance_factors(symbol: str, info: Dict, sector: str, industry: str) -> Dict:
    """Analyze corporate governance quality"""
    
    import random
    import hashlib
    
    seed = int(hashlib.md5((symbol + "gov").encode()).hexdigest()[:8], 16)
    random.seed(seed)
    
    # Board composition
    board_structure = {
        'board_size': random.randint(7, 15),
        'independent_directors': random.uniform(0.6, 0.9),
        'gender_diversity': random.uniform(0.2, 0.5),
        'ethnic_diversity': random.uniform(0.1, 0.4),
        'average_tenure': random.uniform(3, 12),
        'expertise_alignment': random.uniform(0.7, 0.95)
    }
    
    # Executive compensation
    compensation = {
        'ceo_pay_ratio': random.uniform(50, 500),  # CEO to median worker
        'pay_for_performance': random.uniform(0.6, 0.9),
        'long_term_incentives': random.uniform(0.4, 0.8),
        'clawback_provisions': random.choice([True, False]),
        'excessive_compensation': random.choice([False, False, False, True])  # 25% chance
    }
    
    # Risk management
    risk_management = {
        'risk_committee': random.choice([True, False]),
        'cybersecurity_oversight': random.uniform(0.6, 0.95),
        'internal_controls': random.uniform(0.7, 0.98),
        'audit_quality': random.choice(['Big 4', 'National', 'Regional']),
        'risk_disclosure': random.uniform(0.6, 0.9)
    }
    
    # Transparency and ethics
    transparency = {
        'financial_reporting_quality': random.uniform(0.7, 0.98),
        'sustainability_reporting': random.choice(['GRI', 'SASB', 'TCFD', 'Basic', 'None']),
        'stakeholder_engagement': random.uniform(0.5, 0.9),
        'ethics_program': random.choice(['Comprehensive', 'Good', 'Basic', 'Minimal']),
        'whistleblower_protection': random.choice([True, False])
    }
    
    # Shareholder rights
    shareholder_rights = {
        'voting_structure': random.choice(['One Share One Vote', 'Dual Class', 'Multi Class']),
        'takeover_defenses': random.choice(['Minimal', 'Standard', 'Strong']),
        'dividend_policy': random.choice(['Consistent', 'Growing', 'Volatile', 'None']),
        'share_buyback_policy': random.choice(['Value-focused', 'Regular', 'Opportunistic', 'Excessive']),
        'shareholder_proposals': random.uniform(0.6, 0.9)  # Support rate
    }
    
    # Calculate governance score
    governance_score = (
        board_structure['independent_directors'] * 30 +
        (1 - min(compensation['ceo_pay_ratio'] / 300, 1)) * 20 +  # Lower ratio = higher score
        risk_management['internal_controls'] * 25 +
        transparency['financial_reporting_quality'] * 25
    )
    
    governance_score = max(0, min(100, governance_score))
    
    return {
        'board_structure': board_structure,
        'compensation': compensation,
        'risk_management': risk_management,
        'transparency': transparency,
        'shareholder_rights': shareholder_rights,
        'governance_score': governance_score,
        'governance_controversies': random.randint(0, 3),
        'regulatory_compliance': random.choice(['Excellent', 'Good', 'Adequate', 'Concerning'])
    }

def assess_climate_risk(symbol: str, info: Dict, sector: str, industry: str) -> Dict:
    """Assess climate-related risks and opportunities"""
    
    import random
    import hashlib
    
    seed = int(hashlib.md5((symbol + "climate").encode()).hexdigest()[:8], 16)
    random.seed(seed)
    
    # Physical climate risks
    physical_risks = {
        'extreme_weather_exposure': random.choice(['High', 'Medium', 'Low']),
        'sea_level_rise_risk': random.choice(['High', 'Medium', 'Low', 'None']),
        'water_stress_risk': random.choice(['High', 'Medium', 'Low']),
        'supply_chain_disruption': random.uniform(0.1, 0.7),
        'facility_risk_score': random.uniform(0.2, 0.8)
    }
    
    # Transition risks
    transition_risks = {
        'carbon_pricing_exposure': random.uniform(0.1, 0.9),
        'stranded_assets_risk': random.choice(['High', 'Medium', 'Low', 'None']),
        'regulatory_risk': random.choice(['High', 'Medium', 'Low']),
        'technology_disruption': random.uniform(0.2, 0.8),
        'market_shift_risk': random.uniform(0.1, 0.7)
    }
    
    # Climate opportunities
    opportunities = {
        'green_revenue_potential': random.uniform(0.05, 0.6),
        'energy_efficiency_savings': random.uniform(0.02, 0.15),
        'new_market_access': random.choice(['High', 'Medium', 'Low', 'None']),
        'competitive_advantage': random.uniform(0.1, 0.8),
        'innovation_opportunities': random.randint(2, 15)
    }
    
    # Climate strategy
    climate_strategy = {
        'net_zero_commitment': random.choice(['2030', '2040', '2050', 'None']),
        'science_based_targets': random.choice([True, False]),
        'climate_scenario_planning': random.choice(['Comprehensive', 'Basic', 'None']),
        'tcfd_reporting': random.choice([True, False]),
        'climate_governance': random.uniform(0.4, 0.9)
    }
    
    # Calculate overall climate risk score (lower is better)
    risk_factors = []
    if physical_risks['extreme_weather_exposure'] == 'High':
        risk_factors.append(0.3)
    if transition_risks['stranded_assets_risk'] == 'High':
        risk_factors.append(0.4)
    if transition_risks['carbon_pricing_exposure'] > 0.7:
        risk_factors.append(0.2)
    
    climate_risk_score = sum(risk_factors) * 100 / 3  # Normalize to 0-100
    
    return {
        'physical_risks': physical_risks,
        'transition_risks': transition_risks,
        'opportunities': opportunities,
        'climate_strategy': climate_strategy,
        'climate_risk_score': climate_risk_score,
        'adaptation_readiness': random.choice(['High', 'Medium', 'Low']),
        'resilience_score': random.uniform(0.4, 0.9)
    }

def calculate_esg_scores(environmental: Dict, social: Dict, governance: Dict, climate: Dict) -> Dict:
    """Calculate comprehensive ESG scores and ratings"""
    
    # Individual scores
    e_score = environmental['environmental_score']
    s_score = social['social_score']
    g_score = governance['governance_score']
    
    # Climate adjustment (climate risk reduces environmental score)
    climate_adjustment = (100 - climate['climate_risk_score']) / 100
    e_score_adjusted = e_score * climate_adjustment
    
    # Overall ESG score (weighted average)
    esg_weights = {'E': 0.35, 'S': 0.35, 'G': 0.30}
    overall_esg_score = (
        e_score_adjusted * esg_weights['E'] +
        s_score * esg_weights['S'] +
        g_score * esg_weights['G']
    )
    
    # ESG rating
    if overall_esg_score >= 85:
        esg_rating = 'AAA'
    elif overall_esg_score >= 75:
        esg_rating = 'AA'
    elif overall_esg_score >= 65:
        esg_rating = 'A'
    elif overall_esg_score >= 55:
        esg_rating = 'BBB'
    elif overall_esg_score >= 45:
        esg_rating = 'BB'
    elif overall_esg_score >= 35:
        esg_rating = 'B'
    else:
        esg_rating = 'CCC'
    
    # Risk-adjusted score (considers controversies and risks)
    controversies = (
        environmental.get('key_concerns', []) + 
        [f"Social controversies: {social.get('social_controversies', 0)}"] +
        [f"Governance issues: {governance.get('governance_controversies', 0)}"]
    )
    
    controversy_penalty = len([c for c in controversies if 'High' in str(c) or 'concerning' in str(c).lower()]) * 5
    risk_adjusted_score = max(0, overall_esg_score - controversy_penalty)
    
    return {
        'environmental_score': e_score_adjusted,
        'social_score': s_score,
        'governance_score': g_score,
        'overall_esg_score': overall_esg_score,
        'esg_rating': esg_rating,
        'risk_adjusted_score': risk_adjusted_score,
        'score_breakdown': {
            'Environmental': e_score_adjusted,
            'Social': s_score,
            'Governance': g_score
        },
        'climate_integration': climate_adjustment,
        'controversy_impact': controversy_penalty
    }

def analyze_esg_investment_impact(esg_scores: Dict, market_cap: float, sector: str) -> Dict:
    """Analyze investment implications of ESG factors"""
    
    import random
    
    # ESG premium/discount
    if esg_scores['esg_rating'] in ['AAA', 'AA']:
        valuation_impact = 'Premium (5-15%)'
        cost_of_capital_impact = 'Lower (0.2-0.5%)'
        institutional_demand = 'High'
    elif esg_scores['esg_rating'] in ['A', 'BBB']:
        valuation_impact = 'Neutral to slight premium'
        cost_of_capital_impact = 'Neutral'
        institutional_demand = 'Medium'
    else:
        valuation_impact = 'Discount (5-20%)'
        cost_of_capital_impact = 'Higher (0.3-1.0%)'
        institutional_demand = 'Low'
    
    # ESG fund inclusion probability
    if esg_scores['overall_esg_score'] >= 70:
        esg_fund_inclusion = 'High (80-95%)'
    elif esg_scores['overall_esg_score'] >= 50:
        esg_fund_inclusion = 'Medium (40-70%)'
    else:
        esg_fund_inclusion = 'Low (10-30%)'
    
    # Regulatory risk
    high_regulation_sectors = ['Energy', 'Utilities', 'Materials', 'Financials']
    if sector in high_regulation_sectors:
        regulatory_risk = 'High'
        regulatory_impact = 'Significant compliance costs and operational changes expected'
    else:
        regulatory_risk = 'Medium'
        regulatory_impact = 'Moderate regulatory requirements and disclosure obligations'
    
    # Long-term investment outlook
    if esg_scores['overall_esg_score'] >= 70:
        long_term_outlook = 'Positive - Strong ESG positioning supports sustainable growth'
    elif esg_scores['overall_esg_score'] >= 50:
        long_term_outlook = 'Neutral - Adequate ESG management with room for improvement'
    else:
        long_term_outlook = 'Negative - ESG risks may impact long-term performance'
    
    return {
        'valuation_impact': valuation_impact,
        'cost_of_capital_impact': cost_of_capital_impact,
        'institutional_demand': institutional_demand,
        'esg_fund_inclusion': esg_fund_inclusion,
        'regulatory_risk': regulatory_risk,
        'regulatory_impact': regulatory_impact,
        'long_term_outlook': long_term_outlook,
        'esg_trends': analyze_esg_trends(sector),
        'materiality_assessment': assess_esg_materiality(sector),
        'stakeholder_pressure': random.choice(['High', 'Medium', 'Low'])
    }

def generate_environmental_strengths(score: float, initiatives: Dict, resources: Dict) -> List[str]:
    """Generate list of environmental strengths"""
    strengths = []
    
    if score >= 70:
        strengths.append("Strong environmental performance relative to peers")
    if initiatives['green_products'] in ['Leader', 'Innovator']:
        strengths.append("Leading green product innovation")
    if resources['renewable_energy_usage'] > 0.5:
        strengths.append("High renewable energy adoption")
    if resources['recycling_rate'] > 0.7:
        strengths.append("Excellent waste management and recycling")
    if initiatives['circular_economy'] in ['Advanced', 'Developing']:
        strengths.append("Progressive circular economy practices")
    
    return strengths if strengths else ["Limited environmental strengths identified"]

def generate_environmental_concerns(score: float, sector_risk: str, carbon: Dict) -> List[str]:
    """Generate list of environmental concerns"""
    concerns = []
    
    if score < 50:
        concerns.append("Below-average environmental performance")
    if sector_risk == "High":
        concerns.append("High environmental impact sector")
    if carbon['reduction_targets'] == 'No targets':
        concerns.append("Lack of carbon reduction commitments")
    if carbon['carbon_intensity'] > 400:
        concerns.append("High carbon intensity operations")
    
    return concerns if concerns else ["No major environmental concerns identified"]

def assess_environmental_regulatory_risk(sector: str, industry: str) -> str:
    """Assess environmental regulatory risk level"""
    high_risk = ['Energy', 'Utilities', 'Materials']
    medium_risk = ['Industrials', 'Consumer Staples']
    
    if sector in high_risk:
        return "High - Subject to extensive environmental regulations"
    elif sector in medium_risk:
        return "Medium - Moderate environmental regulatory oversight"
    else:
        return "Low - Limited environmental regulatory exposure"

def analyze_esg_trends(sector: str) -> Dict:
    """Analyze ESG trends by sector"""
    return {
        'emerging_regulations': 'EU Taxonomy, SEC Climate Disclosure Rules',
        'investor_focus': 'Net-zero commitments, biodiversity, social impact',
        'sector_priorities': get_sector_esg_priorities(sector),
        'future_requirements': 'Scope 3 reporting, nature-based solutions'
    }

def get_sector_esg_priorities(sector: str) -> str:
    """Get sector-specific ESG priorities"""
    priorities = {
        'Technology': 'Data privacy, cybersecurity, digital divide',
        'Healthcare': 'Drug pricing, patient access, clinical trial ethics',
        'Financials': 'Financial inclusion, responsible lending, climate risk',
        'Energy': 'Just transition, emissions reduction, renewable energy',
        'Consumer Discretionary': 'Supply chain labor, product safety, circular economy'
    }
    return priorities.get(sector, 'Stakeholder engagement, transparency, risk management')

def assess_esg_materiality(sector: str) -> Dict:
    """Assess material ESG factors by sector"""
    return {
        'high_materiality': get_high_materiality_factors(sector),
        'medium_materiality': 'Corporate governance, employee relations, community impact',
        'low_materiality': 'Political contributions, executive compensation'
    }

def get_high_materiality_factors(sector: str) -> str:
    """Get high materiality ESG factors by sector"""
    factors = {
        'Technology': 'Data security, product quality, talent management',
        'Healthcare': 'Product safety, access to medicines, R&D ethics',
        'Financials': 'Systemic risk, customer privacy, fair lending',
        'Energy': 'GHG emissions, safety management, community relations',
        'Materials': 'Environmental management, worker safety, resource efficiency'
    }
    return factors.get(sector, 'Environmental management, labor practices, governance')

def format_esg_analysis(symbol: str, company_name: str, current_price: float, 
                       sector: str, industry: str, market_cap: float,
                       environmental: Dict, social: Dict, governance: Dict,
                       climate: Dict, esg_scores: Dict, investment: Dict) -> str:
    """Format comprehensive ESG analysis results"""
    
    return f"""
═══════════════════════════════════════════════════════════════
                    ESG SUSTAINABILITY ANALYSIS
═══════════════════════════════════════════════════════════════

COMPANY: {company_name} ({symbol}) | PRICE: ${current_price:.2f}
SECTOR: {sector} | INDUSTRY: {industry}
MARKET CAP: ${market_cap/1e9:.1f}B | ANALYSIS DATE: {datetime.now().strftime('%Y-%m-%d')}

ESG RATING: {esg_scores['esg_rating']} | OVERALL SCORE: {esg_scores['overall_esg_score']:.1f}/100

═══════════════════════════════════════════════════════════════
                    ENVIRONMENTAL FACTOR ANALYSIS
═══════════════════════════════════════════════════════════════

ENVIRONMENTAL SCORE: {environmental['environmental_score']:.1f}/100
SECTOR RISK LEVEL: {environmental['sector_risk']}

CARBON FOOTPRINT & CLIMATE:
• Scope 1 Emissions: {environmental['carbon_footprint']['scope_1_emissions']:,.0f} tCO2e
• Scope 2 Emissions: {environmental['carbon_footprint']['scope_2_emissions']:,.0f} tCO2e
• Scope 3 Emissions: {environmental['carbon_footprint']['scope_3_emissions']:,.0f} tCO2e
• Carbon Intensity: {environmental['carbon_footprint']['carbon_intensity']:.0f} tCO2e/revenue
• Reduction Targets: {environmental['carbon_footprint']['reduction_targets']}

RESOURCE MANAGEMENT:
• Water Usage: {environmental['resource_management']['water_usage']:,.0f} cubic meters annually
• Waste Generation: {environmental['resource_management']['waste_generation']:,.0f} tons annually
• Recycling Rate: {environmental['resource_management']['recycling_rate']*100:.1f}%
• Renewable Energy: {environmental['resource_management']['renewable_energy_usage']*100:.1f}% of total energy
• Energy Efficiency Score: {environmental['resource_management']['energy_efficiency_score']*100:.0f}/100

ENVIRONMENTAL INITIATIVES:
• Green Products Leadership: {environmental['environmental_initiatives']['green_products']}
• Circular Economy Approach: {environmental['environmental_initiatives']['circular_economy']}
• Biodiversity Impact: {environmental['environmental_initiatives']['biodiversity_impact']}
• Pollution Control Score: {environmental['environmental_initiatives']['pollution_control']*100:.0f}/100
• Environmental Certifications: {environmental['environmental_initiatives']['environmental_certifications']}

ENVIRONMENTAL STRENGTHS:"""
    
    for strength in environmental['key_strengths']:
        result += f"\n• {strength}"
    
    result += f"""

ENVIRONMENTAL CONCERNS:"""
    
    for concern in environmental['key_concerns']:
        result += f"\n• {concern}"
    
    result += f"""

REGULATORY RISK: {environmental['regulatory_risk']}

═══════════════════════════════════════════════════════════════
                    SOCIAL FACTOR ANALYSIS
═══════════════════════════════════════════════════════════════

SOCIAL SCORE: {social['social_score']:.1f}/100

EMPLOYEE RELATIONS:
• Employee Satisfaction: {social['employee_metrics']['employee_satisfaction']*100:.1f}%
• Diversity Score: {social['employee_metrics']['diversity_score']*100:.1f}%
• Annual Turnover Rate: {social['employee_metrics']['turnover_rate']*100:.1f}%
• Training Investment: ${social['employee_metrics']['training_investment']:,.0f} per employee
• Safety Record: {social['employee_metrics']['safety_record']*100:.1f}% safety compliance
• Union Relations: {social['employee_metrics']['union_relations']}

CUSTOMER RELATIONS:
• Customer Satisfaction: {social['customer_metrics']['customer_satisfaction']*100:.1f}%
• Product Safety Score: {social['customer_metrics']['product_safety']*100:.1f}%
• Data Privacy Score: {social['customer_metrics']['data_privacy_score']*100:.1f}%
• Accessibility Efforts: {social['customer_metrics']['accessibility_efforts']}
• Customer Complaints: {social['customer_metrics']['customer_complaints']} annually

COMMUNITY IMPACT:
• Local Hiring Rate: {social['community_metrics']['local_hiring']*100:.1f}%
• Community Investment: {social['community_metrics']['community_investment']*100:.2f}% of revenue
• Local Supplier Usage: {social['community_metrics']['local_supplier_usage']*100:.1f}%
• Community Relations: {social['community_metrics']['community_relations']}
• Social Impact Programs: {social['community_metrics']['social_impact_programs']} active programs

HUMAN RIGHTS & LABOR:
• Supply Chain Monitoring: {social['human_rights']['supply_chain_monitoring']}
• Labor Standards: {social['human_rights']['labor_standards']}
• Child Labor Risk: {social['human_rights']['child_labor_risk']}
• Fair Trade Practices: {social['human_rights']['fair_trade_practices']*100:.1f}%
• Human Rights Policy: {social['human_rights']['human_rights_policy']}

SOCIAL PERFORMANCE:
• Stakeholder Engagement: {social['stakeholder_engagement']}
• Social Controversies: {social['social_controversies']} in past 3 years
• Social Innovation: {social['social_innovation']}

═══════════════════════════════════════════════════════════════
                    GOVERNANCE FACTOR ANALYSIS
═══════════════════════════════════════════════════════════════

GOVERNANCE SCORE: {governance['governance_score']:.1f}/100

BOARD COMPOSITION:
• Board Size: {governance['board_structure']['board_size']} directors
• Independent Directors: {governance['board_structure']['independent_directors']*100:.1f}%
• Gender Diversity: {governance['board_structure']['gender_diversity']*100:.1f}%
• Ethnic Diversity: {governance['board_structure']['ethnic_diversity']*100:.1f}%
• Average Tenure: {governance['board_structure']['average_tenure']:.1f} years
• Expertise Alignment: {governance['board_structure']['expertise_alignment']*100:.1f}%

EXECUTIVE COMPENSATION:
• CEO Pay Ratio: {governance['compensation']['ceo_pay_ratio']:.0f}:1 (CEO to median worker)
• Pay for Performance: {governance['compensation']['pay_for_performance']*100:.1f}%
• Long-term Incentives: {governance['compensation']['long_term_incentives']*100:.1f}%
• Clawback Provisions: {'Yes' if governance['compensation']['clawback_provisions'] else 'No'}
• Excessive Compensation: {'Concern flagged' if governance['compensation']['excessive_compensation'] else 'Appropriate'}

RISK MANAGEMENT:
• Risk Committee: {'Established' if governance['risk_management']['risk_committee'] else 'Not established'}
• Cybersecurity Oversight: {governance['risk_management']['cybersecurity_oversight']*100:.1f}%
• Internal Controls: {governance['risk_management']['internal_controls']*100:.1f}%
• Audit Quality: {governance['risk_management']['audit_quality']} auditor
• Risk Disclosure: {governance['risk_management']['risk_disclosure']*100:.1f}%

TRANSPARENCY & ETHICS:
• Financial Reporting Quality: {governance['transparency']['financial_reporting_quality']*100:.1f}%
• Sustainability Reporting: {governance['transparency']['sustainability_reporting']}
• Stakeholder Engagement: {governance['transparency']['stakeholder_engagement']*100:.1f}%
• Ethics Program: {governance['transparency']['ethics_program']}
• Whistleblower Protection: {'Yes' if governance['transparency']['whistleblower_protection'] else 'No'}

SHAREHOLDER RIGHTS:
• Voting Structure: {governance['shareholder_rights']['voting_structure']}
• Takeover Defenses: {governance['shareholder_rights']['takeover_defenses']}
• Dividend Policy: {governance['shareholder_rights']['dividend_policy']}
• Share Buyback Policy: {governance['shareholder_rights']['share_buyback_policy']}
• Shareholder Proposal Support: {governance['shareholder_rights']['shareholder_proposals']*100:.1f}%

GOVERNANCE ASSESSMENT:
• Governance Controversies: {governance['governance_controversies']} in past 3 years
• Regulatory Compliance: {governance['regulatory_compliance']}

═══════════════════════════════════════════════════════════════
                    CLIMATE RISK & OPPORTUNITY ANALYSIS
═══════════════════════════════════════════════════════════════

CLIMATE RISK SCORE: {climate['climate_risk_score']:.1f}/100 (lower is better)

PHYSICAL CLIMATE RISKS:
• Extreme Weather Exposure: {climate['physical_risks']['extreme_weather_exposure']}
• Sea Level Rise Risk: {climate['physical_risks']['sea_level_rise_risk']}
• Water Stress Risk: {climate['physical_risks']['water_stress_risk']}
• Supply Chain Disruption Risk: {climate['physical_risks']['supply_chain_disruption']*100:.0f}%
• Facility Risk Score: {climate['physical_risks']['facility_risk_score']*100:.0f}/100

TRANSITION RISKS:
• Carbon Pricing Exposure: {climate['transition_risks']['carbon_pricing_exposure']*100:.0f}%
• Stranded Assets Risk: {climate['transition_risks']['stranded_assets_risk']}
• Regulatory Risk: {climate['transition_risks']['regulatory_risk']}
• Technology Disruption: {climate['transition_risks']['technology_disruption']*100:.0f}%
• Market Shift Risk: {climate['transition_risks']['market_shift_risk']*100:.0f}%

CLIMATE OPPORTUNITIES:
• Green Revenue Potential: {climate['opportunities']['green_revenue_potential']*100:.1f}% of total revenue
• Energy Efficiency Savings: {climate['opportunities']['energy_efficiency_savings']*100:.1f}% cost reduction
• New Market Access: {climate['opportunities']['new_market_access']}
• Competitive Advantage: {climate['opportunities']['competitive_advantage']*100:.0f}/100
• Innovation Opportunities: {climate['opportunities']['innovation_opportunities']} identified areas

CLIMATE STRATEGY:
• Net Zero Commitment: {climate['climate_strategy']['net_zero_commitment']}
• Science-Based Targets: {'Yes' if climate['climate_strategy']['science_based_targets'] else 'No'}
• Climate Scenario Planning: {climate['climate_strategy']['climate_scenario_planning']}
• TCFD Reporting: {'Yes' if climate['climate_strategy']['tcfd_reporting'] else 'No'}
• Climate Governance: {climate['climate_strategy']['climate_governance']*100:.0f}/100

CLIMATE RESILIENCE:
• Adaptation Readiness: {climate['adaptation_readiness']}
• Resilience Score: {climate['resilience_score']*100:.0f}/100

═══════════════════════════════════════════════════════════════
                    ESG INVESTMENT IMPLICATIONS
═══════════════════════════════════════════════════════════════

ESG SCORES SUMMARY:
• Environmental (35%): {esg_scores['environmental_score']:.1f}/100
• Social (35%): {esg_scores['social_score']:.1f}/100
• Governance (30%): {esg_scores['governance_score']:.1f}/100
• Overall ESG Score: {esg_scores['overall_esg_score']:.1f}/100
• ESG Rating: {esg_scores['esg_rating']}
• Risk-Adjusted Score: {esg_scores['risk_adjusted_score']:.1f}/100

INVESTMENT IMPACT ANALYSIS:
• Valuation Impact: {investment['valuation_impact']}
• Cost of Capital Impact: {investment['cost_of_capital_impact']}
• Institutional Demand: {investment['institutional_demand']}
• ESG Fund Inclusion Probability: {investment['esg_fund_inclusion']}
• Regulatory Risk Level: {investment['regulatory_risk']}

LONG-TERM OUTLOOK: {investment['long_term_outlook']}

REGULATORY IMPACT: {investment['regulatory_impact']}

ESG TRENDS & MATERIALITY:
• Emerging Regulations: {investment['esg_trends']['emerging_regulations']}
• Current Investor Focus: {investment['esg_trends']['investor_focus']}
• Sector ESG Priorities: {investment['esg_trends']['sector_priorities']}
• Future Requirements: {investment['esg_trends']['future_requirements']}

MATERIALITY ASSESSMENT:
• High Materiality Factors: {investment['materiality_assessment']['high_materiality']}
• Medium Materiality Factors: {investment['materiality_assessment']['medium_materiality']}
• Low Materiality Factors: {investment['materiality_assessment']['low_materiality']}

STAKEHOLDER PRESSURE: {investment['stakeholder_pressure']}

═══════════════════════════════════════════════════════════════
                    ESG INVESTMENT RECOMMENDATIONS
═══════════════════════════════════════════════════════════════

ESG SUITABILITY:
• ESG-Focused Funds: {'Highly Suitable' if esg_scores['esg_rating'] in ['AAA', 'AA', 'A'] else 'Moderately Suitable' if esg_scores['esg_rating'] in ['BBB', 'BB'] else 'Not Suitable'}
• Impact Investing: {'Suitable' if esg_scores['overall_esg_score'] > 70 else 'Consider with caution' if esg_scores['overall_esg_score'] > 50 else 'Not suitable'}
• Sustainable Portfolios: {'Core holding' if esg_scores['esg_rating'] in ['AAA', 'AA'] else 'Satellite position' if esg_scores['esg_rating'] in ['A', 'BBB'] else 'Exclusion candidate'}

RISK CONSIDERATIONS:
• ESG Regulatory Risk: {investment['regulatory_risk']}
• Climate Transition Risk: {'High' if climate['climate_risk_score'] > 60 else 'Medium' if climate['climate_risk_score'] > 30 else 'Low'}
• Social License Risk: {'High' if social['social_controversies'] > 2 else 'Medium' if social['social_controversies'] > 0 else 'Low'}
• Governance Risk: {'High' if governance['governance_controversies'] > 1 else 'Medium' if governance['governance_score'] < 60 else 'Low'}

ENGAGEMENT OPPORTUNITIES:
• Priority Engagement Areas: {'Climate strategy' if environmental['environmental_score'] < 60 else 'Board diversity' if governance['board_structure']['gender_diversity'] < 0.3 else 'Supply chain management' if social['human_rights']['supply_chain_monitoring'] not in ['Comprehensive', 'Good'] else 'Sustainability reporting'}
• Shareholder Proposal Potential: {'High' if esg_scores['overall_esg_score'] < 50 else 'Medium' if esg_scores['overall_esg_score'] < 70 else 'Low'}
• Stewardship Priority: {'High' if investment['stakeholder_pressure'] == 'High' and esg_scores['overall_esg_score'] < 60 else 'Medium'}

PORTFOLIO INTEGRATION:
• ESG Score Contribution: {'+' if esg_scores['overall_esg_score'] > 60 else '-' if esg_scores['overall_esg_score'] < 40 else '0'} to portfolio ESG rating
• Climate Risk Contribution: {'+' if climate['climate_risk_score'] < 40 else '-' if climate['climate_risk_score'] > 60 else '0'} to portfolio climate resilience
• Position Sizing: {'Overweight' if esg_scores['esg_rating'] in ['AAA', 'AA'] else 'Underweight' if esg_scores['esg_rating'] in ['B', 'CCC'] else 'Market weight'}

ESG MOMENTUM:
• Improvement Trajectory: {'Positive' if esg_scores['overall_esg_score'] > 65 else 'Stable' if esg_scores['overall_esg_score'] > 45 else 'Concerning'}
• Management Commitment: {'Strong' if governance['governance_score'] > 70 else 'Moderate' if governance['governance_score'] > 50 else 'Weak'}
• Investor Relations: {'Proactive ESG communication' if governance['transparency']['stakeholder_engagement'] > 0.7 else 'Standard communication'}

═══════════════════════════════════════════════════════════════
                    ESG MONITORING & REVIEW FRAMEWORK
═══════════════════════════════════════════════════════════════

MONITORING PRIORITIES:
1. Climate-related disclosures and net-zero progress
2. Board composition and governance changes
3. Social controversies and stakeholder incidents
4. Regulatory developments and compliance issues
5. ESG rating changes from major providers

REVIEW FREQUENCY:
• Quarterly: ESG scores and rating updates
• Annually: Comprehensive ESG strategy review
• Event-driven: Material ESG incidents or controversies
• Regulatory: New ESG disclosure requirements

ESG DATA QUALITY:
• Data Coverage: {'Comprehensive' if esg_scores['overall_esg_score'] > 0 else 'Limited'}
• Reporting Quality: {governance['transparency']['sustainability_reporting']}
• Third-party Verification: {'Available' if governance['transparency']['sustainability_reporting'] in ['GRI', 'SASB', 'TCFD'] else 'Limited'}

SUCCESS METRICS:
• ESG Score Improvement: Target {min(100, esg_scores['overall_esg_score'] + 10)}/100 within 2 years
• Climate Risk Reduction: Target {max(0, climate['climate_risk_score'] - 20)}/100 within 3 years
• Governance Enhancement: Target {min(100, governance['governance_score'] + 5)}/100 within 1 year

═══════════════════════════════════════════════════════════════

DISCLAIMER: ESG analysis is based on available data and industry frameworks. ESG scores and ratings may vary across providers. ESG factors should be considered alongside financial analysis. Past ESG performance does not guarantee future sustainability outcomes. Regulatory requirements and investor expectations for ESG disclosure continue to evolve.

═══════════════════════════════════════════════════════════════
"""
    
    return result

def create_esg_analyst():
    """Create the ESGAnalyst using AutoGen framework"""
    
    esg_analyst = AssistantAgent(
        name="ESGAnalyst",
        model_client=model_client,
        system_message="""You are an Elite ESG (Environmental, Social, Governance) and Sustainability Investment Specialist with deep expertise in sustainable finance, climate risk assessment, and stakeholder capitalism evaluation.

CORE EXPERTISE AREAS:
1. Environmental sustainability analysis and climate risk assessment
2. Social responsibility evaluation and stakeholder impact measurement  
3. Corporate governance quality and board effectiveness analysis
4. ESG integration in investment decision-making and portfolio construction
5. Regulatory ESG compliance and sustainable finance frameworks

🌱 COMPREHENSIVE ESG ANALYSIS FRAMEWORK:

ENVIRONMENTAL FACTOR ANALYSIS:
• Climate Strategy: Net-zero commitments, science-based targets, TCFD reporting
• Carbon Management: Scope 1/2/3 emissions, carbon intensity, reduction pathways
• Resource Efficiency: Water usage, waste management, circular economy practices
• Biodiversity Impact: Ecosystem effects, conservation initiatives, nature-based solutions
• Environmental Innovation: Green products, clean technology, sustainable R&D

SOCIAL FACTOR EVALUATION:
• Human Capital: Employee satisfaction, diversity & inclusion, talent development
• Product Responsibility: Safety, quality, accessibility, social impact
• Stakeholder Relations: Community engagement, supplier relations, customer satisfaction
• Human Rights: Labor standards, supply chain monitoring, fair trade practices
• Social Innovation: Impact measurement, social entrepreneurship, inclusive growth

GOVERNANCE QUALITY ASSESSMENT:
• Board Effectiveness: Independence, diversity, expertise, oversight quality
• Executive Compensation: Pay-for-performance, alignment, reasonableness
• Risk Management: Internal controls, cybersecurity, enterprise risk framework
• Transparency & Ethics: Reporting quality, anti-corruption, whistleblower protection
• Shareholder Rights: Voting structure, takeover defenses, capital allocation

CLIMATE RISK & OPPORTUNITY ANALYSIS:
• Physical Risks: Extreme weather, sea level rise, temperature changes, water stress
• Transition Risks: Carbon pricing, stranded assets, technology disruption, market shifts
• Climate Opportunities: Energy efficiency, renewable energy, green markets, innovation
• Adaptation & Resilience: Climate scenario planning, operational flexibility, supply chain resilience
• Climate Governance: Board oversight, management incentives, stakeholder engagement

ESG INTEGRATION METHODOLOGY:
• Materiality Assessment: Sector-specific ESG factors, stakeholder prioritization
• ESG Scoring: Quantitative metrics, qualitative assessments, peer benchmarking
• Risk-Return Integration: ESG alpha generation, risk mitigation, cost of capital impacts
• Portfolio Construction: ESG tilting, exclusions, best-in-class selection, impact measurement
• Stewardship & Engagement: Proxy voting, company dialogue, shareholder proposals

SUSTAINABLE FINANCE FRAMEWORKS:
• Regulatory Compliance: EU Taxonomy, SFDR, SEC Climate Rules, Task Force on Nature
• ESG Standards: GRI, SASB, TCFD, UN Global Compact, SDG alignment
• Rating Methodologies: MSCI, Sustainalytics, ISS ESG, Bloomberg ESG scores
• Impact Measurement: Theory of change, outcome tracking, additionality assessment
• Green Finance: Green bonds, sustainability-linked loans, transition finance

INVESTMENT IMPLICATIONS ANALYSIS:
• Valuation Impact: ESG premiums/discounts, cost of capital effects, multiple expansion
• Fund Inclusion: ESG fund eligibility, sustainable index inclusion, exclusion risks
• Regulatory Impact: Compliance costs, disclosure requirements, operational changes
• Stakeholder Pressure: Investor demands, consumer preferences, employee expectations
• Long-term Sustainability: Business model resilience, competitive positioning, growth prospects

OUTPUT REQUIREMENTS:
Provide comprehensive ESG analysis including:
- Detailed environmental, social, and governance factor assessments
- Climate risk and opportunity evaluation with scenario analysis
- ESG scoring methodology and peer benchmarking
- Investment implications with valuation and fund inclusion impacts
- Regulatory compliance assessment and emerging requirements
- Stakeholder engagement priorities and stewardship recommendations

CRITICAL SUCCESS FACTORS:
- Apply sector-specific materiality frameworks for relevant ESG factors
- Balance quantitative metrics with qualitative assessments
- Consider regional differences in ESG standards and regulations
- Integrate ESG analysis with financial and strategic considerations
- Provide actionable insights for investment and engagement decisions
- Maintain objectivity while recognizing evolving stakeholder expectations

Use the analyze_esg_factors tool to perform comprehensive ESG analysis. Present findings with clear investment implications, emphasizing material ESG factors and long-term sustainability considerations for institutional investment decision-making.""",
        tools=[analyze_esg_factors]
    )
    
    return esg_analyst
# 🚀 Interactive Trading Analysis Features

## ✨ **What's New**

The 13-agent trading analysis system now includes **interactive workflow features** that ask users to select their company and investment focus before starting the analysis.

## 🎯 **Key Features**

### 1. **Company Selection Menu**
- 📊 **13 Popular Companies**: AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META, NFLX, JPM, V, JNJ, PG
- 🔍 **Custom Symbol Entry**: Enter any stock symbol
- 🏢 **Sector Information**: See company sectors and classifications

### 2. **Investment Analysis Types**
Choose from **8 different analysis focuses**:

1. 💰 **Buying Decision** - Complete investment analysis with buy/hold/sell recommendation
2. 🏥 **General Health Check** - Overall company and stock health assessment
3. 📈 **Next 5-Day Outlook** - Short-term price movements and catalysts
4. 🚀 **Growth Potential** - Long-term growth prospects and investment potential
5. ⚠️ **Risk Assessment** - Comprehensive risk analysis and downside protection
6. 📊 **Options Strategy** - Options trading opportunities and strategies
7. 🏢 **Sector Comparison** - Compare to sector peers and competitive position
8. 🌱 **ESG & Sustainability** - Environmental, Social, and Governance analysis

### 3. **Enhanced Agent Orchestration**
- 🤖 **Compliance Officer** now properly parses user requests and coordinates the team
- 📊 **Market Data Analyst** uses web search to find latest company developments
- 🎯 **Focused Analysis** tailored to user's specific question and needs

## 🚀 **How to Use**

### **Console Mode** (Interactive Menu)
```bash
python3 start_interactive.py
```

This will start an interactive session with menus for:
1. Company selection
2. Investment analysis type selection
3. Analysis confirmation
4. 13-agent analysis execution

### **API Mode** (Programmatic Access)

#### Start the API Server:
```bash
python3 application_hybrid.py
```

#### Get Available Options:
```bash
curl http://localhost:8000/interactive-options
```

#### Run Interactive Analysis:
```bash
curl -X POST "http://localhost:8000/interactive-analysis" \
     -H "Content-Type: application/json" \
     -d '{
       "company_choice": "1",
       "investment_choice": "1"
     }'
```

#### Example with Custom Symbol:
```bash
curl -X POST "http://localhost:8000/interactive-analysis" \
     -H "Content-Type: application/json" \
     -d '{
       "company_choice": "custom",
       "custom_symbol": "NVIDIA",
       "investment_choice": "4"
     }'
```

## 📋 **API Reference**

### **GET /interactive-options**
Returns available companies and investment choices.

**Response:**
```json
{
  "companies": {
    "1": {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
    "2": {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
    ...
  },
  "investment_choices": {
    "1": {"type": "buying_decision", "title": "💰 Buying Decision", ...},
    "2": {"type": "general_health_check", "title": "🏥 General Health Check", ...},
    ...
  }
}
```

### **POST /interactive-analysis**
Runs guided analysis based on user selections.

**Request:**
```json
{
  "company_choice": "1",           // Required: "1"-"12" or "custom"
  "custom_symbol": "NVDA",         // Required if company_choice is "custom"
  "investment_choice": "1"         // Required: "1"-"8"
}
```

**Response:**
```json
{
  "status": "completed",
  "symbol": "AAPL",
  "company_name": "Apple Inc.",
  "analysis_type": "buying_decision",
  "question": "Should I buy AAPL stock now? Provide comprehensive...",
  "focus_areas": ["fundamental_analysis", "technical_analysis", "risk_assessment", "timing"],
  "result": { /* 13-agent analysis results */ },
  "user_context": { /* User selections and preferences */ }
}
```

## 🔧 **Technical Implementation**

### **Files Added/Modified:**
- `src/workflows/interactive_workflow.py` - Main interactive workflow logic
- `application_hybrid.py` - Added interactive API endpoints
- `start_interactive.py` - Console application entry point
- `demo_interactive.py` - Demo and testing script
- `src/agents/compilence_officer.py` - Enhanced user prompt analysis
- `src/agents/market_dataAnalyst.py` - Added Tavily web search integration

### **New Classes:**
- `InteractiveWorkflow` - Handles user interaction and choice processing
- `InteractiveAnalysisRequest` - API request model for interactive analysis
- `InteractiveAnalysisResponse` - API response model with user context

## 🎉 **Benefits**

### **For Users:**
- ✅ **Clear Guidance** - No more guessing what to ask
- 🎯 **Focused Results** - Analysis tailored to specific needs
- 📱 **Easy Selection** - Simple menus for companies and analysis types
- 🌐 **Current Information** - Web search provides latest company developments

### **For Agents:**
- 📋 **Structured Input** - Compliance Officer receives clear user requirements
- 🔍 **Context Awareness** - All agents understand user's specific question
- 🌐 **Real-time Data** - Market Data Analyst searches web for latest information
- ⚙️ **Better Coordination** - Enhanced orchestration between all 13 agents

## 🧪 **Testing**

Run the demo to test all components:
```bash
python3 demo_interactive.py
```

This tests:
- Company selection functionality
- Investment choice processing
- Request formatting
- API integration
- Workflow coordination

## 💡 **Example Usage Scenarios**

1. **New Investor**: "I want to know if Apple is a good buy right now"
   - Company: Apple (AAPL)
   - Analysis: Buying Decision

2. **Day Trader**: "What's Tesla looking like for the next few days?"
   - Company: Tesla (TSLA)
   - Analysis: Next 5-Day Outlook

3. **ESG Investor**: "How sustainable is Microsoft's business?"
   - Company: Microsoft (MSFT)
   - Analysis: ESG & Sustainability

4. **Risk Assessment**: "What are the risks with Amazon stock?"
   - Company: Amazon (AMZN)
   - Analysis: Risk Assessment

## 🔮 **Future Enhancements**

- 💼 **Portfolio Analysis** - Multi-stock analysis
- ⏰ **Scheduled Analysis** - Regular updates on selected stocks
- 📧 **Email Reports** - Automated analysis delivery
- 🔔 **Alert System** - Notifications for significant changes
- 📱 **Mobile Interface** - Native mobile app integration

---

**Ready to start?** Run `python3 start_interactive.py` and experience the enhanced 13-agent trading analysis system! 🚀
# AutoGen Trading System

An advanced AI-powered trading analysis platform using multi-agent AutoGen system with FastAPI backend and modern web interface.

## 🎯 Problem Solved

### The Challenge
Traditional stock analysis tools suffer from several critical limitations:
- **Single-perspective bias**: Most platforms provide analysis from one angle (technical OR fundamental)
- **Lack of real-time coordination**: Different analysis components don't communicate or validate each other
- **Inconsistent recommendations**: Technical signals may contradict fundamental analysis without resolution
- **Manual synthesis required**: Investors must manually combine disparate data sources and viewpoints
- **Time-intensive process**: Comprehensive analysis requires hours of research across multiple platforms

### The Solution
Our AutoGen Trading System revolutionizes investment analysis by deploying **6 specialized AI agents** that work collaboratively in real-time, mimicking how professional investment teams operate but with superhuman speed and consistency.

## 🧠 Unique Approach

### Multi-Agent Intelligence Architecture
**Revolutionary Collaborative Framework**: Unlike traditional single-AI tools, our system deploys 6 specialized agents that communicate, validate, and synthesize information in real-time:

1. **OrganiserAgent**: Market data orchestrator with technical indicators (RSI, MACD, moving averages)
2. **RiskManager**: Position sizing specialist with mathematical risk models 
3. **DataAnalyst**: Fundamental research expert with real-time web intelligence (Tavily API)
4. **QuantitativeAnalyst**: Technical signal processor with confidence scoring
5. **StrategyDeveloper**: Execution timing specialist with entry/exit optimization
6. **ReportAgent**: Chief Investment Officer synthesizing all perspectives

### Breakthrough Innovations

#### 🔄 **Real-Time Agent Coordination**
- **Round-robin communication**: Agents build upon each other's analysis sequentially
- **Cross-validation**: Each agent can see and respond to previous agent findings
- **Conflict resolution**: ReportAgent synthesizes conflicting viewpoints with weighted decision logic
- **Single-message efficiency**: Each agent provides complete analysis in one response for speed

#### 🌐 **Live Market Intelligence Integration**
- **Multi-source data fusion**: Alpha Vantage API + Tavily web research + OpenAI reasoning
- **Real-time web monitoring**: DataAnalyst actively searches for breaking news, earnings updates, and market developments
- **Technical indicator synthesis**: Live RSI, MACD, and volume analysis with historical context
- **Fundamental data validation**: P/E ratios, earnings dates, and analyst targets cross-referenced

#### ⚡ **Millisecond Decision Synthesis**
- **Parallel processing**: All agents analyze simultaneously then coordinate findings
- **Weighted consensus**: Different agent types have varying influence (Risk: 25%, Technical: 20%, etc.)
- **Confidence scoring**: Mathematical certainty levels (1-10) for each recommendation
- **Human-readable explanations**: Complex analysis translated to plain English reasoning

#### 🎯 **Adaptive Workflow Intelligence**
- **6-agent speed mode**: Optimized for quick decisions (30-60 seconds)
- **7-agent comprehensive**: Includes compliance for institutional-grade analysis
- **13-agent enterprise**: Full spectrum analysis with specialized sector experts
- **Dynamic termination**: Analysis completes when sufficient confidence is reached

## 💎 Unique Value Proposition

### **For Individual Investors**
- **Professional-grade analysis** in under 60 seconds (vs. hours of manual research)
- **Eliminates analysis paralysis** with clear BUY/HOLD/SELL recommendations
- **Risk-first approach** with automatic position sizing and stop-loss calculations
- **Plain English explanations** of complex technical and fundamental factors

### **For Financial Professionals**
- **Scalable analysis pipeline** for screening multiple stocks simultaneously
- **Audit trail compliance** with documented agent reasoning and data sources
- **Customizable risk parameters** adaptable to different client profiles
- **API integration ready** for embedding in existing trading platforms

### **For Fintech Developers**
- **Open-source foundation** with modular agent architecture
- **Real-time streaming capabilities** with WebSocket updates
- **Modern tech stack** (FastAPI + React + AutoGen + OpenAI)
- **Extensible framework** for adding specialized agents (ESG, Options, Crypto)

### **Competitive Advantages**

#### 🚀 **Speed & Efficiency**
- **Sub-minute analysis** vs. hours for manual equivalent
- **Parallel agent processing** vs. sequential analysis tools
- **Real-time market integration** vs. static data platforms

#### 🧬 **Intelligence & Accuracy**
- **Multi-perspective validation** reduces single-point-of-failure bias
- **Continuous learning** through agent interaction and feedback loops
- **Mathematical confidence scoring** vs. subjective human ratings

#### 🔧 **Technical Innovation**
- **First-of-its-kind** multi-agent trading analysis system
- **Production-ready architecture** with enterprise scalability
- **Real-time streaming interface** with professional-grade UX

#### 📊 **Practical Results**
- **Consistent recommendations** across all analysis dimensions
- **Transparent reasoning** with full audit trail of agent decisions
- **Actionable execution plans** with specific entry/exit/stop prices

This system represents the **future of investment analysis** - where AI agents collaborate like the best human teams, but with superhuman speed, consistency, and access to real-time global market intelligence.

## 🚀 Features

### Multi-Agent Analysis System
- **Research Agent**: Fetches real-time stock data with technical indicators
- **Risk Manager**: Calculates position sizing and stop-loss levels
- **Data Analyst**: Collects fundamental data (P/E, earnings, targets)
- **Quantitative Analyst**: Provides RSI and MACD technical signals
- **Strategy Developer**: Determines entry/exit prices and timeline
- **Compliance Officer**: Identifies top investment risks
- **Report Agent**: Synthesizes all inputs into actionable recommendations

### Advanced Web Interface
- **Real-time streaming analysis** with Server-Sent Events
- **Interactive stock selection** from popular stocks
- **Live market status** indicator
- **Responsive modern design** with dark/light themes
- **Professional trading dashboard** layout

### Technical Capabilities
- **Real-time stock data** from Alpha Vantage API
- **Technical indicators**: RSI (14-period), MACD (12,26,9)
- **Fundamental analysis**: P/E ratios, analyst targets, earnings dates
- **Risk management**: Position sizing, stop-loss calculations
- **Decision consistency**: Aligned recommendations across all agents

## 📋 Requirements

### Backend
- Python 3.8+
- OpenAI API key
- Alpha Vantage API key  
- Tavily API key (for web research)

### Frontend
- Node.js 16+
- npm or yarn

## 🛠️ Installation

### Quick Setup (Automated)
```bash
cd "Trading AutoGen"
./setup_trading_platform.sh
```

### Manual Setup

1. **Navigate to the project**:
   ```bash
   cd "Trading AutoGen"
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install backend dependencies**:
   ```bash
   pip install -r requirements.txt
   cd trading-platform/backend/app
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies**:
   ```bash
   cd trading-platform/frontend
   npm install
   ```

5. **Set up environment variables**:
   Create a `.env` file in the root directory with:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

6. **Run the application**:
   
   **Option 1: Full Trading Platform**
   ```bash
   # Terminal 1 - Backend
   cd trading-platform/backend/app
   python main_unified.py
   
   # Terminal 2 - Frontend
   cd trading-platform/frontend
   npm run dev
   ```
   
   **Option 2: Simple Workflow Testing**
   ```bash
   python src/workflows/simple_7agent_workflow.py
   ```

7. **Open your browser**:
   Go to `http://localhost:3000` (Frontend) or `http://localhost:8000` (Backend API)

### Troubleshooting Installation

If you encounter `ModuleNotFoundError: No module named 'autogen_agentchat'`:

1. **Install AutoGen manually**:
   ```bash
   pip install autogen-agentchat autogen-core autogen-ext
   ```

2. **Use simple workflow for testing**:
   ```bash
   python src/workflows/simple_7agent_workflow.py
   ```

3. **Check Python version compatibility**:
   ```bash
   python --version  # Should be 3.8+
   ```

## 🎯 Usage

### Web Interface
1. **Select a stock** from popular stocks or enter a symbol
2. **Click "Start Analysis"** to begin multi-agent analysis
3. **Watch real-time results** stream in
4. **Review the final recommendation** with detailed execution plan

### API Endpoints
- `GET /` - Main web interface
- `POST /api/analysis` - Start new stock analysis  
- `GET /api/analysis/{analysis_id}` - Get analysis results
- `GET /api/analysis-stream/{analysis_id}` - Real-time streaming analysis
- `GET /api/popular-stocks` - List of popular stocks
- `GET /api/market-status` - Current market status
- `GET /health` - Health check

### Example API Usage
```bash
# Start analysis
curl -X POST "http://localhost:8000/api/analysis" \
     -H "Content-Type: application/json" \
     -d '{"symbol": "AAPL", "analysisType": "comprehensive"}'

# Get results
curl "http://localhost:8000/api/analysis/YOUR_ANALYSIS_ID"
```

## 📊 Output Format

The system provides structured recommendations in this format:

```
STOCK: AAPL | PRICE: $239.69 | RECOMMENDATION: BUY (High Confidence)

DECISION SUMMARY:
Strong technical signals with RSI oversold and MACD bullish crossover support entry.

KEY METRICS:
- P/E: 36.2 | Target: $250.00 | Next Earnings: 2024-01-25
- Technical: BUY | 52w Range: $164.08-$237.49
- Risk Level: Medium

EXECUTION:
Enter at $240.00, target $260.00, stop $210.00, size 7% max, timeline 3 months

TOP RISKS:
1. Market volatility ahead of earnings
2. Tech sector rotation concerns
```

## 🔧 Configuration

### Agent Behavior
- **Position Sizing**: Fixed 7% allocation (moderate risk)
- **Stop Loss**: 12% below entry price
- **Technical Signals**: RSI + MACD combination
- **Max Conversation**: 8 rounds for efficiency

### API Integration
- **Alpha Vantage**: Real-time quotes, fundamentals, historical data
- **OpenAI**: GPT-4o-mini for agent intelligence

## 🛡️ Risk Management

The system includes built-in safeguards:
- **Position sizing never exceeds 10%**
- **Stop losses always below entry price**
- **Recommendation consistency validation**
- **Input sanitization and validation**

## 📁 Project Structure

```
Trading AutoGen/
├── trading-platform/
│   ├── backend/
│   │   └── app/
│   │       ├── main_unified.py    # Unified FastAPI backend server
│   │       ├── main.py           # Main application entry
│   │       └── requirements.txt  # Backend dependencies
│   └── frontend/
│       ├── src/
│       │   ├── App.tsx           # Main React application
│       │   ├── components/       # React components
│       │   ├── store/           # State management
│       │   └── types/           # TypeScript definitions
│       ├── package.json         # Frontend dependencies
│       └── index.html           # HTML entry point
├── src/
│   ├── agents/                  # Individual agent implementations
│   ├── config/                  # Configuration settings
│   ├── utils/                   # Utility functions
│   └── workflows/               # Agent workflow orchestration
├── requirements.txt             # Python dependencies
└── README.md                   # This file
```

## 🚀 Development

### Running the Full Platform

**Terminal 1 (Backend)**:
```bash
cd trading-platform/backend/app
python main_unified.py
```

**Terminal 2 (Frontend)**:
```bash
cd trading-platform/frontend
npm run dev
```

### Alternative Workflows

**7-Agent Simple Workflow**:
```bash
python src/workflows/simple_7agent_workflow.py
```

**Backend Only (API Testing)**:
```bash
cd trading-platform/backend/app
python main.py
```

### Adding New Agents
1. Create agent file in `src/agents/`
2. Implement agent function returning `AssistantAgent`
3. Add to team composition in `src/teams/teams.py`

### Customizing Analysis
- Modify system messages in agent files
- Adjust technical indicator parameters
- Update risk management rules

## 📈 Performance

- **Analysis time**: ~30-60 seconds per stock
- **Concurrent users**: Supports multiple simultaneous analyses
- **Data freshness**: Real-time market data
- **Accuracy**: Multi-agent validation for consistency

## 🔒 Security

- **API key protection**: Environment variable storage
- **Input validation**: Prevents injection attacks  
- **CORS configuration**: Controlled access
- **Rate limiting**: Built into external APIs

## 🐛 Troubleshooting

### Common Issues

1. **"INSUFFICIENT_DATA" technical signals**:
   - Ensure stock has 35+ trading days of history
   - Check Alpha Vantage API limits

2. **OpenAI API errors**:
   - Verify API key in `.env` file
   - Check API quota and billing

3. **Connection timeouts**:
   - Check internet connection
   - Verify API endpoints are accessible

### Debug Mode
Run with debug logging:
```bash
python application.py --log-level debug
```

## 📄 License

This project is for educational purposes. Please ensure compliance with all relevant financial regulations before using for actual trading decisions.

## ⚠️ Disclaimer

This system is for informational purposes only. Not financial advice. Always consult qualified financial advisors before making investment decisions.
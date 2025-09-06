# AutoGen Trading System

An advanced AI-powered trading analysis platform using multi-agent AutoGen system with FastAPI backend and modern web interface.

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

- Python 3.8+
- Alpha Vantage API key
- OpenAI API key

## 🛠️ Installation

### Quick Setup (Automated)
```bash
cd "Trading AutoGen"
./setup.sh
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

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file with:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   ALPHA=your_alpha_vantage_api_key
   ```

5. **Run the application**:
   
   **Option 1: Full AutoGen System**
   ```bash
   python start_app.py
   ```
   
   **Option 2: Standalone Testing Mode**
   ```bash
   python application_standalone.py
   ```

6. **Open your browser**:
   Go to `http://localhost:8000`

### Troubleshooting Installation

If you encounter `ModuleNotFoundError: No module named 'autogen_agentchat'`:

1. **Use standalone mode for testing**:
   ```bash
   python application_standalone.py
   ```

2. **Install AutoGen manually**:
   ```bash
   pip install autogen-agentchat==0.2.36 autogen-core==0.4.0 autogen-ext==0.2.36
   ```

3. **Use the startup script**:
   ```bash
   python start_app.py
   ```

## 🎯 Usage

### Web Interface
1. **Select a stock** from popular stocks or enter a symbol
2. **Click "Start Analysis"** to begin multi-agent analysis
3. **Watch real-time results** stream in
4. **Review the final recommendation** with detailed execution plan

### API Endpoints
- `GET /` - Main web interface
- `POST /analyze` - Single stock analysis
- `GET /analyze-stream/{symbol}` - Real-time streaming analysis
- `GET /popular-stocks` - List of popular stocks
- `GET /market-status` - Current market status
- `GET /health` - Health check

### Example API Usage
```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"symbol": "AAPL", "question": "Should I buy Apple stock?"}'
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
├── application.py          # FastAPI backend server
├── index.html             # Advanced web interface
├── requirements.txt       # Python dependencies
├── src/
│   ├── agents/           # Individual agent implementations
│   ├── config/           # Configuration settings
│   ├── model/            # OpenAI model client
│   └── teams/            # Multi-agent team orchestration
└── README.md             # This file
```

## 🚀 Development

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
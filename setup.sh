#!/bin/bash

echo "🤖 AutoGen Trading System Setup"
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✅ pip3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env template..."
    cat > .env << EOL
# OpenAI API Key (required)
OPENAI_API_KEY=your_openai_api_key_here

# Alpha Vantage API Key (required)
ALPHA=your_alpha_vantage_api_key_here

# Optional: OpenAI Model (default: gpt-4o-mini)
MODEL=gpt-4o-mini
EOL
    echo "✅ .env template created"
    echo "⚠️  Please edit .env file with your actual API keys"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run the application:"
echo "   python application_standalone.py  (for testing without AutoGen)"
echo "   python start_app.py              (for full AutoGen system)"
echo ""
echo "3. Open browser to http://localhost:8000"
echo ""
echo "Need API keys?"
echo "- OpenAI: https://platform.openai.com/api-keys"
echo "- Alpha Vantage: https://www.alphavantage.co/support/#api-key"
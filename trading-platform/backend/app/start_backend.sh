#!/bin/bash

# Trading Platform Backend Startup Script
# Supports both 7-agent and 13-agent workflows

echo "🚀 Trading Platform Backend Setup"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "main_unified.py" ]; then
    echo "❌ Error: Please run this script from the backend/app directory"
    echo "Current directory: $(pwd)"
    echo "Expected files: main_unified.py, main_7agent.py, main_13agent.py"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1)
echo "🐍 Python version: $python_version"

# Check if virtual environment exists
if [ ! -d "../venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv ../venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source ../venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r ../requirements.txt

# Check if AI frameworks are available
echo "🤖 Checking AI framework availability..."

# Check AutoGen
python3 -c "
try:
    from autogen_agentchat.messages import TextMessage
    print('✅ AutoGen framework available')
except ImportError as e:
    print('❌ AutoGen framework not available:', e)
    print('   Install with: pip install autogen-agentchat')
"

# Check CrewAI
python3 -c "
try:
    import crewai
    print('✅ CrewAI framework available')
except ImportError as e:
    print('⚠️  CrewAI framework not available:', e)
    print('   Install with: pip install crewai')
    print('   Note: CrewAI is optional - 13-agent workflow will use fallback')
"

echo ""
echo "🎯 Available backend options:"
echo "1. Unified Backend (supports both 7-agent and 13-agent workflows) - Port 8000"
echo "2. 7-Agent Backend only - Port 8000"  
echo "3. 13-Agent Backend only - Port 8001"
echo ""

read -p "👉 Choose option (1-3): " choice

case $choice in
    1)
        echo "🚀 Starting Unified Backend (7-agent + 13-agent support)..."
        python3 main_unified.py
        ;;
    2)
        echo "🚀 Starting 7-Agent Backend..."
        python3 main_7agent.py
        ;;
    3)
        echo "🚀 Starting 13-Agent Backend..."
        python3 main_13agent.py
        ;;
    *)
        echo "❌ Invalid choice. Defaulting to Unified Backend..."
        python3 main_unified.py
        ;;
esac

#!/usr/bin/env python3
"""
AutoGen Trading System Startup Script
This script checks dependencies and starts the FastAPI application
"""

import sys
import os
import subprocess
import importlib.util

def check_module(module_name):
    """Check if a module is installed"""
    spec = importlib.util.find_spec(module_name)
    return spec is not None

def install_requirements():
    """Install requirements from requirements.txt"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def check_environment():
    """Check if environment variables are set"""
    required_vars = ["OPENAI_API_KEY", "ALPHA"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file with:")
        print("OPENAI_API_KEY=your_openai_api_key")
        print("ALPHA=your_alpha_vantage_api_key")
        return False
    
    print("✅ Environment variables configured")
    return True

def start_application():
    """Start the FastAPI application"""
    print("🚀 Starting AutoGen Trading System...")
    try:
        # Import and run the application
        from application import app
        import uvicorn
        
        print("📊 AutoGen Trading System is running!")
        print("🌐 Open your browser to: http://localhost:8000")
        print("Press Ctrl+C to stop the server")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all requirements are installed")
        return False
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        return False

def main():
    """Main startup function"""
    print("🤖 AutoGen Trading System Startup")
    print("=" * 50)
    
    # Check critical modules
    required_modules = [
        "fastapi",
        "uvicorn", 
        "pydantic",
        "python_dotenv",
        "requests"
    ]
    
    missing_modules = []
    for module in required_modules:
        if not check_module(module):
            missing_modules.append(module)
    
    # Install requirements if needed
    if missing_modules:
        print(f"❌ Missing modules: {', '.join(missing_modules)}")
        if not install_requirements():
            return
    else:
        print("✅ Core modules available")
    
    # Check environment
    if not check_environment():
        return
    
    # Try to check AutoGen modules (these might need manual installation)
    autogen_modules = ["autogen_agentchat", "autogen_core", "autogen_ext"]
    missing_autogen = []
    
    for module in autogen_modules:
        if not check_module(module):
            missing_autogen.append(module)
    
    if missing_autogen:
        print(f"⚠️  Missing AutoGen modules: {', '.join(missing_autogen)}")
        print("Installing AutoGen packages...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "autogen-agentchat", "autogen-core", "autogen-ext"])
            print("✅ AutoGen packages installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install AutoGen packages")
            print("Please install manually:")
            print("pip install autogen-agentchat autogen-core autogen-ext")
            return
    else:
        print("✅ AutoGen modules available")
    
    # Start the application
    start_application()

if __name__ == "__main__":
    main()
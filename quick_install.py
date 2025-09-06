#!/usr/bin/env python3
"""
Quick installation script for AutoGen Trading System
This installs packages one by one to avoid version conflicts
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a single package"""
    print(f"Installing {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    print("🚀 AutoGen Trading System - Quick Install")
    print("=" * 50)
    
    # Install packages in order
    packages = [
        "fastapi",
        "uvicorn[standard]", 
        "pydantic",
        "python-multipart",
        "jinja2",
        "python-dotenv",
        "requests",
        "openai",
        "tiktoken"
    ]
    
    print("📦 Installing core packages...")
    failed_packages = []
    
    for package in packages:
        if not install_package(package):
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n⚠️  Some core packages failed to install: {failed_packages}")
        print("You can still run the standalone version")
    else:
        print("\n✅ Core packages installed successfully!")
    
    # Try to install AutoGen packages
    print("\n🤖 Installing AutoGen packages...")
    autogen_packages = [
        "autogen-agentchat",
        "autogen-core", 
        "autogen-ext"
    ]
    
    autogen_success = True
    for package in autogen_packages:
        if not install_package(package):
            autogen_success = False
    
    print("\n" + "=" * 50)
    
    if autogen_success:
        print("🎉 All packages installed successfully!")
        print("\nYou can now run:")
        print("  python application.py       # Full AutoGen system")
        print("  python start_app.py         # Smart startup script")
    else:
        print("⚠️  AutoGen packages had issues, but you can still run:")
        print("  python application_standalone.py  # Standalone mode")
    
    print("\n🌐 Then open: http://localhost:8000")

if __name__ == "__main__":
    main()
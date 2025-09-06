#!/usr/bin/env python3
"""
Install latest AutoGen packages for the Trading System
"""

import subprocess
import sys

def install_package(package):
    """Install a package using pip"""
    print(f"Installing {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    print("🚀 Installing Latest AutoGen Packages")
    print("=" * 50)
    
    # Core packages first
    core_packages = [
        "fastapi",
        "uvicorn[standard]",
        "python-dotenv",
        "requests", 
        "openai",
        "pydantic"
    ]
    
    print("📦 Installing core packages...")
    for package in core_packages:
        install_package(package)
    
    # AutoGen packages
    autogen_packages = [
        "autogen-agentchat",
        "autogen-core", 
        "autogen-ext"
    ]
    
    print("\n🤖 Installing latest AutoGen packages...")
    success = True
    for package in autogen_packages:
        if not install_package(package):
            success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All packages installed successfully!")
        print("\n✅ You can now run:")
        print("   python application.py")
        print("\n🌐 Then open: http://localhost:8000")
    else:
        print("⚠️  Some packages failed to install.")
        print("You can still run in simulation mode:")
        print("   python application.py")

if __name__ == "__main__":
    main()
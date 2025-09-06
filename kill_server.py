#!/usr/bin/env python3
"""
Kill any existing AutoGen Trading System servers
"""

import subprocess
import sys
import os

def kill_processes_on_port(port):
    """Kill processes using a specific port"""
    try:
        # Find processes using the port
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"Found {len(pids)} processes using port {port}")
            
            for pid in pids:
                try:
                    subprocess.run(['kill', '-9', pid], check=True)
                    print(f"✅ Killed process {pid}")
                except subprocess.CalledProcessError:
                    print(f"❌ Could not kill process {pid}")
            
            return True
        else:
            print(f"No processes found using port {port}")
            return False
            
    except FileNotFoundError:
        print("lsof command not found, trying alternative method...")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def kill_uvicorn_processes():
    """Kill uvicorn processes by name"""
    try:
        subprocess.run(['pkill', '-f', 'uvicorn'], check=True)
        print("✅ Killed uvicorn processes")
        return True
    except subprocess.CalledProcessError:
        print("No uvicorn processes found")
        return False
    except Exception as e:
        print(f"Error killing uvicorn: {e}")
        return False

def main():
    print("🛑 AutoGen Trading System - Server Killer")
    print("=" * 50)
    
    # Try to kill processes on common ports
    ports = [8000, 8001, 8002, 8080]
    killed_any = False
    
    for port in ports:
        print(f"\n🔍 Checking port {port}...")
        if kill_processes_on_port(port):
            killed_any = True
    
    print(f"\n🔍 Checking for uvicorn processes...")
    if kill_uvicorn_processes():
        killed_any = True
    
    print("\n" + "=" * 50)
    if killed_any:
        print("🎉 Server processes killed successfully!")
        print("✅ You can now run: python application.py")
    else:
        print("ℹ️  No server processes were found running")
    
    print("\n💡 If you still get 'Address already in use' errors,")
    print("   the app will automatically find the next available port.")

if __name__ == "__main__":
    main()
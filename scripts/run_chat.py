#!/usr/bin/env python3
"""
Simple launcher script for the chat client
"""

import subprocess
import sys
import os

def main():
    """Launch the Streamlit chat client"""
    
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    client_path = os.path.join(project_root, "src", "clients", "chat_client.py")
    
    # Check if the client exists
    if not os.path.exists(client_path):
        print("❌ Error: chat_client.py not found. Make sure the project structure is correct.")
        return
    
    # Check if Streamlit is installed
    try:
        import streamlit
    except ImportError:
        print("❌ Streamlit not installed. Installing dependencies...")
        requirements_path = os.path.join(project_root, "requirements", "client_requirements.txt")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_path])
    
    print("🚀 Starting Banking Transaction Chat Client...")
    print("📱 The chat interface will open in your web browser")
    print("🔗 URL: http://localhost:8501")
    print("\n💡 Example queries you can try:")
    print("   • 'Show me all Starbucks purchases'")
    print("   • 'Find grocery spending over $50'")
    print("   • 'What did I spend on gas last month?'")
    print("   • 'Give me a spending summary for this year'")
    print("\n⏹️  Press Ctrl+C to stop the server")
    
    # Launch Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", client_path,
            "--server.port", "8501",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Chat client stopped.")

if __name__ == "__main__":
    main()

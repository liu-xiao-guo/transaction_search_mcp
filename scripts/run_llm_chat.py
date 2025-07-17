#!/usr/bin/env python3
"""
Launcher script for the LLM-powered chat client
"""

import subprocess
import sys
import os

def main():
    """Launch the LLM-powered Streamlit chat client"""
    
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    client_path = os.path.join(project_root, "src", "clients", "chat_client_llm.py")
    
    # Check if the client exists
    if not os.path.exists(client_path):
        print("❌ Error: chat_client_llm.py not found. Make sure the project structure is correct.")
        return
    
    print("🤖 Starting LLM-Powered Banking Transaction Chat Client...")
    print("📱 The chat interface will open in your web browser")
    print("🔗 URL: http://localhost:8502")
    print("\n🔧 Requirements:")
    print("   • LM Studio running on http://localhost:1234")
    print("   • A model loaded that supports tool calling")
    print("   • Elasticsearch with transaction data")
    print("\n💡 This version uses your local LLM to:")
    print("   • Understand natural language queries")
    print("   • Automatically choose the right tools")
    print("   • Provide intelligent responses")
    print("\n⏹️  Press Ctrl+C to stop the server")
    
    # Launch Streamlit on a different port
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", client_path,
            "--server.port", "8502",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 LLM chat client stopped.")

if __name__ == "__main__":
    main()

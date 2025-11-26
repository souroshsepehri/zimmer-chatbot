#!/usr/bin/env python3
"""
Test script to verify SmartAIAgent initialization
Run this on the server to check if the agent is properly configured.
"""

import os
import sys

# Load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Loaded .env file using python-dotenv")
except ImportError:
    print("⚠ python-dotenv not available, relying on system environment variables")

print("\n=== ENV CHECK ===")
api_key = os.getenv("OPENAI_API_KEY")
smart_agent_enabled = os.getenv("SMART_AGENT_ENABLED")

print(f"OPENAI_API_KEY present: {bool(api_key)}")
if api_key:
    print(f"  Length: {len(api_key)} characters")
    print(f"  Starts with: {api_key[:10]}...")

print(f"SMART_AGENT_ENABLED env: {smart_agent_enabled}")

print("\n=== SMART AGENT OBJECT ===")
try:
    from services.smart_agent import smart_agent
    
    print(f"smart_agent.enabled: {smart_agent.enabled}")
    print(f"smart_agent.llm type: {type(smart_agent.llm)}")
    
    if smart_agent.llm is not None:
        print(f"  Model: {smart_agent.model_name}")
        print("✓ SmartAIAgent is properly initialized!")
    else:
        print("✗ SmartAIAgent.llm is None - agent is disabled")
        print("\nPossible reasons:")
        if not api_key:
            print("  - OPENAI_API_KEY is not set")
        if smart_agent_enabled and smart_agent_enabled.lower() not in ("1", "true", "yes", "y", "on"):
            print(f"  - SMART_AGENT_ENABLED is '{smart_agent_enabled}' (should be 'true' or '1')")
        
except Exception as e:
    print(f"✗ Error importing or checking smart_agent: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n=== TEST COMPLETE ===")


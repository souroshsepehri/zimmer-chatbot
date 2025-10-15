#!/usr/bin/env python3
"""
Setup script for API keys
"""

import os
import sys

def setup_api_keys():
    """Setup API keys for Smart Agent"""
    print("Smart Agent API Keys Setup")
    print("=" * 40)
    
    # Check current environment variables
    print("\nCurrent API Keys:")
    openai_key = os.getenv('OPENAI_API_KEY')
    news_key = os.getenv('NEWS_API_KEY')
    weather_key = os.getenv('WEATHER_API_KEY')
    
    print(f"OpenAI API Key: {'[SET]' if openai_key else '[NOT SET]'}")
    print(f"News API Key: {'[SET]' if news_key else '[NOT SET]'}")
    print(f"Weather API Key: {'[SET]' if weather_key else '[NOT SET]'}")
    
    # Instructions
    print("\n" + "=" * 40)
    print("API Keys Setup Instructions:")
    print("=" * 40)
    
    print("\n1. OpenAI API Key (Required for AI responses):")
    print("   - Visit: https://platform.openai.com/api-keys")
    print("   - Create a new API key")
    print("   - Set environment variable:")
    print("     Windows: set OPENAI_API_KEY=your_key_here")
    print("     Linux/Mac: export OPENAI_API_KEY=your_key_here")
    
    print("\n2. News API Key (Optional, for news functionality):")
    print("   - Visit: https://newsapi.org/register")
    print("   - Register for free API key")
    print("   - Set environment variable:")
    print("     Windows: set NEWS_API_KEY=your_key_here")
    print("     Linux/Mac: export NEWS_API_KEY=your_key_here")
    
    print("\n3. Weather API Key (Optional, for weather functionality):")
    print("   - Visit: https://openweathermap.org/api")
    print("   - Register for free API key")
    print("   - Set environment variable:")
    print("     Windows: set WEATHER_API_KEY=your_key_here")
    print("     Linux/Mac: export WEATHER_API_KEY=your_key_here")
    
    print("\n" + "=" * 40)
    print("Free APIs (No key required):")
    print("=" * 40)
    print("[FREE] Translation API (MyMemory)")
    print("[FREE] Currency API (ExchangeRate)")
    print("[FREE] Quote API (Quotable)")
    print("[FREE] Joke API (Official Joke API)")
    print("[FREE] Wikipedia API")
    print("[FREE] GitHub API")
    print("[FREE] Timezone API (WorldTimeAPI)")
    
    print("\n" + "=" * 40)
    print("Testing Instructions:")
    print("=" * 40)
    print("1. Set your API keys using the commands above")
    print("2. Restart your terminal/command prompt")
    print("3. Run: python test_smart_agent.py")
    print("4. Or start the server: npm start")
    print("5. Open: http://localhost:8000/api/smart-agent/interface")
    
    print("\n" + "=" * 40)
    print("Quick Test (without API keys):")
    print("=" * 40)
    print("Even without API keys, you can test:")
    print("- Web content reading")
    print("- Wikipedia searches")
    print("- Basic API integration")
    print("- URL analysis")
    
    # Create .env file template
    env_content = """# Smart Agent API Keys
# Copy this file to .env and add your actual API keys

# Required for AI responses
OPENAI_API_KEY=your_openai_api_key_here

# Optional - for enhanced functionality
NEWS_API_KEY=your_news_api_key_here
WEATHER_API_KEY=your_weather_api_key_here

# Note: The following APIs work without keys:
# - Translation (MyMemory)
# - Currency (ExchangeRate)
# - Quotes (Quotable)
# - Jokes (Official Joke API)
# - Wikipedia
# - GitHub
# - Timezone (WorldTimeAPI)
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_content)
    
    print(f"\n[SUCCESS] Created .env.template file")
    print("  Copy this to .env and add your actual API keys")

if __name__ == "__main__":
    setup_api_keys()

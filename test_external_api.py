#!/usr/bin/env python3
"""
Test script for external API connection
"""

import asyncio
import aiohttp
import json
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_external_api():
    """Test the external API connection"""
    
    # Test different configurations
    configs = [
        {"url": "http://85.208.254.187", "port": None},
        {"url": "http://85.208.254.187", "port": 8000},
        {"url": "http://85.208.254.187", "port": 8001},
        {"url": "http://85.208.254.187", "port": 8002},
        {"url": "http://85.208.254.187", "port": 8003},
        {"url": "http://85.208.254.187", "port": 8080},
        {"url": "http://85.208.254.187", "port": 3000},
        {"url": "http://85.208.254.187", "port": 5000},
    ]
    
    print("🔍 Testing External API Connection")
    print("=" * 50)
    
    for config in configs:
        if config["port"]:
            base_url = f"{config['url']}:{config['port']}"
        else:
            base_url = config["url"]
        
        print(f"\n🌐 Testing: {base_url}")
        
        # Test endpoints
        endpoints = [
            "/health",
            "/api/health",
            "/api/chat", 
            "/api/simple-chat",
            "/api/smart-chat",
            "/docs",
            "/openapi.json",
            "/status"
        ]
        
        working_endpoints = []
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            for endpoint in endpoints:
                try:
                    url = f"{base_url}{endpoint}"
                    async with session.get(url) as response:
                        if response.status in [200, 404, 405]:  # 404/405 means endpoint exists
                            working_endpoints.append({
                                "endpoint": endpoint,
                                "status": response.status,
                                "url": url
                            })
                            print(f"  ✅ {endpoint} - Status {response.status}")
                        else:
                            print(f"  ❌ {endpoint} - Status {response.status}")
                except Exception as e:
                    print(f"  ❌ {endpoint} - Error: {str(e)[:50]}...")
        
        if working_endpoints:
            print(f"\n🎉 Found working configuration!")
            print(f"   Base URL: {base_url}")
            print(f"   Working endpoints: {len(working_endpoints)}")
            
            # Test a chat message if chat endpoint is available
            chat_endpoints = [ep for ep in working_endpoints if "chat" in ep["endpoint"]]
            if chat_endpoints:
                chat_endpoint = chat_endpoints[0]["endpoint"]
                print(f"\n💬 Testing chat endpoint: {chat_endpoint}")
                
                try:
                    url = f"{base_url}{chat_endpoint}"
                    payload = {"message": "سلام", "debug": False}
                    
                    async with session.post(
                        url,
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            print(f"  ✅ Chat test successful!")
                            print(f"  📝 Response: {data.get('answer', 'No answer')[:100]}...")
                        else:
                            print(f"  ❌ Chat test failed - Status {response.status}")
                except Exception as e:
                    print(f"  ❌ Chat test error: {str(e)[:50]}...")
            
            # Generate configuration
            print(f"\n📝 Configuration for .env file:")
            print(f"EXTERNAL_API_URL=http://85.208.254.187")
            if config["port"]:
                print(f"EXTERNAL_API_PORT={config['port']}")
            else:
                print(f"EXTERNAL_API_PORT=80")
            print(f"EXTERNAL_API_TIMEOUT=30")
            print(f"EXTERNAL_API_ENABLED=true")
            
            return base_url, working_endpoints
    
    print(f"\n❌ No working configuration found")
    print(f"   The server might be:")
    print(f"   - Behind a firewall")
    print(f"   - Running on a non-standard port")
    print(f"   - Not properly configured")
    print(f"   - Using HTTPS instead of HTTP")
    
    return None, []

async def test_local_integration():
    """Test the local chatbot with external API integration"""
    print(f"\n🔧 Testing Local Integration")
    print("=" * 50)
    
    try:
        # Test if local server is running
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.get("http://localhost:8002/health") as response:
                if response.status == 200:
                    print("✅ Local chatbot server is running")
                    
                    # Test external API endpoints
                    endpoints = [
                        "/api/external-api/status",
                        "/api/external-api/endpoints", 
                        "/api/external-api/test"
                    ]
                    
                    for endpoint in endpoints:
                        try:
                            url = f"http://localhost:8002{endpoint}"
                            async with session.get(url) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    print(f"✅ {endpoint} - Working")
                                    if endpoint == "/api/external-api/status":
                                        print(f"   Status: {data.get('status', 'Unknown')}")
                                else:
                                    print(f"❌ {endpoint} - Status {response.status}")
                        except Exception as e:
                            print(f"❌ {endpoint} - Error: {str(e)[:50]}...")
                else:
                    print("❌ Local chatbot server is not running")
                    print("   Start it with: python -m uvicorn backend.app:app --host 0.0.0.0 --port 8002")
    except Exception as e:
        print(f"❌ Cannot connect to local server: {e}")
        print("   Make sure the chatbot server is running on port 8002")

async def main():
    """Main test function"""
    print("🚀 External API Connection Test")
    print("=" * 50)
    
    # Test external API
    base_url, endpoints = await test_external_api()
    
    # Test local integration
    await test_local_integration()
    
    print(f"\n📋 Summary:")
    if base_url:
        print(f"✅ Found working external API: {base_url}")
        print(f"✅ {len(endpoints)} endpoints available")
    else:
        print(f"❌ No working external API found")
    
    print(f"\n🔧 Next Steps:")
    if base_url:
        print(f"1. Add the configuration to your .env file")
        print(f"2. Restart your chatbot server")
        print(f"3. Test: http://localhost:8002/api/external-api/status")
    else:
        print(f"1. Check if the server is running on a different port")
        print(f"2. Verify firewall settings")
        print(f"3. Contact the server administrator")

if __name__ == "__main__":
    asyncio.run(main())

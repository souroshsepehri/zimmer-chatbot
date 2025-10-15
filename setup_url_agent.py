#!/usr/bin/env python3
"""
Setup and test URL agent functionality
"""

import os
import sys
import requests
import time

def setup_openai_key():
    """Help user set up OpenAI API key"""
    print("🔑 OpenAI API Key Setup")
    print("=" * 40)
    
    # Check if key is already set
    current_key = os.getenv("OPENAI_API_KEY")
    if current_key:
        print(f"✅ OpenAI API key is already set: {current_key[:10]}...")
        return True
    
    print("❌ OpenAI API key is not set")
    print("\nTo get an OpenAI API key:")
    print("1. Go to https://platform.openai.com/api-keys")
    print("2. Sign in to your OpenAI account")
    print("3. Click 'Create new secret key'")
    print("4. Copy the key")
    print("\nThen set it using one of these methods:")
    print("\nMethod 1 - Command Prompt:")
    print("set OPENAI_API_KEY=your_key_here")
    print("\nMethod 2 - PowerShell:")
    print("$env:OPENAI_API_KEY='your_key_here'")
    print("\nMethod 3 - Set it now (temporary):")
    
    api_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        print("✅ API key set for this session")
        return True
    else:
        print("⚠️ Skipping API key setup")
        return False

def test_server_connection():
    """Test if server is running"""
    print("\n🌐 Testing Server Connection")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running on port 8002")
            return True
        else:
            print(f"❌ Server returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("\n💡 To start the server:")
        print("python start_fixed_url_agent.py")
        return False

def test_url_agent_with_simple_website():
    """Test URL agent with a simple website"""
    print("\n🔍 Testing URL Agent with Simple Website")
    print("=" * 40)
    
    # Test with a simple, reliable website
    test_url = "https://example.com"
    
    try:
        print(f"Adding website: {test_url}")
        response = requests.post("http://localhost:8002/api/url-agent/add-website", 
                               json={"url": test_url, "max_pages": 3},
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Website added successfully!")
            print(f"   - Pages scraped: {result.get('pages_scraped', 0)}")
            print(f"   - Message: {result.get('message', 'No message')}")
            return True
        else:
            print(f"❌ Failed to add website: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error adding website: {e}")
        return False

def test_search_functionality():
    """Test search functionality"""
    print("\n🔍 Testing Search Functionality")
    print("=" * 40)
    
    try:
        # Test search
        response = requests.post("http://localhost:8002/api/url-agent/search",
                               json={"query": "example", "use_primary_only": False},
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Search successful!")
            print(f"   - Answer: {result.get('answer', 'No answer')[:100]}...")
            print(f"   - Source: {result.get('source', 'Unknown')}")
            return True
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error searching: {e}")
        return False

def test_with_your_website():
    """Test with user's website"""
    print("\n🌐 Testing with Your Website")
    print("=" * 40)
    
    website_url = input("Enter your website URL (or press Enter to skip): ").strip()
    if not website_url:
        print("⚠️ Skipping custom website test")
        return True
    
    # Add https if not present
    if not website_url.startswith(('http://', 'https://')):
        website_url = 'https://' + website_url
    
    try:
        print(f"Adding your website: {website_url}")
        response = requests.post("http://localhost:8002/api/url-agent/add-website",
                               json={"url": website_url, "max_pages": 10},
                               timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Your website added successfully!")
            print(f"   - Pages scraped: {result.get('pages_scraped', 0)}")
            print(f"   - Message: {result.get('message', 'No message')}")
            
            # Test search on your website
            search_query = input("Enter a search query to test (or press Enter to skip): ").strip()
            if search_query:
                print(f"Searching for: {search_query}")
                search_response = requests.post("http://localhost:8002/api/url-agent/search",
                                              json={"query": search_query, "use_primary_only": False},
                                              timeout=10)
                
                if search_response.status_code == 200:
                    search_result = search_response.json()
                    print("✅ Search successful!")
                    print(f"   - Answer: {search_result.get('answer', 'No answer')}")
                    print(f"   - Source: {search_result.get('source', 'Unknown')}")
                else:
                    print(f"❌ Search failed: {search_response.status_code}")
            
            return True
        else:
            print(f"❌ Failed to add your website: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error with your website: {e}")
        return False

def main():
    """Main setup and test function"""
    print("🚀 URL Agent Setup and Test")
    print("=" * 50)
    
    # Step 1: Setup OpenAI API key
    api_key_set = setup_openai_key()
    
    # Step 2: Test server connection
    server_running = test_server_connection()
    if not server_running:
        print("\n❌ Cannot proceed without server running")
        return
    
    # Step 3: Test with simple website
    if api_key_set:
        simple_test_passed = test_url_agent_with_simple_website()
        if simple_test_passed:
            test_search_functionality()
            test_with_your_website()
        else:
            print("\n❌ Basic URL agent test failed")
    else:
        print("\n⚠️ Skipping URL agent tests (no API key)")
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    print("✅ Server is running")
    if api_key_set:
        print("✅ OpenAI API key is configured")
        print("✅ URL agent should be working")
        print("\n💡 You can now:")
        print("1. Add websites via the admin panel")
        print("2. Search both FAQ database and website content")
        print("3. Use the dual database interface")
    else:
        print("❌ OpenAI API key is not configured")
        print("💡 URL agent requires OpenAI API key for embeddings")
        print("   Set it and restart the server to use URL agent")

if __name__ == "__main__":
    main()

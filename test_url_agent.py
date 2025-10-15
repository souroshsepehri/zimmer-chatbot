#!/usr/bin/env python3
"""
Test URL Agent functionality to diagnose website reading issues
"""

import sys
import os
import asyncio
import requests

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_url_agent():
    """Test URL agent functionality"""
    print("🔍 Testing URL Agent Functionality")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("\n1. Testing server connection...")
    try:
        response = requests.get("http://localhost:8002/health")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server returned status: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Make sure the server is running with: python start_fixed_url_agent.py")
        return
    
    # Test 2: Test adding a simple website
    print("\n2. Testing website addition...")
    test_url = "https://example.com"  # Simple test website
    
    try:
        response = requests.post("http://localhost:8002/api/url-agent/add-website", json={
            "url": test_url,
            "max_pages": 5
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Website addition response: {result}")
        else:
            print(f"❌ Website addition failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error adding website: {e}")
    
    # Test 3: Check website list
    print("\n3. Testing website list...")
    try:
        response = requests.get("http://localhost:8002/api/url-agent/websites")
        
        if response.status_code == 200:
            websites = response.json()
            print(f"✅ Found {len(websites)} websites in database")
            for website in websites:
                print(f"   - {website.get('url', 'Unknown')} ({website.get('total_words', 0)} words)")
        else:
            print(f"❌ Failed to get website list: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting website list: {e}")
    
    # Test 4: Test search functionality
    print("\n4. Testing search functionality...")
    try:
        response = requests.post("http://localhost:8002/api/url-agent/search", json={
            "query": "example",
            "use_primary_only": False
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Search response: {result}")
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error searching: {e}")
    
    # Test 5: Test dual database search
    print("\n5. Testing dual database search...")
    try:
        response = requests.post("http://localhost:8002/api/dual-database/search", json={
            "query": "test",
            "use_primary_only": False
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Dual database search response: {result}")
        else:
            print(f"❌ Dual database search failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error in dual database search: {e}")

def test_web_scraper_directly():
    """Test web scraper directly"""
    print("\n6. Testing web scraper directly...")
    try:
        from services.web_scraper import get_web_scraper
        
        scraper = get_web_scraper()
        scraper.max_pages = 3
        
        # Test scraping a simple website
        pages = scraper.scrape_website("https://example.com")
        
        if pages:
            print(f"✅ Scraper found {len(pages)} pages")
            for page in pages:
                print(f"   - {page.url}: {len(page.content)} characters")
        else:
            print("❌ Scraper found no pages")
            
    except Exception as e:
        print(f"❌ Error testing scraper directly: {e}")
        import traceback
        traceback.print_exc()

def test_vectorstore():
    """Test vector store functionality"""
    print("\n7. Testing vector store...")
    try:
        from services.web_vectorstore import get_web_vectorstore
        
        vectorstore = get_web_vectorstore()
        
        # Check if vectorstore is loaded
        if vectorstore._load_vectorstore():
            print("✅ Vector store loaded successfully")
            print(f"   - {len(vectorstore.web_mapping)} chunks in mapping")
            print(f"   - {len(vectorstore.website_metadata)} websites in metadata")
        else:
            print("⚠️ No existing vector store found")
            
    except Exception as e:
        print(f"❌ Error testing vector store: {e}")
        import traceback
        traceback.print_exc()

def check_openai_api():
    """Check OpenAI API configuration"""
    print("\n8. Checking OpenAI API configuration...")
    try:
        from core.config import settings
        
        if settings.openai_api_key:
            print("✅ OpenAI API key is configured")
            print(f"   - Model: {settings.openai_model}")
            print(f"   - Embedding Model: {settings.embedding_model}")
        else:
            print("❌ OpenAI API key is not configured")
            print("💡 Set it with: set OPENAI_API_KEY=your_key_here")
            
    except Exception as e:
        print(f"❌ Error checking OpenAI configuration: {e}")

async def main():
    """Main test function"""
    await test_url_agent()
    test_web_scraper_directly()
    test_vectorstore()
    check_openai_api()
    
    print("\n" + "=" * 50)
    print("🔧 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    print("If you're having issues with URL agent:")
    print("1. Make sure the server is running")
    print("2. Check OpenAI API key is set")
    print("3. Verify the website URL is accessible")
    print("4. Check server logs for detailed error messages")
    print("5. Try with a simple website like https://example.com first")

if __name__ == "__main__":
    asyncio.run(main())
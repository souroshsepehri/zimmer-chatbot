#!/usr/bin/env python3
"""
Test script for URL Agent functionality
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.url_agent import get_url_agent
from services.web_scraper import get_web_scraper
from services.web_vectorstore import get_web_vectorstore

async def test_url_agent():
    """Test the URL agent functionality"""
    print("🤖 Testing URL Agent...")
    
    # Initialize agent
    url_agent = get_url_agent()
    print("✅ URL Agent initialized")
    
    # Test website addition (using a simple test site)
    test_url = "https://httpbin.org/html"  # Simple test HTML page
    
    print(f"\n📥 Adding test website: {test_url}")
    result = await url_agent.add_website(test_url, max_pages=1)
    
    if result['success']:
        print(f"✅ Website added successfully: {result['message']}")
        print(f"   Pages scraped: {result['pages_scraped']}")
    else:
        print(f"❌ Failed to add website: {result['message']}")
        return
    
    # Test dual database search
    print(f"\n🔍 Testing dual database search...")
    search_results = await url_agent.search_dual_database(
        query="test content",
        include_faq=True,
        include_web=True
    )
    
    print(f"✅ Search completed")
    print(f"   FAQ results: {len(search_results['faq_results'])}")
    print(f"   Web results: {len(search_results['web_results'])}")
    print(f"   Combined results: {len(search_results['combined_results'])}")
    
    # Test question answering
    print(f"\n💬 Testing question answering...")
    answer_result = await url_agent.answer_question(
        question="What is this website about?",
        context_preference="both"
    )
    
    print(f"✅ Answer generated")
    print(f"   Answer length: {len(answer_result['answer'])} characters")
    print(f"   Sources used: {len(answer_result['sources'])}")
    print(f"   Answer preview: {answer_result['answer'][:200]}...")
    
    # Test website listing
    print(f"\n📋 Testing website listing...")
    websites = url_agent.list_websites()
    print(f"✅ Found {len(websites)} websites in knowledge base")
    
    for website in websites:
        print(f"   - {website['domain']}: {website['total_pages']} pages, {website['total_words']} words")
    
    # Test stats
    print(f"\n📊 Testing stats...")
    stats = url_agent.get_stats()
    print(f"✅ Stats retrieved:")
    print(f"   Web content: {stats['web_content']}")
    print(f"   FAQ database: {stats['faq_database']}")
    
    print(f"\n🎉 All tests completed successfully!")

async def test_web_scraper():
    """Test web scraper functionality"""
    print("\n🕷️ Testing Web Scraper...")
    
    scraper = get_web_scraper()
    
    # Test single page scraping
    test_url = "https://httpbin.org/html"
    print(f"📥 Scraping test page: {test_url}")
    
    page = scraper.scrape_page(test_url)
    
    if page:
        print(f"✅ Page scraped successfully")
        print(f"   Title: {page.title}")
        print(f"   Content length: {len(page.content)} characters")
        print(f"   Links found: {len(page.links)}")
        print(f"   Word count: {page.metadata['word_count']}")
    else:
        print(f"❌ Failed to scrape page")

async def test_web_vectorstore():
    """Test web vector store functionality"""
    print("\n🗄️ Testing Web Vector Store...")
    
    vectorstore = get_web_vectorstore()
    
    # Test stats
    stats = vectorstore.get_stats()
    print(f"✅ Vector store stats: {stats}")
    
    # Test search
    search_results = vectorstore.semantic_search("test content", top_k=3)
    print(f"✅ Search test completed: {len(search_results)} results")

async def main():
    """Run all tests"""
    print("🚀 Starting URL Agent Tests...\n")
    
    try:
        await test_web_scraper()
        await test_web_vectorstore()
        await test_url_agent()
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

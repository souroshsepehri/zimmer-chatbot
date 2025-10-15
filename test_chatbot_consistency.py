#!/usr/bin/env python3
"""
Test chatbot consistency with multiple queries
"""

import requests
import time
import json

def test_chatbot_consistency():
    """Test chatbot with various queries to identify inconsistencies"""
    
    test_queries = [
        "سفارش",
        "چطور سفارش بدم؟",
        "ساعات کاری",
        "ساعات کاری شما چیه؟",
        "قیمت",
        "قیمت‌های شما چقدره؟",
        "تماس",
        "چطور می‌تونم با شما تماس بگیرم؟",
        "گارانتی",
        "آیا گارانتی دارید؟",
        "سوال نامربوط",
        "چیزی که در دیتابیس نیست",
        "سلام",
        "کمک",
        "پشتیبانی"
    ]
    
    print("🧪 Testing Chatbot Consistency")
    print("=" * 50)
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        try:
            print(f"\n{i:2d}. Testing: '{query}'")
            
            response = requests.post("http://localhost:8002/api/chat", json={
                "message": query,
                "debug": True
            })
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', 'No answer')
                source = data.get('debug_info', {}).get('source', 'unknown')
                success = data.get('debug_info', {}).get('success', False)
                
                print(f"    ✅ Status: 200")
                print(f"    📝 Answer: {answer[:100]}{'...' if len(answer) > 100 else ''}")
                print(f"    🔍 Source: {source}")
                print(f"    ✅ Success: {success}")
                
                results.append({
                    "query": query,
                    "answer": answer,
                    "source": source,
                    "success": success,
                    "status": "success"
                })
                
            else:
                print(f"    ❌ Status: {response.status_code}")
                print(f"    ❌ Error: {response.text}")
                
                results.append({
                    "query": query,
                    "status": "error",
                    "error": response.text
                })
                
        except Exception as e:
            print(f"    ❌ Exception: {e}")
            results.append({
                "query": query,
                "status": "exception",
                "error": str(e)
            })
        
        # Small delay between requests
        time.sleep(0.5)
    
    # Analyze results
    print("\n" + "=" * 50)
    print("📊 CONSISTENCY ANALYSIS")
    print("=" * 50)
    
    successful_queries = [r for r in results if r.get('status') == 'success']
    error_queries = [r for r in results if r.get('status') == 'error']
    exception_queries = [r for r in results if r.get('status') == 'exception']
    
    print(f"✅ Successful responses: {len(successful_queries)}/{len(test_queries)}")
    print(f"❌ Error responses: {len(error_queries)}")
    print(f"💥 Exception responses: {len(exception_queries)}")
    
    # Check for inconsistent sources
    sources = {}
    for result in successful_queries:
        source = result.get('source', 'unknown')
        sources[source] = sources.get(source, 0) + 1
    
    print(f"\n📈 Response Sources:")
    for source, count in sources.items():
        print(f"   {source}: {count} responses")
    
    # Check for failed queries
    failed_queries = [r for r in successful_queries if not r.get('success', False)]
    if failed_queries:
        print(f"\n⚠️  Queries that returned fallback answers: {len(failed_queries)}")
        for result in failed_queries:
            print(f"   - '{result['query']}'")
    
    # Check for empty or very short answers
    short_answers = [r for r in successful_queries if len(r.get('answer', '')) < 20]
    if short_answers:
        print(f"\n⚠️  Very short answers: {len(short_answers)}")
        for result in short_answers:
            print(f"   - '{result['query']}' -> '{result['answer']}'")
    
    # Save detailed results
    with open('chatbot_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Detailed results saved to: chatbot_test_results.json")
    
    return results

if __name__ == "__main__":
    test_chatbot_consistency()

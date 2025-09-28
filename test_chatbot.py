#!/usr/bin/env python3
"""
Test chatbot with simple retriever
"""

import requests
import json

def test_chatbot():
    try:
        # Test chat endpoint
        print("🤖 Testing chatbot with FAQ database...")
        
        test_messages = [
            "چطور می‌تونم سفارش بدم؟",
            "ساعات کاری شما چیه؟",
            "چطور با پشتیبانی تماس بگیرم؟",
            "سلام",
            "قیمت محصولات چقدره؟"
        ]
        
        for message in test_messages:
            print(f"\n📝 User: {message}")
            
            response = requests.post("http://localhost:8000/api/chat", json={
                "message": message,
                "debug": True
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"🤖 Bot: {data['answer']}")
                
                if data.get('debug_info'):
                    debug = data['debug_info']
                    print(f"   Source: {debug.get('source', 'unknown')}")
                    print(f"   Success: {debug.get('success', False)}")
                    if debug.get('retrieval_results'):
                        print(f"   Found {len(debug['retrieval_results'])} FAQ matches")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_chatbot()

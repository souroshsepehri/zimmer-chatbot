#!/usr/bin/env python3
"""
Test script to verify the chatbot interface is working
"""
import requests

def test_chatbot_interface():
    """Test the chatbot interface"""
    url = "https://zimmer-chatbot-4.onrender.com/"
    
    print(f"🧪 Testing chatbot interface at: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            content = response.text
            if "بات هوشمند زیمر" in content:
                print("✅ Chatbot interface found!")
                print("✅ HTML content is being served correctly")
                return True
            elif "message" in content.lower() and "Persian Chatbot API" in content:
                print("❌ Still showing JSON instead of HTML")
                print("❌ The HTML interface is not being served")
                return False
            else:
                print("❓ Unknown response")
                print(f"Response preview: {content[:200]}...")
                return False
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    test_chatbot_interface()

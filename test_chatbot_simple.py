import requests
import json

def test_chatbot():
    base_url = "https://zimmer-chatbot-4.onrender.com"
    
    print("Testing chatbot endpoints...")
    
    # Test database
    try:
        response = requests.get(f"{base_url}/test-db", timeout=10)
        print(f"Database test: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Database status: {data}")
        else:
            print(f"Database error: {response.text}")
    except Exception as e:
        print(f"Database test error: {e}")
    
    # Test chat
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json={"message": "سلام"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Chat test: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Chat response: {data.get('answer', 'No answer')}")
        else:
            print(f"Chat error: {response.text}")
    except Exception as e:
        print(f"Chat test error: {e}")

if __name__ == "__main__":
    test_chatbot()

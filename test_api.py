import requests
import json

def test_api():
    url = "https://zimmer-chatbot-4.onrender.com/api/chat"
    
    try:
        response = requests.post(
            url,
            json={"message": "سلام"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Answer: {data.get('answer', 'No answer')}")
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
#!/usr/bin/env python3
"""
Detailed test to check if logging is really disabled
"""

import requests
import json
import time

def test_logging_detailed():
    print("🔍 DETAILED LOGGING TEST")
    print("=" * 50)
    
    try:
        # Get initial log count
        print("1. Getting initial log count...")
        response = requests.get("http://localhost:8000/api/logs")
        if response.status_code == 200:
            logs = response.json()
            if isinstance(logs, list):
                initial_count = len(logs)
            else:
                initial_count = logs.get('total', 0)
            print(f"   Initial log count: {initial_count}")
        else:
            print(f"   ❌ Error getting logs: {response.status_code}")
            return
        
        # Send multiple test messages
        test_messages = [
            "تست اول",
            "تست دوم", 
            "سفارش",
            "پشتیبانی"
        ]
        
        print(f"\n2. Sending {len(test_messages)} test messages...")
        for i, message in enumerate(test_messages, 1):
            print(f"   Sending message {i}: {message}")
            response = requests.post("http://localhost:8000/api/chat", json={
                "message": message,
                "debug": False
            })
            
            if response.status_code == 200:
                print(f"   ✅ Message {i} sent successfully")
            else:
                print(f"   ❌ Message {i} failed: {response.status_code}")
        
        # Wait a moment
        time.sleep(1)
        
        # Check final log count
        print(f"\n3. Checking final log count...")
        response = requests.get("http://localhost:8000/api/logs")
        if response.status_code == 200:
            logs = response.json()
            if isinstance(logs, list):
                final_count = len(logs)
            else:
                final_count = logs.get('total', 0)
            print(f"   Final log count: {final_count}")
            
            # Calculate difference
            new_logs = final_count - initial_count
            print(f"   New logs created: {new_logs}")
            
            if new_logs == 0:
                print("   ✅ LOGGING IS COMPLETELY DISABLED!")
            else:
                print(f"   ❌ LOGGING IS STILL ACTIVE - {new_logs} new logs created!")
                
                # Show the new logs
                if isinstance(logs, list) and len(logs) > initial_count:
                    print("   Recent logs:")
                    for log in logs[-new_logs:]:
                        print(f"     - {log.get('user_text', 'N/A')} -> {log.get('ai_text', 'N/A')[:50]}...")
        else:
            print(f"   ❌ Error getting final logs: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_logging_detailed()

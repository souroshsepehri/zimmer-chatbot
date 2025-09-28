#!/usr/bin/env python3
"""
Check if logging is disabled by counting chat logs
"""

import requests
import json

def check_logging_disabled():
    print("📊 CHECKING IF LOGGING IS DISABLED")
    print("=" * 50)
    
    try:
        # Get current log count
        response = requests.get("http://localhost:8000/api/logs")
        if response.status_code == 200:
            logs = response.json()
            if isinstance(logs, list):
                log_count = len(logs)
            else:
                log_count = logs.get('total', 0)
            
            print(f"Current log count: {log_count}")
            
            # Send a test message
            print("\nSending test message...")
            test_response = requests.post("http://localhost:8000/api/chat", json={
                "message": "تست برای بررسی لاگ",
                "debug": False
            })
            
            if test_response.status_code == 200:
                print("✅ Test message sent successfully")
                
                # Check log count again
                response2 = requests.get("http://localhost:8000/api/logs")
                if response2.status_code == 200:
                    logs2 = response2.json()
                    if isinstance(logs2, list):
                        new_log_count = len(logs2)
                    else:
                        new_log_count = logs2.get('total', 0)
                    
                    print(f"New log count: {new_log_count}")
                    
                    if new_log_count == log_count:
                        print("✅ LOGGING IS DISABLED - No new logs created!")
                    else:
                        print("❌ LOGGING IS STILL ACTIVE - New logs were created")
                else:
                    print("⚠️  Could not check log count after test")
            else:
                print(f"❌ Test message failed: {test_response.status_code}")
        else:
            print(f"❌ Could not get current log count: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_logging_disabled()

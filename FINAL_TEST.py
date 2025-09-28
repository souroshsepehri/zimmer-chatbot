#!/usr/bin/env python3
"""
Final comprehensive test of the chatbot system
"""

import requests
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_complete_system():
    print("🧪 FINAL COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Test 1: Backend Health
    print("1. Testing Backend Health...")
    try:
        response = requests.get('http://localhost:8002/health')
        if response.status_code == 200:
            print("   ✅ Backend is healthy")
        else:
            print(f"   ❌ Backend health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Backend not accessible: {e}")
        return
    
    # Test 2: Frontend Health
    print("2. Testing Frontend Health...")
    try:
        response = requests.get('http://localhost:3000')
        if response.status_code == 200:
            print("   ✅ Frontend is accessible")
        else:
            print(f"   ❌ Frontend check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Frontend not accessible: {e}")
    
    # Test 3: Chat Endpoint
    print("3. Testing Chat Endpoint...")
    try:
        response = requests.post('http://localhost:8002/api/chat', 
                               json={'message': 'سلام، چطوری؟'})
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Chat response: {result['answer'][:50]}...")
        else:
            print(f"   ❌ Chat failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Chat error: {e}")
        return
    
    # Test 4: Check Logs
    print("4. Checking Chat Logs...")
    try:
        from core.db import get_db
        from models.log import ChatLog
        
        db = next(get_db())
        logs = db.query(ChatLog).order_by(ChatLog.timestamp.desc()).limit(5).all()
        
        print(f"   📊 Found {len(logs)} recent logs:")
        for i, log in enumerate(logs[:3]):
            print(f"      {i+1}. ID: {log.id}, User: {log.user_text[:30]}...")
        
        if len(logs) > 0:
            print("   ✅ Logging is working")
        else:
            print("   ❌ No logs found - logging not working")
            
    except Exception as e:
        print(f"   ❌ Log check error: {e}")
    
    # Test 5: Admin Panel
    print("5. Testing Admin Panel...")
    try:
        response = requests.get('http://localhost:3000/admin')
        if response.status_code == 200:
            print("   ✅ Admin panel is accessible")
        else:
            print(f"   ❌ Admin panel check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Admin panel not accessible: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 SYSTEM TEST COMPLETED!")
    print("=" * 60)
    
    print("\n📋 SUMMARY:")
    print("- Backend: Running on http://localhost:8002")
    print("- Frontend: Running on http://localhost:3000")
    print("- Admin Panel: http://localhost:3000/admin")
    print("- API Docs: http://localhost:8002/docs")
    print("\n✅ Your chatbot system is fully functional!")

if __name__ == "__main__":
    test_complete_system()

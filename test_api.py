#!/usr/bin/env python3
"""
Test script to verify API endpoints are working
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_api():
    try:
        # Test health endpoint
        print("🔍 Testing health endpoint...")
        response = requests.get("http://localhost:8000/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        
        # Test categories endpoint
        print("\n🔍 Testing categories endpoint...")
        response = requests.get(f"{BASE_URL}/categories")
        print(f"Categories: {response.status_code}")
        if response.status_code == 200:
            categories = response.json()
            print(f"Found {len(categories)} categories:")
            for cat in categories:
                print(f"  - {cat['name']} (ID: {cat['id']})")
        
        # Test creating a new category
        print("\n🔍 Testing category creation...")
        test_category = {
            "name": "تست دسته‌بندی",
            "slug": "test-category"
        }
        response = requests.post(f"{BASE_URL}/categories", json=test_category)
        print(f"Create category: {response.status_code}")
        if response.status_code == 200:
            print("✅ Category created successfully!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()

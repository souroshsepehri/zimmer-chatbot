"""
Smoke test for site-scoped chat flow

This script tests:
1. Adding a test site to the database
2. Sending a chat request with site_host
3. Verifying site resolution and scoped responses
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from core.db import engine, SessionLocal
from models.tracked_site import TrackedSite
from services.sites_service import resolve_site_by_host, extract_domain_from_url
import requests
import json

def create_test_site(db: Session) -> TrackedSite:
    """Create a test site for testing"""
    # Check if test site already exists
    existing = db.query(TrackedSite).filter(
        TrackedSite.domain == "testsite.com"
    ).first()
    
    if existing:
        print(f"✓ Test site already exists: {existing.name} (id: {existing.id})")
        return existing
    
    # Create new test site
    test_site = TrackedSite(
        name="Test Site",
        url="https://testsite.com",
        domain=extract_domain_from_url("https://testsite.com"),
        description="Test site for smoke testing",
        is_active=True
    )
    
    db.add(test_site)
    db.commit()
    db.refresh(test_site)
    
    print(f"✓ Created test site: {test_site.name} (id: {test_site.id}, domain: {test_site.domain})")
    return test_site

def test_site_resolution(db: Session):
    """Test site resolution by host"""
    print("\n--- Testing Site Resolution ---")
    
    test_hosts = [
        "testsite.com",
        "www.testsite.com",
        "testsite.com:443",
        "https://testsite.com",
        "unknown-site.com"
    ]
    
    for host in test_hosts:
        site = resolve_site_by_host(db, host)
        if site:
            print(f"✓ Resolved '{host}' -> {site.name} (id: {site.id})")
        else:
            print(f"✗ Could not resolve '{host}'")

def test_chat_endpoint(base_url: str = "http://localhost:8001"):
    """Test chat endpoint with site_host"""
    print("\n--- Testing Chat Endpoint ---")
    
    # Test 1: Chat with site_host (should resolve site)
    print("\nTest 1: Chat request with site_host='testsite.com'")
    response = requests.post(
        f"{base_url}/api/chat",
        headers={"Content-Type": "application/json"},
        json={
            "channel": "website-widget",
            "user_id": "test-user",
            "message": "یک سوال درباره محتوای همین سایت تست",
            "site_host": "testsite.com"
        },
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Request successful")
        print(f"  Answer: {data.get('answer', '')[:100]}...")
        print(f"  Source: {data.get('source')}")
        print(f"  Success: {data.get('success')}")
        
        # Check debug_info for site information
        debug_info = data.get('debug_info', {})
        metadata = debug_info.get('metadata', {})
        if metadata.get('tracked_site_id'):
            print(f"  ✓ Site resolved: site_id={metadata.get('tracked_site_id')}")
        else:
            print(f"  ⚠ No site_id in metadata")
            
        # Verify SmartAIAgent was NOT called
        if debug_info.get('smart_agent_raw') is None:
            print(f"  ✓ SmartAIAgent was NOT called (as expected)")
        else:
            print(f"  ✗ WARNING: SmartAIAgent was called!")
    else:
        print(f"✗ Request failed: {response.status_code}")
        print(f"  Response: {response.text}")
    
    # Test 2: Chat without site_host (should still work)
    print("\nTest 2: Chat request without site_host (backward compatibility)")
    response = requests.post(
        f"{base_url}/api/chat",
        headers={"Content-Type": "application/json"},
        json={
            "channel": "telegram",
            "user_id": "test-user-2",
            "message": "سلام"
        },
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Request successful (backward compatible)")
        print(f"  Answer: {data.get('answer', '')[:100]}...")
        print(f"  Source: {data.get('source')}")
    else:
        print(f"✗ Request failed: {response.status_code}")
        print(f"  Response: {response.text}")
    
    # Test 3: Chat with unknown site_host (should return fallback)
    print("\nTest 3: Chat request with unknown site_host")
    response = requests.post(
        f"{base_url}/api/chat",
        headers={"Content-Type": "application/json"},
        json={
            "channel": "website-widget",
            "user_id": "test-user-3",
            "message": "سوال تست",
            "site_host": "unknown-site.com"
        },
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Request successful")
        print(f"  Answer: {data.get('answer', '')[:100]}...")
        print(f"  Source: {data.get('source')}")
        print(f"  Success: {data.get('success')}")
        
        # Should be fallback
        if data.get('source') == 'fallback':
            print(f"  ✓ Correctly returned fallback for unknown site")
        else:
            print(f"  ⚠ Expected fallback, got: {data.get('source')}")
    else:
        print(f"✗ Request failed: {response.status_code}")
        print(f"  Response: {response.text}")

def main():
    """Run all smoke tests"""
    print("=" * 60)
    print("Site-Scoped Chat Flow Smoke Test")
    print("=" * 60)
    
    # Initialize database session
    db = SessionLocal()
    
    try:
        # Step 1: Create test site
        print("\n--- Step 1: Creating Test Site ---")
        test_site = create_test_site(db)
        
        # Step 2: Test site resolution
        test_site_resolution(db)
        
        # Step 3: Test chat endpoint
        print("\n--- Step 3: Testing Chat Endpoint ---")
        print("Make sure the backend server is running on http://localhost:8001")
        print("Press Enter to continue or Ctrl+C to skip endpoint tests...")
        try:
            input()
        except KeyboardInterrupt:
            print("\nSkipping endpoint tests...")
            return
        
        test_chat_endpoint()
        
        print("\n" + "=" * 60)
        print("Smoke test completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during smoke test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()








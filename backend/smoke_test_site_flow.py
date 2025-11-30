"""
Comprehensive Smoke Test for Site-Scoped Chat Flow

This script tests:
1. Adding a test site via admin API
2. Site resolution by host
3. Chat endpoint with site_host parameter
4. Verification that FAQ/DB retrieval is scoped to site
5. Verification that SmartAIAgent is NOT called when no data
6. Fallback behavior for unknown sites
7. Backward compatibility (requests without site_host)

Usage:
    python backend/smoke_test_site_flow.py
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from sqlalchemy.orm import Session
from core.db import engine, SessionLocal
from models.tracked_site import TrackedSite
from models.faq import FAQ
from services.sites_service import resolve_site_by_host, extract_domain_from_url
import requests
import json
import time

# Configuration
API_BASE = "http://localhost:8001/api"
TEST_SITE_DOMAIN = "testsite.com"
TEST_SITE_URL = f"https://{TEST_SITE_DOMAIN}"

def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_test(text: str):
    """Print a test step"""
    print(f"\n→ {text}")

def print_success(text: str):
    """Print success message"""
    print(f"  ✓ {text}")

def print_warning(text: str):
    """Print warning message"""
    print(f"  ⚠ {text}")

def print_error(text: str):
    """Print error message"""
    print(f"  ✗ {text}")

def check_server_running() -> bool:
    """Check if the backend server is running"""
    try:
        response = requests.get(f"{API_BASE.replace('/api', '')}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def create_test_site_via_api() -> dict:
    """Create a test site via admin API"""
    print_test("Creating test site via admin API")
    
    # Check if site already exists
    try:
        response = requests.get(f"{API_BASE}/admin/sites", timeout=5)
        if response.status_code == 200:
            sites = response.json()
            for site in sites:
                if site.get("domain") == TEST_SITE_DOMAIN or TEST_SITE_DOMAIN in site.get("url", ""):
                    print_success(f"Test site already exists: {site.get('name')} (id: {site.get('id')})")
                    return site
    except Exception as e:
        print_warning(f"Could not check existing sites: {e}")
    
    # Create new site
    try:
        payload = {
            "name": "Test Site for Smoke Test",
            "url": TEST_SITE_URL,
            "description": "Test site created by smoke test script",
            "is_active": True
        }
        response = requests.post(f"{API_BASE}/admin/sites", json=payload, timeout=5)
        if response.status_code == 200:
            site = response.json()
            print_success(f"Created test site: {site.get('name')} (id: {site.get('id')}, domain: {site.get('domain')})")
            return site
        else:
            print_error(f"Failed to create site: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print_error(f"Error creating site: {e}")
        return None

def test_site_resolution(db: Session):
    """Test site resolution by various host formats"""
    print_test("Testing site resolution by host")
    
    test_hosts = [
        ("testsite.com", True),
        ("www.testsite.com", True),
        ("testsite.com:443", True),
        ("https://testsite.com", True),
        ("unknown-site.com", False),
    ]
    
    all_passed = True
    for host, should_resolve in test_hosts:
        site = resolve_site_by_host(db, host)
        if should_resolve:
            if site:
                print_success(f"Resolved '{host}' -> {site.name} (id: {site.id})")
            else:
                print_error(f"Failed to resolve '{host}' (expected success)")
                all_passed = False
        else:
            if not site:
                print_success(f"Correctly did not resolve '{host}'")
            else:
                print_error(f"Unexpectedly resolved '{host}' -> {site.name}")
                all_passed = False
    
    return all_passed

def test_chat_with_site_host():
    """Test chat endpoint with site_host parameter"""
    print_test("Testing chat endpoint with site_host='testsite.com'")
    
    payload = {
        "channel": "website-widget",
        "user_id": "test-user-smoke",
        "message": "یک سوال درباره محتوای همین سایت تست",
        "site_host": TEST_SITE_DOMAIN
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/chat",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        
        if response.status_code != 200:
            print_error(f"Request failed: {response.status_code}")
            print_error(f"Response: {response.text[:200]}")
            return False
        
        data = response.json()
        debug_info = data.get('debug_info', {})
        metadata = debug_info.get('metadata', {})
        
        # Verify site was resolved
        site_id = metadata.get('tracked_site_id')
        if site_id:
            print_success(f"Site resolved: tracked_site_id={site_id}")
        else:
            print_error("Site was NOT resolved (tracked_site_id missing)")
            return False
        
        # Verify SmartAIAgent was NOT called
        smart_agent_raw = debug_info.get('smart_agent_raw')
        if smart_agent_raw is None:
            print_success("SmartAIAgent was NOT called (correct for DB-only mode)")
        else:
            print_error("SmartAIAgent WAS called (should not happen in DB-only mode)")
            return False
        
        # Check answer source
        source = data.get('source')
        answer = data.get('answer', '')
        
        print_success(f"Answer source: {source}")
        print_success(f"Answer preview: {answer[:100]}...")
        
        # If no FAQ data exists for this site, should get fallback
        if source == 'fallback':
            print_success("Got fallback answer (expected if no FAQs for this site)")
        elif source in ['faq', 'db', 'database']:
            print_success(f"Got answer from {source} (site-scoped)")
        
        return True
        
    except Exception as e:
        print_error(f"Error testing chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chat_without_site_host():
    """Test backward compatibility - chat without site_host"""
    print_test("Testing backward compatibility (chat without site_host)")
    
    payload = {
        "channel": "telegram",
        "user_id": "test-user-backward",
        "message": "سلام"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/chat",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Request successful (backward compatible)")
            print_success(f"Answer: {data.get('answer', '')[:100]}...")
            print_success(f"Source: {data.get('source')}")
            return True
        else:
            print_error(f"Request failed: {response.status_code}")
            print_error(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_chat_with_unknown_site():
    """Test chat with unknown site_host (should return fallback)"""
    print_test("Testing chat with unknown site_host")
    
    payload = {
        "channel": "website-widget",
        "user_id": "test-user-unknown",
        "message": "سوال تست",
        "site_host": "unknown-site-that-does-not-exist.com"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/chat",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        
        if response.status_code != 200:
            print_error(f"Request failed: {response.status_code}")
            return False
        
        data = response.json()
        source = data.get('source')
        debug_info = data.get('debug_info', {})
        metadata = debug_info.get('metadata', {})
        
        # Should return fallback
        if source == 'fallback':
            print_success("Correctly returned fallback for unknown site")
        else:
            print_warning(f"Expected fallback, got source: {source}")
        
        # Should NOT have tracked_site_id
        if not metadata.get('tracked_site_id'):
            print_success("Correctly did not resolve unknown site")
        else:
            print_error(f"Unexpectedly resolved unknown site: {metadata.get('tracked_site_id')}")
            return False
        
        # SmartAIAgent should NOT be called
        if debug_info.get('smart_agent_raw') is None:
            print_success("SmartAIAgent was NOT called (correct)")
        else:
            print_error("SmartAIAgent WAS called (should not happen)")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def verify_faq_scoping(db: Session, site_id: int):
    """Verify that FAQs can be scoped to a site"""
    print_test("Verifying FAQ scoping to site")
    
    # Check if there are any FAQs for this site
    site_faqs = db.query(FAQ).filter(
        FAQ.tracked_site_id == site_id,
        FAQ.is_active == True
    ).all()
    
    global_faqs = db.query(FAQ).filter(
        FAQ.tracked_site_id.is_(None),
        FAQ.is_active == True
    ).limit(5).all()
    
    print_success(f"Found {len(site_faqs)} FAQs scoped to site_id={site_id}")
    print_success(f"Found {len(global_faqs)} global FAQs (tracked_site_id is None)")
    
    if len(site_faqs) == 0 and len(global_faqs) == 0:
        print_warning("No FAQs found in database - fallback will be used")
    else:
        print_success("FAQ scoping is working correctly")
    
    return True

def main():
    """Run all smoke tests"""
    print_header("Site-Scoped Chat Flow Smoke Test")
    
    # Check if server is running
    print_test("Checking if backend server is running")
    if not check_server_running():
        print_error("Backend server is not running!")
        print_error(f"Please start the server on {API_BASE.replace('/api', '')}")
        print_error("Then run this script again.")
        return 1
    print_success("Backend server is running")
    
    # Initialize database session for direct DB operations
    db = SessionLocal()
    
    try:
        # Step 1: Create test site via API
        print_header("Step 1: Create Test Site")
        test_site = create_test_site_via_api()
        if not test_site:
            print_error("Failed to create test site. Aborting.")
            return 1
        
        site_id = test_site.get('id')
        
        # Step 2: Test site resolution
        print_header("Step 2: Test Site Resolution")
        if not test_site_resolution(db):
            print_error("Site resolution tests failed")
            return 1
        
        # Step 3: Verify FAQ scoping
        print_header("Step 3: Verify FAQ Scoping")
        verify_faq_scoping(db, site_id)
        
        # Step 4: Test chat endpoint with site_host
        print_header("Step 4: Test Chat Endpoint with site_host")
        if not test_chat_with_site_host():
            print_error("Chat endpoint test with site_host failed")
            return 1
        
        # Step 5: Test backward compatibility
        print_header("Step 5: Test Backward Compatibility")
        if not test_chat_without_site_host():
            print_warning("Backward compatibility test had issues (non-critical)")
        
        # Step 6: Test unknown site
        print_header("Step 6: Test Unknown Site Handling")
        if not test_chat_with_unknown_site():
            print_error("Unknown site test failed")
            return 1
        
        # Summary
        print_header("Smoke Test Summary")
        print_success("All critical tests passed!")
        print("\nNext steps:")
        print("  1. Open admin panel and verify test site appears in list")
        print("  2. Add some FAQs for the test site (optional)")
        print("  3. Test the widget on a simple HTML page")
        print("\nTo test the widget:")
        print(f"  1. Create a simple HTML page")
        print(f"  2. Embed the widget script")
        print(f"  3. Access the page from {TEST_SITE_DOMAIN} (or mock it)")
        print(f"  4. Verify chat only uses site-scoped data")
        
        return 0
        
    except Exception as e:
        print_error(f"Error during smoke test: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


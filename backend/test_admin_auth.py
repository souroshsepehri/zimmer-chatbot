"""
Simple test script to verify admin authentication is working.
Run this after starting the server.
"""
import requests
import time

BASE_URL = "http://localhost:8001"

def test_admin_redirect():
    """Test that /admin redirects to /admin/login when not authenticated"""
    print("Testing /admin redirect...")
    response = requests.get(f"{BASE_URL}/admin", allow_redirects=False)
    print(f"Status: {response.status_code}")
    print(f"Location: {response.headers.get('Location', 'N/A')}")
    assert response.status_code == 303, "Should redirect with 303"
    assert "/admin/login" in response.headers.get("Location", ""), "Should redirect to /admin/login"
    print("✓ /admin redirects to /admin/login\n")

def test_login_page():
    """Test that login page is accessible"""
    print("Testing /admin/login page...")
    response = requests.get(f"{BASE_URL}/admin/login")
    print(f"Status: {response.status_code}")
    assert response.status_code == 200, "Login page should be accessible"
    assert "Admin Login" in response.text, "Should show login form"
    print("✓ Login page is accessible\n")

def test_non_admin_routes():
    """Test that non-admin routes are not affected"""
    print("Testing non-admin routes...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    assert response.status_code == 200, "Root route should work"
    print("✓ Root route works\n")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check status: {response.status_code}")
    assert response.status_code == 200, "Health check should work"
    print("✓ Health check works\n")

def test_api_admin_protection():
    """Test that /api/admin routes are protected"""
    print("Testing /api/admin protection...")
    response = requests.get(f"{BASE_URL}/api/admin/bot-settings", allow_redirects=False)
    print(f"Status: {response.status_code}")
    # API routes should return 401, not redirect
    assert response.status_code == 401, "API routes should return 401 when not authenticated"
    print("✓ /api/admin routes are protected\n")

if __name__ == "__main__":
    print("=" * 50)
    print("Admin Authentication Test")
    print("=" * 50)
    print()
    
    try:
        test_non_admin_routes()
        test_admin_redirect()
        test_login_page()
        test_api_admin_protection()
        
        print("=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)
        print()
        print("Next steps:")
        print("1. Open http://localhost:8001/admin/login in a browser")
        print("2. Login with: zimmer admin / admin1234")
        print("3. You should be redirected to /admin")
        print("4. Wait 5+ minutes without activity, then try accessing /admin again")
        print("5. You should be redirected back to /admin/login")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server. Make sure the server is running:")
        print("   cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8001")


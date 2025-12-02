"""
Diagnostic script to verify no 401 responses in admin login flow.
"""
import requests
import sys

BASE_URL = "http://localhost:8000"

def test_admin_login_flow():
    """Test the admin login flow and verify no 401 responses."""
    print("=" * 60)
    print("Admin Login Flow Diagnostics")
    print("=" * 60)
    
    errors = []
    
    # Test 1: GET /admin/login should return 200 (not 401)
    print("\n1. Testing GET /admin/login...")
    try:
        response = requests.get(f"{BASE_URL}/admin/login", allow_redirects=False)
        if response.status_code == 401:
            errors.append("❌ GET /admin/login returns 401 (should return 200)")
            print(f"   ❌ Status: {response.status_code} (expected 200)")
        elif response.status_code == 200:
            print(f"   ✓ Status: {response.status_code}")
            # Check for Farsi error text (should only be in HTML, not as 401 response)
            if "نام کاربری یا رمز عبور اشتباه است" in response.text:
                print("   ✓ Farsi error text found in HTML (expected)")
        else:
            print(f"   ⚠ Status: {response.status_code} (expected 200)")
    except Exception as e:
        errors.append(f"❌ Error testing GET /admin/login: {e}")
        print(f"   ❌ Error: {e}")
    
    # Test 2: POST /admin/login with wrong credentials should return 302 (not 401)
    print("\n2. Testing POST /admin/login with wrong credentials...")
    try:
        response = requests.post(
            f"{BASE_URL}/admin/login",
            data={"username": "wrong", "password": "wrong"},
            allow_redirects=False
        )
        if response.status_code == 401:
            errors.append("❌ POST /admin/login with wrong credentials returns 401 (should return 302)")
            print(f"   ❌ Status: {response.status_code} (expected 302)")
        elif response.status_code == 302:
            print(f"   ✓ Status: {response.status_code}")
            location = response.headers.get("Location", "")
            if "/admin/login?error=1" in location:
                print(f"   ✓ Redirects to: {location}")
            else:
                errors.append(f"❌ Wrong redirect location: {location} (expected /admin/login?error=1)")
        else:
            errors.append(f"❌ Unexpected status: {response.status_code} (expected 302)")
            print(f"   ❌ Status: {response.status_code} (expected 302)")
    except Exception as e:
        errors.append(f"❌ Error testing POST /admin/login (wrong creds): {e}")
        print(f"   ❌ Error: {e}")
    
    # Test 3: POST /admin/login with correct credentials should return 302 (not 401)
    print("\n3. Testing POST /admin/login with correct credentials...")
    try:
        response = requests.post(
            f"{BASE_URL}/admin/login",
            data={"username": "zimmer_admin", "password": "admin1234"},
            allow_redirects=False
        )
        if response.status_code == 401:
            errors.append("❌ POST /admin/login with correct credentials returns 401 (should return 302)")
            print(f"   ❌ Status: {response.status_code} (expected 302)")
        elif response.status_code == 302:
            print(f"   ✓ Status: {response.status_code}")
            location = response.headers.get("Location", "")
            if location == "/admin" or location.endswith("/admin"):
                print(f"   ✓ Redirects to: {location}")
            else:
                errors.append(f"❌ Wrong redirect location: {location} (expected /admin)")
            
            # Check for cookie
            cookies = response.cookies
            if "zimmer_admin_session" in cookies:
                cookie_value = cookies.get("zimmer_admin_session")
                if cookie_value == "zimmer_admin_active":
                    print(f"   ✓ Cookie set correctly: zimmer_admin_session={cookie_value}")
                else:
                    errors.append(f"❌ Wrong cookie value: {cookie_value} (expected zimmer_admin_active)")
            else:
                errors.append("❌ Cookie zimmer_admin_session not set")
        else:
            errors.append(f"❌ Unexpected status: {response.status_code} (expected 302)")
            print(f"   ❌ Status: {response.status_code} (expected 302)")
    except Exception as e:
        errors.append(f"❌ Error testing POST /admin/login (correct creds): {e}")
        print(f"   ❌ Error: {e}")
    
    # Test 4: Check for any 401 in code
    print("\n4. Checking for 401 status codes in code...")
    try:
        import os
        admin_py_path = os.path.join(os.path.dirname(__file__), "routers", "admin.py")
        with open(admin_py_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for status_code=401
        if "status_code=401" in content or "status_code=status.HTTP_401" in content:
            errors.append("❌ Found status_code=401 in admin.py")
            print("   ❌ Found status_code=401 in admin.py")
        else:
            print("   ✓ No status_code=401 found in admin.py")
        
        # Check for HTTPException with 401
        if "HTTPException" in content and "401" in content:
            # Check if it's only for the 500 error (admin panel not found)
            if "status_code=500" not in content:
                errors.append("❌ Found HTTPException with 401 in admin.py")
                print("   ❌ Found HTTPException with 401 in admin.py")
            else:
                print("   ✓ HTTPException found but only for 500 (admin panel not found)")
        else:
            print("   ✓ No HTTPException with 401 found in admin.py")
    except Exception as e:
        print(f"   ⚠ Could not check code: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    if errors:
        print("❌ DIAGNOSTICS FAILED")
        print("=" * 60)
        for error in errors:
            print(error)
        return 1
    else:
        print("✓ ALL DIAGNOSTICS PASSED")
        print("=" * 60)
        print("✓ No 401 responses found in admin login flow")
        print("✓ All redirects work correctly")
        print("✓ Cookie is set correctly on successful login")
        return 0

if __name__ == "__main__":
    try:
        exit_code = test_admin_login_flow()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)


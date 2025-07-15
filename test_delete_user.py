#!/usr/bin/env python3
"""
Test script to verify user deletion functionality
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_user_deletion():
    """Test complete user deletion workflow"""
    
    print("Testing User Deletion Functionality")
    print("=" * 40)
    
    # Create a session
    session = requests.Session()
    
    # Step 1: Login as engineer
    print("1. Logging in as engineer...")
    login_response = session.post(f"{BASE_URL}/login", data={
        "username": "engineer1",
        "password": "engineer123"
    })
    
    if login_response.status_code == 200:
        print("✓ Login successful")
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    # Step 2: Create a test user
    print("2. Creating test user...")
    create_response = session.post(f"{BASE_URL}/add_user", data={
        "username": "deletetest",
        "password": "test123",
        "role": "storesman",
        "assigned_site_id": "1"
    })
    
    if create_response.status_code == 200:
        print("✓ Test user created")
    else:
        print(f"❌ User creation failed: {create_response.status_code}")
        print(create_response.text[:500])
        return
    
    # Step 3: Get user management page to verify user exists
    print("3. Verifying user exists...")
    manage_response = session.get(f"{BASE_URL}/manage_users")
    
    if manage_response.status_code == 200 and "deletetest" in manage_response.text:
        print("✓ Test user exists in user management")
    else:
        print("❌ Test user not found in user management")
        return
    
    # Step 4: Extract user ID from the page
    import re
    user_id_match = re.search(r'confirmDelete\((\d+), \'deletetest\'\)', manage_response.text)
    if user_id_match:
        user_id = user_id_match.group(1)
        print(f"✓ Found user ID: {user_id}")
    else:
        print("❌ Could not extract user ID")
        return
    
    # Step 5: Test deletion
    print("4. Testing user deletion...")
    delete_response = session.post(f"{BASE_URL}/delete_user", data={
        "user_id": user_id
    })
    
    print(f"Delete response status: {delete_response.status_code}")
    print(f"Delete response headers: {dict(delete_response.headers)}")
    
    if delete_response.status_code == 200:
        print("✓ Delete request successful")
    else:
        print(f"❌ Delete request failed: {delete_response.status_code}")
        print("Response content:", delete_response.text[:500])
        return
    
    # Step 6: Verify user is deleted
    print("5. Verifying user deletion...")
    verify_response = session.get(f"{BASE_URL}/manage_users")
    
    if verify_response.status_code == 200 and "deletetest" not in verify_response.text:
        print("✓ User successfully deleted")
    else:
        print("❌ User still exists after deletion")
        return
    
    print("\n" + "=" * 40)
    print("✓ User deletion functionality working correctly")

if __name__ == "__main__":
    test_user_deletion()
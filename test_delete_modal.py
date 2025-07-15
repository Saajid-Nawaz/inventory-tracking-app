#!/usr/bin/env python3
"""
Test script to debug delete modal functionality
"""

import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "http://localhost:5000"

def test_delete_modal():
    """Test the delete modal functionality"""
    
    print("Testing Delete Modal Functionality")
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
        "username": "modaltest",
        "password": "test123",
        "role": "storesman",
        "assigned_site_id": "1"
    })
    
    if create_response.status_code == 200:
        print("✓ Test user created")
    else:
        print(f"❌ User creation failed: {create_response.status_code}")
        return
    
    # Step 3: Get user management page
    print("3. Getting user management page...")
    manage_response = session.get(f"{BASE_URL}/manage_users")
    
    if manage_response.status_code == 200:
        print("✓ User management page loaded")
        
        # Parse the HTML to examine the delete button structure
        soup = BeautifulSoup(manage_response.text, 'html.parser')
        
        # Find the delete button for modaltest
        delete_button = None
        for button in soup.find_all('button', {'class': 'btn btn-sm btn-outline-danger'}):
            if 'modaltest' in button.get('onclick', ''):
                delete_button = button
                break
        
        if delete_button:
            print(f"✓ Found delete button: {delete_button.get('onclick')}")
            
            # Extract the onclick function parameters
            onclick_text = delete_button.get('onclick')
            match = re.search(r'confirmDelete\((\d+), \'([^\']+)\'\)', onclick_text)
            if match:
                user_id = match.group(1)
                username = match.group(2)
                print(f"✓ Delete button parameters: ID={user_id}, Username={username}")
                
                # Check if the modal exists
                modal = soup.find('div', {'id': 'deleteUserModal'})
                if modal:
                    print("✓ Delete modal found in HTML")
                    
                    # Check if the form exists
                    form = modal.find('form', {'id': 'deleteUserForm'})
                    if form:
                        print(f"✓ Delete form found with action: {form.get('action')}")
                        
                        # Check for hidden input
                        hidden_input = form.find('input', {'name': 'user_id'})
                        if hidden_input:
                            print(f"✓ Hidden input found with ID: {hidden_input.get('id')}")
                        else:
                            print("❌ Hidden input not found")
                    else:
                        print("❌ Delete form not found")
                else:
                    print("❌ Delete modal not found")
            else:
                print("❌ Could not parse onclick parameters")
        else:
            print("❌ Delete button not found")
    else:
        print(f"❌ User management page failed: {manage_response.status_code}")
    
    # Step 4: Test direct delete API call
    print("4. Testing direct delete API call...")
    
    # First, find the user ID
    if manage_response.status_code == 200:
        user_id_match = re.search(r'confirmDelete\((\d+), \'modaltest\'\)', manage_response.text)
        if user_id_match:
            user_id = user_id_match.group(1)
            print(f"✓ Found user ID: {user_id}")
            
            # Try to delete directly
            delete_response = session.post(f"{BASE_URL}/delete_user", data={
                "user_id": user_id
            })
            
            if delete_response.status_code == 200:
                print("✓ Direct delete API call successful")
            else:
                print(f"❌ Direct delete API call failed: {delete_response.status_code}")
                print(f"Response: {delete_response.text[:200]}")
        else:
            print("❌ Could not find user ID for direct delete test")

if __name__ == "__main__":
    test_delete_modal()
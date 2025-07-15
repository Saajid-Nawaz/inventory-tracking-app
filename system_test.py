#!/usr/bin/env python3
"""
Comprehensive System Test for Multi-Site Inventory Management System
Tests all core functionalities to verify MVP readiness
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"
session = requests.Session()

def test_login(username, password):
    """Test user login"""
    print(f"\n=== Testing Login for {username} ===")
    
    # Get login page first
    response = session.get(f"{BASE_URL}/login")
    print(f"Login page status: {response.status_code}")
    
    # Attempt login
    login_data = {
        'username': username,
        'password': password
    }
    response = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    print(f"Login response status: {response.status_code}")
    
    # Check final URL and content
    final_url = response.url
    print(f"Final URL: {final_url}")
    
    # Check if redirected to dashboard
    if "Dashboard" in response.text or "dashboard" in final_url:
        print(f"✓ Login successful for {username}")
        return True
    elif "Invalid" in response.text:
        print(f"✗ Login failed for {username} - Invalid credentials")
        return False
    else:
        print(f"✗ Login failed for {username} - Unknown error")
        print(f"Response content preview: {response.text[:200]}...")
        return False

def test_api_endpoints():
    """Test core API endpoints"""
    print("\n=== Testing API Endpoints ===")
    
    endpoints = [
        "/api/materials",
        "/api/sites",
        "/api/pending_counts"
    ]
    
    for endpoint in endpoints:
        try:
            response = session.get(f"{BASE_URL}{endpoint}")
            print(f"{endpoint}: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✓ {endpoint} working")
            else:
                print(f"  ✗ {endpoint} failed")
        except Exception as e:
            print(f"  ✗ {endpoint} error: {e}")

def test_page_access():
    """Test access to key pages"""
    print("\n=== Testing Page Access ===")
    
    pages = [
        "/receive_materials",
        "/bulk_receive_materials", 
        "/request_materials",
        "/batch_request",
        "/approve_requests",
        "/stock_adjustments",
        "/stock_transfer",
        "/reports"
    ]
    
    for page in pages:
        try:
            response = session.get(f"{BASE_URL}{page}")
            print(f"{page}: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✓ {page} accessible")
            else:
                print(f"  ✗ {page} not accessible")
        except Exception as e:
            print(f"  ✗ {page} error: {e}")

def test_material_receipt():
    """Test material receipt functionality"""
    print("\n=== Testing Material Receipt ===")
    
    # Test data for material receipt
    receipt_data = {
        'site_id': 1,
        'material_id': 1,
        'quantity': 100,
        'unit_cost': 12.50,
        'supplier': 'Test Supplier',
        'invoice_number': 'INV001',
        'project_code': 'PROJ001',
        'notes': 'Test receipt'
    }
    
    try:
        response = session.post(f"{BASE_URL}/process_receive_material", data=receipt_data)
        print(f"Material receipt status: {response.status_code}")
        if response.status_code in [200, 302]:
            print("  ✓ Material receipt working")
        else:
            print("  ✗ Material receipt failed")
    except Exception as e:
        print(f"  ✗ Material receipt error: {e}")

def test_bulk_receipt():
    """Test bulk material receipt"""
    print("\n=== Testing Bulk Material Receipt ===")
    
    # Test data for bulk receipt
    bulk_data = {
        'supplier': 'Bulk Test Supplier',
        'invoice_number': 'BULK001',
        'project_code': 'PROJ001',
        'material_id[]': [1, 2, 3],
        'quantity[]': [50, 100, 75],
        'unit_cost[]': [12.50, 0.85, 25.00]
    }
    
    try:
        response = session.post(f"{BASE_URL}/process_bulk_receive_material", data=bulk_data)
        print(f"Bulk receipt status: {response.status_code}")
        if response.status_code in [200, 302]:
            print("  ✓ Bulk receipt working")
        else:
            print("  ✗ Bulk receipt failed")
    except Exception as e:
        print(f"  ✗ Bulk receipt error: {e}")

def test_material_request():
    """Test material request functionality"""
    print("\n=== Testing Material Request ===")
    
    request_data = {
        'material_id': 1,
        'quantity': 10,
        'purpose': 'Test purpose',
        'priority': 'normal'
    }
    
    try:
        response = session.post(f"{BASE_URL}/process_request_material", data=request_data)
        print(f"Material request status: {response.status_code}")
        if response.status_code in [200, 302]:
            print("  ✓ Material request working")
        else:
            print("  ✗ Material request failed")
    except Exception as e:
        print(f"  ✗ Material request error: {e}")

def test_stock_transfer():
    """Test stock transfer functionality"""
    print("\n=== Testing Stock Transfer ===")
    
    transfer_data = {
        'from_site_id': 1,
        'to_site_id': 2,
        'material_id[]': [1],
        'quantity[]': [25],
        'reason': 'Test transfer',
        'priority': 'normal'
    }
    
    try:
        response = session.post(f"{BASE_URL}/process_stock_transfer", data=transfer_data)
        print(f"Stock transfer status: {response.status_code}")
        if response.status_code in [200, 302]:
            print("  ✓ Stock transfer working")
        else:
            print("  ✗ Stock transfer failed")
    except Exception as e:
        print(f"  ✗ Stock transfer error: {e}")

def run_comprehensive_test():
    """Run all system tests"""
    print("=== COMPREHENSIVE SYSTEM TEST ===")
    print(f"Started at: {datetime.now()}")
    
    # Test engineer login with correct credentials
    if test_login("engineer1", "engineer123"):
        test_api_endpoints()
        test_page_access()
        test_material_receipt()
        test_bulk_receipt()
        test_material_request()
        test_stock_transfer()
    
    # Test storesman login with correct credentials
    session.get(f"{BASE_URL}/logout")
    if test_login("storesman1", "store123"):
        test_page_access()
        test_material_request()
    
    print(f"\n=== TEST COMPLETED at {datetime.now()} ===")

if __name__ == "__main__":
    run_comprehensive_test()
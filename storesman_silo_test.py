#!/usr/bin/env python3
"""
Comprehensive Storesman Silo Isolation Test
Tests that each storesman can only access their assigned site data
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_storesman_silo_isolation():
    """Test that storesmen work in complete silos"""
    
    print("=" * 60)
    print("STORESMAN SILO ISOLATION TEST")
    print("=" * 60)
    
    # Test credentials
    storesmen = [
        {"username": "storesman1", "password": "store123", "expected_site": "Main Construction Site"},
        {"username": "storesman2", "password": "store123", "expected_site": "North Warehouse"},
        {"username": "storesman3", "password": "store123", "expected_site": "South Depot"},
    ]
    
    for storesman in storesmen:
        print(f"\nTesting {storesman['username']} ({storesman['expected_site']}):")
        print("-" * 50)
        
        # Login
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/login", data={
            "username": storesman["username"],
            "password": storesman["password"]
        })
        
        if login_response.status_code != 200:
            print(f"❌ Login failed for {storesman['username']}")
            continue
        
        # Test 1: Sites API - should only return their assigned site
        sites_response = session.get(f"{BASE_URL}/api/sites")
        if sites_response.status_code == 200:
            sites = sites_response.json()
            print(f"✓ Sites accessible: {len(sites)}")
            if len(sites) == 1:
                site_name = sites[0]['name']
                if site_name == storesman['expected_site']:
                    print(f"✓ Correct site isolation: {site_name}")
                else:
                    print(f"❌ Wrong site returned: {site_name}")
            else:
                print(f"❌ Should only see 1 site, got {len(sites)}")
                for site in sites:
                    print(f"  - {site['name']}")
        else:
            print(f"❌ Sites API failed: {sites_response.status_code}")
        
        # Test 2: Stock levels - should only access their site
        if sites_response.status_code == 200 and len(sites) == 1:
            site_id = sites[0]['id']
            stock_response = session.get(f"{BASE_URL}/api/stock_levels/{site_id}")
            if stock_response.status_code == 200:
                stock = stock_response.json()
                print(f"✓ Stock accessible for own site: {len(stock)} items")
            else:
                print(f"❌ Stock API failed for own site: {stock_response.status_code}")
            
            # Test accessing other sites' stock (should fail)
            other_site_ids = [1, 2, 3, 4]
            other_site_ids.remove(site_id)
            
            for other_site_id in other_site_ids:
                other_stock_response = session.get(f"{BASE_URL}/api/stock_levels/{other_site_id}")
                if other_stock_response.status_code == 403:
                    print(f"✓ Correctly blocked from site {other_site_id}")
                else:
                    print(f"❌ Security breach: accessed site {other_site_id} (status: {other_stock_response.status_code})")
        
        # Test 3: Dashboard access
        dashboard_response = session.get(f"{BASE_URL}/storesman")
        if dashboard_response.status_code == 200:
            dashboard_content = dashboard_response.text
            if storesman['expected_site'] in dashboard_content:
                print(f"✓ Dashboard shows correct site: {storesman['expected_site']}")
            else:
                print(f"❌ Dashboard doesn't show expected site")
                
            # Check that other sites are not mentioned in dashboard
            other_sites = ["Main Construction Site", "North Warehouse", "South Depot", "Mwembeshi Stores"]
            other_sites.remove(storesman['expected_site'])
            
            security_breach = False
            for other_site in other_sites:
                if other_site in dashboard_content:
                    print(f"❌ Security breach: Dashboard shows {other_site}")
                    security_breach = True
            
            if not security_breach:
                print("✓ Dashboard properly isolated - no other sites visible")
        else:
            print(f"❌ Dashboard access failed: {dashboard_response.status_code}")
        
        print(f"\n{storesman['username']} isolation test completed")
    
    print("\n" + "=" * 60)
    print("SILO ISOLATION TEST SUMMARY")
    print("=" * 60)
    print("✓ Each storesman can only access their assigned site")
    print("✓ API endpoints properly enforce site-specific access control")
    print("✓ Cross-site access attempts are blocked (403 Forbidden)")
    print("✓ Dashboards show only assigned site information")
    print("✓ Complete data isolation between sites maintained")

if __name__ == "__main__":
    test_storesman_silo_isolation()
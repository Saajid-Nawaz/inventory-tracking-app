#!/usr/bin/env python3
"""
Comprehensive MVP Test - Creates 10 entries, tests approvals, transfers, and reports
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"
session = requests.Session()

def login_engineer():
    """Login as engineer1"""
    response = session.post(f"{BASE_URL}/login", data={
        'username': 'engineer1',
        'password': 'engineer123'
    }, allow_redirects=True)
    return "site_engineer" in response.url

def login_storesman():
    """Login as storesman1"""
    response = session.post(f"{BASE_URL}/login", data={
        'username': 'storesman1',
        'password': 'store123'
    }, allow_redirects=True)
    return "storesman" in response.url

def create_10_material_receipts():
    """Create 10 material receipts"""
    print("\n=== Creating 10 Material Receipts ===")
    
    receipts = [
        {'site_id': 1, 'material_id': 1, 'quantity': 100, 'unit_cost': 12.50, 'supplier': 'ABC Supplies'},
        {'site_id': 1, 'material_id': 2, 'quantity': 500, 'unit_cost': 0.85, 'supplier': 'Steel Corp'},
        {'site_id': 1, 'material_id': 3, 'quantity': 200, 'unit_cost': 2.25, 'supplier': 'Block Masters'},
        {'site_id': 2, 'material_id': 1, 'quantity': 80, 'unit_cost': 12.50, 'supplier': 'ABC Supplies'},
        {'site_id': 2, 'material_id': 4, 'quantity': 50, 'unit_cost': 25.00, 'supplier': 'Sand Plus'},
        {'site_id': 2, 'material_id': 5, 'quantity': 75, 'unit_cost': 30.00, 'supplier': 'Gravel Co'},
        {'site_id': 3, 'material_id': 1, 'quantity': 120, 'unit_cost': 12.50, 'supplier': 'ABC Supplies'},
        {'site_id': 3, 'material_id': 2, 'quantity': 300, 'unit_cost': 0.85, 'supplier': 'Steel Corp'},
        {'site_id': 3, 'material_id': 3, 'quantity': 150, 'unit_cost': 2.25, 'supplier': 'Block Masters'},
        {'site_id': 1, 'material_id': 4, 'quantity': 100, 'unit_cost': 25.00, 'supplier': 'Sand Plus'},
    ]
    
    success_count = 0
    for i, receipt in enumerate(receipts):
        receipt_data = {
            'site_id': receipt['site_id'],
            'material_id': receipt['material_id'],
            'quantity': receipt['quantity'],
            'unit_cost': receipt['unit_cost'],
            'supplier': receipt['supplier'],
            'invoice_number': f'INV-{i+1:03d}',
            'project_code': f'PROJ-{i+1:03d}',
            'notes': f'Test receipt {i+1}'
        }
        
        response = session.post(f"{BASE_URL}/process_receive_material", data=receipt_data)
        if response.status_code in [200, 302]:
            success_count += 1
            print(f"✓ Receipt {i+1} processed successfully")
        else:
            print(f"✗ Receipt {i+1} failed (Status: {response.status_code})")
    
    print(f"Created {success_count}/10 material receipts")
    return success_count

def create_10_material_requests():
    """Create 10 material requests"""
    print("\n=== Creating 10 Material Requests ===")
    
    requests_data = [
        {'material_id': 1, 'quantity': 20, 'purpose': 'Foundation work'},
        {'material_id': 2, 'quantity': 100, 'purpose': 'Reinforcement'},
        {'material_id': 3, 'quantity': 50, 'purpose': 'Wall construction'},
        {'material_id': 4, 'quantity': 10, 'purpose': 'Plastering'},
        {'material_id': 5, 'quantity': 15, 'purpose': 'Concrete mix'},
        {'material_id': 1, 'quantity': 25, 'purpose': 'Floor work'},
        {'material_id': 2, 'quantity': 75, 'purpose': 'Column work'},
        {'material_id': 3, 'quantity': 30, 'purpose': 'Partition walls'},
        {'material_id': 4, 'quantity': 20, 'purpose': 'Finishing'},
        {'material_id': 5, 'quantity': 10, 'purpose': 'Paving'},
    ]
    
    success_count = 0
    for i, req in enumerate(requests_data):
        request_data = {
            'material_id': req['material_id'],
            'quantity': req['quantity'],
            'purpose': req['purpose'],
            'priority': 'normal'
        }
        
        response = session.post(f"{BASE_URL}/process_request_material", data=request_data)
        if response.status_code in [200, 302]:
            success_count += 1
            print(f"✓ Request {i+1} created successfully")
        else:
            print(f"✗ Request {i+1} failed (Status: {response.status_code})")
    
    print(f"Created {success_count}/10 material requests")
    return success_count

def create_10_stock_transfers():
    """Create 10 stock transfer requests"""
    print("\n=== Creating 10 Stock Transfer Requests ===")
    
    transfers = [
        {'from_site_id': 1, 'to_site_id': 2, 'material_id': 1, 'quantity': 10},
        {'from_site_id': 1, 'to_site_id': 3, 'material_id': 2, 'quantity': 50},
        {'from_site_id': 2, 'to_site_id': 1, 'material_id': 4, 'quantity': 5},
        {'from_site_id': 2, 'to_site_id': 3, 'material_id': 5, 'quantity': 8},
        {'from_site_id': 3, 'to_site_id': 1, 'material_id': 1, 'quantity': 15},
        {'from_site_id': 3, 'to_site_id': 2, 'material_id': 2, 'quantity': 25},
        {'from_site_id': 1, 'to_site_id': 2, 'material_id': 3, 'quantity': 20},
        {'from_site_id': 2, 'to_site_id': 3, 'material_id': 1, 'quantity': 12},
        {'from_site_id': 3, 'to_site_id': 1, 'material_id': 4, 'quantity': 18},
        {'from_site_id': 1, 'to_site_id': 3, 'material_id': 5, 'quantity': 6},
    ]
    
    success_count = 0
    for i, transfer in enumerate(transfers):
        transfer_data = {
            'from_site_id': transfer['from_site_id'],
            'to_site_id': transfer['to_site_id'],
            'material_id[]': [transfer['material_id']],
            'quantity[]': [transfer['quantity']],
            'reason': f'Transfer {i+1} - Site rebalancing',
            'priority': 'normal'
        }
        
        response = session.post(f"{BASE_URL}/process_stock_transfer", data=transfer_data)
        if response.status_code in [200, 302]:
            success_count += 1
            print(f"✓ Transfer {i+1} created successfully")
        else:
            print(f"✗ Transfer {i+1} failed (Status: {response.status_code})")
    
    print(f"Created {success_count}/10 stock transfers")
    return success_count

def test_reports():
    """Test report generation"""
    print("\n=== Testing Reports ===")
    
    # Test PDF report
    response = session.get(f"{BASE_URL}/generate_pdf_report", params={'report_type': 'stock_summary', 'site_id': 1})
    print(f"PDF Report Status: {response.status_code}")
    
    # Test Excel report  
    response = session.get(f"{BASE_URL}/generate_excel_report", params={'report_type': 'stock_summary', 'site_id': 1})
    print(f"Excel Report Status: {response.status_code}")
    
    # Test transaction history
    response = session.get(f"{BASE_URL}/generate_pdf_report", params={'report_type': 'transaction_history', 'site_id': 1})
    print(f"Transaction History Report Status: {response.status_code}")

def run_comprehensive_test():
    """Run comprehensive MVP test"""
    print("=== COMPREHENSIVE MVP TEST ===")
    print(f"Started at: {datetime.now()}")
    
    # Login as engineer
    if not login_engineer():
        print("✗ Engineer login failed")
        return
    
    print("✓ Engineer login successful")
    
    # Create test data
    receipts = create_10_material_receipts()
    
    # Logout and login as storesman
    session.get(f"{BASE_URL}/logout")
    if not login_storesman():
        print("✗ Storesman login failed")
        return
    
    print("✓ Storesman login successful")
    
    # Create requests
    requests_count = create_10_material_requests()
    
    # Logout and login as engineer again
    session.get(f"{BASE_URL}/logout")
    if not login_engineer():
        print("✗ Engineer re-login failed")
        return
    
    # Create transfers
    transfers = create_10_stock_transfers()
    
    # Test reports
    test_reports()
    
    print(f"\n=== TEST SUMMARY ===")
    print(f"Material Receipts: {receipts}/10")
    print(f"Material Requests: {requests_count}/10")
    print(f"Stock Transfers: {transfers}/10")
    print(f"Test completed at: {datetime.now()}")

if __name__ == "__main__":
    run_comprehensive_test()
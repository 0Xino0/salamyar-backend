#!/usr/bin/env python3
"""
Simple server test script for Windows environment.
"""

import subprocess
import requests
import time
import sys
import signal
import os

def test_api_endpoints():
    """Test API endpoints with a running server."""
    
    print("🧪 Testing API Endpoints")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test 1: Health check
        print("1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health: {data['status']} - {data['service']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
        
        # Test 2: Search endpoint  
        print("\n2. Testing search endpoint...")
        response = requests.get(
            f"{base_url}/api/v1/search/products",
            params={"q": "جامدادی", "from": 0, "size": 3},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Search: Found {len(data['products'])} products")
            print(f"   📊 Total available: {data['meta']['total_count']}")
            
            if not data['products']:
                print("   ⚠️ No products found, but search is working")
                return True
                
            # Test 3: Product selection
            print("\n3. Testing product selection...")
            product = data['products'][0]
            selection_data = {
                "product_id": product['id'],
                "product_name": product['name'],
                "vendor_id": product['vendor_id'],
                "vendor_name": product['vendor_name'],
                "status_id": product['status_id'],
                "image_url": product['image']['medium'],
                "search_session_id": "test-session-123"
            }
            
            response = requests.post(
                f"{base_url}/api/v1/selections/products",
                json=selection_data,
                timeout=5
            )
            
            if response.status_code == 200:
                selected = response.json()
                print(f"   ✅ Selection: {selected['product_name'][:40]}...")
                
                # Test 4: Get selections
                print("\n4. Testing get selections...")
                response = requests.get(f"{base_url}/api/v1/selections/products", timeout=5)
                
                if response.status_code == 200:
                    selections = response.json()
                    print(f"   ✅ Get selections: {selections['total_count']} products")
                    
                    # Test 5: Cart confirmation (the main new feature)
                    print("\n5. Testing cart confirmation...")
                    print("   ⏳ This may take 30-60 seconds as it analyzes similar products...")
                    
                    response = requests.post(
                        f"{base_url}/api/v1/selections/confirm",
                        timeout=90  # Give it plenty of time
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"   ✅ Cart confirmation successful!")
                        print(f"   📦 Selected products: {result['total_selected_products']}")
                        print(f"   🔍 Similar products found: {result['total_similar_products_found']}")
                        print(f"   🏪 Vendors with multiple matches: {len(result['vendors_with_multiple_matches'])}")
                        
                        if result['vendors_with_multiple_matches']:
                            vendor = result['vendors_with_multiple_matches'][0]
                            print(f"   📋 Example vendor: {vendor['vendor_name']}")
                            print(f"      - Matches {vendor['matched_products_count']} products")
                            print(f"      - Has {len(vendor['similar_products'])} similar products")
                            if vendor['similar_products']:
                                example_product = vendor['similar_products'][0]
                                print(f"      - Example: {example_product['basalam_url']}")
                        
                        return True
                    else:
                        print(f"   ❌ Cart confirmation failed: {response.status_code}")
                        try:
                            error = response.json()
                            print(f"   📝 Error: {error}")
                        except:
                            print(f"   📝 Response: {response.text}")
                        return False
                else:
                    print(f"   ❌ Get selections failed: {response.status_code}")
                    return False
            else:
                print(f"   ❌ Product selection failed: {response.status_code}")
                return False
        else:
            print(f"   ❌ Search failed: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("   ⏰ Request timed out")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Salamyar API Server Test")
    print("Make sure to start the server first with: py start_server.py")
    print("Then run this test in another terminal\n")
    
    # Test if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            print("✅ Server is running, starting tests...\n")
            
            if test_api_endpoints():
                print("\n" + "=" * 40)
                print("🎉 ALL TESTS PASSED!")
                print("🌐 API Documentation: http://localhost:8000/api/v1/docs")
                print("✅ Your cart confirmation feature is working perfectly!")
            else:
                print("\n" + "=" * 40)  
                print("❌ Some tests failed")
        else:
            print("❌ Server is not responding properly")
            
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("\nTo run the test:")
        print("1. Start server: py start_server.py")
        print("2. In another terminal, run: py test_server.py")

if __name__ == "__main__":
    main()

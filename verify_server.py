#!/usr/bin/env python3
"""
Simple verification that the server is running and accessible.
"""

import time
import requests
import json
from urllib.parse import urlencode

def test_api_endpoints():
    """Test all API endpoints."""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Salamyar API endpoints...")
    print("=" * 50)
    
    try:
        # Test health endpoint
        print("1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed: {data['status']}")
            print(f"   📊 Service: {data['service']}")
            print(f"   🔢 Version: {data['version']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
            
        # Test search endpoint
        print("\n2. Testing search endpoint...")
        search_params = {"q": "آیفون", "from": 0, "size": 3}
        response = requests.get(
            f"{base_url}/api/v1/search/products",
            params=search_params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Search successful!")
            print(f"   📱 Found {data['meta']['total_count']} total products")
            print(f"   📄 Showing {len(data['products'])} products")
            print(f"   ➡️ Has more: {data['meta']['has_more']}")
            
            if data['products']:
                first_product = data['products'][0]
                print(f"   🎯 First product: {first_product['name'][:50]}...")
                print(f"   💰 Price: {first_product['price']:,.0f} تومان")
                
                # Test product selection
                print("\n3. Testing product selection...")
                selection_data = {
                    "product_id": first_product['id'],
                    "product_name": first_product['name'],
                    "vendor_id": first_product['vendor_id'],
                    "vendor_name": first_product['vendor_name'],
                    "status_id": first_product['status_id'],
                    "image_url": first_product['image']['medium']
                }
                
                response = requests.post(
                    f"{base_url}/api/v1/selections/products",
                    json=selection_data,
                    timeout=5
                )
                
                if response.status_code == 200:
                    selected = response.json()
                    print(f"   ✅ Product selected: {selected['product_name'][:30]}...")
                    
                    # Test getting selections
                    print("\n4. Testing get selections...")
                    response = requests.get(f"{base_url}/api/v1/selections/products", timeout=5)
                    
                    if response.status_code == 200:
                        selections = response.json()
                        print(f"   ✅ Retrieved {selections['total_count']} selected products")
                        
                        # Test removing selection
                        print("\n5. Testing remove selection...")
                        response = requests.delete(
                            f"{base_url}/api/v1/selections/products/{first_product['id']}",
                            timeout=5
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            print(f"   ✅ Product removed: {result['message']}")
                            return True
                        else:
                            print(f"   ❌ Remove failed: {response.status_code}")
                    else:
                        print(f"   ❌ Get selections failed: {response.status_code}")
                else:
                    print(f"   ❌ Product selection failed: {response.status_code}")
        else:
            print(f"   ❌ Search failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        print("   Make sure the server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return False

def main():
    """Main function."""
    print("🚀 Salamyar API Live Verification")
    print(f"⏰ Starting at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Wait a moment for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(2)
    
    success = test_api_endpoints()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print()
        print("✅ Your Salamyar API is working perfectly!")
        print("📚 Documentation: http://localhost:8000/api/v1/docs")
        print("🔍 Search API: http://localhost:8000/api/v1/search/products")
        print("📦 Selection API: http://localhost:8000/api/v1/selections/products")
        print()
        print("🌐 Ready for frontend integration!")
    else:
        print("❌ Some tests failed.")
        print("   Check that the server is running: py -m uvicorn app.main:app --reload")
    
    return 0 if success else 1

if __name__ == "__main__":
    main()

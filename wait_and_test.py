#!/usr/bin/env python3
"""
Wait for server to start and then test it.
"""

import requests
import time

def wait_for_server(max_attempts=10):
    """Wait for server to start."""
    print("⏳ Waiting for server to start...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ Server is running after {attempt + 1} attempts")
                return True
        except:
            pass
        
        print(f"   Attempt {attempt + 1}/{max_attempts}...")
        time.sleep(2)
    
    print("❌ Server failed to start after waiting")
    return False

def test_basic_functionality():
    """Test basic API functionality."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test health
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data['status']}")
        
        # Test search
        print("🔍 Testing search...")
        response = requests.get(
            "http://localhost:8000/api/v1/search/products",
            params={"q": "جامدادی", "from": 0, "size": 2},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search: Found {len(data['products'])} products")
            
            if data['products']:
                # Test selection
                print("📦 Testing product selection...")
                product = data['products'][0]
                selection_data = {
                    "product_id": product['id'],
                    "product_name": product['name'],
                    "vendor_id": product['vendor_id'],
                    "vendor_name": product['vendor_name'],
                    "status_id": product['status_id'],
                    "image_url": product['image']['medium'],
                    "search_session_id": "test-session"
                }
                
                response = requests.post(
                    "http://localhost:8000/api/v1/selections/products",
                    json=selection_data,
                    timeout=5
                )
                
                if response.status_code == 200:
                    print("✅ Product selection working")
                    
                    # Test get selections
                    response = requests.get("http://localhost:8000/api/v1/selections/products")
                    if response.status_code == 200:
                        selections = response.json()
                        print(f"✅ Get selections: {selections['total_count']} products")
                        
                        # Test cart confirmation (might take time)
                        print("🛒 Testing cart confirmation (this may take a while)...")
                        response = requests.post(
                            "http://localhost:8000/api/v1/selections/confirm",
                            timeout=45
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            print(f"✅ Cart confirmation working!")
                            print(f"   Selected: {result['total_selected_products']}")
                            print(f"   Similar found: {result['total_similar_products_found']}")
                            print(f"   Vendors: {len(result['vendors_with_multiple_matches'])}")
                        else:
                            print(f"❌ Cart confirmation failed: {response.status_code}")
                    else:
                        print(f"❌ Get selections failed: {response.status_code}")
                else:
                    print(f"❌ Product selection failed: {response.status_code}")
        else:
            print(f"❌ Search failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    if wait_for_server():
        test_basic_functionality()
        print("\n🎉 All tests completed!")
        print("🌐 API Docs: http://localhost:8000/api/v1/docs")
    else:
        print("❌ Could not connect to server")

#!/usr/bin/env python3
"""
Quick test to verify server is working and test the cart confirmation functionality.
"""

import requests
import time
import json

def test_server_health():
    """Test if server is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and healthy")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return False

def test_search_endpoint():
    """Test the search endpoint."""
    try:
        response = requests.get(
            "http://localhost:8000/api/v1/search/products",
            params={"q": "جامدادی", "from": 0, "size": 3},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search endpoint working - found {len(data['products'])} products")
            return data.get('products', [])
        else:
            print(f"❌ Search endpoint failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return []

def test_product_selection(products):
    """Test product selection."""
    if not products:
        print("❌ No products to select")
        return False
    
    try:
        product = products[0]
        selection_data = {
            "product_id": product['id'],
            "product_name": product['name'],
            "vendor_id": product['vendor_id'],
            "vendor_name": product['vendor_name'],
            "status_id": product['status_id'],
            "image_url": product['image']['medium'],
            "search_session_id": "test-session-1"
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/selections/products",
            json=selection_data,
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ Product selection working")
            return True
        else:
            print(f"❌ Product selection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Product selection test failed: {e}")
        return False

def test_get_selections():
    """Test getting selections."""
    try:
        response = requests.get("http://localhost:8000/api/v1/selections/products", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get selections working - {data['total_count']} products selected")
            return data['total_count'] > 0
        else:
            print(f"❌ Get selections failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get selections test failed: {e}")
        return False

def test_cart_confirmation():
    """Test cart confirmation endpoint."""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/selections/confirm",
            timeout=30  # Give it time for API calls
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cart confirmation working!")
            print(f"   Selected products: {data['total_selected_products']}")
            print(f"   Similar products found: {data['total_similar_products_found']}")
            print(f"   Vendors with matches: {len(data['vendors_with_multiple_matches'])}")
            return True
        elif response.status_code == 400:
            error = response.json()
            print(f"⚠️ Cart confirmation returned 400 (expected if no products): {error['detail']}")
            return True  # This is expected if no products
        else:
            print(f"❌ Cart confirmation failed: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error}")
            except:
                print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Cart confirmation test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Quick API Test")
    print("=" * 30)
    
    # Test server health
    if not test_server_health():
        print("\n❌ Server is not running. Start with: py start_server.py")
        return
    
    time.sleep(1)
    
    # Test search
    products = test_search_endpoint()
    time.sleep(1)
    
    # Test selection
    if products:
        test_product_selection(products)
        time.sleep(1)
        
        # Test get selections
        if test_get_selections():
            time.sleep(1)
            
            # Test cart confirmation
            test_cart_confirmation()
    
    print("\n" + "=" * 30)
    print("🎉 Quick test completed!")
    print("🌐 Visit: http://localhost:8000/api/v1/docs")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Simple test for the specific search endpoint that was failing.
"""

import requests
import time
import json

def test_search_endpoint():
    """Test the search endpoint with the exact parameters from the error."""
    
    print("🔍 Testing Search Endpoint Fix")
    print("=" * 40)
    
    # Wait a moment for server to start
    print("⏳ Waiting for server...")
    time.sleep(3)
    
    url = "http://localhost:8000/api/v1/search/products"
    params = {
        "q": "آیفون",
        "from": 0,
        "size": 12
    }
    
    print(f"📡 Testing: {url}")
    print(f"📋 Params: {params}")
    print()
    
    try:
        response = requests.get(url, params=params, timeout=15)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS! API is working")
            print(f"📱 Total products found: {data['meta']['total_count']}")
            print(f"📄 Products returned: {len(data['products'])}")
            print(f"➡️ Has more pages: {data['meta']['has_more']}")
            
            if data['products']:
                first_product = data['products'][0]
                print(f"🎯 First product: {first_product['name'][:50]}...")
                print(f"💰 Price: {first_product['price']:,.0f} تومان")
                print(f"🏪 Vendor: {first_product['vendor_name']}")
                
            print("\n🎉 The search endpoint is now working correctly!")
            return True
            
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"📝 Error message: {error_data}")
            except:
                print(f"📝 Response text: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        print("   Make sure the server is running!")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_search_endpoint()
    
    if success:
        print("\n" + "="*40)
        print("🎊 ENDPOINT FIXED SUCCESSFULLY!")
        print("🌐 Your API is ready for frontend integration")
        print("📚 View docs at: http://localhost:8000/api/v1/docs")
    else:
        print("\n" + "="*40)
        print("❌ Endpoint still needs fixing")
        print("   Check server logs for details")

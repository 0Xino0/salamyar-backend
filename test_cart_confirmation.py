#!/usr/bin/env python3
"""
Test script for the new cart confirmation functionality.

This script demonstrates:
1. Single selection per search constraint
2. Cart confirmation with vendor overlap analysis
3. Similar products finding via MLT API
"""

import asyncio
import httpx
import json
import uuid
import time

BASE_URL = "http://localhost:8000/api/v1"


async def test_cart_confirmation_flow():
    """Test the complete cart confirmation flow."""
    
    print("🛒 Testing Cart Confirmation Flow")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # Step 1: Search for different products and select one from each search
        print("📝 Step 1: Searching and selecting products...")
        
        search_queries = ["جامدادی", "کیف", "دفتر"]
        selected_products = []
        
        for i, query in enumerate(search_queries, 1):
            print(f"\n🔍 Search {i}: '{query}'")
            
            # Generate a unique search session ID
            search_session_id = str(uuid.uuid4())
            
            # Search for products
            response = await client.get(
                f"{BASE_URL}/search/products",
                params={"q": query, "from": 0, "size": 5},
                timeout=15
            )
            
            if response.status_code == 200:
                search_results = response.json()
                products = search_results.get("products", [])
                
                if products:
                    # Select the first product from this search
                    product = products[0]
                    print(f"   📦 Found {len(products)} products")
                    print(f"   ✅ Selecting: {product['name'][:50]}...")
                    
                    selection_data = {
                        "product_id": product['id'],
                        "product_name": product['name'],
                        "vendor_id": product['vendor_id'],
                        "vendor_name": product['vendor_name'],
                        "status_id": product['status_id'],
                        "image_url": product['image']['medium'],
                        "search_session_id": search_session_id
                    }
                    
                    # Select the product
                    select_response = await client.post(
                        f"{BASE_URL}/selections/products",
                        json=selection_data,
                        timeout=10
                    )
                    
                    if select_response.status_code == 200:
                        selected = select_response.json()
                        selected_products.append(selected)
                        print(f"   ✅ Selected successfully!")
                    else:
                        print(f"   ❌ Selection failed: {select_response.status_code}")
                else:
                    print(f"   ⚠️ No products found for '{query}'")
            else:
                print(f"   ❌ Search failed: {response.status_code}")
            
            # Small delay between searches
            time.sleep(1)
        
        # Step 2: Test single selection constraint by trying to select another product from same search
        if selected_products:
            print(f"\n📝 Step 2: Testing single selection per search constraint...")
            
            # Search again with same session ID
            first_search_session = selected_products[0].get('search_session_id')
            if first_search_session:
                response = await client.get(
                    f"{BASE_URL}/search/products",
                    params={"q": "جامدادی", "from": 5, "size": 3},
                    timeout=15
                )
                
                if response.status_code == 200:
                    search_results = response.json()
                    products = search_results.get("products", [])
                    
                    if products:
                        # Try to select a different product with same search session
                        product = products[0]
                        print(f"   🔄 Trying to replace selection with: {product['name'][:50]}...")
                        
                        replacement_data = {
                            "product_id": product['id'],
                            "product_name": product['name'],
                            "vendor_id": product['vendor_id'],
                            "vendor_name": product['vendor_name'],
                            "status_id": product['status_id'],
                            "image_url": product['image']['medium'],
                            "search_session_id": first_search_session
                        }
                        
                        replace_response = await client.post(
                            f"{BASE_URL}/selections/products",
                            json=replacement_data,
                            timeout=10
                        )
                        
                        if replace_response.status_code == 200:
                            print(f"   ✅ Replacement successful (previous selection should be replaced)")
                        else:
                            print(f"   ❌ Replacement failed: {replace_response.status_code}")
        
        # Step 3: Check current selections
        print(f"\n📝 Step 3: Checking current selections...")
        
        response = await client.get(f"{BASE_URL}/selections/products", timeout=10)
        
        if response.status_code == 200:
            selections = response.json()
            print(f"   📦 Current selections: {selections['total_count']}")
            
            for product in selections['products']:
                print(f"   - {product['product_name'][:40]}... (Vendor: {product['vendor_name']})")
        else:
            print(f"   ❌ Failed to get selections: {response.status_code}")
            return
        
        # Step 4: Confirm cart and analyze vendor overlaps
        print(f"\n📝 Step 4: Confirming cart and analyzing vendor overlaps...")
        print("   ⏳ This may take a while as we analyze similar products...")
        
        try:
            confirm_response = await client.post(
                f"{BASE_URL}/selections/confirm",
                timeout=60  # Give it more time for API calls
            )
            
            if confirm_response.status_code == 200:
                result = confirm_response.json()
                
                print(f"\n🎉 Cart confirmation completed!")
                print(f"   📊 Total selected products: {result['total_selected_products']}")
                print(f"   🔍 Total similar products found: {result['total_similar_products_found']}")
                print(f"   🏪 Vendors with multiple matches: {len(result['vendors_with_multiple_matches'])}")
                
                # Show processing summary
                print(f"\n📋 Processing Summary:")
                for product_id, summary in result['processing_summary'].items():
                    print(f"   📦 {summary['product_name'][:40]}...")
                    print(f"      - Similar products found: {summary['similar_products_found']}")
                    print(f"      - Vendors found: {summary['vendors_found']}")
                
                # Show vendor matches
                if result['vendors_with_multiple_matches']:
                    print(f"\n🏪 Vendors with Multiple Matches:")
                    for vendor in result['vendors_with_multiple_matches']:
                        print(f"\n   🏪 {vendor['vendor_name']} (ID: {vendor['vendor_id']})")
                        print(f"      📊 Matches {vendor['matched_products_count']} of your selected products")
                        print(f"      🛍️ Similar products available: {len(vendor['similar_products'])}")
                        
                        # Show some similar products
                        for i, product in enumerate(vendor['similar_products'][:3], 1):
                            print(f"      {i}. {product['name'][:40]}...")
                            print(f"         💰 Price: {product['price']:,.0f} تومان")
                            print(f"         🔗 Link: {product['basalam_url']}")
                        
                        if len(vendor['similar_products']) > 3:
                            print(f"      ... and {len(vendor['similar_products']) - 3} more products")
                else:
                    print(f"   ℹ️ No vendors found with multiple matches")
                    print(f"   💡 Try selecting products from different categories for better results")
                
            else:
                print(f"   ❌ Cart confirmation failed: {confirm_response.status_code}")
                try:
                    error_data = confirm_response.json()
                    print(f"   📝 Error: {error_data}")
                except:
                    print(f"   📝 Response: {confirm_response.text}")
                
        except httpx.TimeoutException:
            print(f"   ⏰ Request timed out - this is normal for the first run as it processes many API calls")
        except Exception as e:
            print(f"   ❌ Error during confirmation: {e}")


async def main():
    """Main function."""
    print("🚀 Salamyar Cart Confirmation Test")
    print("Make sure the server is running on http://localhost:8000")
    print()
    
    try:
        await test_cart_confirmation_flow()
        
        print("\n" + "=" * 50)
        print("🎊 Test completed!")
        print("📚 View API docs: http://localhost:8000/api/v1/docs")
        print("🛒 Try the /selections/confirm endpoint in the docs!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("\nMake sure the server is running:")
        print("  py start_server.py")


if __name__ == "__main__":
    asyncio.run(main())

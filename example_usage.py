#!/usr/bin/env python3
"""
Example usage of the Salamyar Product Search API.

This script demonstrates how to use the API endpoints.
Make sure the server is running before executing this script.
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000/api/v1"


async def demo_api_usage():
    """Demonstrate API usage with real examples."""
    
    async with httpx.AsyncClient() as client:
        print("🚀 Salamyar Product Search API Demo\n")
        
        # 1. Health check
        print("1. Checking API health...")
        response = await client.get("http://localhost:8000/health")
        health = response.json()
        print(f"   Status: {health['status']}")
        print(f"   Service: {health['service']}")
        print(f"   Version: {health['version']}\n")
        
        # 2. Search for products
        print("2. Searching for products...")
        search_query = "آیفون"
        print(f"   Query: '{search_query}'")
        
        response = await client.get(
            f"{BASE_URL}/search/products",
            params={"q": search_query, "from": 0, "size": 5}
        )
        
        if response.status_code == 200:
            search_results = response.json()
            print(f"   Found {search_results['meta']['total_count']} total products")
            print(f"   Showing first {len(search_results['products'])} products:")
            
            for i, product in enumerate(search_results['products'][:3], 1):
                print(f"     {i}. {product['name']}")
                print(f"        Price: {product['price']:,.0f} تومان")
                print(f"        Vendor: {product['vendor_name']}")
                print(f"        Available: {'Yes' if product['is_available'] else 'No'}")
                print()
            
            # 3. Select a product
            if search_results['products']:
                print("3. Selecting a product...")
                product_to_select = search_results['products'][0]
                
                selection_data = {
                    "product_id": product_to_select['id'],
                    "product_name": product_to_select['name'],
                    "vendor_id": product_to_select['vendor_id'],
                    "vendor_name": product_to_select['vendor_name'],
                    "status_id": product_to_select['status_id'],
                    "image_url": product_to_select['image']['medium']
                }
                
                response = await client.post(
                    f"{BASE_URL}/selections/products",
                    json=selection_data
                )
                
                if response.status_code == 200:
                    selected = response.json()
                    print(f"   ✅ Selected: {selected['product_name']}")
                    print(f"   Selection ID: {selected['id']}")
                    print(f"   Selected at: {selected['selected_at']}")
                    print()
                    
                    # 4. Get selected products
                    print("4. Getting all selected products...")
                    response = await client.get(f"{BASE_URL}/selections/products")
                    
                    if response.status_code == 200:
                        selections = response.json()
                        print(f"   Total selected products: {selections['total_count']}")
                        
                        for product in selections['products']:
                            print(f"   - {product['product_name']}")
                            print(f"     Vendor: {product['vendor_name']}")
                            print(f"     Selected: {product['selected_at']}")
                        print()
                    
                    # 5. Search for more products and select another one
                    print("5. Searching for a different product...")
                    search_query2 = "کش ورزشی"
                    print(f"   Query: '{search_query2}'")
                    
                    response = await client.get(
                        f"{BASE_URL}/search/products",
                        params={"q": search_query2, "from": 0, "size": 3}
                    )
                    
                    if response.status_code == 200:
                        search_results2 = response.json()
                        print(f"   Found {search_results2['meta']['total_count']} total products")
                        
                        if search_results2['products']:
                            # Select another product
                            product_to_select2 = search_results2['products'][0]
                            print(f"   Selecting: {product_to_select2['name']}")
                            
                            selection_data2 = {
                                "product_id": product_to_select2['id'],
                                "product_name": product_to_select2['name'],
                                "vendor_id": product_to_select2['vendor_id'],
                                "vendor_name": product_to_select2['vendor_name'],
                                "status_id": product_to_select2['status_id'],
                                "image_url": product_to_select2['image']['medium']
                            }
                            
                            response = await client.post(
                                f"{BASE_URL}/selections/products",
                                json=selection_data2
                            )
                            
                            if response.status_code == 200:
                                print("   ✅ Product selected successfully!")
                                print()
                    
                    # 6. Get updated selections
                    print("6. Getting updated selected products...")
                    response = await client.get(f"{BASE_URL}/selections/products")
                    
                    if response.status_code == 200:
                        selections = response.json()
                        print(f"   Total selected products: {selections['total_count']}")
                        
                        for product in selections['products']:
                            print(f"   - {product['product_name']}")
                            print(f"     Vendor: {product['vendor_name']}")
                        print()
                    
                    # 7. Remove a product
                    print("7. Removing the first selected product...")
                    first_product_id = selections['products'][0]['product_id']
                    
                    response = await client.delete(
                        f"{BASE_URL}/selections/products/{first_product_id}"
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"   ✅ {result['message']}")
                        print()
                    
                    # 8. Final selections check
                    print("8. Final selected products...")
                    response = await client.get(f"{BASE_URL}/selections/products")
                    
                    if response.status_code == 200:
                        final_selections = response.json()
                        print(f"   Total remaining selected products: {final_selections['total_count']}")
                        
                        for product in final_selections['products']:
                            print(f"   - {product['product_name']}")
                            print(f"     Vendor: {product['vendor_name']}")
                        print()
        
        print("🎉 Demo completed! Check the API documentation at:")
        print("   http://localhost:8000/api/v1/docs")


async def test_infinite_scroll():
    """Demonstrate infinite scroll pagination."""
    
    print("\n📜 Testing Infinite Scroll Pagination\n")
    
    async with httpx.AsyncClient() as client:
        query = "موبایل"
        page_size = 5
        current_offset = 0
        
        print(f"Search query: '{query}'")
        print(f"Page size: {page_size}")
        print("=" * 50)
        
        page = 1
        while True:
            print(f"Page {page} (offset: {current_offset})")
            
            response = await client.get(
                f"{BASE_URL}/search/products",
                params={"q": query, "from": current_offset, "size": page_size}
            )
            
            if response.status_code == 200:
                results = response.json()
                
                print(f"  Products in this page: {len(results['products'])}")
                print(f"  Total available: {results['meta']['total_count']}")
                print(f"  Has more: {results['meta']['has_more']}")
                
                for i, product in enumerate(results['products'], 1):
                    print(f"    {i}. {product['name'][:50]}...")
                
                if not results['meta']['has_more'] or page >= 3:  # Limit to 3 pages for demo
                    print("\n  End of results or demo limit reached.")
                    break
                
                current_offset += len(results['products'])
                page += 1
                print()
            else:
                print(f"  Error: {response.status_code}")
                break


if __name__ == "__main__":
    print("Make sure the API server is running on http://localhost:8000")
    print("You can start it with: python start_server.py\n")
    
    try:
        asyncio.run(demo_api_usage())
        asyncio.run(test_infinite_scroll())
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure the server is running:")
        print("  python start_server.py")

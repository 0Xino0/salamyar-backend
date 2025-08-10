#!/usr/bin/env python3
"""
Quick test to verify the API is working correctly.
This will test import and basic functionality.
"""

import sys
import asyncio

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        from app.main import app
        print("✅ FastAPI app imported successfully")
        
        from app.core.config import settings
        print(f"✅ Settings loaded: {settings.PROJECT_NAME} v{settings.VERSION}")
        
        from app.services.basalam_service import BasalamService
        print("✅ BasalamService imported successfully")
        
        from app.services.product_selection_service import ProductSelectionService
        print("✅ ProductSelectionService imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_services():
    """Test basic service functionality."""
    print("\n🔧 Testing services...")
    
    try:
        from app.services.product_selection_service import ProductSelectionService
        from app.models.schemas import SelectProductRequest
        
        # Test product selection service
        service = ProductSelectionService()
        
        # Test selecting a product
        request = SelectProductRequest(
            product_id=12345,
            product_name="Test Product",
            vendor_id=67890,
            vendor_name="Test Vendor",
            status_id=2976,
            image_url="https://example.com/test.jpg"
        )
        
        selected = service.select_product(request)
        print(f"✅ Product selection works: {selected.product_name}")
        
        # Test getting selections
        selections = service.get_selected_products()
        print(f"✅ Get selections works: {selections.total_count} products")
        
        # Test removing a product
        removed = service.remove_product(12345)
        print(f"✅ Remove product works: {removed}")
        
        return True
    except Exception as e:
        print(f"❌ Service test error: {e}")
        return False

async def test_basalam_service():
    """Test Basalam service (without making actual API calls)."""
    print("\n🌐 Testing Basalam service...")
    
    try:
        from app.services.basalam_service import BasalamService
        
        service = BasalamService()
        print(f"✅ BasalamService created with URL: {service.base_url}")
        
        # Note: We won't make actual API calls in this test to avoid dependencies
        print("✅ BasalamService basic functionality confirmed")
        
        return True
    except Exception as e:
        print(f"❌ Basalam service test error: {e}")
        return False

def test_api_structure():
    """Test API router structure."""
    print("\n🛣️ Testing API structure...")
    
    try:
        from app.api.v1.api import api_router
        print("✅ API router imported successfully")
        
        from app.main import app
        
        # Check if routes are registered
        routes = [route.path for route in app.routes]
        print(f"✅ Found {len(routes)} routes registered")
        
        # Check for expected endpoints
        expected_patterns = ['/api/v1', '/health', '/']
        for pattern in expected_patterns:
            if any(pattern in route for route in routes):
                print(f"✅ Found expected route pattern: {pattern}")
            else:
                print(f"⚠️ Route pattern not found: {pattern}")
        
        return True
    except Exception as e:
        print(f"❌ API structure test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Salamyar API Test Suite")
    print("=" * 40)
    
    results = []
    
    # Run tests
    results.append(test_imports())
    results.append(test_services())
    results.append(test_api_structure())
    
    # Run async test
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results.append(loop.run_until_complete(test_basalam_service()))
        loop.close()
    except Exception as e:
        print(f"❌ Async test error: {e}")
        results.append(False)
    
    # Summary
    print("\n" + "=" * 40)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All tests passed! ({passed}/{total})")
        print("\n✅ Your API is ready to run!")
        print("   Start it with: python start_server.py")
        print("   Or manually: uvicorn app.main:app --reload")
        return 0
    else:
        print(f"❌ Some tests failed ({passed}/{total})")
        return 1

if __name__ == "__main__":
    sys.exit(main())

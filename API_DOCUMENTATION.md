# Salamyar Product Search API Documentation

## Overview

The Salamyar Product Search API is a RESTful web service that enables users to search for products from the Basalam marketplace and manage their product selections. The API follows RESTful principles and implements proper versioning.

## Base URL

```
http://localhost:8000/api/v1
```

## API Endpoints

### 1. Product Search

#### Search Products
**Endpoint:** `GET /api/v1/search/products`

Search for products with infinite scroll pagination support.

**Query Parameters:**
- `q` (required): Search query string (1-500 characters)
- `from` (optional): Pagination offset (default: 0)
- `size` (optional): Number of results per page (default: 12, max: 50)

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/search/products?q=آیفون&from=0&size=12"
```

**Example Response:**
```json
{
  "products": [
    {
      "id": 19584783,
      "name": "Apple 4s 16 خاص",
      "price": 58000000.0,
      "image": {
        "medium": "https://statics.basalam.com/public-57/users/V6gE0z/01-25/...",
        "small": "https://statics.basalam.com/public-57/users/V6gE0z/01-25/..."
      },
      "vendor_id": 1124329,
      "vendor_name": "اپل استور و قطعات",
      "status_id": 2976,
      "status_title": "در دسترس",
      "category_title": "گوشی موبایل",
      "is_available": true,
      "has_free_shipping": false,
      "rating_average": 0.0,
      "rating_count": 0,
      "stock": 1
    }
  ],
  "meta": {
    "total_count": 2836,
    "page_size": 12,
    "current_offset": 0,
    "has_more": true
  }
}
```

### 2. Product Selection Management

#### Select a Product
**Endpoint:** `POST /api/v1/selections/products`

Add a product to the user's selection list.

**Request Body:**
```json
{
  "product_id": 19584783,
  "product_name": "Apple 4s 16 خاص",
  "vendor_id": 1124329,
  "vendor_name": "اپل استور و قطعات",
  "status_id": 2976,
  "image_url": "https://statics.basalam.com/public-57/users/V6gE0z/01-25/..."
}
```

**Example Response:**
```json
{
  "id": 1,
  "product_id": 19584783,
  "product_name": "Apple 4s 16 خاص",
  "vendor_id": 1124329,
  "vendor_name": "اپل استور و قطعات",
  "status_id": 2976,
  "image_url": "https://statics.basalam.com/public-57/users/V6gE0z/01-25/...",
  "selected_at": "2024-01-15T10:30:00Z"
}
```

#### Get Selected Products
**Endpoint:** `GET /api/v1/selections/products`

Retrieve all selected products.

**Example Response:**
```json
{
  "products": [
    {
      "id": 1,
      "product_id": 19584783,
      "product_name": "Apple 4s 16 خاص",
      "vendor_id": 1124329,
      "vendor_name": "اپل استور و قطعات",
      "status_id": 2976,
      "image_url": "https://statics.basalam.com/public-57/users/V6gE0z/01-25/...",
      "selected_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_count": 1
}
```

#### Remove Selected Product
**Endpoint:** `DELETE /api/v1/selections/products/{product_id}`

Remove a product from the selection list.

**Example Response:**
```json
{
  "message": "Product 19584783 removed from selection successfully.",
  "success": true
}
```

#### Clear All Selections
**Endpoint:** `DELETE /api/v1/selections/products`

Remove all products from the selection list.

**Example Response:**
```json
{
  "message": "Successfully cleared 5 selected products.",
  "success": true
}
```

#### Confirm Shopping Cart
**Endpoint:** `POST /api/v1/selections/confirm`

Analyze selected products and find vendors with multiple matching items. This endpoint:
1. Takes all selected products from the user's cart
2. For each product, finds up to 100 similar products using Basalam's MLT API
3. Analyzes vendors that have similar products for multiple selected items
4. Returns vendors with at least 2 matches along with product links

**Example Response:**
```json
{
  "total_selected_products": 3,
  "total_similar_products_found": 287,
  "vendors_with_multiple_matches": [
    {
      "vendor_id": 52878,
      "vendor_name": "دستسازه های هنری دستینه",
      "matched_products_count": 2,
      "user_selected_products": [17881765, 16175727],
      "similar_products": [
        {
          "id": 16143448,
          "name": "جامدادی چرمی طرح زبان انگلیسی",
          "price": 900000.0,
          "vendor_id": 52878,
          "vendor_name": "دستسازه های هنری دستینه",
          "status_id": 2976,
          "image_url": "https://statics.basalam.com/.../image.jpg",
          "basalam_url": "https://basalam.com/p/16143448",
          "original_product_id": 17881765
        }
      ]
    }
  ],
  "processing_summary": {
    "17881765": {
      "product_name": "جامدادی چرمی عکاس دوربین عکاسی",
      "similar_products_found": 95,
      "vendors_found": 23
    }
  }
}
```

### 3. Health Check

#### Basic Health Check
**Endpoint:** `GET /`

**Example Response:**
```json
{
  "status": "ok",
  "message": "Salamyar Product Search API is running",
  "version": "1.0.0"
}
```

#### Detailed Health Check
**Endpoint:** `GET /health`

**Example Response:**
```json
{
  "status": "healthy",
  "service": "Salamyar Product Search API",
  "version": "1.0.0"
}
```

## Frontend Integration Guide

### Implementing Infinite Scroll

To implement infinite scroll with the search API:

```javascript
class ProductSearch {
  constructor() {
    this.currentQuery = '';
    this.currentOffset = 0;
    this.pageSize = 12;
    this.hasMore = true;
    this.loading = false;
  }

  async searchProducts(query, reset = true) {
    if (this.loading) return;
    
    if (reset) {
      this.currentOffset = 0;
      this.hasMore = true;
      this.currentQuery = query;
    }

    if (!this.hasMore) return;

    this.loading = true;
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/search/products?q=${encodeURIComponent(query)}&from=${this.currentOffset}&size=${this.pageSize}`
      );
      
      const data = await response.json();
      
      if (reset) {
        this.displayProducts(data.products); // Replace existing products
      } else {
        this.appendProducts(data.products); // Add to existing products
      }
      
      this.currentOffset += data.products.length;
      this.hasMore = data.meta.has_more;
      
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      this.loading = false;
    }
  }

  async loadMore() {
    if (this.currentQuery) {
      await this.searchProducts(this.currentQuery, false);
    }
  }
}
```

### Managing Product Selection

```javascript
class ProductSelection {
  constructor() {
    this.currentSearchSessionId = null;
  }

  // Generate a new search session ID for each search
  startNewSearch() {
    this.currentSearchSessionId = this.generateUUID();
    return this.currentSearchSessionId;
  }

  async selectProduct(product) {
    try {
      const response = await fetch('http://localhost:8000/api/v1/selections/products', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product_id: product.id,
          product_name: product.name,
          vendor_id: product.vendor_id,
          vendor_name: product.vendor_name,
          status_id: product.status_id,
          image_url: product.image.medium || product.image.small,
          search_session_id: this.currentSearchSessionId // Only one selection per search
        })
      });
      
      const selectedProduct = await response.json();
      this.updateSelectionUI(selectedProduct);
      
    } catch (error) {
      console.error('Failed to select product:', error);
    }
  }

  async getSelectedProducts() {
    try {
      const response = await fetch('http://localhost:8000/api/v1/selections/products');
      const data = await response.json();
      return data.products;
    } catch (error) {
      console.error('Failed to get selected products:', error);
      return [];
    }
  }

  async removeProduct(productId) {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/selections/products/${productId}`, {
        method: 'DELETE'
      });
      
      const result = await response.json();
      if (result.success) {
        this.removeFromSelectionUI(productId);
      }
      
    } catch (error) {
      console.error('Failed to remove product:', error);
    }
  }

  // Cart confirmation and vendor overlap analysis
  async confirmCart() {
    try {
      this.showLoadingMessage('Analyzing your cart for vendor overlaps...');
      
      const response = await fetch('http://localhost:8000/api/v1/selections/confirm', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        const analysis = await response.json();
        this.displayVendorAnalysis(analysis);
      } else {
        const error = await response.json();
        this.showError(error.detail || 'Failed to analyze cart');
      }
      
    } catch (error) {
      console.error('Failed to confirm cart:', error);
      this.showError('Failed to confirm cart. Please try again.');
    }
  }

  displayVendorAnalysis(analysis) {
    console.log('Vendor Analysis Results:', analysis);
    
    // Display vendors with multiple matches
    if (analysis.vendors_with_multiple_matches.length > 0) {
      analysis.vendors_with_multiple_matches.forEach(vendor => {
        console.log(`Vendor: ${vendor.vendor_name}`);
        console.log(`Matches ${vendor.matched_products_count} of your products`);
        
        vendor.similar_products.forEach(product => {
          console.log(`- ${product.name}: ${product.basalam_url}`);
        });
      });
    } else {
      console.log('No vendors found with multiple matches');
    }
  }

  generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }
}
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error message",
  "detail": "Detailed error description (optional)",
  "success": false
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Not Found (product not found in selection)
- `500`: Internal Server Error

## Interactive API Documentation

Once the server is running, you can access interactive API documentation at:
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

## Running the Server

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

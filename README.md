# Salamyar Product Search API

A modern RESTful API for searching products on Basalam marketplace and managing product selections. This API enables frontend applications to implement infinite scroll product search and selection functionality.

## 🚀 Features

- **Product Search**: Search products from Basalam marketplace with pagination
- **Infinite Scroll**: Built-in pagination support for seamless infinite scroll UX
- **Product Selection**: Manage user's selected products with full CRUD operations
- **RESTful Design**: Well-structured API following REST principles
- **API Versioning**: Proper versioning (v1) for future compatibility
- **Interactive Documentation**: Auto-generated API docs with Swagger UI
- **Type Safety**: Full Pydantic models for request/response validation
- **CORS Support**: Ready for frontend integration

## 🏗️ API Structure

```
/api/v1/
├── search/
│   └── products          # Search products with pagination
├── selections/
│   └── products          # Manage selected products (CRUD)
├── docs                  # Interactive API documentation
└── redoc                 # Alternative API documentation
```

## 🛠️ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
```bash
# Option 1: Using the startup script
python start_server.py

# Option 2: Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access the API
- **API Base URL**: http://localhost:8000/api/v1
- **Interactive Docs**: http://localhost:8000/api/v1/docs
- **Health Check**: http://localhost:8000/health

## 📚 API Usage Examples

### Search Products
```bash
# Search for iPhone products
curl "http://localhost:8000/api/v1/search/products?q=آیفون&from=0&size=12"

# Infinite scroll - next page
curl "http://localhost:8000/api/v1/search/products?q=آیفون&from=12&size=12"
```

### Select Products
```bash
# Select a product
curl -X POST "http://localhost:8000/api/v1/selections/products" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 19584783,
    "product_name": "Apple 4s 16 خاص",
    "vendor_id": 1124329,
    "vendor_name": "اپل استور و قطعات",
    "status_id": 2976,
    "image_url": "https://example.com/image.jpg"
  }'

# Get selected products
curl "http://localhost:8000/api/v1/selections/products"

# Remove a selected product
curl -X DELETE "http://localhost:8000/api/v1/selections/products/19584783"
```

## 🧪 Testing the API

Run the example usage script to see the API in action:

```bash
python example_usage.py
```

This script demonstrates:
- Product searching with different queries
- Product selection and management
- Infinite scroll pagination
- Error handling

## 🏛️ Architecture

### Project Structure
```
app/
├── api/v1/               # API version 1
│   ├── endpoints/        # API endpoint definitions
│   └── api.py           # Main API router
├── core/                # Core application configuration
│   ├── config.py        # Settings and configuration
│   └── dependencies.py  # Dependency injection
├── models/              # Pydantic models
│   ├── basalam.py       # Basalam API response models
│   └── schemas.py       # API request/response schemas
├── services/            # Business logic services
│   ├── basalam_service.py      # Basalam API integration
│   └── product_selection_service.py  # Product selection management
└── main.py             # FastAPI application setup
```

### Key Components

1. **BasalamService**: Handles integration with Basalam search API
2. **ProductSelectionService**: Manages user's product selections (in-memory storage)
3. **Pydantic Models**: Type-safe request/response validation
4. **API Versioning**: `/api/v1/` prefix for future compatibility

## 🌐 Frontend Integration

### Infinite Scroll Implementation
```javascript
// Example JavaScript integration
async function loadProducts(query, offset = 0) {
  const response = await fetch(
    `http://localhost:8000/api/v1/search/products?q=${encodeURIComponent(query)}&from=${offset}&size=12`
  );
  const data = await response.json();
  
  // Append products to your UI
  displayProducts(data.products);
  
  // Check if more products are available
  if (data.meta.has_more) {
    // User can load more by calling loadProducts(query, offset + 12)
  }
}
```

### Product Selection Management
```javascript
// Select a product
async function selectProduct(product) {
  await fetch('http://localhost:8000/api/v1/selections/products', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      product_id: product.id,
      product_name: product.name,
      vendor_id: product.vendor_id,
      vendor_name: product.vendor_name,
      status_id: product.status_id,
      image_url: product.image.medium
    })
  });
}
```

## 📖 Documentation

- **API Documentation**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Interactive API Docs**: http://localhost:8000/api/v1/docs (when server is running)

## 🔄 Migration from Telegram Bot

This project was originally a Telegram bot. The bot functionality has been preserved but is currently disabled. To re-enable:

1. Uncomment telegram-bot dependencies in `requirements.txt`
2. Set up environment variables for Telegram and Gemini API
3. Modify `main.py` to include bot startup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. See the license file for details.
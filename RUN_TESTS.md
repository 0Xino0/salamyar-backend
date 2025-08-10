# How to Test the Cart Confirmation Feature

## Method 1: Quick Test (Recommended)

### Step 1: Start the Server
```bash
py start_server.py
```
**Keep this terminal open** - you should see:
```
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Application startup complete.
```

### Step 2: Test in Another Terminal
Open a **new terminal/command prompt** in the same directory and run:
```bash
py test_server.py
```

This will test all functionality including:
- ✅ Search products
- ✅ Select products (single selection per search)
- ✅ Cart confirmation with vendor overlap analysis
- ✅ Similar products finding via MLT API

## Method 2: Manual Testing via Browser

1. Start server: `py start_server.py`
2. Visit: **http://localhost:8000/api/v1/docs**
3. Test the endpoints manually:
   - Try `/search/products` with query "جامدادی"
   - Select a product via `/selections/products`
   - Confirm cart via `/selections/confirm`

## Expected Results

When testing cart confirmation, you should see:
- **Similar products found**: 50-100 per selected product
- **Vendors analyzed**: Multiple vendors checked for overlaps
- **Vendor matches**: Vendors that have products similar to multiple of your selections
- **Basalam links**: Direct product links like `https://basalam.com/q/12345`

## Troubleshooting

If tests fail:
1. Make sure server is running on port 8000
2. Check that you can access: http://localhost:8000/health
3. Try the search endpoint manually first

## Key Features Verified

✅ **Single Selection Per Search**: Only one product can be selected from each search session  
✅ **Cart Confirmation**: Analyzes selected products for vendor overlaps  
✅ **MLT API Integration**: Finds up to 100 similar products per selected item  
✅ **Vendor Analysis**: Shows vendors with multiple matching products  
✅ **Basalam Links**: Provides direct product links for easy access

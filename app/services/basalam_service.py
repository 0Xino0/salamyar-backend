"""Service for integrating with Basalam search API."""

import logging
from typing import Optional, Dict, Any
import httpx
from app.core.config import settings
from app.models.schemas import SearchProduct, SearchResponse, SearchMeta, ProductImage

logger = logging.getLogger(__name__)


class BasalamService:
    """Service for interacting with Basalam search API."""
    
    def __init__(self):
        self.base_url = settings.BASALAM_SEARCH_URL
        self.timeout = 15.0
    
    async def search_products(
        self, 
        query: str, 
        from_offset: int = 0, 
        size: int = 12
    ) -> Optional[SearchResponse]:
        """
        Search products using Basalam API.
        
        Args:
            query: Search query string
            from_offset: Pagination offset
            size: Number of results to return
            
        Returns:
            SearchResponse object or None if error
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "from": from_offset,
                    "q": query,
                    "size": size,
                    "adsImpressionDisable": True,
                }
                
                response = await client.get(
                    self.base_url,
                    params=params,
                    headers={"Accept": "application/json"}
                )
                
                if response.status_code != 200:
                    logger.error(f"Basalam API error: {response.status_code} - {response.text}")
                    return None
                
                # Parse the JSON response directly
                try:
                    response_data = response.json()
                    return self._transform_json_to_search_response(response_data, from_offset, size)
                except Exception as e:
                    logger.error(f"Failed to parse Basalam response: {e}")
                    logger.debug(f"Raw response: {response.text[:500]}...")
                    return None
                
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return None
    
    def _transform_json_to_search_response(
        self, 
        response_data: Dict[str, Any], 
        from_offset: int, 
        size: int
    ) -> SearchResponse:
        """Transform raw JSON response to our API format."""
        
        # Extract products from response
        products_data = response_data.get("products", [])
        search_products = []
        
        for product in products_data:
            try:
                # Extract required fields with safe defaults
                product_id = product.get("id")
                if not product_id:
                    continue
                
                # Extract vendor information
                vendor = product.get("vendor", {})
                vendor_id = vendor.get("id")
                if not vendor_id:
                    continue
                
                # Extract photo information
                photo = product.get("photo", {})
                
                # Extract status information
                status = product.get("status", {})
                
                # Extract rating information
                rating = product.get("rating", {})
                
                search_product = SearchProduct(
                    id=product_id,
                    name=product.get("name", ""),
                    price=float(product.get("price", 0)),
                    image=ProductImage(
                        medium=photo.get("MEDIUM"),
                        small=photo.get("SMALL")
                    ),
                    vendor_id=vendor_id,
                    vendor_name=vendor.get("name", ""),
                    status_id=status.get("id", 0),
                    status_title=status.get("title", ""),
                    category_title=product.get("categoryTitle", ""),
                    is_available=product.get("IsAvailable", False),
                    has_free_shipping=product.get("isFreeShipping", False),
                    rating_average=float(rating.get("average", 0)),
                    rating_count=int(rating.get("count", 0)),
                    stock=int(product.get("stock", 0))
                )
                search_products.append(search_product)
                
            except Exception as e:
                logger.warning(f"Failed to parse product {product.get('id', 'unknown')}: {e}")
                continue
        
        # Extract metadata
        meta_data = response_data.get("meta", {})
        total_count = meta_data.get("count", 0)
        current_offset = from_offset
        returned_count = len(search_products)
        has_more = (current_offset + returned_count) < total_count
        
        meta = SearchMeta(
            total_count=total_count,
            page_size=size,
            current_offset=current_offset,
            has_more=has_more
        )
        
        logger.info(f"Successfully transformed {len(search_products)} products from Basalam response")
        
        return SearchResponse(
            products=search_products,
            meta=meta
        )

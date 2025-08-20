"""Service for Basalam Similar Products (MLT - More Like This) API integration."""

import logging
from typing import List, Dict, Any, Optional
import httpx
from collections import defaultdict

from app.core.config import settings
from app.models.schemas import (
    SelectedProduct, 
    SimilarProduct, 
    VendorMatch, 
    CartConfirmationResponse
)

logger = logging.getLogger(__name__)


class SimilarProductsService:
    """Service for finding similar products and analyzing vendor overlaps."""
    
    def __init__(self):
        self.mlt_api_url = "https://search.basalam.com/ai-engine/api/v2.0/mlt"
        self.timeout = 15.0
        self.max_similar_products_per_item = 100
        self.page_size = 24  # Default page size for pagination
    
    async def find_vendor_overlaps(
        self, 
        selected_products: List[SelectedProduct]
    ) -> CartConfirmationResponse:
        """
        Find vendor overlaps by analyzing similar products for each selected product.
        
        Args:
            selected_products: List of user's selected products
            
        Returns:
            CartConfirmationResponse with vendor analysis
        """
        if not selected_products:
            return CartConfirmationResponse(
                total_selected_products=0,
                total_similar_products_found=0,
                vendors_with_multiple_matches=[],
                processing_summary={}
            )
        
        logger.info(f"Starting vendor overlap analysis for {len(selected_products)} selected products")
        
        all_similar_products = []
        processing_summary = {}
        
        # Find similar products for each selected product
        for selected_product in selected_products:
            logger.info(f"Finding similar products for: {selected_product.product_name}")
            
            similar_products = await self._find_similar_products_for_item(selected_product)
            all_similar_products.extend(similar_products)
            
            processing_summary[selected_product.product_id] = {
                "product_name": selected_product.product_name,
                "similar_products_found": len(similar_products),
                "vendors_found": len(set(p.vendor_id for p in similar_products))
            }
            
            logger.info(f"Found {len(similar_products)} similar products for {selected_product.product_name}")
        
        # Analyze vendor overlaps
        vendor_overlaps = self._analyze_vendor_overlaps(selected_products, all_similar_products)
        
        # Filter vendors with at least 2 matches
        vendors_with_multiple_matches = [
            vendor for vendor in vendor_overlaps 
            if vendor.matched_products_count >= 2
        ]
        
        # Sort by number of matches (descending) and then by vendor name
        vendors_with_multiple_matches.sort(
            key=lambda v: (-v.matched_products_count, v.vendor_name)
        )
        
        logger.info(f"Found {len(vendors_with_multiple_matches)} vendors with multiple matches")
        
        return CartConfirmationResponse(
            total_selected_products=len(selected_products),
            total_similar_products_found=len(all_similar_products),
            vendors_with_multiple_matches=vendors_with_multiple_matches,
            processing_summary=processing_summary
        )
    
    async def _find_similar_products_for_item(
        self, 
        selected_product: SelectedProduct
    ) -> List[SimilarProduct]:
        """
        Find up to 100 similar products for a single selected product.
        
        Args:
            selected_product: The product to find similar items for
            
        Returns:
            List of similar products
        """
        similar_products = []
        from_offset = 0
        
        try:
            while len(similar_products) < self.max_similar_products_per_item:
                # Calculate how many more products we need
                remaining_needed = self.max_similar_products_per_item - len(similar_products)
                current_page_size = min(self.page_size, remaining_needed)
                
                # Make API request
                page_products = await self._fetch_similar_products_page(
                    selected_product, from_offset, current_page_size
                )
                
                if not page_products:
                    # No more products available
                    break
                
                similar_products.extend(page_products)
                from_offset += len(page_products)
                
                # If we got fewer products than requested, we've reached the end
                if len(page_products) < current_page_size:
                    break
                
                logger.debug(f"Fetched {len(page_products)} products, total: {len(similar_products)}")
        
        except Exception as e:
            logger.error(f"Error finding similar products for {selected_product.product_id}: {e}")
        
        return similar_products[:self.max_similar_products_per_item]
    
    async def _fetch_similar_products_page(
        self, 
        selected_product: SelectedProduct, 
        from_offset: int, 
        size: int
    ) -> List[SimilarProduct]:
        """
        Fetch a single page of similar products from the MLT API.
        
        Args:
            selected_product: The product to find similar items for
            from_offset: Pagination offset
            size: Number of products to fetch
            
        Returns:
            List of similar products from this page
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {
                    "fromCard": "true",
                    "ads": "false", 
                    "title": selected_product.product_name,
                    "productId": selected_product.product_id,
                    "status": selected_product.status_id,
                    "from": from_offset,
                    "size": size
                }
                
                response = await client.get(
                    self.mlt_api_url,
                    params=params,
                    headers={"Accept": "application/json"}
                )
                
                if response.status_code != 200:
                    logger.error(f"MLT API error: {response.status_code} - {response.text}")
                    return []
                
                # Parse the JSON response
                response_data = response.json()
                return self._parse_similar_products_response(
                    response_data, selected_product.product_id
                )
                
        except Exception as e:
            logger.error(f"Error fetching similar products page: {e}")
            return []
    
    def _parse_similar_products_response(
        self, 
        response_data: Dict[str, Any], 
        original_product_id: int
    ) -> List[SimilarProduct]:
        """
        Parse the MLT API response and convert to SimilarProduct objects.
        
        Args:
            response_data: Raw API response
            original_product_id: ID of the original selected product
            
        Returns:
            List of SimilarProduct objects
        """
        similar_products = []
        products_data = response_data.get("products", [])
        
        for product in products_data:
            try:
                product_id = product.get("id")
                if not product_id:
                    continue
                
                vendor = product.get("vendor", {})
                vendor_id = vendor.get("id")
                if not vendor_id:
                    continue
                
                photo = product.get("photo", {})
                status = product.get("status", {})
                
                similar_product = SimilarProduct(
                    id=product_id,
                    name=product.get("name", ""),
                    price=float(product.get("price", 0)),
                    vendor_id=vendor_id,
                    vendor_name=vendor.get("name", ""),
                    status_id=status.get("id", 0),
                    image_url=photo.get("MEDIUM") or photo.get("SMALL"),
                    basalam_url=f"https://basalam.com/p/{product_id}",
                    original_product_id=original_product_id
                )
                similar_products.append(similar_product)
                
            except Exception as e:
                logger.warning(f"Failed to parse similar product {product.get('id', 'unknown')}: {e}")
                continue
        
        return similar_products
    
    def _analyze_vendor_overlaps(
        self, 
        selected_products: List[SelectedProduct], 
        all_similar_products: List[SimilarProduct]
    ) -> List[VendorMatch]:
        """
        Analyze vendor overlaps from similar products.
        
        Args:
            selected_products: User's selected products
            all_similar_products: All similar products found
            
        Returns:
            List of VendorMatch objects
        """
        # Group similar products by vendor
        vendor_products = defaultdict(list)
        for similar_product in all_similar_products:
            vendor_products[similar_product.vendor_id].append(similar_product)
        
        vendor_matches = []
        
        for vendor_id, products in vendor_products.items():
            # Find which of the user's selected products this vendor has similar items for
            user_products_covered = set()
            for product in products:
                user_products_covered.add(product.original_product_id)
            
            # Only include vendors that have similar products for at least 1 user product
            if len(user_products_covered) >= 1:
                vendor_name = products[0].vendor_name if products else ""
                
                vendor_match = VendorMatch(
                    vendor_id=vendor_id,
                    vendor_name=vendor_name,
                    matched_products_count=len(user_products_covered),
                    user_selected_products=list(user_products_covered),
                    similar_products=products
                )
                vendor_matches.append(vendor_match)
        
        return vendor_matches

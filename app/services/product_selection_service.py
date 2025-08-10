"""Service for managing product selections."""

import logging
from typing import List, Optional, Dict
from datetime import datetime
import threading
from app.models.schemas import (
    SelectProductRequest, 
    SelectedProduct, 
    SelectedProductsResponse
)

logger = logging.getLogger(__name__)


class ProductSelectionService:
    """Service for managing user product selections."""
    
    def __init__(self):
        # In-memory storage for selected products
        # In a real application, this would be a database
        self._selected_products: Dict[int, SelectedProduct] = {}
        self._lock = threading.Lock()
        self._next_id = 1
    
    def select_product(self, request: SelectProductRequest) -> SelectedProduct:
        """
        Add a product to the selection.
        
        Args:
            request: Product selection request
            
        Returns:
            SelectedProduct object
        """
        with self._lock:
            # Check if product is already selected
            existing = self._find_by_product_id(request.product_id)
            if existing:
                logger.info(f"Product {request.product_id} already selected")
                return existing
            
            # Create new selected product
            selected_product = SelectedProduct(
                id=self._next_id,
                product_id=request.product_id,
                product_name=request.product_name,
                vendor_id=request.vendor_id,
                vendor_name=request.vendor_name,
                status_id=request.status_id,
                image_url=request.image_url,
                selected_at=datetime.now()
            )
            
            self._selected_products[selected_product.id] = selected_product
            self._next_id += 1
            
            logger.info(f"Product {request.product_id} selected successfully")
            return selected_product
    
    def get_selected_products(self) -> SelectedProductsResponse:
        """
        Get all selected products.
        
        Returns:
            SelectedProductsResponse with all selected products
        """
        with self._lock:
            products = list(self._selected_products.values())
            # Sort by selection time (most recent first)
            products.sort(key=lambda p: p.selected_at, reverse=True)
            
            return SelectedProductsResponse(
                products=products,
                total_count=len(products)
            )
    
    def remove_product(self, product_id: int) -> bool:
        """
        Remove a product from selection.
        
        Args:
            product_id: ID of the product to remove
            
        Returns:
            True if product was removed, False if not found
        """
        with self._lock:
            # Find the selection by product_id
            selection_id = None
            for sel_id, product in self._selected_products.items():
                if product.product_id == product_id:
                    selection_id = sel_id
                    break
            
            if selection_id is not None:
                del self._selected_products[selection_id]
                logger.info(f"Product {product_id} removed from selection")
                return True
            
            logger.warning(f"Product {product_id} not found in selection")
            return False
    
    def clear_selections(self) -> int:
        """
        Clear all selected products.
        
        Returns:
            Number of products that were cleared
        """
        with self._lock:
            count = len(self._selected_products)
            self._selected_products.clear()
            logger.info(f"Cleared {count} selected products")
            return count
    
    def get_product_by_id(self, product_id: int) -> Optional[SelectedProduct]:
        """
        Get a selected product by its product_id.
        
        Args:
            product_id: Product ID to search for
            
        Returns:
            SelectedProduct if found, None otherwise
        """
        with self._lock:
            return self._find_by_product_id(product_id)
    
    def _find_by_product_id(self, product_id: int) -> Optional[SelectedProduct]:
        """Helper method to find a product by product_id (without lock)."""
        for product in self._selected_products.values():
            if product.product_id == product_id:
                return product
        return None
    
    def get_selections_by_vendor(self, vendor_id: int) -> List[SelectedProduct]:
        """
        Get all selected products from a specific vendor.
        
        Args:
            vendor_id: Vendor ID to filter by
            
        Returns:
            List of selected products from the vendor
        """
        with self._lock:
            vendor_products = [
                product for product in self._selected_products.values() 
                if product.vendor_id == vendor_id
            ]
            # Sort by selection time
            vendor_products.sort(key=lambda p: p.selected_at, reverse=True)
            return vendor_products

"""Pydantic models for API request and response structures."""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# Search related models
class SearchRequest(BaseModel):
    """Request model for product search."""
    q: str = Field(..., description="Search query", min_length=1, max_length=500)
    from_: int = Field(0, alias="from", description="Pagination offset", ge=0)
    size: int = Field(12, description="Number of results per page", ge=1, le=50)


class ProductImage(BaseModel):
    """Product image URLs."""
    medium: Optional[str] = None
    small: Optional[str] = None


class SearchProduct(BaseModel):
    """Product model for search results."""
    id: int
    name: str
    price: float
    image: ProductImage
    vendor_id: int
    vendor_name: str
    status_id: int
    status_title: str
    category_title: str
    is_available: bool
    has_free_shipping: bool
    rating_average: float
    rating_count: int
    stock: int


class SearchMeta(BaseModel):
    """Search metadata."""
    total_count: int
    page_size: int
    current_offset: int
    has_more: bool


class SearchResponse(BaseModel):
    """Response model for product search."""
    products: List[SearchProduct]
    meta: SearchMeta


# Product selection related models
class SelectProductRequest(BaseModel):
    """Request model for selecting a product."""
    product_id: int
    product_name: str
    vendor_id: int
    vendor_name: str
    status_id: int
    image_url: Optional[str] = None
    search_session_id: Optional[str] = None  # To track which search this product came from


class SelectedProduct(BaseModel):
    """Model for a selected product."""
    id: int
    product_id: int
    product_name: str
    vendor_id: int
    vendor_name: str
    status_id: int
    image_url: Optional[str] = None
    selected_at: datetime
    search_session_id: Optional[str] = None  # Track search session


class SelectedProductsResponse(BaseModel):
    """Response model for selected products."""
    products: List[SelectedProduct]
    total_count: int


class RemoveProductRequest(BaseModel):
    """Request model for removing a selected product."""
    product_id: int


# Shopping cart confirmation models
class SimilarProduct(BaseModel):
    """Model for a similar product found via MLT API."""
    id: int
    name: str
    price: float
    vendor_id: int
    vendor_name: str
    status_id: int
    image_url: Optional[str] = None
    basalam_url: str  # https://basalam.com/p/{product_id}
    original_product_id: int  # Which user's selected product this is similar to


class VendorMatch(BaseModel):
    """Model for a vendor that has multiple products from user's selection."""
    vendor_id: int
    vendor_name: str
    matched_products_count: int  # How many of user's products this vendor has
    user_selected_products: List[int]  # IDs of user's selected products
    similar_products: List[SimilarProduct]  # Similar products from this vendor


class CartConfirmationResponse(BaseModel):
    """Response model for cart confirmation."""
    total_selected_products: int
    total_similar_products_found: int
    vendors_with_multiple_matches: List[VendorMatch]
    processing_summary: dict  # Summary of processing for each selected product


# Generic response models
class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    success: bool = False

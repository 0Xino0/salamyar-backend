"""Dependency injection for services."""

from functools import lru_cache
from app.services.basalam_service import BasalamService
from app.services.product_selection_service import ProductSelectionService
from app.services.similar_products_service import SimilarProductsService


@lru_cache()
def get_basalam_service() -> BasalamService:
    """Get singleton BasalamService instance."""
    return BasalamService()


@lru_cache()
def get_selection_service() -> ProductSelectionService:
    """Get singleton ProductSelectionService instance."""
    return ProductSelectionService()


@lru_cache()
def get_similar_products_service() -> SimilarProductsService:
    """Get singleton SimilarProductsService instance."""
    return SimilarProductsService()

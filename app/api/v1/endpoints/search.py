"""Search endpoints for product search functionality."""

import logging
from fastapi import APIRouter, HTTPException, Query, Depends
from app.models.schemas import SearchResponse, ErrorResponse
from app.core.config import settings
from app.core.dependencies import get_basalam_service
from app.services.basalam_service import BasalamService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/products",
    response_model=SearchResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Search products",
    description="Search for products using the Basalam marketplace API with pagination support for infinite scroll.",
    tags=["Search"]
)
async def search_products(
    q: str = Query(..., description="Search query", min_length=1, max_length=500),
    from_: int = Query(0, alias="from", description="Pagination offset", ge=0),
    size: int = Query(
        settings.DEFAULT_PAGE_SIZE, 
        description="Number of results per page", 
        ge=1, 
        le=settings.MAX_PAGE_SIZE
    ),
    basalam_service: BasalamService = Depends(get_basalam_service)
):
    """
    Search for products with pagination support.
    
    This endpoint provides infinite scroll functionality by supporting
    pagination through `from` and `size` parameters.
    
    **Usage for infinite scroll:**
    - Start with `from=0` and `size=12`
    - For next page: increment `from` by `size` (e.g., `from=12`, `from=24`, etc.)
    - Continue until `meta.has_more` is `false`
    
    **Parameters:**
    - **q**: Search query (required)
    - **from**: Starting offset for pagination (default: 0)
    - **size**: Number of results per page (default: 12, max: 50)
    
    **Returns:**
    - List of products matching the search query
    - Pagination metadata for infinite scroll implementation
    """
    try:
        logger.info(f"Searching products: query='{q}', from={from_}, size={size}")
        
        result = await basalam_service.search_products(
            query=q,
            from_offset=from_,
            size=size
        )
        
        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to search products. Please try again later."
            )
        
        logger.info(f"Search successful: {len(result.products)} products found")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in search: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while searching products."
        )

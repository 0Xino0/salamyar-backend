"""Product selection endpoints for managing user's selected products."""

import logging
from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import (
    SelectProductRequest,
    SelectedProduct,
    SelectedProductsResponse,
    RemoveProductRequest,
    MessageResponse,
    ErrorResponse
)
from app.core.dependencies import get_selection_service
from app.services.product_selection_service import ProductSelectionService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/products",
    response_model=SelectedProduct,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Select a product",
    description="Add a product to the user's selection list.",
    tags=["Product Selection"]
)
async def select_product(
    request: SelectProductRequest,
    selection_service: ProductSelectionService = Depends(get_selection_service)
):
    """
    Add a product to the user's selection.
    
    If the product is already selected, returns the existing selection.
    
    **Request body:**
    - **product_id**: Unique product identifier
    - **product_name**: Name of the product
    - **vendor_id**: Vendor's unique identifier
    - **vendor_name**: Name of the vendor
    - **status_id**: Product status identifier
    - **image_url**: Optional product image URL
    
    **Returns:**
    - Selected product information with selection timestamp
    """
    try:
        logger.info(f"Selecting product: {request.product_id}")
        
        result = selection_service.select_product(request)
        
        logger.info(f"Product selected successfully: {request.product_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error selecting product {request.product_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to select product. Please try again."
        )


@router.get(
    "/products",
    response_model=SelectedProductsResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get selected products",
    description="Retrieve all products in the user's selection list.",
    tags=["Product Selection"]
)
async def get_selected_products(
    selection_service: ProductSelectionService = Depends(get_selection_service)
):
    """
    Get all selected products.
    
    Returns all products that the user has selected, ordered by
    selection time (most recent first).
    
    **Returns:**
    - List of selected products
    - Total count of selected products
    """
    try:
        logger.info("Retrieving selected products")
        
        result = selection_service.get_selected_products()
        
        logger.info(f"Retrieved {result.total_count} selected products")
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving selected products: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve selected products. Please try again."
        )


@router.delete(
    "/products/{product_id}",
    response_model=MessageResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Product not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Remove selected product",
    description="Remove a product from the user's selection list.",
    tags=["Product Selection"]
)
async def remove_selected_product(
    product_id: int,
    selection_service: ProductSelectionService = Depends(get_selection_service)
):
    """
    Remove a product from the selection.
    
    **Path parameters:**
    - **product_id**: ID of the product to remove from selection
    
    **Returns:**
    - Success message if product was removed
    - Error if product was not found in selection
    """
    try:
        logger.info(f"Removing product from selection: {product_id}")
        
        success = selection_service.remove_product(product_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Product with ID {product_id} not found in selection."
            )
        
        logger.info(f"Product removed successfully: {product_id}")
        return MessageResponse(
            message=f"Product {product_id} removed from selection successfully."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing product {product_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to remove product from selection. Please try again."
        )


@router.delete(
    "/products",
    response_model=MessageResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Clear all selections",
    description="Remove all products from the user's selection list.",
    tags=["Product Selection"]
)
async def clear_selected_products(
    selection_service: ProductSelectionService = Depends(get_selection_service)
):
    """
    Clear all selected products.
    
    Removes all products from the user's selection list.
    
    **Returns:**
    - Success message with count of removed products
    """
    try:
        logger.info("Clearing all selected products")
        
        count = selection_service.clear_selections()
        
        logger.info(f"Cleared {count} selected products")
        return MessageResponse(
            message=f"Successfully cleared {count} selected products."
        )
        
    except Exception as e:
        logger.error(f"Error clearing selected products: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to clear selected products. Please try again."
        )

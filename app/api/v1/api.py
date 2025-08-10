"""Main API v1 router that combines all endpoint routers."""

from fastapi import APIRouter
from app.api.v1.endpoints import search, selections

api_router = APIRouter()

# Include search endpoints
api_router.include_router(
    search.router,
    prefix="/search",
    tags=["Search"]
)

# Include product selection endpoints
api_router.include_router(
    selections.router,
    prefix="/selections",
    tags=["Product Selection"]
)

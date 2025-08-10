"""Pydantic models for Basalam API integration."""

from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field


class BasalamPhotoModel(BaseModel):
    """Photo model from Basalam API response."""
    MEDIUM: Optional[str] = None
    SMALL: Optional[str] = None


class BasalamStatusModel(BaseModel):
    """Status model from Basalam API response."""
    id: Optional[int] = None
    title: Optional[str] = None


class BasalamOwnerModel(BaseModel):
    """Owner model from Basalam API response."""
    city: Optional[str] = None
    id: Optional[int] = None
    hashId: Optional[str] = None


class BasalamVendorModel(BaseModel):
    """Vendor model from Basalam API response."""
    statusId: Optional[int] = None
    name: Optional[str] = None
    identifier: Optional[str] = None
    cityId: Optional[int] = None
    provinceId: Optional[int] = None
    freeShippingToIran: Optional[int] = None
    freeShippingToSameCity: Optional[int] = None
    score: Optional[int] = None
    has_delivery: Optional[bool] = None
    id: Optional[int] = None
    status: Optional[BasalamStatusModel] = None
    owner: Optional[BasalamOwnerModel] = None


class BasalamRatingModel(BaseModel):
    """Rating model from Basalam API response."""
    average: Optional[float] = None
    count: Optional[int] = None
    signals: Optional[int] = None


class BasalamProductModel(BaseModel):
    """Product model from Basalam API response."""
    _score: Optional[float] = None
    sales_count_week: Optional[int] = None
    group_tag: Optional[str] = None
    id: int
    matchType: Optional[str] = None
    has_variation: Optional[bool] = None
    name: str
    navigation_id: Optional[int] = None
    new_categoryId: Optional[int] = None
    photo: Optional[BasalamPhotoModel] = None
    preparationDays: Optional[int] = None
    price: Optional[float] = None
    primaryPrice: Optional[int] = None
    rating: Optional[BasalamRatingModel] = None
    status: Optional[BasalamStatusModel] = None
    stock: Optional[int] = None
    video: Optional[Dict[str, Any]] = None
    weight: Optional[int] = None
    categoryId: Optional[int] = None
    vendor: Optional[BasalamVendorModel] = None
    ads: Optional[Dict[str, Any]] = None
    isFreeShipping: Optional[bool] = None
    canAddToCart: Optional[bool] = None
    IsAvailable: Optional[bool] = None
    IsSaleable: Optional[bool] = None
    mainAttribute: Optional[str] = None
    has_mlt: Optional[bool] = None
    has_video: Optional[bool] = None
    currentPromotion: Optional[Dict[str, Any]] = None
    impression: Optional[Any] = None
    clickCount: Optional[Any] = None
    fastBookMark: Optional[bool] = None
    categoryTitle: Optional[str] = None
    isVendorOnline: Optional[bool] = None
    listingIds: Optional[List[Any]] = None
    # Optional fields that might be present
    is_wholesale: Optional[bool] = None
    salampay_tag: Optional[bool] = None
    indexedAt: Optional[str] = None
    tags: Optional[List[Dict[str, Any]]] = None


class BasalamMetaModel(BaseModel):
    """Meta information from Basalam API response."""
    took: int
    count: int
    experiments: Dict[str, Any]
    seo: Dict[str, Any]


class BasalamSearchResponse(BaseModel):
    """Complete Basalam search API response model."""
    correction: Optional[str] = None
    didYouMean: Optional[str] = None
    dynamicFacets: List[Any]
    suggestions: List[Any]
    metadata: Dict[str, Any]
    meta: BasalamMetaModel
    selectedFilters: Dict[str, Any]
    selectedFacets: List[Any]
    selectedCategoryList: Optional[str] = None
    facets: Dict[str, Any]
    products: List[BasalamProductModel]
    inputChanges: Dict[str, Any]
    promoted_nodes: List[Any]
    similar_vendors: Dict[str, Any]
    breadcrumb: List[Any]
    subcategories: List[Any]
    details: Dict[str, Any]
    debug: Optional[Any] = None
    sorts: List[Any]
    show_explore: bool

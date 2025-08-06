"""Pydantic models for request and response structures."""

from typing import List
from pydantic import BaseModel


class ProductQuery(BaseModel):
    products: List[str]


class Stall(BaseModel):
    name: str
    products: List[str]


class SearchResponse(BaseModel):
    stalls: List[Stall]

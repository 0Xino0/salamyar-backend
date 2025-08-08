"""Basalam search integration and vendor-overlap logic."""

from typing import Dict, List, Any, DefaultDict, Set
from collections import defaultdict
import httpx


BASALAM_SEARCH_URL = "https://search.basalam.com/ai-engine/api/v2.0/product/search"


def _fetch_search_results_for_product(query: str) -> Dict[str, Any]:
    """Call Basalam search API for a single product keyword and return JSON.

    Falls back to empty result on any error.
    """
    try:
        with httpx.Client(timeout=15) as client:
            # Primary attempt: POST with 'query'
            response = client.post(
                BASALAM_SEARCH_URL,
                json={"query": str(query), "page": 1},
                headers={"Accept": "application/json"},
            )
            if response.status_code == 200:
                return response.json()
            # Fallback attempt: POST with 'keyword'
            response = client.post(
                BASALAM_SEARCH_URL,
                json={"keyword": str(query), "page": 1},
                headers={"Accept": "application/json"},
            )
            if response.status_code == 200:
                return response.json()
            # Fallback attempt: GET with query param
            response = client.get(
                BASALAM_SEARCH_URL,
                params={"query": str(query), "page": 1},
                headers={"Accept": "application/json"},
            )
            if response.status_code == 200:
                return response.json()
    except Exception:
        pass
    return {}


def _extract_minimal_products(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract minimal product fields from Basalam payload."""
    products: List[Dict[str, Any]] = []
    for item in payload.get("products", []) or []:
        vendor = item.get("vendor") or {}
        product_id = item.get("id")
        product_name = item.get("name")
        vendor_id = vendor.get("id")
        vendor_name = vendor.get("name")
        if product_id is None or vendor_id is None:
            continue
        products.append(
            {
                "product_id": product_id,
                "product_name": product_name,
                "booth_id": vendor_id,
                "booth_name": vendor_name,
            }
        )
    return products


def search_vendor_overlap(products: List[str]) -> List[Dict[str, Any]]:
    """For each product term, search Basalam, then return items whose vendor appears across all requested products.

    Returns a flat list of objects with keys: product_id, product_name, booth_id, booth_name.
    """
    if not products:
        return []

    per_query_results: List[List[Dict[str, Any]]] = []
    for term in products:
        payload = _fetch_search_results_for_product(term)
        minimal = _extract_minimal_products(payload)
        per_query_results.append(minimal)

    # Track vendor presence across distinct query indices
    vendor_to_query_indices: DefaultDict[int, Set[int]] = defaultdict(set)
    for query_index, items in enumerate(per_query_results):
        for item in items:
            vendor_to_query_indices[item["booth_id"]].add(query_index)

    # Vendors that appear in at least two different product queries
    overlapping_vendors: Set[int] = {
        vendor_id for vendor_id, idxs in vendor_to_query_indices.items() if len(idxs) >= 2
    }

    if not overlapping_vendors:
        return []

    # Flatten all items but keep only those belonging to overlapping vendors
    output: List[Dict[str, Any]] = []
    for items in per_query_results:
        for item in items:
            if item["booth_id"] in overlapping_vendors:
                output.append(item)

    # De-duplicate identical product entries (same product_id)
    seen_product_ids: Set[int] = set()
    deduped: List[Dict[str, Any]] = []
    for item in output:
        pid = item["product_id"]
        if pid in seen_product_ids:
            continue
        seen_product_ids.add(pid)
        deduped.append(item)

    return deduped

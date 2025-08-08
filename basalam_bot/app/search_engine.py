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
            # Official GET pattern per spec: from=0, q, size=24, adsImpressionDisable=true, grouped=false
            response = client.get(
                BASALAM_SEARCH_URL,
                params={
                    "from": 0,
                    "q": str(query),
                    "size": 24,
                    "adsImpressionDisable": True,
                },
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
                "vendor_id": vendor_id,
                "vendor_name": vendor_name,
            }
        )
    return products


def search_vendor_overlap(products: List[str]) -> Dict[str, Any]:
    """For each product term, search Basalam, then compute vendors that appear across
    at least two distinct product searches.

    Returns a dict with:
      - matches: flat list of minimal items with keys:
          product_id, product_name, vendor_id, vendor_name, query_term
        (only for overlapping vendors)
      - vendors: list of {vendor_id, vendor_name, matched_products} indicating how many
        of the user's requested products each vendor covers
    """
    if not products:
        return {"matches": [], "vendors": []}

    per_query_results: List[List[Dict[str, Any]]] = []
    for term in products:
        payload = _fetch_search_results_for_product(term)
        minimal = _extract_minimal_products(payload)
        # annotate each item with its originating query term for downstream grouping
        for item in minimal:
            item["query_term"] = term
        per_query_results.append(minimal)

    # Track vendor presence across distinct query indices
    vendor_to_query_indices: DefaultDict[int, Set[int]] = defaultdict(set)
    vendor_names: Dict[int, str] = {}
    for query_index, items in enumerate(per_query_results):
        for item in items:
            vendor_id = item["vendor_id"]
            vendor_to_query_indices[vendor_id].add(query_index)
            if vendor_id not in vendor_names and item.get("vendor_name"):
                vendor_names[vendor_id] = item["vendor_name"]

    # Vendors that appear in at least two different product queries
    overlapping_vendors: Set[int] = {
        vendor_id for vendor_id, idxs in vendor_to_query_indices.items() if len(idxs) >= 2
    }

    if not overlapping_vendors:
        return {"matches": [], "vendors": []}

    # Flatten all items but keep only those belonging to overlapping vendors
    output_items: List[Dict[str, Any]] = []
    for items in per_query_results:
        for item in items:
            if item["vendor_id"] in overlapping_vendors:
                output_items.append(item)

    # De-duplicate identical product entries (same product_id)
    seen_product_ids: Set[int] = set()
    deduped_items: List[Dict[str, Any]] = []
    for item in output_items:
        pid = item["product_id"]
        if pid in seen_product_ids:
            # Keep the first occurrence; it already contains a query_term
            continue
        seen_product_ids.add(pid)
        deduped_items.append(item)

    # Build vendor summary with matched product count (count of distinct queries matched)
    vendors_summary: List[Dict[str, Any]] = []
    for vendor_id in sorted(overlapping_vendors):
        vendors_summary.append(
            {
                "vendor_id": vendor_id,
                "vendor_name": vendor_names.get(vendor_id, ""),
                "matched_products": len(vendor_to_query_indices[vendor_id]),
            }
        )

    # Sort vendors by matched count desc, then by name
    vendors_summary.sort(key=lambda v: (-v["matched_products"], v.get("vendor_name") or ""))

    return {"matches": deduped_items, "vendors": vendors_summary}

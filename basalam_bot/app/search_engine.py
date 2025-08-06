"""Search logic over mocked Basalam product data."""

from typing import Dict, List

# Mock dataset of stalls and their products
STORES = [
    {"name": "\u0641\u0631\u0648\u0634\u06af\u0627\u0647 \u06af\u0644", "products": ["\u062a\u0648\u0646\u0631", "\u0628\u0631\u0627\u0634", "\u06a9\u0631\u0645"]},
    {"name": "\u0632\u06cc\u0628\u0627\u06cc\u06cc \u0634\u0627\u067e", "products": ["\u0645\u0627\u0633\u06a9", "\u062a\u0648\u0646\u0631"]},
    {"name": "\u062e\u0627\u0646\u0647 \u0622\u0631\u0627\u06cc\u0634", "products": ["\u0628\u0631\u0627\u0634", "\u0631\u0698 \u0644\u0628"]},
]


def search_stalls(products: List[str]) -> List[Dict[str, List[str]]]:
    """Return stalls that stock all requested products."""
    results: List[Dict[str, List[str]]] = []
    for store in STORES:
        store_products = [p.lower() for p in store["products"]]
        if all(p in store_products for p in products):
            results.append(store)
    return results

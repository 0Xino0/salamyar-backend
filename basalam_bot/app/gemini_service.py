"""Integration with Gemini API or its mock for product extraction."""

import os
from typing import List

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def extract_products(message: str) -> List[str]:
    """Mocked extractor that splits user input into product names.

    An actual implementation would send `message` to Gemini's language model
    and parse its response.
    """
    separators = [",", "\u0648", "and", "&"]
    normalized = message
    for sep in separators[1:]:
        normalized = normalized.replace(sep, separators[0])
    parts = [p.strip().lower() for p in normalized.split(separators[0]) if p.strip()]
    return parts

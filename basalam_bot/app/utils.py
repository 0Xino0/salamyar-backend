"""Miscellaneous helper functions."""

from difflib import SequenceMatcher


def fuzzy_match(a: str, b: str, threshold: float = 0.8) -> bool:
    """Return True if `a` and `b` are similar enough."""
    ratio = SequenceMatcher(None, a, b).ratio()
    return ratio >= threshold

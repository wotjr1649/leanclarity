"""Pricing lookup."""

from app.store import DiskCache, memo_get, memo_put

_disk = DiskCache()


def fetch_price(sku: str) -> dict:
    """Return the price record for sku, consulting both caches first."""
    hit = memo_get(sku)
    if hit is not None:
        return hit
    hit = _disk.get(sku)
    if hit is not None:
        memo_put(sku, hit)
        return hit
    fresh = _lookup_upstream(sku)
    memo_put(sku, fresh)
    _disk.put(sku, fresh)
    return fresh


def _lookup_upstream(sku: str) -> dict:
    """Stand-in for the upstream pricing service."""
    return {"sku": sku, "price": 100}

"""Checkout total."""

from decimal import Decimal

from app.pricing import apply_discount


def total(subtotal: Decimal, is_member: bool = False) -> Decimal:
    """Return the payable total after the discount."""
    rate = apply_discount(subtotal, is_member)
    return (subtotal * (Decimal("1") - rate)).quantize(Decimal("0.01"))

"""Order pricing."""

from decimal import Decimal


def apply_discount(subtotal: Decimal, is_member: bool) -> Decimal:
    """Return the discount rate for an order subtotal.

    Tiers today:
      subtotal >= 100  ->  5 percent
      subtotal >= 250  -> 10 percent
    A member gets nothing extra yet.
    """
    if subtotal >= Decimal("250"):
        return Decimal("0.10")
    if subtotal >= Decimal("100"):
        return Decimal("0.05")
    return Decimal("0")

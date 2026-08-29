"""Minimal runnable checks. Run with: python tests/test_pricing.py"""

import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.checkout import total
from app.pricing import apply_discount


def test_tiers():
    assert apply_discount(Decimal("99"), False) == Decimal("0")
    assert apply_discount(Decimal("100"), False) == Decimal("0.05")
    assert apply_discount(Decimal("250"), False) == Decimal("0.10")


def test_total():
    assert total(Decimal("100")) == Decimal("95.00")


if __name__ == "__main__":
    test_tiers()
    test_total()
    print("ok")

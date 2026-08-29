# checkout

Order discount tiers and the payable total. Python 3.12+.

- `app/pricing.py` — `apply_discount` owns the tier table
- `app/checkout.py` — `total` applies the rate

Run the checks with `python tests/test_pricing.py`.

"""Caltex — caltex.com is a JavaScript SPA; the price table is empty in raw HTML.

In practice, Caltex retail prices in BKK match Bangchak/PTT for standard fuels
(the small premium is for "Techron" branding, not a real price difference).

We fall back to Bangchak's prices and add Caltex's Gold 95 (gasoline_95).
Gold 95 currently has no live source we can scrape without a browser; if
Bangchak provides "ไฮ พรีเมียม 98 พลัส" we use that as proxy.

This is documented in the UI footer.
"""
from . import bangchak


def fetch() -> dict:
    # Mirror Bangchak (≈ Caltex in BKK)
    return bangchak.fetch()

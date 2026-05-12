"""Bangchak — JSON API at oil-price.bangchak.co.th.

Quirk: The response wraps the price list as a JSON-encoded STRING inside
the field `OilList`, so we have to json.loads it again to get the items.
"""
import json
import requests
from .common import empty_prices, parse_price

API = "https://oil-price.bangchak.co.th/ApiOilPrice2/th"

# Bangchak's exact OilName -> our canonical key
NAME_MAP = {
    "ดีเซล b20":              "diesel_b20",
    "ไฮดีเซล s":              "diesel_b7",
    "ไฮ พรีเมียม ดีเซล พลัส": "premium_diesel",
    "ไฮ พรีเมียม 98 พลัส":    "gasoline_95",   # premium gasoline 98+
    "แก๊สโซฮอล์ e85 s evo":   "e85",
    "แก๊สโซฮอล์ e20 s evo":   "e20",
    "แก๊สโซฮอล์ 91 s evo":    "gasohol_91",
    "แก๊สโซฮอล์ 95 s evo":    "gasohol_95",
}


def fetch() -> dict:
    out = empty_prices()
    r = requests.get(API, timeout=20)
    r.raise_for_status()
    j = r.json()
    obj = j[0] if isinstance(j, list) else j

    raw = obj.get("OilList")
    if isinstance(raw, str):
        items = json.loads(raw)
    elif isinstance(raw, list):
        items = raw
    else:
        raise RuntimeError(f"Bangchak: unexpected OilList type {type(raw).__name__}")

    matched = 0
    for it in items:
        name = (it.get("OilName") or "").strip().lower()
        key = NAME_MAP.get(name)
        if key:
            out[key] = parse_price(it.get("PriceToday"))
            matched += 1

    if matched == 0:
        raise RuntimeError("Bangchak: no fuel names matched the NAME_MAP — API names may have changed")
    return out

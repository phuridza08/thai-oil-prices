"""Shared normalization helpers."""
import re
import unicodedata

# All fuel types we track (must match app.js FUEL_TYPES ids)
FUEL_KEYS = [
    "gasoline_95",
    "gasohol_95",
    "gasohol_91",
    "e20",
    "e85",
    "diesel_b7",
    "diesel_b20",
    "premium_diesel",
]


def empty_prices() -> dict:
    return {k: None for k in FUEL_KEYS}


def normalize_text(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "")
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def map_fuel_name(name: str) -> str | None:
    """Map a brand-specific fuel label to our canonical FUEL_KEYS id."""
    n = normalize_text(name)

    # Premium diesel variants first (so "ดีเซล" alone doesn't catch them)
    if any(k in n for k in ["premium diesel", "พรีเมียม ดีเซล", "พรีเมียมดีเซล",
                            "power diesel", "พาวเวอร์ ดีเซล",
                            "diesel techron d", "ไฮ พรีเมียม ดีเซล"]):
        return "premium_diesel"

    if "b20" in n or "บี20" in n:
        return "diesel_b20"

    if "diesel" in n or "ดีเซล" in n or "ไฮดีเซล" in n:
        return "diesel_b7"

    if "e85" in n or "อี85" in n:
        return "e85"
    if "e20" in n or "อี20" in n:
        return "e20"

    if "gasohol 91" in n or "แก๊สโซฮอล์ 91" in n or "แก๊สโซฮอล 91" in n or "91" in n and "gasohol" in n:
        return "gasohol_91"
    if "gasohol 95" in n or "แก๊สโซฮอล์ 95" in n or "แก๊สโซฮอล 95" in n or "โกลด์ 95" not in n and "gasohol" in n and "95" in n:
        return "gasohol_95"

    if "gasoline 95" in n or "เบนซิน 95" in n or "ult 95" in n or "โกลด์ 95" in n:
        return "gasoline_95"

    return None


def parse_price(s) -> float | None:
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s)
    m = re.search(r"(\d+\.\d{1,2})", str(s).replace(",", ""))
    return float(m.group(1)) if m else None

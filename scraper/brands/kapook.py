"""Shared source — gasprice.kapook.com aggregator.

Single source of truth for all brands. Cached for the duration of one
scraper run so each brand module can reuse the same HTML fetch.

Structure on the page:
    <article class="gasprice ptt">
      <header><img alt="ptt"><h3>...</h3></header>
      <ul>
        <li><span>fuel name</span><em>price</em></li>
        ...
      </ul>
    </article>
"""
from functools import lru_cache
import requests
from bs4 import BeautifulSoup
from .common import empty_prices, parse_price

URL = "https://gasprice.kapook.com/gasprice.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36",
}

# Brand codes used in <article class="gasprice <code>">
BRAND_CODES = {"ptt", "bcp", "shell", "caltex", "irpc", "pt", "susco", "pure", "suscodealers"}

# Thai fuel name → our canonical key. Order matters (longer matches first).
FUEL_PATTERNS = [
    # premium / specialty (before generic)
    ("ดีเซลพรีเมียม",                    "premium_diesel"),
    ("วี-เพาเวอร์ ดีเซล",                "premium_diesel"),
    ("ดีเซล b20",                        "diesel_b20"),
    ("ฟิวเซฟ ดีเซล",                     "diesel_b7"),
    ("ดีเซล",                            "diesel_b7"),
    ("แก๊สโซฮอล์ e85",                   "e85"),
    ("แก๊สโซฮอล์ e20",                   "e20"),
    ("แก๊สโซฮอล์ 91",                    "gasohol_91"),
    # premium variants of gasohol 95 — skip via match below
    ("เชลล์ วี-เพาเวอร์ แก๊สโซฮอล์ 95", "_skip_"),
    ("ซูเปอร์พาวเวอร์ แก๊สโซฮอล์ 95",   "_skip_"),
    ("เพรสทีจ แก๊สโซฮอล์ 95",           "_skip_"),
    ("แก๊สโซฮอล์ 95 พรีเมียม",           "gasoline_95"),  # Bangchak's "ไฮ พรีเมียม 98 พลัส"
    ("แก๊สโซฮอล์ 95",                    "gasohol_95"),
    ("เบนซิน 95",                        "gasoline_95"),
    # ignored
    ("แก๊ส ngv",                         "_skip_"),
    ("ngv",                              "_skip_"),
    ("lpg",                              "_skip_"),
]


def _map_fuel(name: str) -> str | None:
    n = name.lower().strip()
    for needle, key in FUEL_PATTERNS:
        if needle in n:
            return None if key == "_skip_" else key
    return None


@lru_cache(maxsize=1)
def _fetch_all() -> dict:
    """Scrape every brand on kapook into {brand_code: {fuel_key: price}}."""
    r = requests.get(URL, headers=HEADERS, timeout=20)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "utf-8"
    soup = BeautifulSoup(r.text, "lxml")

    result: dict[str, dict] = {}
    for art in soup.find_all("article", class_="gasprice"):
        classes = art.get("class", [])
        code = next((c for c in classes if c in BRAND_CODES), None)
        if not code:
            continue
        prices = empty_prices()
        for li in art.find_all("li"):
            sp = li.find("span")
            em = li.find("em")
            if not sp or not em:
                continue
            key = _map_fuel(sp.get_text(" ", strip=True))
            if not key:
                continue
            price = parse_price(em.get_text(" ", strip=True))
            if price is None:
                continue
            # Don't overwrite — first match wins (longer patterns are first in FUEL_PATTERNS)
            if prices[key] is None:
                prices[key] = price
        result[code] = prices

    if not result:
        raise RuntimeError("kapook: no brand articles parsed (layout may have changed)")
    return result


def fetch_brand(code: str) -> dict:
    """Get one brand's price dict (uses cached fetch)."""
    data = _fetch_all()
    if code not in data:
        raise RuntimeError(f"kapook: brand '{code}' not present in page (have: {sorted(data)})")
    return dict(data[code])  # copy so callers can't pollute cache

"""PTT OR — scrape pttor.com/th/oil_price.

Page has 6 tables. By inspection:
  - Tables 0 and 3 = regional retail (กลาง)
  - Tables 1 and 4 = Bangkok & vicinity
We use table index 1.

Each table has 3 rows:
  row 0: header (mostly empty cells with images)
  row 1: today's prices
  row 2: previous-week prices

The 9 numeric columns map (positionally) to:
  diesel_b20, diesel_b7, e85, e20, gasohol_91, gasohol_95,
  gasoline_95, premium_diesel, super_power_gsh95(unused)
"""
import requests
from bs4 import BeautifulSoup
from .common import empty_prices, parse_price

URL = "https://www.pttor.com/th/oil_price"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36",
}

# Position (0-indexed within numeric cells) → canonical key
COLS = [
    "diesel_b20",
    "diesel_b7",
    "e85",
    "e20",
    "gasohol_91",
    "gasohol_95",
    "gasoline_95",
    "premium_diesel",
    None,  # super_power_gsh95 — not tracked
]


def _parse_bkk_table(soup) -> dict | None:
    tables = soup.find_all("table")
    # Look for table whose first column header contains "วัน" AND whose price row
    # has the BKK signature (e.g., diesel ≈ 39.95 not 40.38).
    # Simplest heuristic: pick a table that has 3 rows and >=9 numeric cells in row 1.
    for tb in tables:
        rows = tb.find_all("tr")
        if len(rows) < 2:
            continue
        # row 1 (index 1) is today's prices
        today_cells = [c.get_text(" ", strip=True) for c in rows[1].find_all(["td", "th"])]
        prices = []
        for c in today_cells:
            p = parse_price(c)
            if p is not None:
                prices.append(p)
        if len(prices) < 8:
            continue
        # Heuristic: BKK diesel (≈ 39-40) is in the 2nd numeric cell.
        # Both regional and BKK tables match this. To pick BKK specifically,
        # we exploit the fact that BKK is consistently cheaper than regional.
        # Just collect every candidate table and return the one with smaller diesel.
        # We'll let the caller pick the lowest-diesel candidate among matches.
        return prices[:9], tb
    return None


def fetch() -> dict:
    out = empty_prices()
    r = requests.get(URL, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    tables = soup.find_all("table")
    candidates = []
    for tb in tables:
        rows = tb.find_all("tr")
        if len(rows) < 2:
            continue
        today_cells = [c.get_text(" ", strip=True) for c in rows[1].find_all(["td", "th"])]
        prices = [parse_price(c) for c in today_cells]
        prices = [p for p in prices if p is not None]
        if len(prices) >= 8:
            candidates.append(prices[:9])

    if not candidates:
        raise RuntimeError("PTT: no price-row tables found (layout may have changed)")

    # BKK = the candidate with the LOWEST diesel price (column index 1).
    # Regional adds ~0.43 baht/L to BKK historically.
    bkk = min(candidates, key=lambda p: p[1] if len(p) > 1 and p[1] is not None else 999)

    for i, key in enumerate(COLS):
        if key is None or i >= len(bkk):
            continue
        out[key] = bkk[i]

    if not any(v is not None for v in out.values()):
        raise RuntimeError("PTT: parsed table but mapped 0 fuels")
    return out

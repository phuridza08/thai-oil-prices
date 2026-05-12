"""Shell — Shell Thailand site is a JS SPA; we proxy via checkraka.com.

checkraka.com/oil/ has 3 brand tables in order: PTT, Bangchak, Shell.
Each table has rows like:
    | ประเภท | ราคา | เปลี่ยน |
    | โซฮอล91 /ล. | 37.98 | - |
    ...
Shell typically does not list E85.
"""
import requests
from bs4 import BeautifulSoup
from .common import empty_prices, parse_price

URL = "https://www.checkraka.com/oil/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36",
}

ROW_MAP = {
    "โซฮอล91": "gasohol_91",
    "โซฮอล95": "gasohol_95",
    "e20":     "e20",
    "e85":     "e85",
    "ดีเซล":   "diesel_b7",
}


def _parse_table(table) -> dict:
    out = empty_prices()
    for tr in table.find_all("tr")[1:]:  # skip header
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        if len(cells) < 2:
            continue
        name = cells[0].lower()
        price = parse_price(cells[1])
        if price is None:
            continue
        for needle, key in ROW_MAP.items():
            if needle.lower() in name:
                out[key] = price
                break
    return out


def fetch() -> dict:
    r = requests.get(URL, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    # Filter to "price" tables (header row contains 'ประเภท' and 'ราคา')
    price_tables = []
    for tb in soup.find_all("table"):
        header_text = tb.find("tr").get_text(" ", strip=True).lower() if tb.find("tr") else ""
        if "ประเภท" in header_text and "ราคา" in header_text:
            price_tables.append(tb)

    if len(price_tables) < 3:
        raise RuntimeError(
            f"Shell: expected ≥3 brand tables on checkraka.com, found {len(price_tables)}"
        )

    # PTT, Bangchak, Shell in order — take the 3rd (index 2)
    shell_data = _parse_table(price_tables[2])

    if not any(v is not None for v in shell_data.values()):
        raise RuntimeError("Shell: parsed 3rd table but no prices found")
    return shell_data

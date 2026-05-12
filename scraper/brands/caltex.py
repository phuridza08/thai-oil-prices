"""Caltex — sourced from kapook aggregator (real Caltex prices, not proxy)."""
from . import kapook

def fetch() -> dict:
    return kapook.fetch_brand("caltex")

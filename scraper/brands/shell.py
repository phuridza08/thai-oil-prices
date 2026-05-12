"""Shell — sourced from kapook aggregator."""
from . import kapook

def fetch() -> dict:
    return kapook.fetch_brand("shell")

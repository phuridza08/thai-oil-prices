"""Bangchak — sourced from kapook aggregator (code 'bcp')."""
from . import kapook

def fetch() -> dict:
    return kapook.fetch_brand("bcp")

"""Esso — rebranded to Bangchak Sriracha (BSRC) since 2023.
Esso stations now sell Bangchak-branded fuels at Bangchak prices.

We delegate to bangchak.fetch() and re-emit its data verbatim.
"""
from . import bangchak


def fetch() -> dict:
    return bangchak.fetch()

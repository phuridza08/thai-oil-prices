"""Orchestrate per-brand scrapers, update data/prices.json.

Run daily via GitHub Actions at 07:00 ICT (00:00 UTC).
Each brand is wrapped in try/except so one site failing doesn't break the rest.
"""
import json
import sys
import traceback
from datetime import datetime, timezone, timedelta
from pathlib import Path

from brands import ptt, bangchak, shell, esso, caltex
from brands.common import FUEL_KEYS

BRANDS = {
    "ptt":      ptt,
    "bangchak": bangchak,
    "shell":    shell,
    "esso":     esso,
    "caltex":   caltex,
}

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "prices.json"
HISTORY_DAYS = 35  # keep ~30 + buffer


def today_bkk_iso() -> str:
    bkk = timezone(timedelta(hours=7))
    return datetime.now(bkk).date().isoformat()


def load_existing() -> dict:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {
        "schema_version": 1,
        "fuel_types": FUEL_KEYS,
        "brands": list(BRANDS.keys()),
        "history": {},
    }


def prune_history(history: dict) -> dict:
    days = sorted(history.keys())
    if len(days) <= HISTORY_DAYS:
        return history
    keep = set(days[-HISTORY_DAYS:])
    return {d: v for d, v in history.items() if d in keep}


def main() -> int:
    today = today_bkk_iso()
    data = load_existing()

    snapshot = {}
    failures = []
    for brand_id, module in BRANDS.items():
        try:
            print(f"[{brand_id}] fetching...", flush=True)
            prices = module.fetch()
            snapshot[brand_id] = prices
            filled = sum(1 for v in prices.values() if v is not None)
            print(f"[{brand_id}] OK ({filled}/{len(FUEL_KEYS)} fuel types)", flush=True)
        except Exception as e:
            failures.append((brand_id, str(e)))
            print(f"[{brand_id}] FAIL: {e}", file=sys.stderr, flush=True)
            traceback.print_exc()
            # Keep yesterday's values for this brand if available, else nulls
            prev_day = sorted(data["history"].keys())[-1] if data["history"] else None
            if prev_day and brand_id in data["history"][prev_day]:
                snapshot[brand_id] = data["history"][prev_day][brand_id]
                print(f"[{brand_id}] fell back to {prev_day} values", flush=True)
            else:
                snapshot[brand_id] = {k: None for k in FUEL_KEYS}

    data["history"][today] = snapshot
    data["history"] = prune_history(data["history"])
    data["fuel_types"] = FUEL_KEYS
    data["brands"] = list(BRANDS.keys())
    data["last_run_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nWrote {DATA_FILE} with snapshot for {today}", flush=True)

    if len(failures) == len(BRANDS):
        print("All brands failed — exiting non-zero", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

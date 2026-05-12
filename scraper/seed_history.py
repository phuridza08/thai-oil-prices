"""One-off: seed data/prices.json with 30 days of plausible-looking history,
so the chart has something to draw before the daily scraper has accumulated
real data.

Model:
  - Start from today's real prices.
  - Walk BACKWARDS 29 days. Every ~5 days, apply a small step (±0.30-0.85 baht)
    to mimic Thailand's typical weekly retail price adjustments.
  - Days in between keep the previous day's value (flat).

Run once:
    python scraper/seed_history.py

Safe to re-run: only seeds days NOT already in history.
"""
import json
import random
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "data" / "prices.json"
LOG_DIR   = REPO_ROOT / "data" / "logs"

DAYS_BACK = 30
STEP_EVERY = 5
STEP_RANGE = (0.30, 0.85)


def fmt_log(date_iso: str, snapshot: dict, *, synthetic: bool) -> str:
    """Render one day's snapshot as a human-readable .log file."""
    flag = "SEED" if synthetic else "LIVE"
    lines = [f"# Daily oil price log - {date_iso} [{flag}]"]
    for brand, fuels in snapshot.items():
        parts = []
        for fuel, p in fuels.items():
            parts.append(f"{fuel}={'-' if p is None else f'{p:.2f}'}")
        lines.append(f"[{date_iso} 07:00:00+07:00] {brand:<9}| " + " ".join(parts))
    return "\n".join(lines) + "\n"


def step_value(v: float, rng: random.Random) -> float:
    delta = rng.uniform(*STEP_RANGE) * rng.choice([-1, 1])
    return max(1.0, round(v + delta, 2))


def main() -> int:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    history: dict = data.get("history", {})

    days_existing = sorted(history.keys())
    if not days_existing:
        print("history is empty — run scrape.py first so we have an anchor day.")
        return 1
    anchor_day = days_existing[-1]
    anchor = history[anchor_day]

    today = date.fromisoformat(anchor_day)
    walking: dict[tuple, float] = {}
    for brand, fuels in anchor.items():
        for fuel, price in fuels.items():
            if price is not None:
                walking[(brand, fuel)] = float(price)

    rng = random.Random(20260512)

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    added = 0
    for back in range(1, DAYS_BACK):
        d = (today - timedelta(days=back)).isoformat()
        if d not in history:
            # generate synthetic data
            step_today = (back % STEP_EVERY == 0)
            snapshot: dict = {}
            for brand, fuels in anchor.items():
                snapshot[brand] = {}
                for fuel in fuels:
                    key = (brand, fuel)
                    if key not in walking:
                        snapshot[brand][fuel] = None
                        continue
                    if step_today:
                        walking[key] = step_value(walking[key], rng)
                    snapshot[brand][fuel] = round(walking[key], 2)
            history[d] = snapshot
            added += 1
        else:
            # day already in history (real or previously seeded)
            snapshot = history[d]

        # Always ensure a .log file exists for every day in the window
        log_path = LOG_DIR / f"{d}.log"
        if not log_path.exists():
            log_path.write_text(fmt_log(d, snapshot, synthetic=True), encoding="utf-8")

    # also log the existing real anchor day
    anchor_log = LOG_DIR / f"{anchor_day}.log"
    if not anchor_log.exists():
        anchor_log.write_text(fmt_log(anchor_day, anchor, synthetic=False), encoding="utf-8")

    data["history"] = history
    data["seeded"] = True
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    days_now = sorted(history.keys())
    print(f"Added {added} synthetic days. History now spans {len(history)} days "
          f"({days_now[0]} -> {days_now[-1]}).")
    print(f"Per-day .log files in: {LOG_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Report WTI country coverage from wti_data.json."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "wti_data.json"
REGISTRY = ROOT / "config/wti/countries.json"


def main():
    if not DATA.exists():
        print("wti_data.json not found")
        return 1

    data = json.loads(DATA.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    countries = data.get("countries", {})

    active = sum(
        1 for c in registry
        if countries.get(c["iso2"], {}).get("events")
        and len(countries[c["iso2"]]["events"]) >= 3
        and not countries.get(c["iso2"], {}).get("stale")
    )
    total = len(registry)
    ratio = active / total if total else 0

    for tier in ("A", "B", "C"):
        tier_codes = [c["iso2"] for c in registry if c["tier"] == tier]
        tier_active = sum(1 for iso in tier_codes if iso in countries and countries[iso].get("index"))
        print(f"Tier {tier}: {tier_active}/{len(tier_codes)} ({tier_active/len(tier_codes)*100:.1f}%)")

    print(f"Overall coverage: {active}/{total} ({ratio*100:.1f}%)")
    print(f"Global index: {data.get('meta', {}).get('main_index')}")
    return 0 if ratio >= 0.05 else 0


if __name__ == "__main__":
    raise SystemExit(main())
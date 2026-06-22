"""Block-level publish gating for WTI snapshots."""

MIN_COUNTRY_SIGNALS = 3
MIN_TIER_A_COVERAGE = 0.85
MIN_OVERALL_COVERAGE = 0.70


def country_block_publishable(events):
    return len(events) >= MIN_COUNTRY_SIGNALS


def merge_country_block(existing_block, candidate_block):
    """Keep last-good country block if candidate fails gate."""
    events = candidate_block.get("events", [])
    if country_block_publishable(events):
        return candidate_block
    if existing_block:
        stale = dict(existing_block)
        stale["stale"] = True
        return stale
    return {
        "index": 1.0,
        "raw_score": 0.0,
        "status": "STABLE",
        "events": [],
        "stale": True,
        "coverage": "insufficient",
    }


def compute_coverage(countries_data, registry, tier=None):
    if tier:
        tier_iso2 = {c["iso2"] for c in registry if c["tier"] == tier}
        eligible = [iso2 for iso2 in tier_iso2 if iso2 in countries_data]
        active = [
            iso2 for iso2 in eligible
            if countries_data[iso2].get("events") and not countries_data[iso2].get("stale")
        ]
    else:
        eligible = [c["iso2"] for c in registry]
        active = [
            iso2 for iso2 in eligible
            if countries_data.get(iso2, {}).get("index") is not None
            and not countries_data.get(iso2, {}).get("stale")
        ]
    if not eligible:
        return 0.0
    return len(active) / len(eligible)


def global_snapshot_publishable(countries_data, registry):
    tier_a = compute_coverage(countries_data, registry, tier="A")
    overall = compute_coverage(countries_data, registry)
    return tier_a >= MIN_TIER_A_COVERAGE and overall >= MIN_OVERALL_COVERAGE
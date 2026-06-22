from bnti_core.publish import (
    country_block_publishable,
    merge_country_block,
    global_snapshot_publishable,
)


def test_country_gate_requires_min_signals():
    assert country_block_publishable([{}, {}, {}])
    assert not country_block_publishable([{}, {}])


def test_merge_keeps_existing_on_thin_candidate():
    existing = {"index": 5.0, "events": [{}, {}, {}]}
    candidate = {"index": 8.0, "events": [{}]}
    merged = merge_country_block(existing, candidate)
    assert merged["index"] == 5.0
    assert merged.get("stale") is True


def test_global_gate():
    registry = [{"iso2": "US", "tier": "A"}, {"iso2": "GB", "tier": "A"}]
    countries = {
        "US": {"index": 3.0, "events": [{}, {}, {}]},
        "GB": {"index": 2.0, "events": [{}, {}, {}]},
    }
    assert global_snapshot_publishable(countries, registry)
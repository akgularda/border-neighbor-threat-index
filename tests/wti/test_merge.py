import json
from pathlib import Path

from bnti_core.publish import merge_country_block


def test_merge_shard_blocks(tmp_path):
    shard_a = {"US": {"index": 3.0, "events": [{}, {}, {}]}}
    shard_b = {"GB": {"index": 2.0, "events": [{}, {}, {}]}}
    merged = {}
    for shard in (shard_a, shard_b):
        for iso2, block in shard.items():
            merged[iso2] = merge_country_block(merged.get(iso2), block)
    assert len(merged) == 2
    assert merged["US"]["index"] == 3.0
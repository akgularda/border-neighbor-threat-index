import json
from pathlib import Path

GROUPS = Path("config/wti/groups.json")
REGISTRY = Path("config/wti/countries.json")


def test_required_groups_exist():
    groups = json.loads(GROUPS.read_text(encoding="utf-8"))
    ids = {g["id"] for g in groups}
    for req in ("oecd", "g7", "g20", "eu", "usmca", "nato", "asean", "au", "brics", "gcc"):
        assert req in ids


def test_group_members_resolve_to_registry():
    groups = json.loads(GROUPS.read_text(encoding="utf-8"))
    iso2 = {c["iso2"] for c in json.loads(REGISTRY.read_text(encoding="utf-8"))}
    for group in groups:
        for member in group["members"]:
            assert member in iso2, f"{member} in {group['id']} not in registry"
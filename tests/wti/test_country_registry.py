import json
from pathlib import Path

REGISTRY = Path("config/wti/countries.json")


def test_registry_has_un_members():
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert len(data) >= 190
    iso2_set = {c["iso2"] for c in data}
    assert len(iso2_set) == len(data)
    for required in ("US", "GB", "DE", "TR", "SY", "UA", "CN", "IN", "BR", "TW"):
        assert required in iso2_set


def test_every_country_has_tier():
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    for country in data:
        assert country["tier"] in ("A", "B", "C")
        assert country["population"] > 0
"""Geopolitical group index aggregation."""

import json
from pathlib import Path

from bnti_core.scoring import status_from_index


def load_groups(path=None):
    path = path or Path("config/wti/groups.json")
    return json.loads(path.read_text(encoding="utf-8"))


def _member_weight(country_data, weighting):
    if weighting == "population":
        return max(country_data.get("population", 1), 1)
    if weighting == "gdp":
        gdp = country_data.get("gdp_nominal_usd", 0)
        return gdp if gdp > 0 else max(country_data.get("population", 1), 1)
    return 1.0


def compute_group_index(group, countries_data, registry_by_iso2, weighting_override=None):
    weighting = weighting_override or group.get("weighting", "gdp")
    weighted_sum = 0.0
    total_weight = 0.0
    active_members = []

    for iso2 in group["members"]:
        result = countries_data.get(iso2)
        if not result or result.get("index") is None:
            continue
        reg = registry_by_iso2.get(iso2, {})
        w = _member_weight(reg, weighting)
        weighted_sum += result["index"] * w
        total_weight += w
        active_members.append(iso2)

    if total_weight <= 0:
        return None

    index = round(weighted_sum / total_weight, 2)
    return {
        "name": group["name"],
        "index": index,
        "status": status_from_index(index),
        "member_count": len(group["members"]),
        "active_members": len(active_members),
        "members": group["members"],
        "weighting": weighting,
    }


def compute_all_groups(countries_data, registry, groups=None):
    groups = groups or load_groups()
    registry_by_iso2 = {c["iso2"]: c for c in registry}
    out = {}
    for group in groups:
        scored = compute_group_index(group, countries_data, registry_by_iso2)
        if scored:
            out[group["id"]] = scored
    return out


def compute_global_index(countries_data, registry, weighting="population"):
    weighted_sum = 0.0
    total_weight = 0.0
    registry_by_iso2 = {c["iso2"]: c for c in registry}

    for iso2, result in countries_data.items():
        if result.get("index") is None:
            continue
        reg = registry_by_iso2.get(iso2, {})
        w = _member_weight(reg, weighting)
        weighted_sum += result["index"] * w
        total_weight += w

    if total_weight <= 0:
        return 1.0
    return round(weighted_sum / total_weight, 2)


def build_rankings(countries_data, registry_by_iso2, top_n=10):
    ranked = []
    for iso2, result in countries_data.items():
        if result.get("index") is None:
            continue
        ranked.append({
            "iso2": iso2,
            "name": registry_by_iso2.get(iso2, {}).get("name", iso2),
            "index": result["index"],
            "status": result.get("status", "STABLE"),
        })
    ranked.sort(key=lambda x: x["index"], reverse=True)
    return {
        "highest_threat": [r["iso2"] for r in ranked[:top_n]],
        "lowest_threat": [r["iso2"] for r in ranked[-top_n:]],
        "table": ranked,
    }
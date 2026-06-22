"""Build WTI country registry from REST Countries API."""

import json
import urllib.request
from pathlib import Path

TIER_A_ISO2 = {
    "AF", "AR", "AU", "BD", "BR", "CA", "CD", "CN", "CO", "DE", "DZ", "EG",
    "ET", "FR", "GB", "HT", "ID", "IN", "IQ", "IR", "IL", "IT", "JP", "KP",
    "KR", "LB", "MA", "MM", "MX", "NG", "PK", "PS", "RU", "SA", "SD", "SO",
    "SY", "TR", "TW", "UA", "US", "VE", "YE", "ZA",
}

TIER_B_ISO2 = {
    "AE", "AM", "AO", "AT", "AZ", "BE", "BG", "BH", "BO", "CH", "CI", "CL",
    "CM", "CR", "CY", "CZ", "DK", "DO", "EC", "EE", "ES", "FI", "GE", "GH",
    "GR", "GT", "HN", "HR", "HU", "IE", "IS", "JM", "JO", "KE", "KW", "KZ",
    "LT", "LU", "LV", "LY", "MT", "MY", "MZ", "NI", "NL", "NO", "NZ", "OM",
    "PA", "PE", "PH", "PL", "PT", "PY", "QA", "RO", "RW", "SE", "SG", "SI",
    "SK", "SN", "SV", "TH", "TN", "TT", "TZ", "UG", "UY", "UZ", "VN", "ZM",
    "ZW",
}


def fetch_countries():
    url = (
        "https://restcountries.com/v3.1/all"
        "?fields=cca2,name,region,subregion,population"
    )
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.loads(resp.read())


def assign_tier(iso2):
    if iso2 in TIER_A_ISO2:
        return "A"
    if iso2 in TIER_B_ISO2:
        return "B"
    return "C"


def main():
    raw = fetch_countries()
    out = []
    for entry in sorted(raw, key=lambda x: x["cca2"]):
        iso2 = entry["cca2"]
        out.append({
            "iso2": iso2,
            "name": entry["name"]["common"],
            "region": entry.get("region") or "Unknown",
            "subregion": entry.get("subregion") or "Unknown",
            "tier": assign_tier(iso2),
            "population": entry.get("population") or 1,
            "gdp_nominal_usd": 0,
            "importance_weight": 1.0,
        })
    path = Path("config/wti/countries.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(out)} countries to {path}")


if __name__ == "__main__":
    main()
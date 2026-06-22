# World Threat Index (WTI) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a global threat monitoring index for all 195 UN countries and 13 major geopolitical groups, using BNTI's proven LLM + deterministic scoring pipeline.

**Architecture:** Extract shared logic into `bnti_core/`, add `worldthreatindex.py` analyzer with sharded CI, publish `wti_data.json`, and serve a world-map dashboard at `wti/`.

**Tech Stack:** Python 3.11+, feedparser, requests, pandas, openrouter/free, GitHub Actions matrix, D3/TopoJSON, existing BNTI CSS.

## Global Constraints

- LLM model: `openrouter/free` only (with backup key failover)
- Category enum: identical to BNTI (`military_conflict` … `neutral`)
- Index range: 1.0–10.0 with STABLE/ELEVATED/CRITICAL thresholds
- Do not break existing BNTI pipeline or `bnti_data.json` publish path
- Zero additional infrastructure cost (GitHub Actions + Pages)

---

## Phase 1: Foundation — Country Registry & Shared Core

### Task 1: Country registry builder script

**Files:**
- Create: `scripts/build_country_registry.py`
- Create: `config/wti/countries.json`
- Test: `tests/wti/test_country_registry.py`

**Interfaces:**
- Produces: `config/wti/countries.json` — list of dicts with keys `iso2`, `name`, `region`, `subregion`, `tier`, `population`, `gdp_nominal_usd`, `importance_weight`

- [ ] **Step 1: Write the failing test**

```python
# tests/wti/test_country_registry.py
import json
from pathlib import Path

REGISTRY = Path("config/wti/countries.json")

def test_registry_has_195_un_members():
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    assert len(data) >= 193
    iso2_set = {c["iso2"] for c in data}
    assert len(iso2_set) == len(data)
    for required in ("US", "GB", "DE", "TR", "SY", "UA", "CN", "IN", "BR"):
        assert required in iso2_set

def test_every_country_has_tier():
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    for c in data:
        assert c["tier"] in ("A", "B", "C")
        assert c["population"] > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/wti/test_country_registry.py -v`  
Expected: FAIL — file not found

- [ ] **Step 3: Implement registry builder**

```python
# scripts/build_country_registry.py
"""Fetch UN member states from REST Countries API, assign tiers, write config."""
import json, urllib.request
from pathlib import Path

TIER_A_ISO2 = {
    "AR","AU","BR","CA","CN","FR","DE","IN","ID","IT","JP","MX","RU","SA",
    "ZA","KR","TR","GB","US","SY","UA","YE","SD","MM","AF","IQ","IR","IL",
    "PS","LB","PK","BD","NG","ET","CD","SO","HT","VE","CO","KP","TW","EG",
    "DZ","MA",
}

def fetch_countries():
    url = "https://restcountries.com/v3.1/all?fields=cca2,name,region,subregion,population"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read())

def assign_tier(iso2):
    if iso2 in TIER_A_ISO2:
        return "A"
    if iso2 in {"AT","BE","BG","HR","CY","CZ","DK","EE","FI","GR","HU","IE",
                "LV","LT","LU","MT","NL","PL","PT","RO","SK","SI","ES","SE",
                "CH","NO","IS","NZ","SG","MY","TH","VN","PH","CL","PE","EC",
                "KE","GH","TZ","UG","RW","SN","CI","CM","AO","MZ","ZW","ZM",
                "BO","PY","UY","CR","PA","GT","HN","NI","SV","DO","JM","TT",
                "BH","KW","OM","QA","AE","JO","AZ","GE","AM","KZ","UZ"}:
        return "B"
    return "C"

def main():
    raw = fetch_countries()
    out = []
    for c in sorted(raw, key=lambda x: x["cca2"]):
        iso2 = c["cca2"]
        out.append({
            "iso2": iso2,
            "name": c["name"]["common"],
            "region": c.get("region") or "Unknown",
            "subregion": c.get("subregion") or "Unknown",
            "tier": assign_tier(iso2),
            "population": c.get("population") or 1,
            "gdp_nominal_usd": 0,
            "importance_weight": 1.0,
        })
    path = Path("config/wti/countries.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(out)} countries to {path}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run builder and tests**

Run: `python scripts/build_country_registry.py && pytest tests/wti/test_country_registry.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add scripts/build_country_registry.py config/wti/countries.json tests/wti/test_country_registry.py
git commit -m "feat(wti): add 195-country registry builder"
```

---

### Task 2: Group definitions

**Files:**
- Create: `config/wti/groups.json`
- Test: `tests/wti/test_groups.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/wti/test_groups.py
import json
from pathlib import Path

GROUPS = Path("config/wti/groups.json")
REGISTRY = Path("config/wti/countries.json")

def test_required_groups_exist():
    groups = json.loads(GROUPS.read_text(encoding="utf-8"))
    ids = {g["id"] for g in groups}
    for req in ("oecd","g7","g20","eu","usmca","nato","asean","au","brics","gcc"):
        assert req in ids

def test_group_members_resolve_to_registry():
    groups = json.loads(GROUPS.read_text(encoding="utf-8"))
    iso2 = {c["iso2"] for c in json.loads(REGISTRY.read_text(encoding="utf-8"))}
    for g in groups:
        for m in g["members"]:
            assert m in iso2, f"{m} in {g['id']} not in registry"
```

- [ ] **Step 2: Run test — expect FAIL**

- [ ] **Step 3: Create groups.json** with all 13 groups and member ISO2 lists (G7: US,CA,FR,DE,IT,JP,GB; EU: 27 members; USMCA: US,MX,CA; etc.)

- [ ] **Step 4: Run tests — expect PASS**

- [ ] **Step 5: Commit** `feat(wti): add geopolitical group definitions`

---

### Task 3: Extract shared scoring module

**Files:**
- Create: `bnti_core/__init__.py`
- Create: `bnti_core/scoring.py`
- Test: `tests/wti/test_scoring.py`

- [ ] **Step 1: Write scoring parity test**

```python
# tests/wti/test_scoring.py
from bnti_core.scoring import category_weights, calculate_final_index, status_from_index

def test_weights_match_bnti():
    assert category_weights()["military_conflict"] == 8.0
    assert category_weights()["trade_agreement"] == -2.0

def test_index_formula():
    assert calculate_final_index(0) == 1.0
    assert 4.0 < calculate_final_index(2.5) < 5.0
    assert status_from_index(8.5) == "CRITICAL"
    assert status_from_index(3.0) == "STABLE"
```

- [ ] **Step 2: Run — expect FAIL**

- [ ] **Step 3: Implement scoring.py** by extracting `LLM_CATEGORY_WEIGHTS`, `calculate_final_index`, status logic from `borderneighboursthreatindex.py`

- [ ] **Step 4: Run — expect PASS**

- [ ] **Step 5: Commit** `refactor: extract bnti_core.scoring from BNTI analyzer`

---

## Phase 2: Global News Ingestion

### Task 4: Mirror URL generator per country

**Files:**
- Create: `bnti_core/ingestion.py`
- Test: `tests/wti/test_ingestion.py`

- [ ] **Step 1: Test mirror URL generation**

```python
def test_mirror_urls_for_country():
    from bnti_core.ingestion import build_mirror_urls
    urls = build_mirror_urls("Ukraine")
    assert len(urls) >= 4
    assert any("news.google.com" in u for u in urls)
    assert any("gdeltproject.org" in u for u in urls)
```

- [ ] **Step 2–5:** Implement `build_mirror_urls(country_name)` using BNTI's `_google_news_url` and `_gdelt_url` patterns; commit.

---

### Task 5: WTI analyzer skeleton with CLI

**Files:**
- Create: `worldthreatindex.py`
- Test: `tests/wti/test_cli.py`

- [ ] **Step 1: Test CLI args**

```python
def test_cli_dry_run(capsys):
    import subprocess, sys
    r = subprocess.run(
        [sys.executable, "worldthreatindex.py", "--dry-run", "--countries", "US,GB"],
        capture_output=True, text=True, timeout=120
    )
    assert r.returncode == 0
    assert "US" in r.stdout or "candidates" in r.stdout.lower()
```

- [ ] **Step 2–5:** Implement `WTIAnalyzer` class extending ingestion patterns from BNTI; `--dry-run`, `--countries`, `--shard`, `--tier` flags; commit.

---

## Phase 3: LLM Attribution at Scale

### Task 6: Global LLM prompt with region-scoped country list

**Files:**
- Modify: `bnti_core/llm.py`
- Test: `tests/wti/test_llm_payloads.py`

- [ ] **Step 1:** Copy and adapt `test_openrouter_payloads.py` patterns for WTI global prompt
- [ ] **Step 2:** Implement region-batched country list injection (max 50 countries per prompt)
- [ ] **Step 3:** Validate JSON schema: `{headline_id, primary_country_iso2, category}` per item
- [ ] **Step 4:** Run `pytest tests/wti/test_llm_payloads.py -v`
- [ ] **Step 5:** Commit

---

### Task 7: Block-level publish gate

**Files:**
- Create: `bnti_core/publish.py`
- Test: `tests/wti/test_publish_gate.py`

- [ ] **Step 1:** Test that invalid country block retains last-good snapshot
- [ ] **Step 2:** Implement `merge_country_block(existing, candidate)` with min 3 signals gate
- [ ] **Step 3:** Implement global coverage gate (≥85% tier-A, ≥70% overall)
- [ ] **Step 4:** Run tests
- [ ] **Step 5:** Commit

---

## Phase 4: Group Aggregation

### Task 8: Group and global composite scorer

**Files:**
- Create: `bnti_core/groups.py`
- Test: `tests/wti/test_group_scoring.py`

- [ ] **Step 1:** Fixture: 7 G7 country indices → expected weighted group index
- [ ] **Step 2:** Implement `compute_group_index(members, countries_data, weighting="gdp")`
- [ ] **Step 3:** Implement `compute_global_index(all_countries, weighting="population")`
- [ ] **Step 4:** Wire into `worldthreatindex.py` publish path → `wti_data.json`
- [ ] **Step 5:** Commit

---

## Phase 5: CI/CD

### Task 9: Matrix workflow and shard merge

**Files:**
- Create: `.github/workflows/wti_update.yml`
- Create: `scripts/merge_wti_shards.py`
- Test: `tests/wti/test_merge.py`

- [ ] **Step 1:** Test merge script with 3 fixture shard JSONs
- [ ] **Step 2:** Implement merge with gating
- [ ] **Step 3:** Create GHA workflow with `strategy.matrix.shard: [0..9]`
- [ ] **Step 4:** Manual `workflow_dispatch` test
- [ ] **Step 5:** Commit

---

## Phase 6: Dashboard

### Task 10: World map dashboard

**Files:**
- Create: `wti/index.html`
- Create: `wti/js/core.js`, `wti/js/map.js`, `wti/js/groups.js`
- Create: `wti/data/world-110m.json` (TopoJSON)

- [ ] **Step 1:** Scaffold HTML using BNTI CSS imports
- [ ] **Step 2:** Load `wti_data.js` and render global composite header
- [ ] **Step 3:** D3 choropleth colored by index (green/yellow/red)
- [ ] **Step 4:** Group tabs with index cards
- [ ] **Step 5:** Rankings table; commit

---

## Phase 7–8: Curation, Docs, Launch

### Task 11: Tier-A feed curation
- Add `config/wti/feeds/US.json`, `GB.json`, … for 45 tier-A countries
- Integrate into ingestion (curated + mirrors)

### Task 12: Coverage validator
- `scripts/validate_wti_coverage.py` — report % countries with valid index

### Task 13: Documentation
- Update README, DEPLOYMENT_GUIDE, methodology.tex with WTI chapter

---

## Self-Review Checklist

| Requirement | Task |
|-------------|------|
| R1 195 countries | Task 1 |
| R2 BNTI taxonomy | Task 3, 6 |
| R3 News ingestion | Task 4, 5, 11 |
| R4 Groups | Task 2, 8 |
| R5 Dashboard | Task 10 |
| R6 CI/CD | Task 9 |
| R7 Briefing | Task 8 (extend) |
| R8 History | Task 8 (extend) |
| N1 Block gating | Task 7 |
| N4 BNTI unaffected | Task 3 (extract only, no BNTI behavior change) |

---

## Execution Options

**Plan saved to:** `docs/superpowers/plans/2026-06-22-world-threat-index-implementation.md`

1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks
2. **GSD Autonomous** — `/gsd:automate` runs all 8 phases with discuss→plan→execute gates
3. **Inline Execution** — implement phases sequentially in this session

**Recommended next command after approval:**

```
/gsd:automate
```

or

```
/gsd:plan-phase 1
```
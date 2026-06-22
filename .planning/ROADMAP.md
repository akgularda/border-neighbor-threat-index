# WTI Roadmap

**Milestone:** v1.0 World Threat Index  
**Status:** v1.0 implemented — awaiting GitHub push + CI first run

---

## Phase 1: Foundation — Country Registry & Shared Core
**Goal:** Extract reusable BNTI engine; build 195-country registry with tiers and weights.

**Requirements:** R1 (partial), N4

**Deliverables:**
- `bnti_core/scoring.py` — category weights, index normalization, status mapping
- `bnti_core/feeds.py` — feed fetch, cache, mirror URL builders
- `bnti_core/llm.py` — OpenRouter batching, validation, failover
- `config/wti/countries.json` — 195 countries with ISO2, tier, population, GDP
- `config/wti/groups.json` — 13 group definitions with member ISO2 lists
- `scripts/build_country_registry.py` — generates registry from REST Countries API + World Bank
- Tests: registry integrity, group membership resolution

**Verification:** `pytest tests/wti/test_country_registry.py tests/wti/test_groups.py -v`

---

## Phase 2: Global News Ingestion
**Goal:** Fetch and deduplicate headlines for any country using universal mirror sources.

**Requirements:** R3, N1

**Deliverables:**
- `bnti_core/ingestion.py` — country-scoped feed processing
- `worldthreatindex.py` skeleton with `--countries` and `--shard` CLI
- Auto-generated mirror queries per country from registry
- Per-country candidate snapshot builder
- Tests: feed URL generation, dedup, 5-country dry-run ingestion

**Verification:** `python worldthreatindex.py --dry-run --countries US,GB,DE,FR,JP` produces candidates

---

## Phase 3: LLM Attribution at Scale
**Goal:** Batch LLM attribution for global country universe with region-scoped prompts.

**Requirements:** R2, N1

**Deliverables:**
- Global attribution prompts (region-batched country lists)
- Shard-aware processing (`--shard N --total-shards 10`)
- Block-level publish gate per country
- `test_wti_llm_payloads.py`, `test_wti_publish_gate.py`
- 10-country end-to-end scoring test

**Verification:** `pytest tests/wti/ -v` + dry-run produces valid `wti_shard_0.json`

---

## Phase 4: Group Aggregation & Global Composite
**Goal:** Compute group indices and world composite from country scores.

**Requirements:** R4, R7

**Deliverables:**
- Group scorer (GDP-weighted + equal-weight)
- Global population-weighted composite
- Rankings generator (top/bottom 10)
- 6-hour global briefing (adapt BNTI summary logic)
- `wti_data.json` / `wti_data.js` publisher
- `wti_history.csv` append logic

**Verification:** Group indices match hand-calculated fixtures for G7, EU samples

---

## Phase 5: CI/CD Matrix Pipeline
**Goal:** Automated tiered updates with shard merge.

**Requirements:** R6, N1, N2, N5

**Deliverables:**
- `.github/workflows/wti_update.yml` — matrix shards + merge job
- `scripts/merge_wti_shards.py` — artifact combiner with gating
- Tier A (2h), B (6h), C (12h) cron schedules
- Feed cache keyed per WTI namespace

**Verification:** Manual `workflow_dispatch` completes; `wti_data.json` updates on Pages

---

## Phase 6: World Dashboard
**Goal:** Interactive world map UI with country and group views.

**Requirements:** R5, R8, N3

**Deliverables:**
- `wti/index.html` — dashboard shell
- `wti/js/core.js`, `map.js`, `groups.js`, `rankings.js`
- TopoJSON world map with threat choropleth
- Group tab panel (OECD, G20, G7, EU, USMCA, NATO, ASEAN, AU, BRICS, etc.)
- Sortable rankings table
- Link from BNTI dashboard to WTI

**Verification:** Dashboard renders locally with published `wti_data.js`; map colors match indices

---

## Phase 7: Source Curation & QA Hardening
**Goal:** Expand curated feeds for tier-A countries; validate against external benchmarks.

**Requirements:** R3 (enhanced), N2

**Deliverables:**
- `config/wti/feeds/{iso2}.json` for tier-A countries (45 countries)
- `scripts/validate_wti_coverage.py` — coverage report
- `scripts/benchmark_wti.py` — ACLED/GDELT correlation check
- Methodology doc: `docs/wti-methodology.md`

**Verification:** ≥90% coverage; top-10 threat list correlates with ACLED hotspots

---

## Phase 8: Documentation & Launch
**Goal:** Ship v1.0 with deployment guide and whitepaper update.

**Deliverables:**
- README WTI section
- `DEPLOYMENT_GUIDE.md` WTI addendum
- `methodology.tex` WTI chapter
- GitHub Pages path: `/border-neighbor-threat-index/wti/`

**Verification:** Full autonomous run for 24h without manual intervention

---

## Dependency Graph

```
Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5
                                              └──► Phase 6
Phase 5 ──► Phase 7 ──► Phase 8
```

Phases 6 and 7 can run in parallel after Phase 5.
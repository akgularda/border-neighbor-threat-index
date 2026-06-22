# World Threat Index (WTI) — Design Specification

**Date:** 2026-06-22  
**Status:** Draft — awaiting approval before implementation  
**Parent project:** [Border Neighbor Threat Index (BNTI)](https://github.com/akgularda/border-neighbor-threat-index)

---

## 1. Purpose

Build a **World Threat Index (WTI)** that applies the proven BNTI methodology — multilingual news ingestion, LLM country attribution + canonical threat labeling, deterministic weight mapping, saturating normalization, and gated publication — to **every UN-recognized sovereign state** (~195 countries), plus **aggregated regional/economic groups** (OECD, G20, G7, EU, USMCA, NATO, ASEAN, AU, BRICS, GCC, and others).

WTI answers: *"What is the current threat pressure inside each country and each major bloc, based on observable news events?"*

It is **not** a border-neighbor lens (that remains BNTI's niche). WTI scores each country on its own domestic and directly-attributed threat environment.

---

## 2. Design Principles (inherited from BNTI)

| Principle | WTI application |
|-----------|-----------------|
| LLM owns semantics | Country + category attribution via `openrouter/free` |
| Deterministic scoring | Same 8-category enum and fixed weights as BNTI |
| No partial corrupt publish | Per-country blocks validate independently; global snapshot merges only validated blocks |
| Saturating 1–10 scale | Reuse `calculate_final_index()` exponential normalization |
| Operational tiers | STABLE (1–4), ELEVATED (4–7), CRITICAL (7–10) |
| Zero-cost ops | GitHub Actions + GitHub Pages, same as BNTI |

---

## 3. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     GitHub Actions (scheduled)                   │
│  wti_update.yml — tiered cron, matrix shards, artifact merge    │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Feed Ingestion │ │  LLM Attribution│ │  Group Aggregate│
│  (per country)  │ │  (batched)      │ │  (post-score)   │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             ▼
                  ┌─────────────────────┐
                  │  wti_data.json/.js  │
                  │  wti_history.csv    │
                  └──────────┬──────────┘
                             ▼
                  ┌─────────────────────┐
                  │  WTI Dashboard      │
                  │  (world map + tabs) │
                  └─────────────────────┘
```

### 3.1 Recommended approach: Extend BNTI repo (not fork)

**Why:** Reuse `borderneighboursthreatindex.py` patterns, CSS, CI secrets, and deployment. Add a parallel `worldthreatindex.py` + `wti/` dashboard. Extract shared logic into `bnti_core/` in Phase 1.

**Alternatives considered:**

| Approach | Pros | Cons |
|----------|------|------|
| **A. Monorepo extension (recommended)** | Shared CI, design system, one deployment | Larger repo |
| B. Separate repo | Clean isolation | Duplicate CI, drift risk |
| C. Library-only core + two products | Best long-term | Highest upfront refactor |

---

## 4. Country Universe

### 4.1 Coverage target

- **195 UN member states** (ISO 3166-1 alpha-2 canonical keys)
- **2 observer states** (Palestine, Vatican) — optional Phase 8
- Taiwan scored as separate entity with `TW` code (news-attributed, documented caveat)

### 4.2 Country registry (`config/wti/countries.json`)

Each entry:

```json
{
  "iso2": "TR",
  "name": "Türkiye",
  "region": "Western Asia",
  "subregion": "Middle East",
  "tier": "A",
  "population": 85300000,
  "gdp_nominal_usd": 1100000000000,
  "importance_weight": 1.2
}
```

**Tiers** (controls refresh cadence and LLM budget):

| Tier | Countries | Refresh | Rationale |
|------|-----------|---------|-----------|
| A | G20 + top conflict states (~45) | Every 2h | High global salience |
| B | Remaining OECD + regional powers (~60) | Every 6h | Medium salience |
| C | All others (~90) | Every 12h | Coverage completeness |

---

## 5. News Sources Strategy

### 5.1 Universal baseline (all countries)

Every country gets **mirror sources** (same pattern as BNTI `mirror_queries`):

1. **Google News RSS** — neutral, debiased queries:
   - `"{Country} news today"`
   - `"{Country} politics"`
   - `"{Country} security"`
   - `"{Country} economy"`

2. **GDELT DOC API** — `mode=artlist`, `maxrecords=25`, same queries

These require **no per-country feed curation** and work on day one for all 195 states.

### 5.2 Curated feeds (progressive enhancement)

`config/wti/feeds/{iso2}.json` — optional native-language RSS per country. Seed list:

- **Tier A countries:** 3–8 curated feeds each (Phase 8 expansion)
- **Conflict hotspots:** Syria, Ukraine, Sudan, Yemen, Myanmar, DRC, etc. — priority curation

### 5.3 External reference indices (validation only, not scoring input)

Use for sanity-checking WTI outputs during development:

| Source | Use |
|--------|-----|
| [ACLED](https://acleddata.com/) | Conflict event density benchmark |
| [GDELT GKG](https://www.gdeltproject.org/) | Volume/tonality cross-check |
| [Fragile States Index](https://fragilestatesindex.org/) | Annual structural risk reference |
| [Global Peace Index](https://www.visionofhumanity.org/maps/) | Annual peace ranking reference |
| [Caldara-Iacoviello GPR](https://www.matteoiacoviello.com/gpr.htm) | Geopolitical risk macro index |

WTI remains **news-event-driven**; these are evaluation baselines only.

---

## 6. LLM Attribution Model

### 6.1 Category enum (unchanged from BNTI)

```
military_conflict      →  8.0
terrorism              →  7.0
border_security        →  5.0
political_instability  →  4.0
humanitarian_crisis    →  3.0
diplomatic_tensions    →  2.5
trade_agreement        → -2.0
neutral                →  0.0
```

### 6.2 Country attribution prompt changes

- Universe = full ISO country list (batched by region to keep prompt size manageable)
- Headline must be **direct main subject** of the named country (not merely "mentioned")
- Cross-border events: attribute to country where the **primary event occurs**
- `IRRELEVANT` for global/generic stories with no country-specific threat signal

### 6.3 Scale strategy

| Constraint | Mitigation |
|------------|------------|
| ~195 countries × 15 headlines × LLM batches | Matrix CI: 10 shards × ~20 countries |
| `openrouter/free` rate limits | Primary + backup keys; exponential backoff |
| 2h full-world refresh impractical | Tiered scheduling (see §4.2) |
| Prompt size | Region-scoped country lists per shard |

**Estimated LLM calls per full cycle:** ~300–500 batched requests (10 headlines/batch), spread across shards.

---

## 7. Scoring & Group Aggregation

### 7.1 Per-country score (same as BNTI)

1. Collect attributed events \(E_k\) for country \(k\)
2. Raw score: \(\bar{T}_k = \frac{1}{|E_k|} \sum_{i \in E_k} W_{c(i)}\)
3. Index: \(I_k = 1 + 9 \cdot (1 - e^{-\bar{T}_k/5 \cdot 1.2})\)
4. Status from thresholds

### 7.2 Global composite index

Population-weighted average across all countries with valid snapshots:

\[
I_{\text{WTI}} = \frac{\sum_k p_k \cdot I_k}{\sum_k p_k}
\]

where \(p_k\) = population weight (World Bank 2024 data).

### 7.3 Regional group scores

Defined in `config/wti/groups.json`:

| Group | ID | Members | Notes |
|-------|-----|---------|-------|
| OECD | `oecd` | 38 members | Economic cooperation |
| G7 | `g7` | 7 | Canada, France, Germany, Italy, Japan, UK, US |
| G20 | `g20` | 19 + EU | Major economies |
| European Union | `eu` | 27 | Post-Brexit membership |
| USMCA | `usmca` | US, Mexico, Canada | Former NAFTA |
| NATO | `nato` | 32 | Military alliance |
| ASEAN | `asean` | 10 | Southeast Asia |
| African Union | `au` | 55 | All AU members |
| BRICS | `brics` | 10+ (2025 expansion) | Brazil, Russia, India, China, SA, UAE, Egypt, Ethiopia, Iran, Indonesia |
| GCC | `gcc` | 6 | Gulf states |
| CIS | `cis` | 9 | Post-Soviet bloc |
| MERCOSUR | `mercosur` | 4 full + associates | South America |
| SCO | `sco` | 10 | Shanghai Cooperation |

**Group index formula:**

```
I_group = Σ(w_i × I_i) / Σ(w_i)
```

where \(w_i\) = GDP nominal weight by default; also expose **equal-weight** variant in dashboard.

**Group status:** Same STABLE/ELEVATED/CRITICAL thresholds on group index.

---

## 8. Data Schema (`wti_data.json`)

```json
{
  "meta": {
    "generated_at": "ISO8601",
    "main_index": 3.82,
    "status": "STABLE",
    "countries_total": 195,
    "countries_active": 178,
    "coverage_ratio": 0.91,
    "version": "1.0.0",
    "next_update": "ISO8601"
  },
  "countries": {
    "US": { "name": "United States", "index": 2.1, "raw_score": 0.8, "status": "STABLE", "events": [...] },
    "SY": { "name": "Syria", "index": 8.4, "raw_score": 6.2, "status": "CRITICAL", "events": [...] }
  },
  "groups": {
    "g7": { "name": "G7", "index": 2.8, "status": "STABLE", "member_count": 7, "members": ["US", "GB", ...] },
    "eu": { "name": "European Union", "index": 3.1, "status": "STABLE", "member_count": 27 }
  },
  "rankings": {
    "highest_threat": ["SY", "SD", "YE", "MM", "UA"],
    "lowest_threat": ["IS", "SG", "CH", "NO", "JP"]
  },
  "history": [...],
  "regional_summary": { "window_hours": 6, "text": "...", "generated_at": "..." }
}
```

---

## 9. Publication Gates (adapted for global scale)

BNTI's all-or-nothing gate does not scale to 195 countries. WTI uses **block-level gating**:

| Gate | Rule |
|------|------|
| Per-country | ≥3 attributed signals OR retain last-good country block |
| Per-shard | All LLM batches in shard must validate |
| Global snapshot | ≥85% tier-A coverage AND ≥70% overall coverage to update `meta.main_index` |
| Stale country | If country block >24h old, mark `stale: true` in UI |
| Summary | 6-hour global briefing required for full publish (reuse BNTI pattern) |

---

## 10. Dashboard (WTI)

### 10.1 Pages

- `/wti/` or `wti/index.html` — main world dashboard
- BNTI dashboard remains at `/` (unchanged)

### 10.2 Components

| Component | Implementation |
|-----------|----------------|
| World choropleth map | TopoJSON (Natural Earth 110m) + D3 or reuse Leaflet |
| Country detail panel | Click country → events, index, trend |
| Group tabs | OECD, G20, G7, EU, USMCA, NATO, ASEAN, AU, BRICS |
| Rankings table | Sortable by index, region, tier |
| Global composite | Header metric (like BNTI main index) |
| 6H briefing | Global (not border-focused) summary |
| Search/filter | By country name, ISO code, region, status |

### 10.3 Visual system

Reuse BNTI CSS (`variables.css`, `layout.css`, `components.css`) for brand consistency.

---

## 11. CI/CD

### 11.1 Workflow: `.github/workflows/wti_update.yml`

```yaml
# Tier A: cron '0 */2 * * *'
# Tier B: cron '0 */6 * * *'  
# Tier C: cron '0 */12 * * *'
# strategy.matrix.shard: [0,1,2,3,4,5,6,7,8,9]
```

Steps per shard:
1. Run `worldthreatindex.py --shard N --total-shards 10 --tier A`
2. Upload `wti_shard_N.json` artifact
3. Merge job combines shards → validates → writes `wti_data.json`
4. Deploy to GitHub Pages

### 11.2 Secrets

Same as BNTI: `OPENROUTER_API_KEY`, `OPENROUTER_API_KEY_BACKUP`

---

## 12. Testing Strategy

| Test | Purpose |
|------|---------|
| `test_wti_country_registry.py` | 195 countries, valid ISO2, no duplicates |
| `test_wti_groups.py` | Group memberships resolve to registry |
| `test_wti_scoring.py` | Scoring parity with BNTI formula |
| `test_wti_publish_gate.py` | Block-level gating logic |
| `test_wti_llm_payloads.py` | Prompt structure for global attribution |
| `test_wti_merge.py` | Shard artifact merge |
| Integration dry-run | `--dry-run --countries US,GB,SY,UA,CN` |

---

## 13. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| LLM cost/time at 195-country scale | Tiered scheduling + matrix sharding |
| Sparse news for small states | GDELT fallback; mark low-confidence |
| Country name ambiguity (Georgia US vs country) | ISO2 in LLM output; disambiguation in prompt |
| Group membership changes (BRICS expansion) | Versioned `groups.json` with `as_of` date |
| Feed blocking in CI | Same cache + proxy fallback as BNTI |
| Free model quality | Strict JSON validation; no-publish on failure |

---

## 14. Success Criteria

1. **Coverage:** ≥90% of 195 countries have a valid index after first 24h run
2. **Accuracy:** Top-10 highest-threat countries align with ACLED/GDELT conflict hotspots (±3 ranks)
3. **Groups:** All 13 defined groups compute and display correctly
4. **Automation:** GitHub Actions runs unattended; dashboard updates on schedule
5. **Stability:** Failed shard does not corrupt existing snapshot
6. **Performance:** Full tier-A cycle completes within 45 minutes

---

## 15. Out of Scope (v1)

- User accounts / alerts
- Historical backfill before launch date
- Sub-national (city/province) scoring
- Predictive forecasting beyond BNTI's simple trend line
- Paid LLM tiers

---

## 16. Approval

This spec must be approved before `/gsd:automate` or implementation begins.

**Next step after approval:** Execute Phase 1 from `.planning/ROADMAP.md`.
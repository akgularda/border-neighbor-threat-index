# WTI Requirements

## Functional

- [R1] Score all 195 UN member states on 1–10 threat index
- [R2] Use same 8-category LLM threat taxonomy as BNTI
- [R3] Ingest news via Google News RSS + GDELT for every country (day-one coverage)
- [R4] Compute aggregated indices for: OECD, G7, G20, EU, USMCA, NATO, ASEAN, AU, BRICS, GCC, CIS, MERCOSUR, SCO
- [R5] Display interactive world map dashboard with country + group views
- [R6] Automated tiered updates via GitHub Actions (2h/6h/12h by country tier)
- [R7] Global 6-hour briefing summary
- [R8] Historical trend tracking (`wti_history.csv`)

## Non-Functional

- [N1] Block-level publish gating — failed country shard must not corrupt snapshot
- [N2] ≥90% country coverage within 24h of first production run
- [N3] Reuse BNTI visual design system
- [N4] BNTI production pipeline unaffected
- [N5] All tests pass in CI before merge

## Data Sources (minimum)

- Google News RSS (per-country neutral queries)
- GDELT DOC API (per-country queries)
- World Bank population/GDP for weighting
- Optional curated RSS per country (progressive)

## Validation References

- ACLED conflict data (dev/QA benchmark)
- GDELT event volume (cross-check)
- Fragile States Index (annual sanity check)
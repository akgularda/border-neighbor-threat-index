# World Threat Index (WTI) Methodology

WTI applies the BNTI production pipeline globally:

1. **Ingestion** — Google News RSS mirrors per country (optional GDELT via `WTI_INCLUDE_GDELT=true`)
2. **Attribution** — `openrouter/free` assigns ISO2 country + canonical threat category
3. **Scoring** — Deterministic BNTI weights → per-country 1–10 index
4. **Aggregation** — Population-weighted global composite; GDP-weighted group indices
5. **Publication** — Block-level gating; shard merge via GitHub Actions

## Groups

OECD, G7, G20, EU, USMCA, NATO, ASEAN, African Union, BRICS, GCC, CIS, MERCOSUR, SCO.

## Thresholds

| Status | Range |
|--------|-------|
| STABLE | 1.0 – 4.0 |
| ELEVATED | 4.0 – 7.0 |
| CRITICAL | 7.0 – 10.0 |

## Scale

195 UN member states + Taiwan (`TW`), tiered refresh (A: 2h, B: 6h, C: 12h).
# World Threat Index (WTI)

## What

Extend the Border Neighbor Threat Index (BNTI) into a **World Threat Index** covering all ~195 UN member states and major geopolitical groups (OECD, G20, G7, EU, USMCA, NATO, ASEAN, AU, BRICS, GCC, CIS, MERCOSUR, SCO).

## Why

BNTI proves the pipeline works for Türkiye's border environment. WTI generalizes the same methodology globally for defense intelligence, journalism, and research use cases.

## Core Constraints

- Model: `openrouter/free` only
- Scoring: deterministic weights (BNTI enum)
- Deployment: GitHub Actions + GitHub Pages (zero cost)
- Publication: gated — no corrupt snapshots
- BNTI dashboard must remain unaffected

## Repository

https://github.com/akgularda/border-neighbor-threat-index

## Key Artifacts

| Artifact | Path |
|----------|------|
| Design spec | `docs/superpowers/specs/2026-06-22-world-threat-index-design.md` |
| Implementation plan | `docs/superpowers/plans/2026-06-22-world-threat-index-implementation.md` |
| Country registry | `config/wti/countries.json` |
| Group definitions | `config/wti/groups.json` |
| Analyzer | `worldthreatindex.py` |
| Dashboard data | `wti_data.json`, `wti_data.js` |
| Dashboard UI | `wti/index.html`, `wti/js/` |

## Owner

Monarch Castle Technologies | Arda Akgul
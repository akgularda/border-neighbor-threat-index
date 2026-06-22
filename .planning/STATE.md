# WTI State

**Last updated:** 2026-06-22  
**Current phase:** 8 (Complete — v1.0 scaffold shipped)  
**Next action:** Push to GitHub; enable `wti_update.yml` with OpenRouter secrets

## Completed

- [x] Phase 1: `bnti_core/`, 195-country registry, 13 groups
- [x] Phase 2: `worldthreatindex.py`, mirror ingestion
- [x] Phase 3: LLM prompts, block-level publish gates
- [x] Phase 4: Group aggregation, `wti_data.json` publisher
- [x] Phase 5: `.github/workflows/wti_update.yml`, shard merge
- [x] Phase 6: `wti/` dashboard (map, groups, rankings)
- [x] Phase 7: `validate_wti_coverage.py`, `docs/wti-methodology.md`
- [x] Phase 8: README, BNTI↔WTI links
- [x] 15/15 unit tests passing
- [x] Dry-run verified (7 countries → global index 2.6)

## Pending (production)

- [ ] Push commits to `akgularda/border-neighbor-threat-index`
- [ ] Full 195-country run via GitHub Actions (needs OpenRouter secrets)
- [ ] Tier-A curated feeds expansion (`config/wti/feeds/`)

## Blockers

None for local development. Production full coverage requires CI secrets + first scheduled run.
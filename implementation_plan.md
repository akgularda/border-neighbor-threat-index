# BNTI LLM Automation Plan

## Approved Direction

This repository should move to a professional, automated pipeline with these rules:

- `openrouter/free` remains the only model tier
- the workflow runs every `2` hours
- the LLM is authoritative for both final `country` and final `category`
- category choice must come from a controlled enum such as:
  - `military_conflict`
  - `terrorism`
  - `border_security`
  - `political_instability`
  - `humanitarian_crisis`
  - `diplomatic_tensions`
  - `trade_agreement`
  - `neutral`
- numeric scoring stays deterministic by mapping the chosen LLM category to a fixed weight
- primary and backup OpenRouter keys are used automatically
- if a run cannot fully validate, the workflow exits successfully but does not publish new public data
- partial publish is not allowed

## Production Behavior

1. Fetch and deduplicate candidate headlines from all configured feeds.
2. Batch headlines into small chunks for `openrouter/free`.
3. Ask the LLM to choose:
   - direct border-neighbor country attribution
   - one canonical threat category
4. Validate every batch response strictly.
5. Build a full candidate snapshot only if all batches succeed.
6. Publish `bnti_data.json` and `bnti_data.js` only after the full candidate passes validation.
7. If anything fails, keep the currently published snapshot unchanged.

## What This Replaces

The old plan is no longer acceptable because it depends on:

- RSS source country as implicit attribution
- XLM-RoBERTa as an authoritative production classifier
- single giant LLM calls
- permissive fallback behavior that can leak bad labels into the public dashboard

## Detailed Documents

Use these as the current source of truth:

- Design: `docs/plans/2026-03-27-bnti-free-llm-automation-design.md`
- Implementation: `docs/plans/2026-03-27-bnti-free-llm-automation-implementation.md`

## Next Step

Execute the implementation plan in order:

1. add tests for LLM-only attribution and publish gating
2. replace the legacy taxonomy with the LLM-owned enum
3. remove XLM-RoBERTa from the authoritative scoring path
4. add batched OpenRouter failover logic
5. gate publishing on full candidate validation
6. update GitHub Actions to a 2-hour schedule with both secrets
7. verify end to end with dry-run and snapshot checks

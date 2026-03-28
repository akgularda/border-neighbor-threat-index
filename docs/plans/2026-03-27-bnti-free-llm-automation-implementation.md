# BNTI Free LLM Automation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the current mixed RSS/XLM/LLM flow with a production-safe `openrouter/free` pipeline that lets the LLM choose final country and category, runs every 2 hours, auto-fails over to a backup key, and never overwrites public data on a bad run.

**Architecture:** Fetch and deduplicate RSS headlines first, then batch them through `openrouter/free` for final country and category labeling using a strict canonical enum. Build a complete candidate snapshot in memory, validate every batch and the final result, and only then promote the candidate to the public files; otherwise exit successfully without publishing.

**Tech Stack:** Python 3.11, `requests`, existing RSS/feed pipeline, GitHub Actions, OpenRouter Chat Completions API, `unittest`.

---

### Task 1: Add failing tests for LLM-only attribution orchestration

**Files:**
- Modify: `test_openrouter_payloads.py`
- Create: `test_llm_publish_gate.py`
- Modify: `test_reattribution.py`

**Step 1: Write the failing test**

Add tests that assert:

- batching uses global ids across chunks
- `openrouter/free` is called in chunks, not one giant batch
- provider responses that reject `reasoning: none` are retried without the `reasoning` field
- if any batch fails after primary+backup attempts, the publish gate returns `invalid`
- the parser does not add country overrides from keyword heuristics

Example test skeleton:

```python
def test_publish_gate_rejects_partial_batch_success():
    result = build_candidate_from_batches(
        total_events=25,
        batch_results=[
            {"ok": True, "items": [...]},
            {"ok": False, "items": []},
        ],
    )
    assert result.valid is False
    assert result.publishable is False
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest test_openrouter_payloads.py test_llm_publish_gate.py`

Expected: FAIL because the current code still lacks the full candidate/publish gate and still mixes old scoring assumptions.

**Step 3: Write minimal implementation**

No implementation yet. Stop after the tests exist and fail.

**Step 4: Run test to verify it still fails for the right reason**

Run: `python -m unittest test_openrouter_payloads.py test_llm_publish_gate.py`

Expected: FAIL on missing orchestration / publish gate behavior, not on syntax errors.

**Step 5: Commit**

If this workspace is attached to git:

```bash
git add test_openrouter_payloads.py test_llm_publish_gate.py test_reattribution.py
git commit -m "test: add failing tests for llm publish gate"
```

### Task 2: Replace the scoring taxonomy with an LLM-owned category enum

**Files:**
- Modify: `borderneighboursthreatindex.py`
- Modify: `README.md`

**Step 1: Write the failing test**

Add tests for the canonical LLM taxonomy:

```python
def test_category_scores_use_llm_enum():
    weights = build_llm_category_weights()
    assert weights["military_conflict"] == 8.0
    assert weights["terrorism"] == 7.0
    assert weights["trade_agreement"] == -2.0
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest test_llm_publish_gate.py -v`

Expected: FAIL because the old `category_weights` still use the legacy XLM labels.

**Step 3: Write minimal implementation**

In `borderneighboursthreatindex.py`:

- replace the legacy category table near `category_weights`
- define the canonical LLM enum in snake_case
- stop treating XLM confidence as part of the final score
- compute event weight directly from the validated LLM label score

Implementation target:

```python
self.category_weights = {
    "military_conflict": 8.0,
    "terrorism": 7.0,
    "border_security": 5.0,
    "political_instability": 4.0,
    "humanitarian_crisis": 3.0,
    "diplomatic_tensions": 2.5,
    "trade_agreement": -2.0,
    "neutral": 0.0,
}
```

**Step 4: Run test to verify it passes**

Run: `python -m unittest test_llm_publish_gate.py -v`

Expected: PASS for taxonomy tests.

**Step 5: Commit**

```bash
git add borderneighboursthreatindex.py README.md test_llm_publish_gate.py
git commit -m "refactor: adopt llm-owned threat taxonomy"
```

### Task 3: Remove XLM-RoBERTa from the authoritative scoring path

**Files:**
- Modify: `borderneighboursthreatindex.py:539`
- Modify: `borderneighboursthreatindex.py:581`
- Modify: `borderneighboursthreatindex.py:1227`

**Step 1: Write the failing test**

Add tests that `process_country()` returns cleaned candidate events without final category/weight decisions, and that final scoring happens after the LLM step.

Example:

```python
def test_process_country_returns_unscored_candidates():
    country, candidates = process_country(...)
    assert "title" in candidates[0]
    assert "category" not in candidates[0] or candidates[0]["category"] is None
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest test_llm_publish_gate.py -v`

Expected: FAIL because `process_country()` currently bakes in XLM labels and weights.

**Step 3: Write minimal implementation**

Refactor:

- `process_country()` should fetch, dedupe, and return headline candidates
- `analyze_news()` should no longer be the production scorer
- `run()` should aggregate raw candidate events across countries, then call the LLM attribution stage, then score from validated LLM categories only

**Step 4: Run test to verify it passes**

Run: `python -m unittest test_llm_publish_gate.py -v`

Expected: PASS for unscored-candidate expectations.

**Step 5: Commit**

```bash
git add borderneighboursthreatindex.py test_llm_publish_gate.py
git commit -m "refactor: make llm the final scoring source"
```

### Task 4: Implement batched OpenRouter attribution with primary and backup keys

**Files:**
- Modify: `borderneighboursthreatindex.py:926`
- Modify: `borderneighboursthreatindex.py:972`
- Modify: `test_reattribution.py`
- Modify: `test_openrouter_payloads.py`

**Step 1: Write the failing test**

Add tests that:

- batches are size `10`
- global ids remain stable across batches
- primary key is tried first
- backup key is used automatically on rate-limit or auth/provider failure
- `openrouter/free` requests are retried without `reasoning` when needed

**Step 2: Run test to verify it fails**

Run: `python -m unittest test_openrouter_payloads.py test_llm_publish_gate.py`

Expected: FAIL on missing backup-key failover and incomplete batch orchestration.

**Step 3: Write minimal implementation**

In `_call_openrouter()`:

- accept an API key argument or a key sequence
- try primary key first, then backup key
- retry on `429`
- retry without `reasoning` only when provider requires it

In `reattribute_countries()`:

- iterate `all_events` in batches of `10`
- merge all valid batch responses into one attribution map
- treat any failed batch as a run-level invalid state

**Step 4: Run test to verify it passes**

Run: `python -m unittest test_openrouter_payloads.py test_llm_publish_gate.py`

Expected: PASS.

**Step 5: Commit**

```bash
git add borderneighboursthreatindex.py test_openrouter_payloads.py test_reattribution.py test_llm_publish_gate.py
git commit -m "feat: add batched openrouter failover pipeline"
```

### Task 5: Add candidate snapshot validation and no-publish gating

**Files:**
- Modify: `borderneighboursthreatindex.py:858`
- Modify: `borderneighboursthreatindex.py:1106`
- Modify: `borderneighboursthreatindex.py:1227`
- Create: `test_candidate_snapshot_gate.py`

**Step 1: Write the failing test**

Add tests for:

- candidate snapshot is publishable only when all batches succeed
- failed batches do not overwrite `bnti_data.json/js`
- bad candidate runs do not append to `bnti_history.csv`
- successful candidate runs promote atomically

Example:

```python
def test_failed_candidate_does_not_replace_live_snapshot(tmp_path):
    write_live_snapshot(tmp_path, old_data)
    publish_candidate(tmp_path, candidate=None, publishable=False)
    assert read_live_snapshot(tmp_path) == old_data
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest test_candidate_snapshot_gate.py -v`

Expected: FAIL because the current code writes live snapshot files during intermediate states.

**Step 3: Write minimal implementation**

Refactor `run()` and snapshot writing so that:

- intermediate progress snapshots are optional or written separately in-memory only
- final publish uses temporary candidate files
- live files are replaced only after all validation passes
- invalid runs return success without file promotion

**Step 4: Run test to verify it passes**

Run: `python -m unittest test_candidate_snapshot_gate.py -v`

Expected: PASS.

**Step 5: Commit**

```bash
git add borderneighboursthreatindex.py test_candidate_snapshot_gate.py
git commit -m "feat: gate public snapshot promotion on complete llm success"
```

### Task 6: Update GitHub Actions for 2-hour cadence and key failover

**Files:**
- Modify: `.github/workflows/bnti_update.yml`
- Modify: `DEPLOYMENT_GUIDE.md`

**Step 1: Write the failing test**

If workflow tests are not practical, write a simple configuration assertion script:

```python
def test_workflow_schedule_and_env():
    workflow = Path(".github/workflows/bnti_update.yml").read_text()
    assert "0 */2 * * *" in workflow
    assert "OPENROUTER_API_KEY_BACKUP" in workflow
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest test_candidate_snapshot_gate.py -v`

Expected: FAIL because the workflow is still hourly and has only one key.

**Step 3: Write minimal implementation**

Update workflow:

- change cron to `0 */2 * * *`
- inject both `OPENROUTER_API_KEY` and `OPENROUTER_API_KEY_BACKUP`
- keep workflow exit success behavior
- commit and deploy only if public files changed

**Step 4: Run test to verify it passes**

Run: `python -m unittest test_candidate_snapshot_gate.py -v`

Expected: PASS for workflow assertions.

**Step 5: Commit**

```bash
git add .github/workflows/bnti_update.yml DEPLOYMENT_GUIDE.md test_candidate_snapshot_gate.py
git commit -m "ci: run bnti every 2 hours with openrouter key failover"
```

### Task 7: End-to-end verification

**Files:**
- Modify: `test_reattribution.py`
- Modify: `README.md`

**Step 1: Write the failing test**

Add a deterministic verification check that known non-border headlines are excluded from the final country buckets.

Example:

```python
def test_non_border_examples_are_not_published():
    assert "UNIFIL calls for halt to military escalation in Southern Lebanon" not in published_iran_titles
    assert "Drone attacks near Baghdad airport raise security concerns" in published_iraq_titles
```

**Step 2: Run test to verify it fails**

Run: `python -m unittest test_reattribution.py -v`

Expected: FAIL against the old snapshot behavior.

**Step 3: Write minimal implementation**

Update the dry-run helper so it mirrors the production batch logic exactly:

- same prompt
- same batch size
- same failover logic
- same validation rules

**Step 4: Run test to verify it passes**

Run:

```bash
python -m unittest test_openrouter_payloads.py test_llm_publish_gate.py test_candidate_snapshot_gate.py -v
python -m py_compile borderneighboursthreatindex.py test_reattribution.py test_openrouter_payloads.py test_llm_publish_gate.py test_candidate_snapshot_gate.py
```

Then run a live dry-run:

```bash
set OPENROUTER_API_KEY=...
set OPENROUTER_API_KEY_BACKUP=...
python -u test_reattribution.py
```

Expected:

- all batches validated or the run reports no-publish
- no Lebanon-only / West-Bank-only / Jordan-Egypt-only headlines inside Iran, Iraq, or Syria
- `bnti_data.json/js` only replaced when the full candidate is valid

**Step 5: Commit**

```bash
git add README.md test_reattribution.py
git commit -m "docs: align dry-run verification with production llm flow"
```

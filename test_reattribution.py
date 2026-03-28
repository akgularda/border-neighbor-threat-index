"""
BNTI local dry-run for OpenRouter attribution.
Uses the same prompt, parser, and key-failover behavior as production.
"""

import json
import logging
import os
import time
import requests

import borderneighboursthreatindex as analyzer_module


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
BACKUP_API_KEY = os.environ.get("OPENROUTER_API_KEY_BACKUP", "")
MODEL = os.environ.get("OPENROUTER_MODEL", "openrouter/free")
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
BATCH_SIZE = 10
BORDER_COUNTRIES = list(analyzer_module.BNTIAnalyzer.BORDER_COUNTRIES)
CATEGORY_WEIGHTS = dict(analyzer_module.BNTIAnalyzer.LLM_CATEGORY_WEIGHTS)

OUT = []


def log(msg):
    OUT.append(msg)
    print(msg)


def build_helper():
    analyzer = object.__new__(analyzer_module.BNTIAnalyzer)
    analyzer.openrouter_api_key = API_KEY
    analyzer.openrouter_backup_api_key = BACKUP_API_KEY
    analyzer.openrouter_model = MODEL
    analyzer.openrouter_base_url = BASE_URL
    analyzer.openrouter_batch_size = BATCH_SIZE
    analyzer.border_countries = list(BORDER_COUNTRIES)
    analyzer.category_weights = dict(CATEGORY_WEIGHTS)
    analyzer.translator = analyzer_module.Translator()
    return analyzer


def check_api_limits():
    try:
        resp = requests.get(
            "https://openrouter.ai/api/v1/key",
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json().get("data", {})
        log("=" * 60)
        log("OPENROUTER API KEY STATUS")
        log("=" * 60)
        log(f"  Free tier:       {data.get('is_free_tier', 'N/A')}")
        log(f"  Credit limit:    {data.get('limit', 'unlimited')}")
        log(f"  Remaining:       {data.get('limit_remaining', 'unlimited')}")
        log(f"  Usage (today):   ${data.get('usage_daily', 0):.6f}")
        log(f"  Usage (total):   ${data.get('usage', 0):.6f}")
        log("=" * 60)
    except Exception as e:
        log(f"Could not check API limits: {e}")


def call_openrouter(prompt, max_retries=2):
    log(f"Calling OpenRouter ({MODEL})...")
    start = time.time()
    response = build_helper()._call_openrouter(prompt, max_retries=max_retries)
    elapsed = time.time() - start
    if response:
        log(f"Response received in {elapsed:.1f}s")
    return response


def build_prompt(all_events, start_index=0):
    return build_helper()._build_attribution_prompt(all_events, start_index=start_index)


def parse_response(response_text, all_events, start_index=0):
    return build_helper()._parse_attribution_response(response_text, all_events, start_index=start_index)


def build_country_audit_prompt(all_events, attribution_map, start_index=0):
    return build_helper()._build_country_audit_prompt(
        all_events,
        attribution_map,
        start_index=start_index,
    )


def parse_country_audit_response(response_text, all_events, start_index=0):
    return build_helper()._parse_country_audit_response(
        response_text,
        all_events,
        start_index=start_index,
    )


def main():
    if not API_KEY:
        log("ERROR: Set OPENROUTER_API_KEY env var!")
        return

    check_api_limits()

    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bnti_data.json")
    with open(data_path, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    all_events = []
    event_sources = []
    for country in BORDER_COUNTRIES:
        for event in data.get("countries", {}).get(country, {}).get("events", []):
            all_events.append(event)
            event_sources.append(country)

    log(f"\nTotal headlines: {len(all_events)}")
    for country in BORDER_COUNTRIES:
        count = sum(1 for source in event_sources if source == country)
        if count > 0:
            log(f"  {country}: {count}")

    helper = build_helper()
    helper._ensure_translated_titles(all_events)

    attribution_map = {}
    for start_index in range(0, len(all_events), BATCH_SIZE):
        batch = all_events[start_index:start_index + BATCH_SIZE]
        prompt = helper._build_attribution_prompt(batch, start_index=start_index)
        log(f"Batch {start_index + 1}-{start_index + len(batch)} prompt length: {len(prompt)} chars")
        response = call_openrouter(prompt)
        if not response:
            log(f"ERROR: No response for batch starting at {start_index + 1}")
            continue
        batch_map = helper._parse_attribution_response(response, batch, start_index=start_index)
        if not batch_map:
            log(f"ERROR: Invalid JSON response for batch starting at {start_index + 1}")
            continue

        audit_prompt = helper._build_country_audit_prompt(batch, batch_map, start_index=start_index)
        audit_response = call_openrouter(audit_prompt)
        if not audit_response:
            log(f"ERROR: No country audit response for batch starting at {start_index + 1}")
            continue
        audit_map = helper._parse_country_audit_response(audit_response, batch, start_index=start_index)
        if not audit_map:
            log(f"ERROR: Invalid country audit JSON response for batch starting at {start_index + 1}")
            continue

        for idx, result in batch_map.items():
            merged = dict(result)
            merged["final_country"] = audit_map[idx]["final_country"]
            attribution_map[idx] = merged

    log(f"\nParsed {len(attribution_map)}/{len(all_events)} attributions")
    log("\n" + "=" * 80)
    log("RE-ATTRIBUTION RESULTS")
    log("=" * 80)

    moved = 0
    dropped = 0
    recategorized = 0
    kept = 0

    for idx, event in enumerate(all_events):
        original_country = event_sources[idx]
        original_category = event.get("category", "?")
        title = event.get("title", "")[:80]
        if idx not in attribution_map:
            kept += 1
            continue

        result = attribution_map[idx]
        primary_country = result["primary_country"]
        final_country = result["final_country"]
        new_category = result.get("category", original_category)

        if final_country == "IRRELEVANT":
            dropped += 1
            log(f"  DROPPED  | was:{original_country:10s} | cat:{new_category:22s} | {title}")
            continue

        if final_country != original_country:
            moved += 1
            log(f"  MOVED    | {original_country:10s} -> {final_country:10s} | cat:{new_category:22s} | {title}")
        else:
            kept += 1

        if primary_country != final_country:
            log(f"  AUDIT    | {primary_country:10s} -> {final_country:10s} | cat:{new_category:22s} | {title}")

        if new_category != original_category:
            recategorized += 1
            log(f"  RECAT    | {original_country:10s} | {original_category:22s} -> {new_category:22s} | {title}")

    log("\n" + "=" * 80)
    log("SUMMARY")
    log("=" * 80)
    log(f"  Kept in place:    {kept}")
    log(f"  Moved:            {moved}")
    log(f"  Dropped:          {dropped}")
    log(f"  Re-categorized:   {recategorized}")
    log(f"  Total processed:  {len(attribution_map)}/{len(all_events)}")

    log("\n" + "=" * 80)
    log("NEW COUNTRY DISTRIBUTION (after reattribution)")
    log("=" * 80)
    new_counts = {country: 0 for country in BORDER_COUNTRIES}
    for idx, original_country in enumerate(event_sources):
        result = attribution_map.get(idx)
        if not result:
            new_counts[original_country] += 1
            continue
        if result["final_country"] == "IRRELEVANT":
            continue
        final_country = result["final_country"]
        if final_country in new_counts:
            new_counts[final_country] += 1

    old_counts = {country: sum(1 for source in event_sources if source == country) for country in BORDER_COUNTRIES}
    for country in BORDER_COUNTRIES:
        old = old_counts.get(country, 0)
        new = new_counts.get(country, 0)
        delta = new - old
        arrow = "UP" if delta > 0 else "DN" if delta < 0 else "=="
        log(f"  {country:10s}: {old:3d} -> {new:3d}  ({arrow} {abs(delta)})")

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_results.txt")
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(OUT))
    log(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()

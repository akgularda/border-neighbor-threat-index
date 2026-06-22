"""World Threat Index (WTI) — global geopolitical threat monitoring."""

import argparse
import concurrent.futures
import json
import logging
import math
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from borderneighboursthreatindex import BNTIAnalyzer
from bnti_core.groups import (
    build_rankings,
    compute_all_groups,
    compute_global_index,
    load_groups,
)
from bnti_core.ingestion import build_mirror_urls
from bnti_core.llm import (
    build_wti_attribution_prompt,
    call_openrouter,
    parse_wti_attribution_response,
)
from bnti_core.publish import global_snapshot_publishable, merge_country_block
from bnti_core.scoring import (
    LLM_CATEGORY_WEIGHTS,
    category_weights,
    compute_country_score,
    status_from_index,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

REGISTRY_PATH = Path("config/wti/countries.json")
GROUPS_PATH = Path("config/wti/groups.json")
FEEDS_DIR = Path("config/wti/feeds")
DATA_JSON = "wti_data.json"
DATA_JS = "wti_data.js"
HISTORY_CSV = "wti_history.csv"


class WTIAnalyzer:
    def __init__(self, output_path=None):
        self.output_path = output_path or os.getcwd()
        self.registry = self._load_registry()
        self.registry_by_iso2 = {c["iso2"]: c for c in self.registry}
        self.feed_engine = BNTIAnalyzer()
        self.feed_engine.output_path = self.output_path
        self.openrouter_batch_size = max(int(os.environ.get("OPENROUTER_BATCH_SIZE", "8")), 1)
        self.model = os.environ.get("OPENROUTER_MODEL", "openrouter/free")

    def _load_registry(self):
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def _country_feed_urls(self, country):
        iso2 = country["iso2"]
        include_gdelt = os.environ.get("WTI_INCLUDE_GDELT", "").lower() in ("1", "true", "yes")
        urls = list(build_mirror_urls(country["name"], include_gdelt=include_gdelt))
        feed_file = FEEDS_DIR / f"{iso2}.json"
        if feed_file.exists():
            curated = json.loads(feed_file.read_text(encoding="utf-8"))
            urls = list(dict.fromkeys(curated.get("feeds", []) + urls))
        return urls

    def _select_countries(self, countries_filter=None, tier=None, shard=None, total_shards=None):
        selected = self.registry
        if countries_filter:
            wanted = {c.strip().upper() for c in countries_filter.split(",") if c.strip()}
            selected = [c for c in selected if c["iso2"] in wanted]
        if tier:
            selected = [c for c in selected if c["tier"] == tier.upper()]
        if shard is not None and total_shards:
            selected = sorted(selected, key=lambda c: c["iso2"])
            selected = [c for i, c in enumerate(selected) if i % total_shards == shard]
        return selected

    def _fetch_country_candidates(self, country):
        urls = self._country_feed_urls(country)
        if not urls:
            return []
        all_entries = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(self.feed_engine.fetch_feed_entries, country["name"], url)
                for url in urls[:12]
            ]
            for future in concurrent.futures.as_completed(futures):
                all_entries.extend(future.result())

        seen = set()
        unique = []
        for entry in all_entries:
            link = getattr(entry, "link", None) or entry.get("link")
            title = getattr(entry, "title", None) or entry.get("title")
            if not link or not title or link in seen:
                continue
            seen.add(link)
            unique.append({
                "title": str(title),
                "translated_title": None,
                "link": str(link),
                "date": getattr(entry, "published", None) or entry.get("published", "N/A"),
                "source_country": country["iso2"],
            })
        return unique[:15]

    def _heuristic_attribution(self, events, valid_iso2):
        """Dry-run fallback when LLM unavailable."""
        result = {}
        for idx, event in enumerate(events):
            iso2 = event.get("source_country", "IRRELEVANT")
            if iso2 not in valid_iso2:
                iso2 = "IRRELEVANT"
            title = (event.get("title") or "").lower()
            category = "neutral"
            for keyword, cat in (
                ("attack", "terrorism"), ("strike", "military_conflict"), ("war", "military_conflict"),
                ("border", "border_security"), ("coup", "political_instability"),
                ("refugee", "humanitarian_crisis"), ("sanction", "diplomatic_tensions"),
            ):
                if keyword in title:
                    category = cat
                    break
            if iso2 == "IRRELEVANT":
                category = "neutral"
            result[idx] = {
                "primary_country": iso2,
                "category": category,
                "subject": event.get("title", "")[:80],
            }
        return result

    def _resolve_attribution_batch(self, events, country_list, valid_iso2, dry_run=False):
        if dry_run:
            return self._heuristic_attribution(events, valid_iso2)

        prompt = build_wti_attribution_prompt(events, country_list)
        response = call_openrouter(prompt, model=self.model)
        parsed = parse_wti_attribution_response(response, events, valid_iso2)
        if len(parsed) == len(events):
            return parsed
        if len(events) == 1:
            return {}
        midpoint = len(events) // 2
        left = self._resolve_attribution_batch(events[:midpoint], country_list, valid_iso2, dry_run)
        if len(left) != midpoint:
            return {}
        right = self._resolve_attribution_batch(events[midpoint:], country_list, valid_iso2, dry_run)
        if len(right) != len(events) - midpoint:
            return {}
        merged = dict(left)
        for key, value in right.items():
            merged[midpoint + key] = value
        return merged

    def _apply_attribution(self, events, attribution_map):
        attributed = []
        for idx, event in enumerate(events):
            attr = attribution_map.get(idx, {})
            country = attr.get("primary_country", "IRRELEVANT")
            if country == "IRRELEVANT":
                continue
            category = attr.get("category", "neutral")
            enriched = dict(event)
            enriched.update({
                "country": country,
                "category": category,
                "weight": LLM_CATEGORY_WEIGHTS.get(category, 0.0),
                "confidence": 1.0,
                "ai_model": self.model,
                "llm_primary_country": country,
                "llm_subject": attr.get("subject", ""),
            })
            attributed.append(enriched)
        return attributed

    def _score_country(self, iso2, events):
        country_events = [e for e in events if e.get("country") == iso2]
        index, raw = compute_country_score(country_events)
        return {
            "name": self.registry_by_iso2[iso2]["name"],
            "index": index,
            "raw_score": raw,
            "status": status_from_index(index),
            "events": country_events,
        }

    def _load_existing_data(self):
        path = Path(self.output_path) / DATA_JSON
        if not path.exists():
            return {"countries": {}, "meta": {}}
        return json.loads(path.read_text(encoding="utf-8"))

    def _build_country_results(self, countries, dry_run=False):
        country_iso_list = [f"{c['iso2']} ({c['name']})" for c in countries]
        valid_iso2 = {c["iso2"] for c in countries}
        all_events = []
        per_country_raw = {}

        for country in countries:
            iso2 = country["iso2"]
            candidates = self._fetch_country_candidates(country)
            per_country_raw[iso2] = candidates
            logger.info(f"{iso2}: {len(candidates)} candidate headlines")
            all_events.extend(candidates)

        attribution_map = {}
        for start in range(0, len(all_events), self.openrouter_batch_size):
            batch = all_events[start:start + self.openrouter_batch_size]
            batch_map = self._resolve_attribution_batch(
                batch, country_iso_list, valid_iso2, dry_run=dry_run
            )
            if len(batch_map) != len(batch):
                logger.warning(f"Attribution failed for batch at {start}")
                if not dry_run:
                    return None
            for local_idx, value in batch_map.items():
                attribution_map[start + local_idx] = value

        attributed = self._apply_attribution(all_events, attribution_map)
        results = {}
        for country in countries:
            iso2 = country["iso2"]
            results[iso2] = self._score_country(iso2, attributed)
        return results

    def _write_dashboard(self, countries_data, publish_meta=True):
        existing = self._load_existing_data()
        merged_countries = dict(existing.get("countries", {}))
        for iso2, block in countries_data.items():
            merged_countries[iso2] = merge_country_block(merged_countries.get(iso2), block)

        groups = compute_all_groups(merged_countries, self.registry, load_groups(GROUPS_PATH))
        main_index = compute_global_index(merged_countries, self.registry)
        status = status_from_index(main_index)
        rankings = build_rankings(merged_countries, self.registry_by_iso2)
        coverage = len([c for c in merged_countries if merged_countries[c].get("index")]) / len(self.registry)

        dashboard = {
            "meta": {
                "generated_at": datetime.now().isoformat(),
                "main_index": main_index,
                "status": status,
                "countries_total": len(self.registry),
                "countries_active": len(merged_countries),
                "coverage_ratio": round(coverage, 2),
                "version": "1.0.0",
                "next_update": (datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(hours=2)).isoformat(),
                "publishable": publish_meta,
            },
            "countries": merged_countries,
            "groups": groups,
            "rankings": {
                "highest_threat": rankings["highest_threat"],
                "lowest_threat": rankings["lowest_threat"],
            },
            "rankings_table": rankings["table"],
            "methodology": {
                "name": "World Threat Index",
                "description": "LLM country attribution + deterministic BNTI category weights.",
                "weights": category_weights(),
                "formula": "PerCountry = 1 + 9*(1 - exp(-avg(weight)/5 * 1.2))",
            },
        }

        json_path = Path(self.output_path) / DATA_JSON
        js_path = Path(self.output_path) / DATA_JS
        json_tmp = f"{json_path}.tmp"
        js_tmp = f"{js_path}.tmp"
        with open(json_tmp, "w", encoding="utf-8") as handle:
            json.dump(dashboard, handle, indent=2, ensure_ascii=False)
        with open(js_tmp, "w", encoding="utf-8") as handle:
            payload = json.dumps(dashboard, indent=2, ensure_ascii=False)
            handle.write(f"window.WTI_DATA = {payload};")
        os.replace(json_tmp, json_path)
        os.replace(js_tmp, js_path)
        return dashboard

    def run(self, countries_filter=None, tier=None, shard=None, total_shards=None,
            dry_run=False, output_shard=None):
        countries = self._select_countries(countries_filter, tier, shard, total_shards)
        logger.info(f"WTI processing {len(countries)} countries (dry_run={dry_run})")

        results = self._build_country_results(countries, dry_run=dry_run)
        if results is None:
            logger.warning("Run failed — no country results")
            return False

        if output_shard is not None:
            shard_path = Path(self.output_path) / f"wti_shard_{output_shard}.json"
            shard_path.write_text(json.dumps({"countries": results}, indent=2), encoding="utf-8")
            logger.info(f"Wrote shard {output_shard} with {len(results)} countries")
            return True

        dashboard = self._write_dashboard(results)
        if not dry_run and not global_snapshot_publishable(dashboard["countries"], self.registry):
            logger.warning("Global coverage gate not met — partial update written with flag")
            dashboard["meta"]["publishable"] = False
        logger.info(f"WTI complete. Global index: {dashboard['meta']['main_index']}")
        return True


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="World Threat Index analyzer")
    parser.add_argument("--dry-run", action="store_true", help="Use heuristic attribution (no LLM)")
    parser.add_argument("--countries", type=str, default=None, help="Comma-separated ISO2 codes")
    parser.add_argument("--tier", type=str, default=None, choices=["A", "B", "C"])
    parser.add_argument("--shard", type=int, default=None)
    parser.add_argument("--total-shards", type=int, default=10)
    parser.add_argument("--output-shard", type=int, default=None)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    analyzer = WTIAnalyzer()
    try:
        ok = analyzer.run(
            countries_filter=args.countries,
            tier=args.tier,
            shard=args.shard,
            total_shards=args.total_shards,
            dry_run=args.dry_run,
            output_shard=args.output_shard,
        )
        return 0 if ok else 0
    except Exception as exc:
        logger.error(f"WTI critical error: {exc}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
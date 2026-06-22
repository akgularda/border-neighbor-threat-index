"""OpenRouter LLM attribution for WTI global country universe."""

import ast
import json
import logging
import os
import re

from bnti_core.scoring import VALID_CATEGORIES

logger = logging.getLogger(__name__)

CATEGORY_LIST_TEXT = "\n".join(
    f'   - "{cat}"' for cat in sorted(VALID_CATEGORIES)
)


def normalize_headline(value):
    return re.sub(r"\s+", " ", str(value or "").replace('"', "'")).strip()


def format_headline_for_prompt(event):
    title = normalize_headline(event.get("translated_title") or event.get("title") or "")
    original = normalize_headline(event.get("title") or "")
    block = f'Headline: "{title}"'
    if original and original != title:
        block += f' | Original: "{original}"'
    return block


def build_wti_attribution_prompt(events, country_list, start_index=0):
    lines = []
    for i, event in enumerate(events):
        lines.append(f"{start_index + i + 1}. {format_headline_for_prompt(event)}")

    countries_text = ", ".join(country_list)
    headlines_block = "\n".join(lines)
    return f"""You are a geopolitical intelligence analyst for the World Threat Index.
Valid countries (ISO2 code or IRRELEVANT): {countries_text}

For each numbered headline:
1. Choose exactly ONE primary_country as ISO2 code, or "IRRELEVANT".
2. Classify into exactly ONE category:
{CATEGORY_LIST_TEXT}
3. Write a short subject phrase.

Rules:
- Attribute from headline content only, never from feed source.
- Country qualifies when headline is directly mainly about that country's territory, government, military, or population.
- Cross-border events: attribute to country where primary event occurs.
- If no single country is clearly the main subject, return IRRELEVANT.

Headlines:
{headlines_block}

Respond ONLY with valid JSON array, no markdown:
[{{"id": 1, "primary_country": "US", "category": "neutral", "subject": "..."}}]"""


def parse_llm_literal(response_text, expected_type):
    if not response_text:
        return None
    text = response_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()

    if expected_type is list:
        match = re.search(r"\[.*\]", text, re.DOTALL)
    else:
        match = re.search(r"\{.*\}", text, re.DOTALL)

    candidates = [text]
    if match:
        candidates.append(match.group(0))

    for candidate in candidates:
        normalized = (
            candidate.replace(""", '"').replace(""", '"')
            .replace("'", "'").replace("'", "'")
        )
        normalized = re.sub(r",(\s*[}\]])", r"\1", normalized)
        for parser in (json.loads, ast.literal_eval):
            try:
                parsed = parser(normalized)
            except (json.JSONDecodeError, SyntaxError, ValueError):
                continue
            if isinstance(parsed, expected_type):
                return parsed
    return None


def parse_wti_attribution_response(response_text, events, valid_iso2, start_index=0):
    attribution_map = {}
    if not response_text:
        return attribution_map

    parsed = parse_llm_literal(response_text, list)
    if not parsed:
        logger.warning("OpenRouter response is not a JSON array")
        return attribution_map

    expected_ids = set(range(start_index + 1, start_index + len(events) + 1))
    seen_ids = set()

    for item in parsed:
        if not isinstance(item, dict):
            return {}
        idx = item.get("id")
        country = str(item.get("primary_country", "")).strip().upper()
        category = str(item.get("category", "")).strip().lower()
        subject = str(item.get("subject", "")).strip()
        if idx not in expected_ids or idx in seen_ids:
            return {}
        if country != "IRRELEVANT" and country not in valid_iso2:
            return {}
        if category not in VALID_CATEGORIES or not subject:
            return {}
        seen_ids.add(idx)
        attribution_map[int(idx) - 1] = {
            "primary_country": country,
            "category": category,
            "subject": subject,
        }

    if seen_ids != expected_ids:
        return {}
    return attribution_map


def call_openrouter(prompt, model=None, max_retries=2, timeout=45):
    import requests

    api_keys = []
    for key in [
        os.environ.get("OPENROUTER_API_KEY", ""),
        os.environ.get("OPENROUTER_API_KEY_BACKUP", ""),
    ]:
        if key and key not in api_keys:
            api_keys.append(key)

    if not api_keys:
        logger.warning("OpenRouter API keys not set")
        return None

    model = model or os.environ.get("OPENROUTER_MODEL", "openrouter/free")
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 8192,
    }

    for api_key in api_keys:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        for attempt in range(max_retries):
            try:
                resp = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=timeout,
                )
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return content
            except Exception as exc:
                logger.warning(f"OpenRouter attempt {attempt + 1} failed: {exc}")
    return None
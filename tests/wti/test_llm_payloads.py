from bnti_core.llm import build_wti_attribution_prompt, parse_wti_attribution_response


def test_prompt_contains_countries():
    events = [{"title": "Test headline", "translated_title": None}]
    prompt = build_wti_attribution_prompt(events, ["US (United States)", "GB (United Kingdom)"])
    assert "US" in prompt
    assert "military_conflict" in prompt


def test_parse_valid_response():
    events = [{"title": "A"}, {"title": "B"}]
    response = '[{"id": 1, "primary_country": "US", "category": "neutral", "subject": "test"}, {"id": 2, "primary_country": "IRRELEVANT", "category": "neutral", "subject": "none"}]'
    parsed = parse_wti_attribution_response(response, events, {"US"})
    assert len(parsed) == 2
    assert parsed[0]["primary_country"] == "US"
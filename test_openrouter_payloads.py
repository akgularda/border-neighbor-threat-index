import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

import requests

import borderneighboursthreatindex as analyzer_module
import test_reattribution as dry_run_module


class OpenRouterPayloadTests(unittest.TestCase):
    def make_analyzer(self):
        analyzer = object.__new__(analyzer_module.BNTIAnalyzer)
        analyzer.openrouter_api_key = "primary-key"
        analyzer.openrouter_backup_api_key = "backup-key"
        analyzer.openrouter_model = "openrouter/free"
        analyzer.openrouter_base_url = "https://openrouter.ai/api/v1/chat/completions"
        analyzer.openrouter_batch_size = 10
        analyzer.border_countries = list(analyzer_module.BNTIAnalyzer.BORDER_COUNTRIES)
        analyzer.category_weights = dict(analyzer_module.BNTIAnalyzer.LLM_CATEGORY_WEIGHTS)
        return analyzer

    @patch("requests.post")
    def test_analyzer_disables_reasoning_in_openrouter_calls(self, mock_post):
        analyzer = self.make_analyzer()

        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "choices": [{"message": {"content": "[]"}}],
        }
        mock_post.return_value = response

        result = analyzer._call_openrouter("prompt", max_retries=0)

        self.assertEqual(result, "[]")
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["json"]["max_tokens"], 8192)
        self.assertEqual(kwargs["json"].get("reasoning"), {"effort": "none"})

    @patch("requests.post")
    def test_analyzer_retries_without_reasoning_when_provider_requires_it(self, mock_post):
        analyzer = self.make_analyzer()

        first = MagicMock()
        first.status_code = 400
        first.text = '{"error":{"message":"Reasoning is mandatory for this endpoint and cannot be disabled."}}'
        first.raise_for_status.side_effect = requests.HTTPError("400 Client Error")

        second = MagicMock()
        second.status_code = 200
        second.json.return_value = {
            "choices": [{"message": {"content": "[]"}}],
        }

        mock_post.side_effect = [first, second]

        result = analyzer._call_openrouter("prompt", max_retries=0)

        self.assertEqual(result, "[]")
        self.assertEqual(mock_post.call_count, 2)
        first_call = mock_post.call_args_list[0].kwargs["json"]
        second_call = mock_post.call_args_list[1].kwargs["json"]
        self.assertEqual(first_call.get("reasoning"), {"effort": "none"})
        self.assertNotIn("reasoning", second_call)

    @patch("time.sleep", return_value=None)
    @patch("requests.post")
    def test_analyzer_tries_backup_key_after_primary_rate_limit(self, mock_post, _mock_sleep):
        analyzer = self.make_analyzer()

        first = MagicMock()
        first.status_code = 429
        first.text = "rate limited"

        second = MagicMock()
        second.status_code = 200
        second.json.return_value = {
            "choices": [{"message": {"content": "[]"}}],
        }

        mock_post.side_effect = [first, second]

        result = analyzer._call_openrouter("prompt", max_retries=0)

        self.assertEqual(result, "[]")
        self.assertEqual(mock_post.call_count, 2)
        primary_auth = mock_post.call_args_list[0].kwargs["headers"]["Authorization"]
        backup_auth = mock_post.call_args_list[1].kwargs["headers"]["Authorization"]
        self.assertEqual(primary_auth, "Bearer primary-key")
        self.assertEqual(backup_auth, "Bearer backup-key")

    def test_analyzer_prompt_numbers_batches_with_global_ids(self):
        analyzer = self.make_analyzer()
        prompt = analyzer._build_attribution_prompt(
            [{"title": "First headline"}, {"title": "Second headline"}],
            start_index=10,
        )
        self.assertIn('11. "First headline"', prompt)
        self.assertIn('12. "Second headline"', prompt)
        self.assertIn("military_conflict", prompt)

    def test_analyzer_prompt_treats_rebuild_headlines_as_main_event_not_conflict_context(self):
        analyzer = self.make_analyzer()
        prompt = analyzer._build_attribution_prompt(
            [
                {
                    "title": "Syria silently rebuilds itself as war with Iran tarnishes Gulf infrastructure - Türkiye Today"
                }
            ]
        )

        self.assertIn("Classify the main event, not background context", prompt)
        self.assertIn("Reconstruction, rebuilding, reopening, recovery", prompt)
        self.assertIn(
            '"Syria silently rebuilds itself as war with Iran tarnishes Gulf infrastructure',
            prompt,
        )
        self.assertIn('["Syria"], "neutral"', prompt)

    def test_analyzer_parser_rejects_incomplete_batch(self):
        analyzer = self.make_analyzer()
        parsed = analyzer._parse_attribution_response(
            '[{"id": 1, "countries": ["Syria"], "category": "military_conflict"}]',
            [{"title": "First headline"}, {"title": "Second headline"}],
            start_index=0,
        )
        self.assertEqual(parsed, {})

    def test_analyzer_parser_keeps_llm_country_choice_without_keyword_override(self):
        analyzer = self.make_analyzer()
        parsed = analyzer._parse_attribution_response(
            '[{"id": 1, "countries": ["IRRELEVANT"], "category": "military_conflict"}]',
            [{"title": "Israel launches strikes on Iran"}],
            start_index=0,
        )
        self.assertEqual(parsed[0]["countries"], ["IRRELEVANT"])

    def test_summary_prompt_demands_structured_six_hour_brief(self):
        analyzer = self.make_analyzer()
        prompt = analyzer._build_regional_summary_prompt(
            [
                {
                    "country": "Iran",
                    "category": "military_conflict",
                    "weight": 8.0,
                    "date": "2026-03-28T05:15:00",
                    "title": "Original title",
                    "translated_title": "Iran exchanges strikes with Israel overnight",
                }
            ],
            datetime(2026, 3, 28, 0, 0, 0),
            datetime(2026, 3, 28, 6, 0, 0),
        )

        self.assertIn("Use only the supplied events", prompt)
        self.assertIn("Do not write a country-by-country list", prompt)
        self.assertIn("exactly 3 bullets", prompt)
        self.assertIn("last completed 6-hour window", prompt)
        self.assertIn('"watch": null', prompt)

    def test_summary_parser_requires_exactly_three_bullets(self):
        analyzer = self.make_analyzer()

        parsed = analyzer._parse_regional_summary_response(
            '{"headline":"Regional pressure centers on Iran and Iraq.","bullets":["One.","Two.","Three."],"watch":null}'
        )
        self.assertEqual(parsed["headline"], "Regional pressure centers on Iran and Iraq.")

        invalid = analyzer._parse_regional_summary_response(
            '{"headline":"Too short.","bullets":["One.","Two."],"watch":null}'
        )
        self.assertIsNone(invalid)

    def test_summary_validator_rejects_unseen_border_country_mentions(self):
        analyzer = self.make_analyzer()
        parsed = {
            "headline": "Armenia faces acute pressure.",
            "bullets": ["Armenia absorbs the sharpest pressure.", "Iraq remains tense.", "Georgia is relatively quiet."],
            "watch": None,
        }
        summary_events = [
            {
                "country": "Iraq",
                "title": "Baghdad airport security alert",
                "translated_title": "Baghdad airport security alert",
            },
            {
                "country": "Georgia",
                "title": "Tbilisi opposition rallies continue",
                "translated_title": "Tbilisi opposition rallies continue",
            },
        ]

        self.assertFalse(analyzer._regional_summary_mentions_are_grounded(parsed, summary_events))

    @patch("test_reattribution.requests.post")
    def test_dry_run_uses_same_openrouter_guardrails(self, mock_post):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "choices": [{"message": {"content": "[]"}}],
            "usage": {},
        }
        mock_post.return_value = response

        original_primary = dry_run_module.API_KEY
        original_backup = dry_run_module.BACKUP_API_KEY
        dry_run_module.API_KEY = "primary-key"
        dry_run_module.BACKUP_API_KEY = "backup-key"
        try:
            result = dry_run_module.call_openrouter("prompt")
        finally:
            dry_run_module.API_KEY = original_primary
            dry_run_module.BACKUP_API_KEY = original_backup

        self.assertEqual(result, "[]")
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["json"]["max_tokens"], 8192)
        self.assertEqual(kwargs["json"].get("reasoning"), {"effort": "none"})

    def test_dry_run_prompt_numbers_batches_with_global_ids(self):
        prompt = dry_run_module.build_prompt(
            [{"title": "First headline"}, {"title": "Second headline"}],
            start_index=10,
        )
        self.assertIn('11. "First headline"', prompt)
        self.assertIn('12. "Second headline"', prompt)
        self.assertIn("military_conflict", prompt)

    def test_dry_run_parser_rejects_incomplete_batch(self):
        parsed = dry_run_module.parse_response(
            '[{"id": 1, "countries": ["Syria"], "category": "military_conflict"}]',
            [{"title": "First headline"}, {"title": "Second headline"}],
            start_index=0,
        )
        self.assertEqual(parsed, {})

    def test_dry_run_parser_keeps_llm_country_choice_without_keyword_override(self):
        parsed = dry_run_module.parse_response(
            '[{"id": 1, "countries": ["IRRELEVANT"], "category": "military_conflict"}]',
            [{"title": "Israel launches strikes on Iran"}],
            start_index=0,
        )
        self.assertEqual(parsed[0]["countries"], ["IRRELEVANT"])


if __name__ == "__main__":
    unittest.main()

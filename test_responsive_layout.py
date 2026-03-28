import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class ResponsiveLayoutTests(unittest.TestCase):
    def setUp(self):
        self.layout_css = (ROOT / "css" / "layout.css").read_text(encoding="utf-8")
        self.components_css = (ROOT / "css" / "components.css").read_text(encoding="utf-8")

    def test_mobile_stacks_map_before_scores_and_feed(self):
        pattern = re.compile(
            r"@media\s*\(max-width:\s*1200px\)\s*\{[\s\S]*?"
            r"\.grid\s*\{[\s\S]*?display:\s*flex;[\s\S]*?flex-direction:\s*column;[\s\S]*?\}[\s\S]*?"
            r"\.map-panel\s*\{[\s\S]*?order:\s*1;[\s\S]*?\}[\s\S]*?"
            r"\.metric-panel\s*\{[\s\S]*?order:\s*2;[\s\S]*?\}[\s\S]*?"
            r"\.feed-panel\s*\{[\s\S]*?order:\s*3;[\s\S]*?\}",
            re.MULTILINE,
        )
        self.assertRegex(self.layout_css, pattern)

    def test_short_desktop_viewports_allow_summary_block_to_shrink_and_scroll(self):
        self.assertRegex(
            self.components_css,
            re.compile(r"\.summary-block\s*\{[\s\S]*?flex-shrink:\s*1;", re.MULTILINE),
        )
        self.assertRegex(
            self.layout_css,
            re.compile(
                r"@media\s*\(min-width:\s*1201px\)\s*and\s*\(max-height:\s*920px\)\s*\{[\s\S]*?"
                r"\.metric-panel\s*\{[\s\S]*?overflow-y:\s*auto;",
                re.MULTILINE,
            ),
        )

    def test_mobile_moves_map_overlay_scores_below_the_svg(self):
        self.assertRegex(
            self.components_css,
            re.compile(
                r"@media\s*\(max-width:\s*1200px\)\s*\{[\s\S]*?"
                r"\.map-wrap\s*\{[\s\S]*?display:\s*flex;[\s\S]*?flex-direction:\s*column;[\s\S]*?\}[\s\S]*?"
                r"\.map-overlay\s*\{[\s\S]*?position:\s*static;[\s\S]*?\}",
                re.MULTILINE,
            ),
        )


if __name__ == "__main__":
    unittest.main()

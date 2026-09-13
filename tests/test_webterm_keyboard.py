"""webterm's one host requirement: the viewport must shrink for the keyboard.

The library ships no on-screen key bar — every key a soft keyboard lacks is
translated from a real keyboard instead (solBench/webterm/readme.md § "Every
key a real keyboard sends"), so there is no glue for this app to carry.

What the library still cannot do from inside is ask Chrome to shrink the
*layout* viewport when the soft keyboard opens. Without that, a
fixed-position element — which is what .wt-root becomes in fullscreen —
stays behind the keyboard, hiding the last terminal rows and the line being
typed. Only this template can set it, so this is where it is pinned.

cldlab has no pytest suite; like test_cldbar_embed.py this runs standalone:

    .venv/bin/python -m unittest discover -s tests
"""

import re
import unittest
from pathlib import Path

TEMPLATE = (Path(__file__).resolve().parent.parent
            / "control-plane" / "templates" / "index.html")


class ViewportHostRequirement(unittest.TestCase):
    def test_the_viewport_shrinks_for_the_soft_keyboard(self):
        html = TEMPLATE.read_text(encoding="utf-8")
        meta = re.search(r"<meta[^>]*name=[\"']viewport[\"'][^>]*>", html)
        self.assertIsNotNone(
            meta, "no viewport meta tag — the terminal cannot be used on a phone")
        self.assertIn(
            "interactive-widget=resizes-content", meta.group(0),
            "soft keyboard will cover the bottom terminal rows in fullscreen")


if __name__ == "__main__":
    unittest.main()

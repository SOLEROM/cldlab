"""cldBar embed — remdev's Claude status bar on cldlab's bottom status bar.

The mechanism belongs to the kit (solBench/cldBar): `cldbar.js` is copied
into static/js and owns the iframe. cldlab only owns *policy* — where the
bar mounts, the optional `app.remdev_url` pin, and how its four themes map
onto remdev's theme slugs.

These tests pin the pitfalls the kit's readme calls out, above all that no
server-rendered `127.0.0.1` reaches the page: an iframe src is fetched by
the *viewer's* browser, so a loopback default renders a blank strip on
every device that is not the station itself.

The embed used to hang off the header, because cldlab had no footer. It now
sits on a real bottom status bar (2026-08-20) — the row the kit's readme
asks for, shared only with fixed-width neighbours (the connection pill and
the address the page was opened on).

cldlab has no pytest suite, so this leans on unittest and the app's own
dependencies (yaml, jinja2) and runs standalone:

    .venv/bin/python -m unittest discover -s tests
"""

import re
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import jinja2

REPO = Path(__file__).resolve().parent.parent
CONTROL_PLANE = REPO / "control-plane"
STATIC_JS = CONTROL_PLANE / "static" / "js"
STATIC_CSS = CONTROL_PLANE / "static" / "css"
TEMPLATE = CONTROL_PLANE / "templates" / "index.html"
# Same checkout path run.sh uses for the shared webterm install.
KIT_DIR = Path("/data/proj/agents/solBench/cldBar")

sys.path.insert(0, str(CONTROL_PLANE))

from modules.config_manager import ConfigManager  # noqa: E402


def render(remdev_url: str = "") -> str:
    """The page as the browser gets it — the Jinja template rendered the way
    the index route renders it."""
    # autoescape=True mirrors Flask, which turns it on for .html templates.
    # A bare Environment defaults to OFF and would render a breakout the real
    # app escapes — a suite that pins escaping must not be laxer than prod.
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(TEMPLATE.parent)),
                             autoescape=True)
    return env.get_template(TEMPLATE.name).render(use_webterm=True,
                                                  remdev_url=remdev_url)


def live_markup(remdev_url: str = "") -> str:
    """The rendered page with its HTML comments stripped: the markup explains
    the pitfall by name, and only live markup can point a viewer at a wrong
    host."""
    return re.sub(r"<!--.*?-->", "", render(remdev_url), flags=re.S)


def region(body: str, opening: str, closing: str) -> str:
    return body.split(opening, 1)[1].split(closing, 1)[0]


def main_css() -> str:
    return (STATIC_CSS / "main.css").read_text(encoding="utf-8")


def write_config(directory: Path, body: str) -> ConfigManager:
    path = directory / "config.yaml"
    path.write_text(body, encoding="utf-8")
    return ConfigManager(str(path))


class MountSlotTest(unittest.TestCase):
    def test_the_status_bar_carries_the_cldbar_mount_slot(self):
        body = render()
        self.assertIn('<footer class="statusbar"', body)
        bar = region(body, '<footer class="statusbar"', "</footer>")
        self.assertIn('id="cldbar-slot"', bar)

    def test_the_header_no_longer_hosts_the_embed(self):
        """One mount point only — a stale header slot would mount a second
        iframe (the glue mounts by id, and the first match wins silently)."""
        header = region(render(), '<header class="header"', "</header>")
        self.assertNotIn("cldbar-slot", header)

    def test_the_kit_helper_and_the_app_glue_are_both_loaded(self):
        body = render()
        self.assertIn("/static/js/cldbar.js", body)
        self.assertIn("/static/js/cldbar-glue.js", body)
        # The kit defines window.cldBar; the glue consumes it.
        self.assertLess(body.index("/static/js/cldbar.js"),
                        body.index("/static/js/cldbar-glue.js"))


class StatusBarTest(unittest.TestCase):
    """The bar itself — cldlab's own chrome, not the kit's."""

    def test_the_bar_gets_a_row_of_its_own(self):
        """The page never scrolls (html/body are overflow:hidden), so the
        status bar is fixed chrome like the header. Its height has to come
        off the layout, or the bar covers the bottom of the terminal."""
        css = main_css()
        self.assertIn("--statusbar-h", css)
        layout = region(css, ".layout {", "}")
        self.assertIn("var(--statusbar-h)", layout)
        statusbar = region(css, ".statusbar {", "}")
        self.assertIn("bottom: 0", statusbar)

    def test_the_connection_pill_sits_on_the_bar(self):
        """A connection pill is exactly the fixed-width neighbour the kit's
        readme asks for, and a status bar is where it belongs. app.js drives
        it by id, so the ids move with the markup."""
        bar = region(render(), '<footer class="statusbar"', "</footer>")
        self.assertIn('id="conn-dot"', bar)
        self.assertIn('id="conn-label"', bar)
        app_js = (STATIC_JS / "app.js").read_text(encoding="utf-8")
        self.assertIn("getElementById('conn-dot')", app_js)
        self.assertIn("getElementById('conn-label')", app_js)

    def test_the_address_readout_is_filled_by_the_browser(self):
        """Which address this tab was opened on (station vs LAN peer) is a
        browser fact: rendering it server-side would print the *server's*
        idea of the host to every viewer — the same mistake as a
        server-rendered iframe src."""
        bar = region(render(), '<footer class="statusbar"', "</footer>")
        self.assertIn('id="status-host"', bar)
        self.assertRegex(bar, r'id="status-host"[^>]*>\s*</span>')
        app_js = (STATIC_JS / "app.js").read_text(encoding="utf-8")
        self.assertIn("status-host", app_js)

    def test_the_embed_is_dropped_where_the_row_cannot_hold_it(self):
        """The bar is 560px and cannot shrink — the kit also caps it at
        55vw, so anything under ~1018px clips the week readout rather than
        scaling it. Drop it there instead of showing a stub."""
        css = main_css()
        widths = [int(width) for width, block in
                  re.findall(r"@media \(max-width: (\d+)px\) \{(.*?)\n\}", css, re.S)
                  if ".cldbar-slot" in block and "display: none" in block]
        self.assertTrue(widths, "no media query drops the cldbar slot")
        self.assertGreaterEqual(max(widths), 1018)


class LoopbackPitfallTest(unittest.TestCase):
    def test_the_page_never_hardcodes_the_station_address(self):
        body = live_markup()
        self.assertNotIn("127.0.0.1", body)
        self.assertNotIn("6005", body)
        self.assertIn('data-remdev-url=""', body)

    def test_a_pinned_origin_reaches_the_slot(self):
        self.assertIn('data-remdev-url="http://station:6005"',
                      render("http://station:6005"))

    def test_the_glue_derives_the_origin_from_the_viewer_address(self):
        src = re.sub(r"//.*", "", (STATIC_JS / "cldbar-glue.js").read_text())
        self.assertNotIn("127.0.0.1", src)
        self.assertNotIn("6005", src)
        # The pin is read off the slot; with none, the kit derives the origin.
        self.assertIn("remdevUrl", src)

    def test_the_index_route_feeds_the_pin_into_the_template(self):
        routes = (CONTROL_PLANE / "modules" / "routes.py").read_text()
        index = routes.split("def index(", 1)[1].split("\n    @app.route", 1)[0]
        self.assertIn("remdev_url", index)


class RemdevUrlPinTest(unittest.TestCase):
    def test_a_pinned_url_is_exposed_stripped_of_its_trailing_slash(self):
        with TemporaryDirectory() as td:
            config = write_config(
                Path(td), "app:\n  remdev_url: 'https://station.ts.net/'\n")
            self.assertEqual(config.remdev_url, "https://station.ts.net")

    def test_no_pin_means_empty_so_the_browser_derives_the_origin(self):
        with TemporaryDirectory() as td:
            self.assertEqual(write_config(Path(td), "app: {}\n").remdev_url, "")

    def test_config_accepts_an_http_or_https_origin(self):
        # The whitelist must stay wide enough for every shape the family
        # actually uses: a port, none, a subpath, an IPv6 literal, a trailing
        # slash (the reader strips it).
        for url in ("http://127.0.0.1:6005", "https://box.ts.net",
                    "https://box.ts.net/remdev", "http://[::1]:6005",
                    "https://station.ts.net/"):
            with TemporaryDirectory() as td:
                config = write_config(Path(td), "app: {}\n")
                ok, err = config.write_raw_yaml(f"app:\n  remdev_url: '{url}'\n")
                self.assertTrue(ok, err)

    def test_config_save_refuses_a_url_that_is_not_an_http_origin(self):
        # The value lands in an iframe src, and the kit throws on a bad
        # origin — which would leave a silently empty slot. Fail at save
        # time instead, where the editor can show the message.
        for bad in ("station:6005", "//station:6005", "javascript:alert(1)", 6005,
                    # Reads as the trusted host, resolves to evil.tld: the
                    # browser treats everything before the @ as userinfo.
                    "https://station.ts.net@evil.tld",
                    # Control bytes have no business in a value bound for an
                    # iframe src (\s does not cover them).
                    "http://station\x00.evil.tld",
                    "http://station\x07.evil.tld",
                    # Nor does a quote, which is what an attribute breakout
                    # would need if autoescaping ever came off.
                    'http://evil.tld"onmouseover="alert(1)'):
            with TemporaryDirectory() as td:
                config = write_config(Path(td), "app: {}\n")
                ok, err = config.write_raw_yaml(f"app:\n  remdev_url: {bad!r}\n")
                self.assertFalse(ok, f"{bad!r} was accepted")
                self.assertIn("remdev_url", err)


    def test_the_pin_is_attribute_escaped_on_its_way_into_the_page(self):
        """Belt to the validator's braces: the pin lands inside an HTML
        attribute, so a quote in it must never close that attribute."""
        page = render('http://evil.tld"onmouseover="alert(1)')
        self.assertNotIn('"onmouseover="', page)
        self.assertIn("data-remdev-url=", page)


class ThemingTest(unittest.TestCase):
    def test_the_glue_maps_every_app_theme_onto_a_remdev_slug(self):
        """A theme missing from the map would silently fall back to the dark
        slug — a dark opaque strip that is invisible on the dark themes and
        obvious only on Light Modern."""
        toggle = (STATIC_JS / "theme-toggle.js").read_text()
        themes = re.search(r"var THEMES = \[(.*?)\]", toggle, re.S).group(1)
        app_themes = set(re.findall(r'"([a-z]+)"', themes))

        glue = (STATIC_JS / "cldbar-glue.js").read_text()
        block = re.search(r"CLDBAR_THEME = \{(.*?)\}", glue, re.S).group(1)
        mapped = dict(re.findall(r'(\w+):\s*"([a-z0-9-]+)"', block))

        self.assertEqual(set(mapped), app_themes)
        self.assertTrue(mapped["light"].endswith("light"))  # sets color-scheme

    def test_the_app_theme_switch_re_points_the_embed(self):
        """theme-toggle.js is vendored 4ColThems and stays unedited: it
        announces a switch with a `themechange` event, so the glue listens
        for that instead of the app patching the toggle."""
        glue = (STATIC_JS / "cldbar-glue.js").read_text()
        self.assertIn("themechange", glue)
        self.assertIn("syncCldBar", glue)

    def test_the_bar_paints_no_background_behind_the_embed(self):
        """The embed's canvas is transparent so the status bar shows
        through; a background on the slot itself would defeat that (and hide
        an opaque-canvas regression, which only a light theme reveals)."""
        slot = region(main_css(), ".cldbar-slot {", "}")
        self.assertNotIn("background", slot)


class KitCopyTest(unittest.TestCase):
    def test_the_kit_copy_is_not_a_local_fork(self):
        """cldbar.js is a copy-in, refreshed by cldBar/install.sh. A local
        edit (or a stale copy) is drift, not an integration."""
        if not KIT_DIR.exists():
            self.skipTest(f"solBench checkout not at {KIT_DIR}")
        self.assertEqual((STATIC_JS / "cldbar.js").read_bytes(),
                         (KIT_DIR / "cldbar.js").read_bytes())


if __name__ == "__main__":
    unittest.main()

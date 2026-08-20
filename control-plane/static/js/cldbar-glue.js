// cldlab — the Claude window/week meters on the bottom status bar.
//
// The bar itself is remdev's service, embedded through the shared cldBar
// kit (solBench/cldBar). static/js/cldbar.js is a *copy-in* of that kit —
// refresh it with `cldBar/install.sh <this dir>`, never edit it here. This
// file is cldlab's policy layer: where the bar mounts, which remdev origin
// it uses, and how the app's four themes map onto remdev's theme slugs.
//
// The bar mounts on cldlab's bottom status bar (it used to hang off the
// header, before that bar existed — the kit's readme asks for a row the
// 560px embed does not have to share). cldlab's theme switcher is vendored
// 4ColThems (theme-toggle.js, kept unedited), which announces a switch with
// a `themechange` event — that event is what re-points the embed here.
(function () {
  "use strict";

  // cldlab theme -> remdev theme slug (a token block in remdev's garage.css).
  // Keep the keys in sync with THEMES in theme-toggle.js: an unmapped theme
  // falls back to the dark slug, which on Light Modern shows up as an opaque
  // dark strip.
  var CLDBAR_THEME = {
    dark: "vscode-dark",
    light: "vscode-light",
    hc: "vscode-hc",
    green: "vscode-green",
  };

  function currentTheme() {
    if (window.Theme4Col && typeof Theme4Col.current === "function") {
      return Theme4Col.current();
    }
    return document.documentElement.getAttribute("data-theme") || "dark";
  }

  // The kit needs the theme slug and, only when the config pins one, an
  // explicit remdev origin. With no pin it derives the origin from the page's
  // own address — a server-rendered 127.0.0.1 would point every remote viewer
  // at their own machine and blank the bar (cldBar readme, "the 127.0.0.1
  // pitfall").
  function cldbarOptions() {
    var slot = document.getElementById("cldbar-slot");
    var pinned = slot && slot.dataset.remdevUrl;
    var opts = { theme: CLDBAR_THEME[currentTheme()] || CLDBAR_THEME.dark };
    if (pinned) opts.url = pinned;
    return opts;
  }

  function setupCldBar() {
    var slot = document.getElementById("cldbar-slot");
    if (!slot || !window.cldBar) return;  // kit not copied in — no meters
    try {
      cldBar.mountCldBar(slot, cldbarOptions());
    } catch (err) {
      // Only a malformed app.remdev_url gets here; the config editor rejects
      // those on save, so this is the belt to that braces.
      console.error("cldBar: not mounted —", err.message);
    }
  }

  // Re-point the embed when the user cycles the app theme. The whole iframe
  // is remounted rather than its src patched: the kit owns the color-scheme
  // derivation, and an iframe whose color-scheme disagrees with the embedded
  // page's loses transparency and paints an opaque canvas over the bar.
  // Reloading the tiny page is cheap.
  function syncCldBar() {
    var slot = document.getElementById("cldbar-slot");
    if (!slot || !window.cldBar) return;
    var frame = slot.querySelector("iframe.cldbar-embed");
    if (frame && frame.src === cldBar.cldBarUrl(cldbarOptions())) return;
    if (frame) frame.remove();
    setupCldBar();
  }

  window.addEventListener("themechange", syncCldBar);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setupCldBar);
  } else {
    setupCldBar();
  }

  window.cldBarGlue = { setup: setupCldBar, sync: syncCldBar };
})();

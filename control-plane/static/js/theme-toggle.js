/* ==========================================================================
   4ColThems — theme toggle (dependency-free, ~2 KB)
   ==========================================================================
   One button in your chrome cycles through the four themes in order:

       dark → light → hc → green → (back to dark)

   The chosen theme is written to <html data-theme="..."> and persisted in
   localStorage so it survives reloads. Pair this with the pre-paint snippet
   (snippets/prepaint.html) so the page restores the saved theme BEFORE first
   paint and never flashes the wrong colors.

   No framework, no build step, no icon font required — the button icons are
   inline SVG defined below. Just include this file with `defer`:

       <script defer src="/path/theme-toggle.js"></script>

   It auto-wires to a button with id="theme-cycle" on DOMContentLoaded and
   also exposes a tiny programmatic API on window.Theme4Col (see bottom) so a
   settings dropdown can call Theme4Col.set("light") directly.
   ========================================================================== */
(function () {
  "use strict";

  /* ---- CONFIG — edit these two lines per app ----------------------------
     STORAGE_KEY must match the key used in the pre-paint snippet.
     THEMES order == the cycle order == the `valid` map in the pre-paint
     snippet == the [data-theme] blocks in themes.css. Keep all in sync. */
  var STORAGE_KEY = "cldlab-theme";
  var THEMES = ["dark", "light", "hc", "green"];

  /* Per-theme presentation: the inline-SVG icon shown for the CURRENT theme
     and the human label used in the button tooltip. Icons stroke/fill with
     `currentColor`, so they inherit the button color (and the accent tint
     when the button is .active). */
  var ICONS = {
    // crescent moon
    dark: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M13.2 9.6A5.6 5.6 0 0 1 6.4 2.8a5.6 5.6 0 1 0 6.8 6.8z" fill="currentColor"/></svg>',
    // sun with rays
    light: '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="3.1" fill="currentColor"/><g stroke="currentColor" stroke-width="1.3" stroke-linecap="round"><path d="M8 1.4v1.8M8 12.8v1.8M1.4 8h1.8M12.8 8h1.8M3.3 3.3l1.3 1.3M11.4 11.4l1.3 1.3M12.7 3.3l-1.3 1.3M4.6 11.4l-1.3 1.3"/></g></svg>',
    // split circle = high contrast
    hc: '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M8 2a6 6 0 0 0 0 12z" fill="currentColor"/></svg>',
    // terminal window with prompt
    green: '<svg viewBox="0 0 16 16" aria-hidden="true"><rect x="1.5" y="2.5" width="13" height="11" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.3"/><path d="M4 6l2.4 2L4 10" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/><path d="M8.6 10.4h3.4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>',
  };
  var LABELS = {
    dark: "Dark Modern",
    light: "Light Modern",
    hc: "Dark High Contrast",
    green: "Garage Green",
  };

  var root = document.documentElement;

  function current() {
    var t = root.getAttribute("data-theme");
    return THEMES.indexOf(t) !== -1 ? t : THEMES[0];
  }

  function set(name) {
    if (THEMES.indexOf(name) === -1) return;
    root.setAttribute("data-theme", name);
    try { localStorage.setItem(STORAGE_KEY, name); } catch (e) {}
    render();
    // Notify non-CSS surfaces (e.g. embedded xterm terminals) that cannot be
    // re-skinned by CSS custom properties alone. See app.js applyTermTheme().
    try {
      window.dispatchEvent(new CustomEvent("themechange", { detail: name }));
    } catch (e) {}
  }

  function cycle() {
    var idx = THEMES.indexOf(current());
    set(THEMES[(idx + 1) % THEMES.length]);
  }

  function render() {
    var active = current();
    var btn = document.getElementById("theme-cycle");
    if (!btn) return;
    var iconHost = document.getElementById("theme-cycle-icon") || btn;
    iconHost.innerHTML = ICONS[active] || ICONS[THEMES[0]];
    var title = "Theme: " + (LABELS[active] || active) + " — click to cycle";
    btn.title = title;
    btn.setAttribute("aria-label", title);
    btn.classList.add("active");
  }

  function init() {
    // Ensure a valid theme is applied even if the pre-paint snippet is absent.
    if (THEMES.indexOf(root.getAttribute("data-theme")) === -1) {
      var saved = null;
      try { saved = localStorage.getItem(STORAGE_KEY); } catch (e) {}
      root.setAttribute("data-theme", THEMES.indexOf(saved) !== -1 ? saved : THEMES[0]);
    }
    var btn = document.getElementById("theme-cycle");
    if (btn) btn.addEventListener("click", cycle);
    render();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  /* Programmatic API — for settings menus, keyboard shortcuts, etc.
     Theme4Col.set("green"); Theme4Col.cycle(); Theme4Col.current();
     Theme4Col.list // ["dark","light","hc","green"] */
  window.Theme4Col = {
    set: set,
    cycle: cycle,
    current: current,
    list: THEMES.slice(),
    labels: LABELS,
  };
})();

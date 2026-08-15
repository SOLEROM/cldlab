/**
 * webterm pilot glue (loaded only when CLDLAB_WEBTERM=1).
 *
 * Runs after app.js (module scripts execute after classic scripts) but before
 * DOMContentLoaded, so it can replace app.js's terminal-related globals with
 * webterm-backed versions before the app boots. Everything non-terminal in
 * app.js (agents, README, config, splitter) is untouched.
 */
import { WebTerm } from '/webterm/static/webterm.js';

const KIND_RE = /^(shell|claude|exec)(-\d+)?$/;

const wt = new WebTerm({
  root: '#webterm-root',
  theme: () => (typeof activeThemeName === 'function' ? activeThemeName() : 'dark'),
  placeholder: 'No terminal session. Click + Shell or + Claude.',
});

// prefix comes from the server (it was previously hardcoded in three places)
const appConfig = await fetch('/api/config').then((r) => r.json()).catch(() => ({}));
const PREFIX = appConfig.tmux_prefix || 'cldcc-';

function sessionsOfAgent(name) {
  // exact parse of <prefix><agent>-<kind>[-N] — no substring matching
  return [...wt.sessions.keys()].filter((id) => {
    const stripped = id.startsWith(PREFIX) ? id.slice(PREFIX.length) : id;
    if (!stripped.startsWith(name + '-')) return false;
    return KIND_RE.test(stripped.slice(name.length + 1));
  });
}

/* ---- neutralize legacy terminal code paths ---- */
window.restoreSessions = () => {};        // webterm restores its own tabs
window.renderSessionTabs = () => {};      // webterm renders its own tab strip
window.showTerminalPlaceholder = () => {};
window.renameActiveTab = () => {};        // double-click a tab to rename
window.applyTermTheme = () => wt.refreshTheme();
window.addEventListener('themechange', () => wt.refreshTheme());

/* ---- webterm-backed replacements ---- */
window.newSession = async (kind) => {
  const name = state.selectedAgent;
  if (!name) return;
  await wt.createSession({ agent: name, kind });
};

window._autoOpenShell = async (name) => {
  if (sessionsOfAgent(name).length) return;
  await wt.createSession({ agent: name, kind: 'shell' });
};

window.activateSession = (sid) => wt.activate(sid);

window.killSession = (event, sid) => {
  if (event) event.stopPropagation();
  wt.killSession(sid);
};

window.closeAgentSessions = async (name) => {
  for (const id of sessionsOfAgent(name)) await wt.killSession(id);
};

window.resetAllSessions = async () => {
  if (!confirm('Kill ALL terminal sessions and PTY connections?')) return;
  await fetch('/webterm/api/reset', { method: 'POST' });
  location.reload();
};

/* on agent select, surface that agent's most recent terminal tab */
const legacySelectAgent = window.selectAgent;
window.selectAgent = async (name) => {
  await legacySelectAgent(name);
  const ids = sessionsOfAgent(name);
  if (ids.length) wt.activate(ids[ids.length - 1]);
};

await wt.mount();
// theme-toggle.js (deferred) may initialize after us — re-resolve once loaded
window.addEventListener('load', () => wt.refreshTheme());
window.wt = wt; // console access for debugging

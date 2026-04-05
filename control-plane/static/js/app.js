/* =============================================
   Claude Control Plane — Frontend SPA
   ============================================= */

'use strict';

const state = {
  socket: null,
  agents: [],
  selectedAgent: null,
  rightTab: 'readme',       // 'readme' | 'config'
  sessions: {},             // sessionId -> { term, fitAddon, element }
  activeSession: null,
  readmeContent: '',
  readmeEditing: false,
  pendingAutoOpen: null,    // agent name awaiting auto-shell on next 'running' status
  tabLabels: {},            // sessionId -> custom display label
  lastAgentSession: {},     // agentName -> last active sessionId for that agent
};

// ── Socket.IO ──────────────────────────────────────────────────────────────

function initSocket() {
  state.socket = io({ transports: ['websocket', 'polling'] });

  state.socket.on('connect', () => {
    setConnStatus(true);
    // Restore existing tmux sessions on every (re)connect
    restoreSessions();
  });
  state.socket.on('disconnect', () => setConnStatus(false));

  state.socket.on('output', ({ session, data }) => {
    const sess = state.sessions[session];
    if (sess) sess.term.write(data);
  });

  state.socket.on('agent_status', ({ agent, status }) => {
    const a = state.agents.find(x => x.name === agent);
    if (a) {
      a.status = status;
      renderAgentList();
      if (state.selectedAgent === agent) {
        updateToolbar();
        // Auto-open a shell if we were waiting for this agent to come up
        if (status === 'running' && state.pendingAutoOpen === agent) {
          state.pendingAutoOpen = null;
          _autoOpenShell(agent);
        }
      }
    }
  });

  state.socket.on('error', ({ message }) => console.warn('WS:', message));
}

function setConnStatus(ok) {
  document.getElementById('conn-dot').className = 'status-dot ' + (ok ? 'connected' : 'disconnected');
  document.getElementById('conn-label').textContent = ok ? 'Connected' : 'Disconnected';
}

async function resetAllSessions() {
  // Close all terminal UI panels
  for (const sid of Object.keys(state.sessions)) {
    await _closeSession(sid);
  }
  showTerminalPlaceholder();
  renderSessionTabs();

  // Kill everything server-side
  await fetchJSON('/api/sessions/reset', { method: 'POST' });
}

// ── Agents ─────────────────────────────────────────────────────────────────

async function refreshAgents() {
  try {
    const data = await fetchJSON('/api/agents');
    state.agents = data.agents || [];
    renderAgentList();
    if (state.selectedAgent) {
      const a = state.agents.find(x => x.name === state.selectedAgent);
      if (a) updateToolbar();
    }
  } catch (e) { console.error('refreshAgents:', e); }
}

function renderAgentList() {
  const el = document.getElementById('agent-list');
  if (!state.agents.length) {
    el.innerHTML = '<div class="empty">No agents configured</div>';
    return;
  }
  el.innerHTML = state.agents.map(a => `
    <div class="agent-item ${a.name === state.selectedAgent ? 'active' : ''}"
         onclick="selectAgent('${esc(a.name)}')">
      <div class="agent-item-dot s-${esc(a.status)}"></div>
      <div class="agent-item-info">
        <div class="agent-item-name">${esc(a.name)}</div>
        <div class="agent-item-meta">${esc(a.type)}</div>
      </div>
    </div>
  `).join('');
}

async function selectAgent(name) {
  state.selectedAgent = name;
  try { localStorage.setItem('ccp_selected_agent', name); } catch(e) {}
  renderAgentList();

  document.getElementById('workspace-empty').style.display = 'none';
  const panel = document.getElementById('agent-panel');
  panel.style.display = 'flex';
  panel.style.flexDirection = 'column';

  const a = state.agents.find(x => x.name === name);
  if (!a) return;

  document.getElementById('panel-agent-name').textContent = a.name;
  document.getElementById('panel-agent-type').textContent = a.type;
  updateToolbar();
  renderInfoPanel(a);
  loadReadme(name);
  renderSessionTabs();

  // Switch terminal view: restore last active session for this agent, or show placeholder
  const agentSessions = Object.keys(state.sessions).filter(sid => sid.includes(name));
  if (agentSessions.length) {
    const last = state.lastAgentSession[name];
    activateSession(last && agentSessions.includes(last) ? last : agentSessions[agentSessions.length - 1]);
  } else {
    Object.values(state.sessions).forEach(s => s.element.style.display = 'none');
    showTerminalPlaceholder();
  }
}

function updateToolbar() {
  const name = state.selectedAgent;
  const a = state.agents.find(x => x.name === name);
  if (!a) return;
  const badge = document.getElementById('panel-status-badge');
  badge.textContent = a.status;
  badge.className = `status-badge s-${a.status}`;

  const actions = document.getElementById('panel-actions');
  if (a.type !== 'docker') { actions.innerHTML = ''; return; }

  const st = a.status;
  const transitional = st === 'starting' || st === 'stopping';
  const canStart   = st === 'stopped' || st === 'error' || st === 'unknown';
  const canStop    = st === 'running';
  const canRestart = st === 'running';

  actions.innerHTML = `
    ${canStart    ? `<button class="btn btn-sm btn-success" onclick="agentAction('start')">▶ Start</button>` : ''}
    ${canStop     ? `<button class="btn btn-sm btn-danger"  onclick="agentAction('stop')">■ Stop</button>` : ''}
    ${canRestart  ? `<button class="btn btn-sm"             onclick="agentAction('restart')">↺ Restart</button>` : ''}
    ${transitional? `<button class="btn btn-sm" disabled>${st === 'starting' ? '⏳ Starting…' : '⏳ Stopping…'}</button>` : ''}
  `;
}

async function agentAction(action) {
  const name = state.selectedAgent;
  if (!name) return;

  // Close all open sessions before restart
  if (action === 'restart') await closeAgentSessions(name);

  // Immediately reflect transitional state so buttons disable right away
  const a = state.agents.find(x => x.name === name);
  if (a) {
    a.status = action === 'stop' ? 'stopping' : 'starting';
    updateToolbar();
    renderAgentList();
  }

  const data = await fetchJSON(`/api/agents/${name}/${action}`, { method: 'POST' });
  if (data.status !== 'ok') {
    // Revert optimistic status on error
    if (a) { a.status = action === 'stop' ? 'running' : 'stopped'; updateToolbar(); renderAgentList(); }
    state.pendingAutoOpen = null;
    alert(data.error || data.message || 'Error');
    return;
  }
  // Mark this agent for auto-shell once it reaches running
  if (action === 'start' || action === 'restart') state.pendingAutoOpen = name;
  setTimeout(refreshAgents, 800);
  setTimeout(refreshAgents, 2500);
}

// ── Right-panel tab switching ──────────────────────────────────────────────

function switchRightTab(tab) {
  state.rightTab = tab;
  document.querySelectorAll('.tabs .tab').forEach(el =>
    el.classList.toggle('active', el.dataset.tab === tab)
  );
  document.getElementById('right-tab-readme').style.display = tab === 'readme' ? 'flex' : 'none';
  document.getElementById('right-tab-config').style.display = tab === 'config'  ? 'flex' : 'none';
  if (tab === 'readme') {
    document.getElementById('right-tab-readme').style.flexDirection = 'column';
    // Always reload root readme when clicking the README tab
    if (state.selectedAgent) loadReadme(state.selectedAgent);
  }
  if (tab === 'config') {
    document.getElementById('right-tab-config').style.flexDirection = 'column';
  }
}

// ── Terminal sessions ───────────────────────────────────────────────────────

function _makeTerminal() {
  const term = new Terminal({
    theme: {
      background:'#0d1117', foreground:'#e6edf3', cursor:'#e6edf3', cursorAccent:'#0d1117',
      selectionBackground:'#264f7855',
      black:'#0d1117',    red:'#f85149',    green:'#3fb950',  yellow:'#d29922',
      blue:'#388bfd',     magenta:'#bc8cff', cyan:'#39c5cf',  white:'#b1bac4',
      brightBlack:'#6e7681', brightRed:'#ff7b72',   brightGreen:'#56d364',
      brightYellow:'#e3b341', brightBlue:'#79c0ff',  brightMagenta:'#d2a8ff',
      brightCyan:'#56d4dd',  brightWhite:'#e6edf3',
    },
    fontFamily:"'JetBrains Mono','Fira Code','Cascadia Code','Courier New',monospace",
    fontSize:13, lineHeight:1.3, cursorBlink:true, scrollback:5000, allowProposedApi:true,
  });
  const fitAddon = new FitAddon.FitAddon();
  term.loadAddon(fitAddon);
  term.loadAddon(new WebLinksAddon.WebLinksAddon());
  return { term, fitAddon };
}

function renderSessionTabs() {
  const container = document.getElementById('terminal-sessions');
  const agentSessions = Object.keys(state.sessions).filter(
    sid => !state.selectedAgent || sid.includes(state.selectedAgent)
  );
  if (!agentSessions.length) { container.innerHTML = ''; return; }
  container.innerHTML = agentSessions.map(sid => {
    const label = state.tabLabels[sid] || sid.replace(/^cldcc-/, '');
    return `
      <div class="session-tab ${sid === state.activeSession ? 'active' : ''}"
           onclick="activateSession('${esc(sid)}')">
        <span>${esc(label)}</span>
        <span class="session-tab-close" onclick="killSession(event,'${esc(sid)}')">✕</span>
      </div>`;
  }).join('');
}

async function _autoOpenShell(agentName) {
  // Check if there's already an open session for this agent
  const hasSession = Object.keys(state.sessions).some(sid => sid.includes(`-${agentName}-`));
  if (hasSession) return;
  // Create and open a shell session automatically
  const data = await fetchJSON('/api/sessions', {
    method: 'POST',
    body: JSON.stringify({ agent: agentName, kind: 'shell' }),
  });
  if (!data.error) openTerminalSession(data.session.session_id);
}

async function newSession(kind) {
  const name = state.selectedAgent;
  if (!name) return;
  const data = await fetchJSON('/api/sessions', {
    method: 'POST',
    body: JSON.stringify({ agent: name, kind }),
  });
  if (data.error) { alert(data.error); return; }
  openTerminalSession(data.session.session_id);
}

function openTerminalSession(sessionId) {
  if (state.sessions[sessionId]) { activateSession(sessionId); return; }

  const wrapper = document.getElementById('xterm-wrapper');
  wrapper.style.display = 'block';
  document.getElementById('terminal-placeholder').style.display = 'none';

  const termDiv = document.createElement('div');
  termDiv.style.cssText = 'position:absolute;inset:0;display:none;';
  wrapper.appendChild(termDiv);

  const { term, fitAddon } = _makeTerminal();
  term.open(termDiv);

  state.sessions[sessionId] = { term, fitAddon, element: termDiv, copyMode: false };

  // Key input — exit copy-mode first if active, then send keystroke
  term.onData(data => {
    const sess = state.sessions[sessionId];
    if (sess && sess.copyMode) {
      sess.copyMode = false;
      state.socket.emit('scroll', { session: sessionId, command: 'exit' });
    }
    state.socket.emit('input', { session: sessionId, data });
  });

  // Mouse wheel — drive tmux copy-mode scroll
  termDiv.addEventListener('wheel', e => {
    e.preventDefault();
    const sess = state.sessions[sessionId];
    if (!sess) return;
    const direction = e.deltaY < 0 ? 'up' : 'down';
    // Lines per notch: scale by deltaY magnitude, min 1 max 10
    const lines = Math.min(10, Math.max(1, Math.round(Math.abs(e.deltaY) / 20)));
    if (!sess.copyMode && direction === 'up') {
      sess.copyMode = true;
      state.socket.emit('scroll', { session: sessionId, command: 'enter' });
      setTimeout(() =>
        state.socket.emit('scroll', { session: sessionId, command: 'up', lines }), 50);
    } else if (sess.copyMode) {
      state.socket.emit('scroll', { session: sessionId, command: direction, lines });
    }
  }, { passive: false });

  new ResizeObserver(() => {
    if (state.activeSession === sessionId) {
      fitAddon.fit();
      state.socket.emit('resize', { session: sessionId, cols: term.cols, rows: term.rows });
    }
  }).observe(wrapper);

  activateSession(sessionId);
  setTimeout(() => {
    fitAddon.fit();
    state.socket.emit('subscribe', { session: sessionId, cols: term.cols, rows: term.rows });
  }, 120);
}

function activateSession(sessionId) {
  Object.values(state.sessions).forEach(s => s.element.style.display = 'none');
  state.activeSession = sessionId;
  // Remember last active session per agent so switching back restores it
  if (state.selectedAgent) state.lastAgentSession[state.selectedAgent] = sessionId;
  const sess = state.sessions[sessionId];
  if (sess) {
    sess.element.style.display = 'block';
    document.getElementById('xterm-wrapper').style.display = 'block';
    document.getElementById('terminal-placeholder').style.display = 'none';
    setTimeout(() => { sess.fitAddon.fit(); sess.term.focus(); }, 50);
  }
  renderSessionTabs();
}

async function killSession(event, sessionId) {
  event.stopPropagation();
  await _closeSession(sessionId);
  const remaining = Object.keys(state.sessions).filter(
    sid => !state.selectedAgent || sid.includes(state.selectedAgent)
  );
  if (remaining.length) activateSession(remaining[remaining.length - 1]);
  else showTerminalPlaceholder();
  renderSessionTabs();
}

function renameActiveTab() {
  const sid = state.activeSession;
  if (!sid) return;
  const current = state.tabLabels[sid] || sid.replace(/^cldcc-/, '');
  const name = prompt('Rename tab:', current);
  if (name === null) return;
  if (name.trim()) {
    state.tabLabels[sid] = name.trim();
  } else {
    delete state.tabLabels[sid];
  }
  renderSessionTabs();
}

async function _closeSession(sessionId) {
  state.socket.emit('unsubscribe', { session: sessionId });
  try { await fetch(`/api/sessions/${encodeURIComponent(sessionId)}`, { method: 'DELETE' }); } catch(e) {}
  const sess = state.sessions[sessionId];
  if (sess) { sess.term.dispose(); sess.element.remove(); delete state.sessions[sessionId]; }
  if (state.activeSession === sessionId) state.activeSession = null;
}

async function closeAgentSessions(agentName) {
  const ids = Object.keys(state.sessions).filter(sid => sid.includes(`-${agentName}-`));
  await Promise.all(ids.map(sid => _closeSession(sid)));
  showTerminalPlaceholder();
  renderSessionTabs();
}

function showTerminalPlaceholder() {
  document.getElementById('terminal-placeholder').style.display = 'flex';
  document.getElementById('xterm-wrapper').style.display = 'none';
}

// ── README — with in-pane navigation ──────────────────────────────────────
//
// state.mdNav: navigation history for the README pane
//   stack: array of { filePath, content }  (filePath relative to agent root)
//   index: current position in stack
//
// The agent's configured readme is always the "home" entry (index 0).

function _navState() {
  if (!state.mdNav) state.mdNav = { stack: [], index: -1 };
  return state.mdNav;
}

// Load the agent's root readme and reset history
async function loadReadme(agentName) {
  const agent = state.agents.find(a => a.name === agentName);
  const rootFile = agent ? agent.readme : 'README.md';
  state.mdNav = { stack: [], index: -1 };
  cancelReadmeEdit();
  // Use the /readme endpoint for the root file so it auto-creates if missing,
  // then hand off to the generic nav stack
  try {
    const data = await fetchJSON(`/api/agents/${encodeURIComponent(agentName)}/readme`);
    const entry = { filePath: rootFile, content: data.content || '' };
    state.mdNav.stack = [entry];
    state.mdNav.index = 0;
    state.readmeContent = entry.content;
    renderReadmeView();
    updateReadmeToolbar();
  } catch(e) {
    document.getElementById('readme-view').innerHTML =
      `<p style="color:var(--danger)">Failed to load README: ${esc(String(e))}</p>`;
  }
}

// Navigate to a file within the agent folder, optionally pushing onto history
async function _navTo(agentName, relPath, push = true) {
  const nav = _navState();

  const data = await fetchJSON(
    `/api/agents/${encodeURIComponent(agentName)}/file?path=${encodeURIComponent(relPath)}`
  );

  const notFound = data.error && data.error.startsWith('File not found');

  if (data.error && !notFound) {
    document.getElementById('readme-view').innerHTML =
      `<p style="color:var(--danger)">Cannot load <code>${esc(relPath)}</code>: ${esc(data.error)}</p>`;
    return;
  }

  const entry = { filePath: relPath, content: notFound ? '' : data.content };

  if (push) {
    nav.stack = nav.stack.slice(0, nav.index + 1);
    nav.stack.push(entry);
    nav.index = nav.stack.length - 1;
  } else {
    if (nav.index >= 0) nav.stack[nav.index] = entry;
  }

  state.readmeContent = entry.content;

  if (notFound) {
    // File doesn't exist yet — open editor so user can create it
    renderReadmeView();
    updateReadmeToolbar();
    toggleReadmeEdit();
  } else {
    cancelReadmeEdit();
    renderReadmeView();
    updateReadmeToolbar();
  }
}

function _currentNavEntry() {
  const nav = _navState();
  return nav.stack[nav.index] || null;
}

function readmeGoBack() {
  const nav = _navState();
  if (nav.index <= 0) return;
  nav.index--;
  const entry = nav.stack[nav.index];
  state.readmeContent = entry.content;
  cancelReadmeEdit();
  renderReadmeView();
  updateReadmeToolbar();
}

function readmeGoForward() {
  const nav = _navState();
  if (nav.index >= nav.stack.length - 1) return;
  nav.index++;
  const entry = nav.stack[nav.index];
  state.readmeContent = entry.content;
  cancelReadmeEdit();
  renderReadmeView();
  updateReadmeToolbar();
}

function updateReadmeToolbar() {
  const nav = _navState();
  const entry = _currentNavEntry();

  document.getElementById('readme-back-btn').disabled    = nav.index <= 0;
  document.getElementById('readme-forward-btn').disabled = nav.index >= nav.stack.length - 1;

  const label = document.getElementById('readme-file-label');
  if (entry) {
    const parts = entry.filePath.split('/');
    label.textContent = parts[parts.length - 1];
    label.title = entry.filePath;
  } else {
    label.textContent = '';
  }
}

function renderReadmeView() {
  const el = document.getElementById('readme-view');
  const html = typeof marked !== 'undefined'
    ? marked.parse(state.readmeContent || '*(empty)*')
    : `<pre>${esc(state.readmeContent)}</pre>`;
  el.innerHTML = html;

  // Intercept clicks on relative .md links — navigate within the pane
  el.querySelectorAll('a[href]').forEach(a => {
    const href = a.getAttribute('href');
    if (!href || href.startsWith('http') || href.startsWith('#') || href.startsWith('mailto')) return;
    if (!href.endsWith('.md')) return;

    a.addEventListener('click', e => {
      e.preventDefault();
      const agentName = state.selectedAgent;
      if (!agentName) return;

      // Resolve the target path relative to the current file's directory
      const entry = _currentNavEntry();
      const currentDir = entry
        ? entry.filePath.split('/').slice(0, -1).join('/')
        : '';
      const resolved = _resolvePath(currentDir, href);
      _navTo(agentName, resolved, true);
    });
  });
}

// Resolve a relative href against a base directory (no URL API needed)
function _resolvePath(baseDir, href) {
  const parts = (baseDir ? baseDir + '/' + href : href).split('/');
  const out = [];
  for (const p of parts) {
    if (p === '.' || p === '') continue;
    if (p === '..') out.pop();
    else out.push(p);
  }
  return out.join('/');
}

function toggleReadmeEdit() {
  const editor = document.getElementById('readme-editor');
  editor.style.display = 'flex';
  editor.value = state.readmeContent;
  editor.focus();
  document.getElementById('readme-view').style.display = 'none';
  document.getElementById('readme-new-btn').style.display = 'none';
  document.getElementById('readme-edit-btn').style.display = 'none';
  document.getElementById('readme-save-btn').style.display = '';
  document.getElementById('readme-cancel-btn').style.display = '';
  state.readmeEditing = true;
}

function cancelReadmeEdit() {
  state.readmeEditing = false;
  document.getElementById('readme-view').style.display = '';
  document.getElementById('readme-editor').style.display = 'none';
  document.getElementById('readme-new-btn').style.display = '';
  document.getElementById('readme-edit-btn').style.display = '';
  document.getElementById('readme-save-btn').style.display = 'none';
  document.getElementById('readme-cancel-btn').style.display = 'none';
}

async function newReadmePage() {
  const agentName = state.selectedAgent;
  if (!agentName) return;

  const agent = state.agents.find(a => a.name === agentName);
  const root = agent ? agent.path : agentName;

  // Suggest current subdirectory as prefix so user knows where they are
  const currentEntry = _currentNavEntry();
  const currentDir = currentEntry ? currentEntry.filePath.split('/').slice(0, -1).join('/') : '';
  const suggestion = currentDir ? currentDir + '/' : '';

  const name = prompt(`New .md file path (relative to ${root}):\n`, suggestion);
  if (!name) return;

  const relPath = name.trim().endsWith('.md') ? name.trim() : name.trim() + '.md';

  // Push a blank nav entry for the new file and open the editor
  const nav = _navState();
  const entry = { filePath: relPath, content: '' };
  nav.stack = nav.stack.slice(0, nav.index + 1);
  nav.stack.push(entry);
  nav.index = nav.stack.length - 1;

  state.readmeContent = '';
  renderReadmeView();
  updateReadmeToolbar();
  toggleReadmeEdit();
}

async function saveReadme() {
  const agentName = state.selectedAgent;
  if (!agentName) return;
  const entry = _currentNavEntry();
  if (!entry) return;

  const content = document.getElementById('readme-editor').value;
  const data = await fetchJSON(`/api/agents/${encodeURIComponent(agentName)}/file`, {
    method: 'POST',
    body: JSON.stringify({ path: entry.filePath, content }),
  });
  if (data.status === 'ok') {
    state.readmeContent = content;
    entry.content = content;      // update history entry too
    renderReadmeView();
    cancelReadmeEdit();
  } else {
    alert(data.error || 'Save failed');
  }
}

// ── Config (agent info) panel ───────────────────────────────────────────────

function renderInfoPanel(agent) {
  const panel = document.getElementById('info-panel');
  const sessions = Object.keys(state.sessions).filter(s => s.includes(agent.name));
  const rows = [
    ['Name',      esc(agent.name)],
    ['Type',      esc(agent.type)],
    ['Status',    `<span class="status-badge s-${esc(agent.status)}">${esc(agent.status)}</span>`],
    ['Path',      esc(agent.path)],
    ['Container', esc(agent.container || '-')],
    ['Share',     agent.share ? esc(agent.share) : '-'],
    ['make_run',  `<code>${esc(agent.make_run || '-')}</code>`],
    ['make_stop', `<code>${esc(agent.make_stop || '-')}</code>`],
    ['Tags',      agent.tags?.length
      ? agent.tags.map(t => `<span class="tag">${esc(t)}</span>`).join(' ')
      : '-'],
    ['Sessions',  sessions.length ? sessions.map(s => `<code>${esc(s)}</code>`).join('<br>') : 'none'],
  ];
  panel.innerHTML = rows.map(([label, value]) => `
    <div class="info-row">
      <div class="info-label">${label}</div>
      <div class="info-value">${value}</div>
    </div>`).join('');
}

// ── Config YAML editor modal ───────────────────────────────────────────────

async function openConfigEditor() {
  try {
    const [yamlData, helpData] = await Promise.all([
      fetchJSON('/api/config/yaml'),
      fetchJSON('/api/config/help'),
    ]);
    document.getElementById('config-yaml-editor').value = yamlData.content || '';
    document.getElementById('config-yaml-error').style.display = 'none';
    const helpEl = document.getElementById('config-help-panel');
    helpEl.innerHTML = typeof marked !== 'undefined'
      ? marked.parse(helpData.content || '')
      : `<pre>${esc(helpData.content || '')}</pre>`;
    document.getElementById('config-modal').style.display = 'flex';
  } catch(e) { alert('Failed to load config: ' + e); }
}

function closeConfigModal(event) {
  if (event && event.target !== document.getElementById('config-modal')) return;
  document.getElementById('config-modal').style.display = 'none';
}

// Also close on direct call
window.closeConfigModal = function(event) {
  if (!event || event.target === document.getElementById('config-modal')) {
    document.getElementById('config-modal').style.display = 'none';
  }
};

async function saveConfigYaml() {
  const content = document.getElementById('config-yaml-editor').value;
  const errEl = document.getElementById('config-yaml-error');
  try {
    const data = await fetchJSON('/api/config/yaml', {
      method: 'POST',
      body: JSON.stringify({ content }),
    });
    if (data.status === 'ok') {
      errEl.style.display = 'none';
      document.getElementById('config-modal').style.display = 'none';
      await refreshAgents();
    } else {
      errEl.textContent = data.error || 'Save failed';
      errEl.style.display = 'block';
    }
  } catch(e) {
    errEl.textContent = 'Request failed: ' + e;
    errEl.style.display = 'block';
  }
}

// ── Drag-to-resize splitter ────────────────────────────────────────────────

function initSplitter() {
  const handle  = document.getElementById('split-handle');
  const left    = document.querySelector('.split-left');
  const area    = document.querySelector('.split-area');
  let dragging  = false;
  let startX, startW;

  handle.addEventListener('mousedown', e => {
    dragging = true;
    startX = e.clientX;
    startW = left.getBoundingClientRect().width;
    handle.classList.add('dragging');
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  });

  document.addEventListener('mousemove', e => {
    if (!dragging) return;
    const areaW = area.getBoundingClientRect().width;
    const newW  = Math.min(Math.max(startW + (e.clientX - startX), 200), areaW - 200);
    left.style.width = newW + 'px';
    left.style.flex  = 'none';
    // Refit active terminal
    if (state.activeSession && state.sessions[state.activeSession]) {
      state.sessions[state.activeSession].fitAddon.fit();
    }
  });

  document.addEventListener('mouseup', () => {
    if (dragging) {
      dragging = false;
      handle.classList.remove('dragging');
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
      if (state.activeSession && state.sessions[state.activeSession]) {
        const sess = state.sessions[state.activeSession];
        sess.fitAddon.fit();
        state.socket.emit('resize', {
          session: state.activeSession,
          cols: sess.term.cols, rows: sess.term.rows,
        });
      }
    }
  });
}

// ── Session restore ────────────────────────────────────────────────────────

// Parse agent name from a full session id like "ccp-plug-affaan-shell" or "ccp-base-claude-2"
// Returns { agent, kind } or null.
function parseSessionId(sessionId, prefix, agentNames) {
  if (!sessionId.startsWith(prefix)) return null;
  const body = sessionId.slice(prefix.length); // e.g. "plug-affaan-shell" or "base-claude-2"

  // Try each known agent name (longest first to avoid prefix clashes)
  const sorted = [...agentNames].sort((a, b) => b.length - a.length);
  for (const agentName of sorted) {
    if (body === agentName || body.startsWith(agentName + '-')) {
      const rest = body.slice(agentName.length); // "-shell", "-claude-2", ""
      const kinds = ['shell', 'claude', 'exec'];
      for (const kind of kinds) {
        if (rest === '-' + kind || rest.startsWith('-' + kind + '-')) {
          return { agent: agentName, kind };
        }
      }
      // Unknown kind suffix — still restore under 'shell'
      if (rest.startsWith('-')) return { agent: agentName, kind: 'shell' };
    }
  }
  return null;
}

async function restoreSessions() {
  try {
    const [sessData, agentData, cfgData] = await Promise.all([
      fetchJSON('/api/sessions'),
      fetchJSON('/api/agents'),
      fetchJSON('/api/config'),
    ]);

    const sessions   = sessData.sessions  || [];
    const agents     = agentData.agents   || [];
    const agentNames = agents.map(a => a.name);
    const prefix     = cfgData.tmux_prefix || 'cldcc-';

    // Update local agent list without re-rendering yet
    state.agents = agents;
    renderAgentList();

    if (!sessions.length) {
      // No existing sessions — just select last agent if remembered
      _restoreSelectedAgent(agentNames);
      return;
    }

    // Group sessions by agent
    const byAgent = {};
    for (const sid of sessions) {
      const parsed = parseSessionId(sid, prefix, agentNames);
      if (!parsed) continue;
      (byAgent[parsed.agent] = byAgent[parsed.agent] || []).push(sid);
    }

    // Determine which agent to show: last selected (if it has sessions) or first with sessions
    let targetAgent = null;
    try { targetAgent = localStorage.getItem('ccp_selected_agent'); } catch(e) {}
    if (!targetAgent || !byAgent[targetAgent]) {
      targetAgent = Object.keys(byAgent)[0] || null;
    }

    // Open sessions for the target agent and select it
    if (targetAgent) {
      await selectAgent(targetAgent);
      for (const sid of (byAgent[targetAgent] || [])) {
        openTerminalSession(sid);
      }
      // Activate the last session
      const sids = byAgent[targetAgent];
      if (sids?.length) activateSession(sids[sids.length - 1]);
    }

    // Pre-open sessions for other agents in the background (no UI switch)
    for (const [agentName, sids] of Object.entries(byAgent)) {
      if (agentName === targetAgent) continue;
      for (const sid of sids) {
        // Create xterm + subscribe but don't switch view
        _openSessionSilent(sid);
      }
    }
  } catch(e) {
    console.warn('restoreSessions failed:', e);
  }
}

function _restoreSelectedAgent(agentNames) {
  let last = null;
  try { last = localStorage.getItem('ccp_selected_agent'); } catch(e) {}
  if (last && agentNames.includes(last)) selectAgent(last);
}

// Open a session and subscribe without switching the visible agent panel
function _openSessionSilent(sessionId) {
  if (state.sessions[sessionId]) return;

  const wrapper = document.getElementById('xterm-wrapper');
  const termDiv = document.createElement('div');
  termDiv.style.cssText = 'position:absolute;inset:0;display:none;';
  wrapper.appendChild(termDiv);

  const { term, fitAddon } = _makeTerminal();
  term.open(termDiv);

  state.sessions[sessionId] = { term, fitAddon, element: termDiv, copyMode: false };

  term.onData(data => {
    const sess = state.sessions[sessionId];
    if (sess && sess.copyMode) {
      sess.copyMode = false;
      state.socket.emit('scroll', { session: sessionId, command: 'exit' });
    }
    state.socket.emit('input', { session: sessionId, data });
  });

  termDiv.addEventListener('wheel', e => {
    e.preventDefault();
    const sess = state.sessions[sessionId];
    if (!sess) return;
    const direction = e.deltaY < 0 ? 'up' : 'down';
    const lines = Math.min(10, Math.max(1, Math.round(Math.abs(e.deltaY) / 20)));
    if (!sess.copyMode && direction === 'up') {
      sess.copyMode = true;
      state.socket.emit('scroll', { session: sessionId, command: 'enter' });
      setTimeout(() =>
        state.socket.emit('scroll', { session: sessionId, command: 'up', lines }), 50);
    } else if (sess.copyMode) {
      state.socket.emit('scroll', { session: sessionId, command: direction, lines });
    }
  }, { passive: false });

  setTimeout(() => {
    fitAddon.fit();
    state.socket.emit('subscribe', { session: sessionId, cols: term.cols, rows: term.rows });
  }, 150);
}

// ── Utilities ─────────────────────────────────────────────────────────────

async function fetchJSON(url, opts = {}) {
  const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
  const resp = await fetch(url, { ...opts, headers });
  return resp.json();
}

function esc(str) {
  if (str == null) return '';
  return String(str)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

// ── Init ──────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  initSocket();
  initSplitter();
  // restoreSessions() is called on socket 'connect' event — covers initial load and reconnects
  setInterval(refreshAgents, 8000);
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') document.getElementById('config-modal').style.display = 'none';
  });
});

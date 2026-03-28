# Claude Docker Control Plane — Final Spec

## 1. Purpose

Build a web-based control plane for managing multiple Claude CLI experiment environments.

Each environment is represented by a folder on disk and is typically started through its own `Makefile`. The system must let the user:

* view all environments
* start and stop them
* open terminal sessions in the browser
* keep per-environment documentation in `README.md`
* optionally open non-Docker shells in the shared project
* later compare outputs across multiple environments

This is not a generic chat UI. It is an orchestration and experimentation UI for multiple isolated Claude CLI environments.

---

## 2. Design principles

* Keep the existing Makefile workflow as the execution source of truth.
* Use tmux as the terminal/session persistence layer.
* Implement browser terminals using the same general architecture as the `ccpan` reference: browser terminal UI backed by a server that manages tmux sessions and PTY/websocket I/O. The reference project is explicitly tmux-based and includes dedicated tmux, PTY, and websocket modules. ([GitHub][1])
* Treat each environment folder as the authoritative source for its metadata and documentation.
* Keep the first version filesystem-native: no database required.
* Support both Docker-backed and plain local-shell sessions.
* Prefer a minimal, practical architecture over a heavy framework.

---

## 3. Core concepts

### 3.1 Agent

An Agent is one experiment environment.

Each agent maps to a folder and has:

* a unique name
* a filesystem path
* a `Makefile`
* a `README.md`
* optional metadata from config
* zero or more terminal sessions

An agent may represent:

* a Docker environment running Claude CLI
* a host shell in a project directory
* a compare/helper environment later

### 3.2 Session

A Session is an interactive terminal session shown in the browser.

Session types:

* `agent_terminal` — terminal attached to an agent workspace
* `agent_claude` — terminal intended to run Claude CLI in the agent environment
* `local_shell` — shell in a local/shared project folder without Docker
* `compare_shell` — optional later helper shell for diff/analysis tools

All terminal sessions must be backed by tmux so they persist if the browser tab reloads or disconnects. This matches the reference approach, whose value proposition is managing multiple tmux sessions from the browser. ([GitHub][1])

### 3.3 README

Each agent has a `README.md` file inside its folder.

This file is the root documentation and experiment notebook for that agent. It replaces any separate notes file.

The UI must load and show this README whenever that agent is selected.

---

## 4. Filesystem model

Expected structure:

```text
workspace/
├── control-plane/
│   ├── server/
│   ├── static/
│   ├── templates/
│   └── config.yaml
│
├── shared_project/
│
└── agents/
    ├── agentA/
    │   ├── Makefile
    │   ├── README.md
    │   ├── docker-compose.yml        # optional
    │   ├── .env                      # optional
    │   └── other agent files
    │
    ├── agentB/
    │   ├── Makefile
    │   ├── README.md
    │   └── ...
    │
    └── compare/
        ├── Makefile                  # optional
        └── README.md
```

Requirements:

* each configured agent path must resolve to a real folder
* `README.md` must exist or be auto-created
* all file access must remain inside the configured agent root

---

## 5. Config model

The app must load a YAML config file at boot.

Example:

```yaml
app:
  host: 127.0.0.1
  port: 5080
  tmux_socket: claude-control
  tmux_prefix: ccp-
  shared_project_path: ../shared_project

agents:
  - name: clean
    path: ../agents/clean
    type: docker
    make_run: "make run NAME=clean"
    make_stop: "make stop NAME=clean"
    readme: README.md
    auto_start: false
    tags: [baseline, no-plugins]

  - name: plugins_a
    path: ../agents/plugins_a
    type: docker
    make_run: "make run NAME=plugins_a"
    make_stop: "make stop NAME=plugins_a"
    readme: README.md
    auto_start: false
    tags: [plugins, experiment]

  - name: shared_shell
    path: ../shared_project
    type: local_shell
    readme: README.md
    auto_start: false
    tags: [host, utility]
```

Rules:

* `name` must be unique
* `type` initially supports:

  * `docker`
  * `local_shell`
* `readme` is relative to `path`
* `make_run` and `make_stop` are optional for `local_shell`
* config is read at startup and exposed via API

---

## 6. Primary user goals

The system must support these workflows:

1. User opens the web UI and sees all configured agents.
2. User clicks an agent and sees:

   * terminal area
   * README area
   * status/actions
3. User starts a Docker agent using the configured Makefile command.
4. User opens a browser terminal to that agent and runs Claude CLI.
5. User edits the agent’s `README.md` while working.
6. User can also open a plain shell into the shared project without Docker.
7. Later, user can run the same prompt across several agents and compare results.

---

## 7. UI specification

## 7.1 Main layout

The UI should be a single-page web app with three main areas:

### Left sidebar

Shows all agents and their status.

Each row should display:

* agent name
* status icon
* type
* optional tags

Example status:

* gray = unknown
* green = running
* red = stopped
* yellow = starting/stopping

### Main center area

Tabbed work area for the selected agent:

* Terminal
* README
* Info
* Compare (phase 2)

### Optional right utility area

Can be added later for:

* quick commands
* recent logs
* multi-agent compare summary

---

## 7.2 Agent selection behavior

When the user selects an agent:

* load its metadata
* load and render its README
* show current status
* show action buttons
* attach or create a tmux-backed terminal session when requested

---

## 7.3 Terminal UI behavior

The browser terminal must be implemented with a tmux-backed server-side session model inspired by `ccpan`, which exposes terminal functionality using PTY/websocket infrastructure around tmux. ([GitHub][1])

Requirements:

* browser terminal must be interactive and low-latency
* supports ANSI color, cursor movement, copy/paste, resize
* survives browser reload by reconnecting to the same tmux session
* one agent can have multiple tabs/sessions if needed
* terminal title should show agent name and session name

Session naming convention:

```text
<tmux_prefix><agent_name>[-<session_kind>][-<index>]
```

Examples:

```text
ccp-clean
ccp-clean-claude
ccp-plugins_a-shell
ccp-shared_shell
```

---

## 7.4 README panel

The README panel must:

* load `README.md` from the selected agent folder
* render markdown in view mode
* allow raw markdown editing in edit mode
* save changes back to disk
* auto-create a default README if missing

Suggested default file:

```md
# <agent-name>

## Purpose

## Setup

## Plugins / Skills

## Notes

## Experiments
```

---

## 7.5 Info panel

The Info panel should show:

* agent name
* path
* type
* tags
* configured commands
* tmux session names
* current runtime state

---

## 8. Terminal/session implementation requirements

The implementation should follow the reference style conceptually:

* tmux for persistence and multiplexing
* backend PTY/session manager
* websocket-driven terminal I/O
* browser UI managing multiple sessions. The reference explicitly describes modules for tmux operations, PTY connections, websocket handlers, and a browser-managed multi-session UI. ([GitHub][1])

Required backend responsibilities:

* create tmux sessions
* attach/detach client connections
* send keystrokes into tmux panes
* stream pane output to browser
* resize panes
* kill sessions when requested
* list active tmux sessions for the configured socket/prefix group

The system should support a configurable tmux socket and session prefix, similar to the reference project’s per-tab socket/prefix idea, but this app may keep one global socket/prefix for simplicity in v1. ([GitHub][1])

---

## 9. Agent lifecycle behavior

### For `docker` agents

Start:

* execute the configured `make_run` command in the agent folder
* mark state as `starting`
* verify success
* mark state as `running`
* optionally create a tmux terminal automatically

Stop:

* execute `make_stop` if configured
* otherwise allow a fallback stop command later
* mark state as `stopping`
* update state to `stopped`

Restart:

* stop then start

Status:

* at minimum track:

  * configured
  * starting
  * running
  * stopping
  * stopped
  * error

### For `local_shell` agents

No Docker lifecycle is required.
Only terminal session creation is needed.

---

## 10. Command execution rules

All lifecycle commands must:

* run in the agent’s configured folder
* capture stdout/stderr
* return structured success/failure responses
* never block the server event loop
* be logged to an internal run log

Command results should be viewable from the UI later.

---

## 11. README handling rules

For each agent:

* resolve `readme_full_path = path + "/" + readme`
* if missing, create it
* reject path traversal attempts
* support UTF-8
* set a reasonable max file size
* save atomically if practical

This file is the primary documentation surface, not a side note.

---

## 12. API specification

Suggested REST + websocket design.

### 12.1 Config and agent listing

`GET /api/config`

* returns app config summary

`GET /api/agents`

* returns all configured agents with current status

`GET /api/agents/<name>`

* returns metadata for one agent

### 12.2 README

`GET /api/agents/<name>/readme`

* returns markdown content

`POST /api/agents/<name>/readme`

* saves markdown content

Body:

```json
{
  "content": "# updated text"
}
```

### 12.3 Lifecycle

`POST /api/agents/<name>/start`

* runs `make_run`

`POST /api/agents/<name>/stop`

* runs `make_stop`

`POST /api/agents/<name>/restart`

* restarts agent

`GET /api/agents/<name>/status`

* returns current status

### 12.4 Terminal sessions

`GET /api/sessions`

* list active tmux-backed sessions

`POST /api/sessions`

* create a session

Body example:

```json
{
  "agent": "clean",
  "kind": "agent_claude"
}
```

`DELETE /api/sessions/<session_id>`

* kill session

### 12.5 Websocket

`WS /ws/sessions/<session_id>`

* bidirectional terminal stream
* input, output, resize, reconnect

---

## 13. Backend architecture

Recommended structure:

```text
control-plane/
├── server.py
├── requirements.txt
├── config.yaml
├── modules/
│   ├── config_manager.py
│   ├── agent_registry.py
│   ├── agent_runtime.py
│   ├── tmux_manager.py
│   ├── pty_bridge.py
│   ├── readme_manager.py
│   ├── command_runner.py
│   ├── routes.py
│   └── websocket_handlers.py
├── static/
│   ├── css/
│   └── js/
└── templates/
    └── index.html
```

This intentionally mirrors the separation style of your reference project, which separates config, tmux, PTY, routes, websocket handlers, templates, and static assets. ([GitHub][1])

Recommended stack:

* Python backend
* Flask or FastAPI
* websocket support
* tmux command integration
* xterm.js in frontend

Flask + Socket.IO is acceptable because your reference already uses that style. The reference README states Flask, Flask-SocketIO, CORS, and eventlet as dependencies. ([GitHub][1])

---

## 14. Frontend requirements

Frontend should be simple and practical.

Must support:

* agent list sidebar
* status indicators
* terminal pane using xterm.js or equivalent
* markdown render/edit panel
* action buttons: start, stop, restart, new terminal
* reconnect-friendly terminal behavior
* clean dark theme
* multiple browser tabs without corrupting server state

Nice to have:

* split view: terminal + README visible at same time
* multiple terminals side by side
* quick command buttons
* output/log modal

---

## 15. Tmux rules

The app must manage its own tmux namespace.

Global config:

* socket name
* session prefix

Do not interfere with unrelated tmux sessions on the machine.

All session listing and cleanup must be filtered to the configured socket and/or prefix.

---

## 16. Logging and state

No database is required in v1.

Use filesystem state:

* in-memory runtime state for active sessions
* optional JSON cache for session metadata
* log command executions to file

Suggested logs:

```text
runtime/logs/server.log
runtime/logs/commands.log
runtime/logs/sessions.log
```

---

## 17. Security and safety constraints

* bind locally by default
* no unauthenticated remote exposure in v1
* sanitize agent names
* sanitize session names
* no arbitrary path access outside configured roots
* no arbitrary command execution beyond configured lifecycle/session operations
* validate resize/input websocket events
* prevent killing unrelated tmux sessions

---

## 18. MVP scope

Version 1 must include:

* YAML config loading
* agent list
* start/stop/restart for Docker agents
* tmux-backed browser terminals
* README load/edit/save
* support for local shell agents
* status display
* stable reconnect behavior

This is enough to replace the current “many local shells + many docker exec flows” workflow.

---

## 19. Phase 2 scope

After MVP:

* compare mode
* send same prompt to multiple agents
* capture outputs side by side
* saved experiment runs
* quick commands per agent
* optional file browser
* optional command history
* optional per-agent runtime metadata like plugins/skills

---

## 20. Out of scope for MVP

Do not build these now:

* generic LLM provider integrations
* chat history database
* authentication/SSO
* distributed multi-host orchestration
* Kubernetes support
* full file editor beyond README
* GUI/X11 display support unless explicitly added later

Note: your reference `ccpan` includes X11/Xvfb/x11vnc/websockify support and flexible GUI panel layouts, but that should be treated as inspiration only, not mandatory scope for this Claude control-plane MVP. ([GitHub][1])

---

## 21. Acceptance criteria

The implementation is successful if:

1. I can define several agents in YAML.
2. The app loads them at startup.
3. I can start a Docker agent from the browser.
4. I can open a browser terminal backed by tmux for that agent.
5. Claude CLI can be run inside that terminal.
6. Reloading the browser does not destroy the tmux session.
7. Selecting an agent shows and allows editing its `README.md`.
8. I can also open a non-Docker shell for the shared project.
9. The system does not break my existing Makefile workflow.

---

## 22. Short implementation note for the coding agent

Build a minimal web control plane for tmux-backed browser terminals and Docker-agent orchestration.

Use:

* YAML config as source of truth
* per-agent folder model
* per-agent `README.md` as documentation source
* Makefile lifecycle commands for Docker agents
* tmux-backed persistent sessions
* browser terminal via websocket + PTY/tmux bridge
* simple SPA-like UI with sidebar, terminal, and README panel

Model the terminal/session architecture after the existing `ccpan` project structure and behavior, but limit the MVP to Claude CLI control-plane needs rather than full X11 GUI management. ([GitHub][1])

If you want, I can turn this into a tighter “copy-paste agent prompt” version with no explanation text around it.

[1]: https://github.com/SOLEROM/ccpan "GitHub - SOLEROM/ccpan: comand and control panels playground · GitHub"

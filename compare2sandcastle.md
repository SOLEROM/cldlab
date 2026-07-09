# cldlab vs Sandcastle — A Full Comparison

## What each system is

**cldlab** is a personal Docker-based lab for running isolated Claude Code CLI environments. It has a web control plane (Flask + SocketIO + xterm.js + tmux) that lets you manage multiple long-lived containers from a browser, connect terminals into them, and experiment with Claude interactively. Think of it as a multi-agent **cockpit**.

**Sandcastle** (`@ai-hero/sandcastle`) is a TypeScript library for orchestrating AI coding agents in isolated sandboxes programmatically. It is built for AFK (Away From Keyboard) automation: you write a script, call `run()`, and the library creates a container, runs the agent, tracks commits, merges branches, tears down the container, and returns a result. Think of it as a **headless agent runner**.

---

## Side-by-side

| Dimension | cldlab | Sandcastle |
|---|---|---|
| **Primary purpose** | Interactive experimentation lab | AFK automation / CI-grade orchestration |
| **Interaction model** | Human-in-the-loop via browser terminal | Programmatic scripts / `npx tsx main.ts` |
| **Container lifecycle** | Long-lived, persistent (start / stop / merge) | Ephemeral per-run (created → run → destroyed) |
| **Git integration** | None built-in; git lives inside the container | Deep: worktrees, branch strategies, commit tracking, merge-back |
| **Multi-agent** | Dashboard managing N containers simultaneously | `Promise.allSettled()` parallel runs; `parallel-planner` template |
| **Auth/credentials** | Seeded from template on first container start; persists inside container | Injected via `.sandcastle/.env` / env vars at run time |
| **Image management** | OverlayFS diff + merge (`make diff / merge`) to promote container → image | Expects pre-built image; `sandcastle docker build-image` just rebuilds |
| **Session resume** | Manual (`claude --resume` typed inside terminal) | Built-in: session capture to host JSONL, `run({ resumeSession })` and `.resume()` / `.fork()` |
| **Prompting** | User types directly in xterm.js terminal | Prompt files with `{{KEY}}` substitution and `` !`command` `` dynamic context |
| **Output capture** | tmux scrollback buffer | Log files, structured output (XML tags + Zod schema), `result.commits[]` |
| **Language / stack** | Python (Flask + SocketIO + eventlet), Makefile, HTML/JS | TypeScript (Effect-TS), Node.js, `npx tsx` |
| **Config model** | `config.yaml` with per-agent entries | `.sandcastle/` directory per repo (Dockerfile, prompt.md, .env) |
| **Sandbox providers** | Docker only | Docker, Podman, Vercel (Firecracker VMs), custom |
| **Completion signals** | None; agent runs until user stops it | `<promise>COMPLETE</promise>` (configurable) stops iteration loop early |
| **Token tracking** | None | Per-iteration usage (`inputTokens`, `cacheCreationInputTokens`, etc.) |

---

## cldlab — strengths

### 1. Interactive first
You see a live terminal and can type, interrupt, and steer the agent mid-session. This is the right UX for exploration: trying out new plugins, debugging prompts, experimenting with tool configurations.

### 2. Persistent state inside the container
The container accumulates history, installed packages, `.claude/` auth, and bash history across restarts. `make merge` promotes that state into a new image layer, so you can capture a known-good configuration and branch from it. This is the OverlayFS layering idea: base → login → custom layer.

### 3. Multi-container cockpit
The web UI shows all defined agents, their Docker status, and lets you open multiple tmux-backed terminals (shell / claude / exec) per agent simultaneously. Managing a farm of specialized containers (awesome, grif, gsd2, fman, etc.) from one browser tab is genuinely convenient.

### 4. No boilerplate per project
Sandcastle needs a `.sandcastle/` directory in every repo. cldlab manages everything centrally from `config.yaml` and a single control plane.

### 5. Share mounts
The `share:` field in `config.yaml` mounts a host directory into `~/share` in the container on demand, wired up automatically by the runtime even if the container is already running (it recreates the container transparently).

### 6. Zero API key management per run
Auth is baked into the container on first start and persists. You don't need to pass `ANTHROPIC_API_KEY` to every invocation.

---

## cldlab — weaknesses

### 1. No git-native workflow
There is no concept of worktrees, branches, or commit tracking. The agent edits files inside the container and you have to manually `git push` or copy changes out. Automation pipelines (plan → implement → review → merge) require hand-rolling everything.

### 2. No AFK / headless mode
If you close the browser the terminal is still alive in tmux, but you can't reliably wait for a run to finish and act on its result programmatically. There is no way to say "run this prompt, wait for it to complete, collect the commits, and open a PR."

### 3. No parallel orchestration
Running N agents on N branches simultaneously requires N browser tabs or manual tmux management. There is no `Promise.all()` equivalent.

### 4. No structured output or session resume
When you want the agent to return a typed answer (a JSON plan, a score, a summary) you have to parse it yourself. Session resume requires manually looking up the session ID and typing `claude --resume <id>` in the terminal.

### 5. No completion signals or iteration control
The agent runs until you interrupt it or it hits a context limit. There is no "stop when the task is done" protocol.

### 6. Python + Makefile stack
The control plane is Flask + eventlet. Extending it (adding new agent types, new orchestration patterns) means writing more Python. The Makefile DSL is a sharp edge for anything non-trivial.

---

## Sandcastle — strengths

### 1. Git-native by design
Branch strategies (`head`, `merge-to-head`, `branch`) are first-class. Every run lands on a branch, commits are tracked and returned as `result.commits[]`, and the merge-back is automatic. This makes it trivial to wire into a PR workflow.

### 2. Programmatic, composable orchestration
Because `run()` is just an async function that returns a typed result, you can build any pipeline in TypeScript:
```ts
const plan = await run({ agent: claudeCode("claude-opus-4-8"), output: Output.object({ tag: "plan", schema }) });
await Promise.allSettled(plan.output.issues.map(issue => run({ ... })));
```
The `parallel-planner` template is a ready-made example of this.

### 3. Session resume and fork
After any run you can call `result.resume("continue where you left off")` or `result.fork("try a different approach")` — the session JSONL is captured automatically to the host and transferred back into the next sandbox. This is a major capability for iterative, multi-turn automation.

### 4. Structured output
`Output.object({ tag, schema })` extracts and validates typed JSON from the agent's stdout without any parsing code. Combined with `resumeSession` on error, you can automatically ask the agent to retry a malformed response.

### 5. Multi-provider
Switch between Docker, Podman, or Vercel microVMs by changing one import. Custom providers are well-defined via `createBindMountSandboxProvider` / `createIsolatedSandboxProvider`.

### 6. Templates for common patterns
`simple-loop`, `sequential-reviewer`, `parallel-planner`, and `parallel-planner-with-review` are ready-made orchestration blueprints that cover 80% of real CI/CD agent workflows.

### 7. Safety and UID alignment
Sandcastle pre-flight checks that the image UID matches the host UID to prevent permission errors (ADR 0014). Abort signals, per-step timeouts, and shutdown registry cleanup make it production-grade.

---

## Sandcastle — weaknesses

### 1. No interactive UI
There is no dashboard. You run a script in a terminal and read log files. If you want to watch the agent in real time you set `logging: { type: "stdout" }`, but you can't steer it mid-run.

### 2. Ephemeral containers — no state accumulation
Every `run()` creates a fresh container. If you want installed packages to persist, you copy `node_modules` via `copyToWorktree` or bake them into the image. There is no OverlayFS layering to capture a known-good state.

### 3. Per-repo configuration
Every repo needs a `.sandcastle/` directory with its own Dockerfile, prompt files, and `.env`. For a lab that just wants to experiment with Claude in various containers, this is overhead.

### 4. TypeScript / Node.js only
The caller script must be TypeScript/JavaScript. If your automation stack is Python, Go, or shell, you're calling it as a subprocess or not using it at all.

### 5. No web dashboard for multi-agent monitoring
When `Promise.allSettled` runs 10 parallel agents, you have 10 log files and console output intermixed. There is no single pane of glass showing their status.

### 6. Requires per-repo Docker image build
`sandcastle docker build-image` must be run before any `run()` call. In cldlab, the image is built once and shared across agents.

---

## Core philosophical difference

| | cldlab | Sandcastle |
|---|---|---|
| **Agent is...** | A persistent environment you live inside | A function call with a return value |
| **You are...** | A pilot steering the agent interactively | A programmer composing async workflows |
| **State lives...** | Inside the container | In git (commits, branches) |
| **Success looks like...** | A conversation that produced useful output | A PR on a named branch with tracked commits |

---

## What each is best for

**Use cldlab when you:**
- Are exploring: testing new plugins, MCP servers, aliases, prompt strategies
- Need to authenticate Claude or `gh` once and reuse that state
- Want to manage a fleet of specialized agent containers from one UI
- Need a REPL-like environment to iterate on ideas interactively
- Want to use OverlayFS to snapshot a working configuration into a new image layer

**Use Sandcastle when you:**
- Want to run agents unattended and act on their results programmatically
- Need agents to produce commits on named branches (CI, automated PRs)
- Are building multi-agent pipelines (plan → implement → review → merge)
- Need session resume or fork across runs
- Want typed, schema-validated output from the agent
- Are deploying to CI (GitHub Actions, etc.) where there is no browser

---

## Potential synthesis

The two systems are not really competitors — they solve different problems. A natural combination:

1. **Prototype interactively in cldlab** — try plugins, dial in prompts, get auth sessions stable.
2. **Automate at scale with Sandcastle** — once a workflow is proven, encode it as a `.sandcastle/main.ts` script that runs in CI or on demand.

The main gap Sandcastle doesn't cover that cldlab does: **interactive terminal access to a running agent**. The main gap cldlab doesn't cover that Sandcastle does: **git-native automation with commit tracking, session resume, and parallel orchestration**. Adding a "headless run" mode to cldlab's control plane (a REST endpoint that triggers a `docker exec` with a prompt file, waits for completion, and returns the result) would close the automation gap while keeping the interactive UI.

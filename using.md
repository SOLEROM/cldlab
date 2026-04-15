# Tool Usage Map

Five plugins, hundreds of tools. This is the map for knowing exactly which tool to reach for and when.

---

## Table of Contents

- [Plugin Personalities](#plugin-personalities)
- [By Workflow Stage](#by-workflow-stage)
  - [Stage 0 — Requirements & idea validation](#stage-0--before-you-touch-code-requirements--idea-validation)
  - [Stage 1 — Design (UI/UX)](#stage-1--design-uiux)
  - [Stage 2 — Implementation](#stage-2--implementation)
  - [Stage 3 — Debugging](#stage-3--debugging)
  - [Stage 4 — Code Review](#stage-4--code-review)
  - [Stage 5 — Testing & QA](#stage-5--testing--qa)
  - [Stage 6 — Security](#stage-6--security)
  - [Stage 7 — Ship](#stage-7--ship)
  - [Stage 8 — Documentation](#stage-8--documentation)
  - [Stage 9 — Learning & Memory](#stage-9--learning--memory)
  - [Stage 10 — Retrospective & Health](#stage-10--retrospective--health)
- [Safety & Guardrails](#safety--guardrails)
- [Browser & Authenticated Web Work](#browser--authenticated-web-work)
- [Multi-Model / Second Opinion](#multi-model--second-opinion)
- [Quick Decision Cheat Sheet](#quick-decision-cheat-sheet)
- [When Plugins Overlap: How to Pick](#when-plugins-overlap-how-to-pick)

---

## Plugin Personalities

Before the map, understand the _character_ of each plugin — that's the fastest orientation:

| Plugin | Character | Reach for it when... |
|--------|-----------|----------------------|
| **supow** (Superpowers) | Strict workflow enforcer | You want a disciplined, gate-driven dev cycle: design → plan → code → test → ship |
| **gstack** | Virtual product team + browser | You need design, product thinking, browser QA, or a full ship pipeline |
| **omc** (oh-my-claudecode) | Autonomous execution engine | You want to hand off a task and let it run: autopilot, persistence, parallel workers |
| **ecc** (Everything Claude Code) | Deep language expertise + learning system | You need language-specific reviewers, build fixers, or want Claude to learn your patterns |
| **awesome** | Broad specialist roster | You need a domain expert that neither gstack nor omc has — 136 agents covering everything |

---

## By Workflow Stage

### Stage 0 — Before you touch code: Requirements & idea validation

**Fuzzy idea, not sure what to build**
```
/office-hours          # gstack — 6 forcing questions, challenges your premise
/deep-interview        # omc — Socratic interview that gates you until requirements are concrete
```

**Clear goal, need a plan**
```
/brainstorming         # supow — REQUIRED before any feature work, refines design before code
/writing-plans         # supow — REQUIRED after brainstorming, breaks work into 2-5min tasks
/plan                  # omc — strategic planning with interview workflow (uses Opus)
ralplan                # omc — consensus planning, prevents running autopilot on vague requests
```

**Already have a plan, want it pressure-tested**
```
/autoplan              # gstack — runs CEO → design → eng → DX review in one pipeline
/plan-ceo-review       # gstack — scope expansion / "what's the 10-star version"
/plan-eng-review       # gstack — architecture, data flow, edge cases, hidden assumptions
/plan-design-review    # gstack — design quality 0-10 per dimension, interactive fixes
/plan-devex-review     # gstack — DX review: TTHW, friction, developer personas
```

Use the table from `gstack/review.md` to pick which plan review applies:
- **End users (UI/web)** → `/plan-design-review`
- **Developers (API/CLI/SDK)** → `/plan-devex-review`
- **Architecture/data** → `/plan-eng-review`
- **Everything** → `/autoplan`

---

### Stage 1 — Design (UI/UX)

```
/design-consultation   # gstack — build design system from scratch, research landscape
/design-shotgun        # gstack — generate 4-6 AI variants, pick favorites, iterate visually
/design-html           # gstack — turn approved mockup into production HTML (Pretext layout)
/design-review         # gstack — designer's-eye QA pass after you've built something
```

The pipeline is linear: `consultation → shotgun → html → design-review`

For quick component work without a full design system:
```
ECC: frontend-design skill     # high-quality production UI from description
omc: designer agent            # UI/UX design agent (Sonnet)
awesome: ui-designer agent     # Figma-to-code, component libraries
```

---

### Stage 2 — Implementation

**Standard disciplined feature work**
```
/using-git-worktrees           # supow — isolate work on new branch first
/test-driven-development       # supow — RED-GREEN-REFACTOR, deletes code written before tests
/subagent-driven-development   # supow — dispatches fresh subagent per task with two-stage review
/executing-plans               # supow — same but with human checkpoints between batches
```

**Autonomous / unattended execution**
```
autopilot              # omc magic keyword — fully autonomous, just describe and walk away
ralph                  # omc magic keyword — persistence mode, won't stop until verified done
ultrawork              # omc skill — parallel execution engine, high-throughput task completion
/team N:executor       # omc — N coordinated agents: plan → prd → exec → verify → fix loop
```

**Language-specific work** — reach for the ECC agent for that language:
```
ecc agents: typescript-reviewer, python-reviewer, go-reviewer, rust-reviewer,
            kotlin-reviewer, java-reviewer, cpp-reviewer, database-reviewer
```

**Multi-service / complex architecture**
```
awesome: fullstack-engineer, backend-developer, frontend-architect, microservices-architect
ecc: claude-devfleet skill     # plan, dispatch parallel agents in isolated worktrees, monitor
/dispatching-parallel-agents   # supow — when 2+ independent tasks can run without shared state
```

---

### Stage 3 — Debugging

**Systematic root cause investigation (default)**
```
/investigate           # gstack — 4-phase: investigate → analyze → hypothesize → implement
                       # Iron Law: no fix without root cause. Auto-freezes affected module.
```

**Competing hypotheses, evidence-driven**
```
/trace                 # omc — parallel tracer agents, competing hypotheses with evidence scoring
tracer agent           # omc — evidence-driven causal tracing, next-probe recommendations
```

**Quick structured debug workflow**
```
/systematic-debugging  # supow — before proposing any fix
/debug                 # omc — diagnose session/repo state using logs and traces
```

**Build errors (language-specific)**
```
ecc agents: build-error-resolver, go-build-resolver, rust-build-resolver,
            kotlin-build-resolver, java-build-resolver, cpp-build-resolver,
            pytorch-build-resolver, typescript-reviewer
```

---

### Stage 4 — Code Review

**Pre-PR review (finding real bugs)**
```
/review                # gstack — staff-engineer review, finds bugs that pass CI
/codex                 # gstack — independent OpenAI Codex review (second opinion, different AI)
                       # Run both → cross-model analysis showing overlapping and unique findings
```

**Review after a plan step completes**
```
/requesting-code-review    # supow — review against plan, reports by severity, blocks on critical
code-reviewer agent        # supow — reviews implementation against plan and coding standards
```

**Deep review with structured feedback**
```
critic agent           # omc — thorough multi-perspective review (Opus)
code-reviewer agent    # omc — severity-rated feedback, SOLID checks, logic defects
```

**Language-specific review**
```
ecc: typescript-reviewer, python-reviewer, go-reviewer, rust-reviewer,
     kotlin-reviewer, java-reviewer, cpp-reviewer, database-reviewer
```

**After receiving review feedback**
```
/receiving-code-review     # supow — before implementing suggestions, verifies they're correct
```

---

### Stage 5 — Testing & QA

**TDD (before writing code)**
```
/test-driven-development   # supow — enforces RED-GREEN-REFACTOR strictly
/testing/tdd               # awesome command — same discipline via command
ecc: tdd-guide agent
```

**QA a live app in the browser**
```
/qa                    # gstack — test, find bugs, fix, generate regression tests, re-verify
/qa-only               # gstack — same but report-only, no code changes
ultraqa                # omc — QA cycling: test → verify → fix → repeat until goal met
```

**Verification before claiming done**
```
/verification-before-completion  # supow — run this before any "it's fixed/done" claim
/verify                          # omc — evidence-based completion check
```

**Coverage and e2e**
```
/testing/test-coverage     # awesome — coverage audit
/testing/e2e               # awesome — Playwright e2e
ecc: e2e-runner agent      # ECC e2e runner
```

---

### Stage 6 — Security

**Full security audit**
```
/cso                   # gstack — CSO mode, OWASP Top 10 + STRIDE, 8/10+ confidence gate
/security/audit        # awesome command
```

**Pre-commit security check**
```
security-reviewer agent    # omc or ecc — OWASP Top 10, secrets, unsafe patterns
/security/hardening        # awesome command
ecc: security-review skill # checklist for auth, input, secrets, API, payments
```

**Scan Claude config for vulnerabilities**
```
ecc: security-scan skill   # scans .claude/, settings.json, MCP configs, hooks (AgentShield)
```

---

### Stage 7 — Ship

**Full ship workflow**
```
/ship                  # gstack — sync main, run tests, audit coverage, push, open PR
/finishing-a-development-branch  # supow — verifies tests, presents merge/PR/keep/discard options
```

**After PR is approved**
```
/land-and-deploy       # gstack — merge PR, wait for CI and deploy, verify production health
```

**Post-deploy monitoring**
```
/canary                # gstack — watches live app for errors, performance regressions
/benchmark             # gstack — page load, Core Web Vitals before/after comparison
```

**Release management**
```
/git/release           # awesome command — full release workflow
/release               # omc skill — analyzes repo release rules, guides the release
```

---

### Stage 8 — Documentation

**Post-ship docs update**
```
/document-release      # gstack — reads all project docs, cross-references the diff, updates stale ones
```

**API / dev docs**
```
/documentation/api-docs    # awesome command
writer agent               # omc — README, API docs, comments (Haiku, cost-efficient)
ecc: doc-updater agent
```

**Onboarding / walkthroughs**
```
/documentation/onboard     # awesome command
ecc: code-tour skill       # creates CodeTour .tour files with step-by-step walkthroughs
```

---

### Stage 9 — Learning & Memory

**Mid-session: just solved something non-trivial**
```
/learn                 # gstack — save project-specific patterns, persists across sessions
learner                # omc skill — extract a reusable skill from current conversation
skillify               # omc skill — turn a repeatable workflow into a skill draft
```

**Ongoing automatic learning**
```
ecc: continuous-learning-v2 skill  # instinct-based, saves patterns via hooks automatically
/instinct-status                   # ecc — show learned instincts with confidence scores
/evolve                            # ecc — cluster related instincts into reusable skills
```

**Persistent knowledge base**
```
wiki                   # omc — LLM Wiki, persistent markdown KB that compounds across sessions
ecc: continuous-learning skill
```

---

### Stage 10 — Retrospective & Health

**Weekly retro**
```
/retro                 # gstack — team-aware, per-person breakdowns, shipping streaks, trends
                       # /retro global — across all your projects and AI tools
```

**Code health check**
```
/health                # gstack — code quality dashboard: type checker, linter, test suite
```

**Cleanup / dead code**
```
/refactoring/dead-code     # awesome command
ecc: refactor-cleaner agent
ai-slop-cleaner            # omc skill — remove AI-generated slop safely
```

---

## Safety & Guardrails

```
/careful               # gstack — warns before rm -rf, DROP TABLE, force-push
/freeze <dir>          # gstack — lock edits to one directory, prevents drift
/guard                 # gstack — activates both careful + freeze together
/unfreeze              # gstack — clear the freeze boundary
eco                    # omc magic keyword — budget mode, 30-50% token savings
```

---

## Browser & Authenticated Web Work

```
/browse                # gstack — real Chromium, real clicks, screenshots (~100ms/command)
/open-gstack-browser   # gstack — headed Chromium with anti-bot stealth, sidebar agent
/setup-browser-cookies # gstack — import cookies from real browser for authenticated testing
/pair-agent            # gstack — share browser with another AI agent (cross-agent coordination)
/devex-review          # gstack — actually tests your onboarding: navigates, times TTHW, screenshots
```

---

## Multi-Model / Second Opinion

```
/codex                 # gstack — independent OpenAI Codex review of same diff
/ask codex             # omc — send any query to Codex
ccg                    # omc — tri-model: Claude + Codex + Gemini synthesized output
```

---

## Quick Decision Cheat Sheet

| Situation | Tool | Plugin |
|-----------|------|--------|
| Vague idea | `/office-hours` or `/deep-interview` | gstack / omc |
| Before any feature | `/brainstorming` | supow |
| Writing a plan | `/writing-plans` | supow |
| Pressure-test a plan | `/autoplan` | gstack |
| UI design from scratch | `design-shotgun → design-html` | gstack |
| Implement disciplined | `using-git-worktrees → test-driven-development` | supow |
| Let it run itself | `autopilot` or `ralph` | omc |
| Build fails | `build-error-resolver` or language-specific build resolver | ecc |
| Debug a bug | `/investigate` | gstack |
| Debug with evidence tree | `/trace` or `tracer` agent | omc |
| Pre-PR review | `/review` + `/codex` | gstack |
| QA a web app | `/qa` | gstack |
| TDD enforcement | `/test-driven-development` | supow |
| Security audit | `/cso` | gstack |
| Quick security check | `security-reviewer` agent | omc / ecc |
| Ship | `/ship` | gstack |
| Post-merge monitoring | `/land-and-deploy` → `/canary` | gstack |
| Update docs after ship | `/document-release` | gstack |
| Save what you learned | `/learn` or `learner` | gstack / omc |
| Weekly retro | `/retro` | gstack |
| Autonomous parallel work | `ultrawork` | omc |
| Need a domain specialist | Browse awesome agents | awesome |

---

## When Plugins Overlap: How to Pick

**Planning:** Use **supow** `writing-plans` for execution plans (task-level, files, steps). Use **gstack** `plan-*-review` for strategic validation (product, architecture, design angles). Use **omc** `/plan` when you want an interview to crystallize vague requirements first.

**Debugging:** Use **gstack** `/investigate` as default — it's the most structured. Add **omc** `/trace` when you want competing hypotheses evaluated simultaneously. Use **ecc** build resolvers for compile/type errors specifically.

**Code Review:** Use **gstack** `/review` as the standard pre-PR gate. Add `/codex` for a second opinion from a different model. Use **supow** `code-reviewer` agent when reviewing against a specific plan. Use **omc** `critic` for the most thorough multi-perspective critique.

**Autonomous work:** **supow** `executing-plans` keeps you in the loop with checkpoints. **omc** `autopilot` / `ralph` hands off completely. Pick based on how much control you want.

**Testing:** Use **supow** `test-driven-development` to enforce discipline while writing. Use **gstack** `/qa` to find bugs in a running app. Use **omc** `ultraqa` to cycle until a quality bar is met.

**Learning:** Use **gstack** `/learn` for project-specific patterns you want to recall next session. Use **ecc** `continuous-learning-v2` for automatic instinct capture via hooks. Use **omc** `wiki` for a persistent structured knowledge base.

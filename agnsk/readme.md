# agent-skills

* ref: https://github.com/addyosmani/agent-skills

## usage

* https://github.com/addyosmani/agent-skills#all-20-skills

## Features
Production-grade engineering workflows that force AI coding agents to actually behave like senior engineers, not interns shipping prototypes to prod.
→ Spec before code (no more "what are we even building")
→ Plan-mode task breakdown into verifiable chunks
→ Incremental implementation in thin vertical slices
→ TDD with the Prove-It pattern (reproduce bugs as failing tests first)
→ Chrome DevTools MCP so the agent has real eyes in the browser
→ 5-axis code review (correctness, readability, architecture, security, perf)
→ OWASP-aware security hardening
→ Git workflow, CI/CD gates, ADRs, staged rollouts


## tree

```
agent-skills/
├── skills/                            # 20 core skills (SKILL.md per directory)
│   ├── idea-refine/                   #   Define
│   ├── spec-driven-development/       #   Define
│   ├── planning-and-task-breakdown/   #   Plan
│   ├── incremental-implementation/    #   Build
│   ├── context-engineering/           #   Build
│   ├── source-driven-development/     #   Build
│   ├── frontend-ui-engineering/       #   Build
│   ├── test-driven-development/       #   Build
│   ├── api-and-interface-design/      #   Build
│   ├── browser-testing-with-devtools/ #   Verify
│   ├── debugging-and-error-recovery/  #   Verify
│   ├── code-review-and-quality/       #   Review
│   ├── code-simplification/          #   Review
│   ├── security-and-hardening/        #   Review
│   ├── performance-optimization/      #   Review
│   ├── git-workflow-and-versioning/   #   Ship
│   ├── ci-cd-and-automation/          #   Ship
│   ├── deprecation-and-migration/     #   Ship
│   ├── documentation-and-adrs/        #   Ship
│   ├── shipping-and-launch/           #   Ship
│   └── using-agent-skills/            #   Meta: how to use this pack
├── agents/                            # 3 specialist personas
├── references/                        # 4 supplementary checklists
├── hooks/                             # Session lifecycle hooks
├── .claude/commands/                  # 7 slash commands
└── docs/                              # Setup guides per tool

```
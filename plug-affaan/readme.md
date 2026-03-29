# everything-claude-code

* home git : https://github.com/affaan-m/everything-claude-code
* [skill list form docker](./skill.list)
* guides: https://x.com/affaanmustafa/status/2014040193557471352

## install

* https://github.com/affaan-m/everything-claude-code

# features

```
1./ 28 agents - typescript-reviewer, python-reviewer, go-reviewer, rust-reviewer, kotlin-reviewer, java-reviewer, database-reviewer, and more
2./ 116 skills - coding-standards, backend-patterns, frontend-patterns, tdd-workflow, security-review, eval-harness, verification-loop, and 100+ more
3./ 59 commands - /tdd, /plan, /e2e, /code-review, /build-fix, /learn, /instinct-status, /evolve, /security-scan, /harness-audit
4./ 15+ hooks - session-start loads context, session-end saves state, pre-compact preserves info, suggest-compact triggers at logical breakpoints
5./ 34 rules across 6 languages - common/, typescript/, python/, golang/, swift/, php/
6./ 14 MCP configurations - GitHub, Supabase, Vercel, Railway, and more
7./ SQLite state store - tracks session history, skill health, instinct confidence scores
8./ AgentShield - security scanner with 1282 tests, 102 rules. Scans CLAUDE[.]md, settings.json, MCP configs, hooks for vulnerabilities.
9./ Selective installation - ./install[.]sh typescript python only installs what you need
10./ Cross-platform - Claude Code, Codex, Cursor, OpenCode. AGENTS[.]md at root is universal.
```

## refactor-clean


## nested

for some code can you /refactor-clean  ,then /test-coverage , finally do a run of /e2e


## rules

```
~/.claude/rules/
  security.md      # No hardcoded secrets, validate inputs
  coding-style.md  # Immutability, file organization
  testing.md       # TDD workflow, 80% coverage
  git-workflow.md  # Commit format, PR process
  agents.md        # When to delegate to subagents
  performance.md   # Model selection, context management
```


## strategic-compact    

skills/strategic-compact




## continuous-learning

When Claude Code discovers something that isn't trivial- a debugging technique, a workaround, some project-specific pattern - it saves that knowledge as a new skill. Next time a similar problem comes up, the skill gets loaded automatically.

https://github.com/affaan-m/everything-claude-code/tree/main/skills/continuous-learning


## learn

un mid-session when you've just solved something non-trivial. It prompts you to extract the pattern right then, drafts a skill file, and asks for confirmation before saving

https://github.com/affaan-m/everything-claude-code/blob/main/commands/learn.md


## Session Log 

create ~/.claude/sessions/YYYY-MM-DD-topic.tmp` - one file per session with current state, completed items, blockers, key decisions, and context for next session.


## Self-Improving 

reflecting over session logs to distill user preferences - essentially building a "diary" of what works and what doesn't. After each session, a reflection agent extracts what went well, what failed, what corrections you made. These learnings update a memory file that loads in subsequent sessions.



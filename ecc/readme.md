# ECC everything-claude-code

* project git : https://github.com/affaan-m/everything-claude-code
* [skill list form docker](./skill.list) | [install log](./install.log)


# features

* [my short guide](./shortGuide.md)
* [security guide](./security.md)
* [hh-plot](./hh.md)

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


## models

```
/model sonnet     - 	Default for most tasks
/model opus 	    -   Complex architecture, debugging, deep reasoning
```

## token optimization

```
~/.claude/settings.json
=========================
{
  "model": "sonnet",
  "env": {
    "MAX_THINKING_TOKENS": "10000",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50",
      "CLAUDE_CODE_SUBAGENT_MODEL": "haiku"
  }
}
```
# my guide


### magic keyword 

```
→ Type "autopilot" and it builds the whole thing autonomously
→ Type "ralph" and it goes into persistence mode, won't stop until the job is verified complete
→ Type "eco" and it switches to budget mode
→ Type "plan" and it runs a planning interview before touching a single file
```

### micromanage

If you're uncertain about requirements:

```
/deep-interview "I want to build a task management app"
```

### Ask providers

```
/ask codex "review this patch"
```



###  continuous execution.
auto-resumes your Claude Code sessions when rate limits reset.


### Team Mode

```
/team 3:executor "fix all TypeScript errors"
```

```
~/.claude/settings.json
========================
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }

```

will run as

```
team-plan → team-prd → team-exec → team-verify → team-fix (loop)
```
# oh-my-claudecode

* git : https://github.com/yeachan-heo/oh-my-claudecode
* docs: https://omc.vibetip.help/docs
* [install](./install.md)
* [omc](./omc.md)


## FEATURES

32 specialized agents for architecture, research, design, testing, and data science. Smart model routing uses Haiku for simple tasks and Opus for complex reasoning automatically. You never think about which model to use



→ Autopilot mode: fully autonomous execution, just describe the task and walk away

→ Ultrapilot mode: spins up parallel agents and runs 3-5x faster on multi-component builds

→ Swarm mode: coordinates multiple agents working independently toward the same goal

→ Pipeline mode: sequential chains for multi-stage processing tasks

→ Ecomode: token-efficient execution that saves 30-50% on costs without sacrificing quality


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
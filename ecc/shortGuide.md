# my short guide

## plan

```
/plan "Add user authentication"
```

## multi

Multi-model commands 

```
# /multi-plan - Multi-agent task decomposition
# /multi-execute - Orchestrated multi-agent workflows 
# /multi-backend - Backend multi-service orchestration 
# /multi-frontend - Frontend multi-service orchestration
# /multi-workflow - General multi-service workflows

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

## Continuous Learning v2

The instinct-based learning system automatically learns your patterns:

```
/instinct-status        # Show learned instincts with confidence
/instinct-import <file> # Import instincts from others
/instinct-export        # Export your instincts for sharing
/evolve                 # Cluster related instincts into skills
```



## learn

un mid-session when you've just solved something non-trivial. It prompts you to extract the pattern right then, drafts a skill file, and asks for confirmation before saving

https://github.com/affaan-m/everything-claude-code/blob/main/commands/learn.md


## Session Log 

create ~/.claude/sessions/YYYY-MM-DD-topic.tmp` - one file per session with current state, completed items, blockers, key decisions, and context for next session.


## Self-Improving 

reflecting over session logs to distill user preferences - essentially building a "diary" of what works and what doesn't. After each session, a reflection agent extracts what went well, what failed, what corrections you made. These learnings update a memory file that loads in subsequent sessions.



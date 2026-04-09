# commands

## short

```
  0. skillkit -h
  1. skillkit -v
  2. skillkit install [--skills,--skill,-s #0] [--all,-a] [--yes,-y] [--global,-g] [--force,-f] [--provider,-p #0] [--list,-l] [--agent #0] [--quiet,-q] [--scan] <source>
  3. skillkit sync [--output,-o #0] [--agent,-a #0] [--enabled-only,-e] [--yes,-y] [--quiet,-q]
  4. skillkit read [--verbose,-v] <skills>
  5. skillkit list [--enabled,-e] [--disabled,-d] [--quality,-q] [--json,-j]
  6. skillkit enable <skills> ...
  7. skillkit disable <skills> ...
  8. skillkit update [--force,-f] ...
  9. skillkit remove [--force,-f] <skills> ...
 10. skillkit init [--agent,-a #0] [--list,-l] [--quiet,-q]
 11. skillkit validate [--verbose,-v] [--quality,-q] [--issues,-i] [--min-score,-m #0] [--json] [--all,-a] [--benchmark,-b] [--strict,-s] [--fix] ...
 12. skillkit fix [--dry-run,-d] [--yes,-y] [--interactive,-i] ...
 13. skillkit create [--full,-f] [--scripts] [--references] [--assets] [--dir,-d #0] <skill-name>
 14. skillkit ui
 15. skillkit translate [--to,-t #0] [--from,-f #0] [--output,-o #0] [--all,-a] [--dry-run,-n] [--metadata,-m] [--force] [--list,-l] [--compat,-c] [source]
 16. skillkit context [--agent,-a #0] [--output,-o #0] [--input,-i #0] [--force,-f] [--dry-run,-n] [--merge,-m] [--json,-j] [--verbose,-v] [action]
 17. skillkit recommend [--limit,-l #0] [--min-score #0] [--category,-c #0] [--verbose,-v] [--update,-u] [--search,-s #0] [--task,-t #0] [--include-installed] [--json,-j] [--path,-p #0] [--quiet,-q] [--explain,-e] [--reasoning,-r] [--show-path] [--hybrid,-H] [--expand,-x] [--rerank] [--build-index]
 18. skillkit status [--history,-h] [--limit,-l #0] [--json,-j] [--path,-p #0]
 19. skillkit pause [--path,-p #0]
 20. skillkit resume [--path,-p #0]
 21. skillkit workflow run [--file,-f #0] [--dry-run,-n] [--verbose,-v] [--continue-on-error] [--json,-j] [--path,-p #0] [--agent,-a #0] [--simulate] [workflowName]
 22. skillkit workflow list [--verbose,-v] [--json,-j] [--path,-p #0]
 23. skillkit workflow create [--description,-d #0] [--stdout] [--path,-p #0] <workflowName>
 24. skillkit run [--agent,-a #0] [--dry-run,-n] [--verify] [--auto-commit] [--continue-on-error] [--verbose,-v] [--json,-j] [--path,-p #0] <skillRef>
 25. skillkit test [--verbose,-v] [--bail,-b] [--tags,-t #0] [--skip-tags #0] [--json,-j] [--path,-p #0] [--timeout #0] [skill]
 26. skillkit marketplace [--limit,-l #0] [--tags,-t #0] [--source,-s #0] [--json,-j] [--quiet,-q] [action] [query]
 27. skillkit memory [--global,-g] [--tags,-t #0] [--limit,-l #0] [--title #0] [--content,-c #0] [--name,-n #0] [--output,-o #0] [--input,-i #0] [--keep-learnings] [--dry-run] [--json,-j] [--verbose,-v] [action] [arg] [ratingArg]
 28. skillkit settings [--set,-s #0] [--get,-g #0] [--json,-j] [--global] [--reset]
 29. skillkit cicd init [--provider,-p #0] [--all,-a] [--force,-f] [--path #0]
 30. skillkit team [--name #0] [--registry #0] [--description,-d #0] [--tags,-t #0] [--skills #0] [--output,-o #0] [--source,-s #0] [--overwrite] [--dry-run] <action>
 31. skillkit plugin [--source,-s #0] [--name,-n #0] [--global,-g] <action>
 32. skillkit methodology [--agent,-a #0] [--dry-run] [--verbose,-v] <action> [target]
 33. skillkit hook [--pattern,-p #0] [--agent,-a #0] [--inject,-i #0] [--priority #0] [--verbose,-v] <action> [target] [skill]
 34. skillkit plan [--file,-f #0] [--output,-o #0] [--name,-n #0] [--goal,-g #0] [--tasks,-t #0] [--template #0] [--tech-stack #0] [--dry-run] [--strict] [--stop-on-error] [--verbose,-v] [--json] <action>
 35. skillkit command [--skill,-s #0] [--name,-n #0] [--description,-d #0] [--agent,-a #0] [--output,-o #0] [--input,-i #0] [--category,-c #0] [--all] [--json] [--dry-run] <action>
 36. skillkit ai [--query,-q #0] [--description,-d #0] [--from-code #0] [--context #0] [--agent,-a #0] [--limit,-l #0] [--min-relevance #0] [--json,-j] [--output,-o #0] <subcommand> [skillName]
 37. skillkit audit [--type,-t #0] [--user,-u #0] [--resource,-r #0] [--success] [--failed] [--since #0] [--until #0] [--limit,-l #0] [--format,-f #0] [--output,-o #0] [--days #0] [--json,-j] [--path,-p #0] <subcommand>
 38. skillkit publish [--output,-o #0] [--dry-run,-n] [--format #0] [path]
 39. skillkit publish submit [--name,-n #0] [--dry-run] [path]
 40. skillkit agent
 41. skillkit agent list [--json,-j] [--project,-p] [--global,-g]
 42. skillkit agent show <name>
 43. skillkit agent create [--model,-m #0] [--description,-d #0] [--global,-g] <name>
 44. skillkit agent from-skill [--inline,-i] [--model,-m #0] [--permission,-p #0] [--global,-g] [--output,-o #0] [--dry-run,-n] <skillName>
 45. skillkit agent translate <--to,-t #0> [--source,-s #0] [--output,-o #0] [--dry-run,-n] [--all,-a] [--recursive,-r] [name]
 46. skillkit agent sync [--agent,-a #0]
 47. skillkit agent validate [--all,-a] [agentPath]
 48. skillkit check [--verbose,-v] [--quiet,-q] ...
 49. skillkit find [--top,-t] [--limit,-l #0] [--install,-i] [--quiet,-q] [--federated,-f] [query]
 50. skillkit manifest
 51. skillkit manifest init [--force,-f]
 52. skillkit manifest add [--skills,-s #0] [--agents,-a #0] <source>
 53. skillkit manifest remove <source>
 54. skillkit manifest install [--yes,-y]
 55. skillkit manifest generate [--output,-o #0]
 56. skillkit primer [--agent,-a #0] [--all-agents,-A] [--output,-o #0] [--dry-run,-n] [--analyze-only] [--verbose,-v] [--examples] [--json,-j] [--dir,-d #0] [--learn,-l] [--commits #0]
 57. skillkit mesh [--name,-n #0] [--port,-p #0] [--tailscale,-t] [--timeout #0] [--json,-j] [--verbose,-v] [--trusted] [--security #0] [action] [arg] [subArg]
 58. skillkit message [--body,-b #0] [--subject,-s #0] [--priority,-p #0] [--type,-t #0] [--unread,-u] [--limit,-l #0] [--agent,-a #0] [--json,-j] [--verbose,-v] [action] [arg] [arg2]
 59. skillkit workflow pipeline [--dry-run,-n] [pipeline]
 60. skillkit workflow pipeline list [--json,-j]
 61. skillkit hook template list [--category,-c #0] [--json,-j]
 62. skillkit hook template apply <id>
 63. skillkit hook template show <id>
 64. skillkit command available [--category,-c #0] [--json,-j]
 65. skillkit command install <id>
 66. skillkit agent install [--global,-g] [--force,-f] [--all,-a] [name]
 67. skillkit agent available [--json,-j] [--category,-c #0] [--installed,-i]
 68. skillkit learn [--commits,-c #0] [--since,-s #0] [--approve,-a] [--show] [--json,-j] [--dir,-d #0]
 69. skillkit pattern status [--category,-c #0] [--json,-j]
 70. skillkit pattern feedback [--success,-s] [--failure,-f] <id>
 71. skillkit pattern approve <id>
 72. skillkit pattern reject <id>
 73. skillkit pattern export [--output,-o #0] [--format,-f #0] [--approved]
 74. skillkit pattern import <file>
 75. skillkit pattern cluster [--generate,-g] [--min-confidence #0]
 76. skillkit session
 77. skillkit session status [--json,-j]
 78. skillkit session start [--agent,-a #0]
 79. skillkit session load [date]
 80. skillkit session list [--limit,-l #0] [--json,-j]
 81. skillkit session note <note>
 82. skillkit session complete <task>
 83. skillkit session wip <task>
 84. skillkit session snapshot save [--desc,-d #0] <name>
 85. skillkit session snapshot restore <name>
 86. skillkit session snapshot list [--json,-j]
 87. skillkit session snapshot delete <name>
 88. skillkit session explain [--json,-j] [--no-git]
 89. skillkit activity [--skill,-s #0] [--limit,-l #0] [--json,-j]
 90. skillkit profile [name]
 91. skillkit profile list [--json,-j]
 92. skillkit profile create <--name,-n #0> <--description,-d #0> [--focus,-f #0]
 93. skillkit profile remove <name>
 94. skillkit guideline
 95. skillkit guideline list [--enabled,-e] [--json,-j]
 96. skillkit guideline show <id>
 97. skillkit guideline enable <id>
 98. skillkit guideline disable <id>
 99. skillkit guideline create <--id #0> <--name,-n #0> [--description,-d #0] [--category,-c #0] [--priority,-p #0]
100. skillkit guideline remove <id>
101. skillkit tree [--depth,-d #0] [--generate,-g] [--markdown,-m] [--stats,-s] [--json,-j] [--quiet,-q] [treePath]
102. skillkit quick
103. skillkit skillmd validate [--verbose,-v] [--json] [path]
104. skillkit skillmd init [--name,-n #0] [--force,-f]
105. skillkit skillmd check [--verbose,-v] [path]
106. skillkit serve [--port,-p #0] [--host,-H #0] [--cors #0] [--cache-ttl #0]
107. skillkit scan [--format,-f #0] [--fail-on #0] [--skip-rules #0] <path>
108. skillkit doctor [--json,-j] [--fix]
109. skillkit save [--name,-n #0] [--agent,-a #0] [--global,-g] [--text,-t #0] [--file,-f #0] [url]
110. skillkit agents
111. skillkit agents init
112. skillkit agents sync
113. skillkit agents show
114. skillkit issue plan [--agent,-a #0] [--output,-o #0] [--no-tests] [--json] [--tech-stack #0] <ref>
115. skillkit issue list [--repo,-r #0] [--label,-l #0] [--limit #0] [--json]
116. skillkit timeline [--type,-t #0] [--skill,-s #0] [--since #0] [--limit,-l #0] [--json,-j]
117. skillkit session handoff [--to #0] [--out,-o #0] [--json,-j]
118. skillkit lineage [--skill,-s #0] [--file,-f #0] [--since #0] [--limit,-l #0] [--json,-j]
```

## --help
```
[skilkit] user:~$ npx skillkit@latest 
━━━ skillkit - 1.19.2 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  $ skillkit <command>

━━━ General commands ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  skillkit activity [--skill,-s #0] [--limit,-l #0] [--json,-j]
    Show skill activity log for git commits

  skillkit agent
    Manage custom AI sub-agents

  skillkit agent available [--json,-j] [--category,-c #0] [--installed,-i]
    List bundled agents available for installation

  skillkit agent create [--model,-m #0] [--description,-d #0] [--global,-g] <name>
    Create a new agent

  skillkit agent from-skill [--inline,-i] [--model,-m #0] [--permission,-p #0] [--global,-g] [--output,-o #0] [--dry-run,-n] <skillName>
    Convert a skill into a Claude Code subagent

  skillkit agent install [--global,-g] [--force,-f] [--all,-a] [name]
    Install a bundled agent template

  skillkit agent list [--json,-j] [--project,-p] [--global,-g]
    List all installed agents

  skillkit agent show <name>
    Show details for a specific agent

  skillkit agent sync [--agent,-a #0]
    Sync agents to target AI coding agent

  skillkit agent translate <--to,-t #0> [--source,-s #0] [--output,-o #0] [--dry-run,-n] [--all,-a] [--recursive,-r] [name]
    Translate agents between AI coding agent formats

  skillkit agent validate [--all,-a] [agentPath]
    Validate agent definitions

  skillkit agents
    Manage AGENTS.md for project-specific agent context

  skillkit agents init
    Generate initial AGENTS.md in current directory

  skillkit agents show
    Display current AGENTS.md content

  skillkit agents sync
    Update managed sections in existing AGENTS.md

  skillkit ai [--query,-q #0] [--description,-d #0] [--from-code #0] [--context #0] [--agent,-a #0] [--limit,-l #0] [--min-relevance #0] [--json,-j] [--output,-o #0] <subcommand> [skillName]
    AI-powered skill search and generation

  skillkit audit [--type,-t #0] [--user,-u #0] [--resource,-r #0] [--success] [--failed] [--since #0] [--until #0] [--limit,-l #0] [--format,-f #0] [--output,-o #0] [--days #0] [--json,-j] [--path,-p #0] <subcommand>
    View and manage audit logs

  skillkit check [--verbose,-v] [--quiet,-q] ...
    Check for available skill updates (dry-run)

  skillkit cicd init [--provider,-p #0] [--all,-a] [--force,-f] [--path #0]
    Initialize CI/CD workflows for skill validation

  skillkit context [--agent,-a #0] [--output,-o #0] [--input,-i #0] [--force,-f] [--dry-run,-n] [--merge,-m] [--json,-j] [--verbose,-v] [action]
    Manage project context for multi-agent skill synchronization

  skillkit create [--full,-f] [--scripts] [--references] [--assets] [--dir,-d #0] <skill-name>
    Create a new skill with proper structure

  skillkit disable <skills> ...
    Disable one or more skills

  skillkit doctor [--json,-j] [--fix]
    Diagnose setup issues and check environment health

  skillkit enable <skills> ...
    Enable one or more skills

  skillkit find [--top,-t] [--limit,-l #0] [--install,-i] [--quiet,-q] [--federated,-f] [query]
    Search for skills in the marketplace

  skillkit fix [--dry-run,-d] [--yes,-y] [--interactive,-i] ...
    Automatically fix common skill quality issues

  skillkit guideline
    Manage coding guidelines (always-on rules)

  skillkit guideline create <--id #0> <--name,-n #0> [--description,-d #0] [--category,-c #0] [--priority,-p #0]
    Create a custom guideline

  skillkit guideline disable <id>
    Disable a guideline

  skillkit guideline enable <id>
    Enable a guideline

  skillkit guideline list [--enabled,-e] [--json,-j]
    List all guidelines

  skillkit guideline remove <id>
    Remove a custom guideline

  skillkit guideline show <id>
    Show guideline content

  skillkit hook [--pattern,-p #0] [--agent,-a #0] [--inject,-i #0] [--priority #0] [--verbose,-v] <action> [target] [skill]
    Manage skill hooks for automatic triggering

  skillkit hook template apply <id>
    Apply a hook template

  skillkit hook template list [--category,-c #0] [--json,-j]
    List available hook templates

  skillkit hook template show <id>
    Show hook template details

  skillkit init [--agent,-a #0] [--list,-l] [--quiet,-q]
    Initialize skillkit in a project

  skillkit install [--skills,--skill,-s #0] [--all,-a] [--yes,-y] [--global,-g] [--force,-f] [--provider,-p #0] [--list,-l] [--agent #0] [--quiet,-q] [--scan] <source>
    Install skills from GitHub, GitLab, Bitbucket, or local path

  skillkit learn [--commits,-c #0] [--since,-s #0] [--approve,-a] [--show] [--json,-j] [--dir,-d #0]
    Extract learnable patterns from git history or sessions

  skillkit lineage [--skill,-s #0] [--file,-f #0] [--since #0] [--limit,-l #0] [--json,-j]
    Show skill impact lineage — which skills produced which changes

  skillkit list [--enabled,-e] [--disabled,-d] [--quality,-q] [--json,-j]
    List all installed skills

  skillkit manifest
    Manage .skills manifest file

  skillkit manifest add [--skills,-s #0] [--agents,-a #0] <source>
    Add a skill source to the manifest

  skillkit manifest generate [--output,-o #0]
    Generate manifest from currently installed skills

  skillkit manifest init [--force,-f]
    Initialize a new .skills manifest

  skillkit manifest install [--yes,-y]
    Install all skills defined in the manifest

  skillkit manifest remove <source>
    Remove a skill source from the manifest

  skillkit marketplace [--limit,-l #0] [--tags,-t #0] [--source,-s #0] [--json,-j] [--quiet,-q] [action] [query]
    Browse and install skills from the marketplace

  skillkit memory [--global,-g] [--tags,-t #0] [--limit,-l #0] [--title #0] [--content,-c #0] [--name,-n #0] [--output,-o #0] [--input,-i #0] [--keep-learnings] [--dry-run] [--json,-j] [--verbose,-v] [action] [arg] [ratingArg]
    Manage session memory across AI coding agents

  skillkit mesh [--name,-n #0] [--port,-p #0] [--tailscale,-t] [--timeout #0] [--json,-j] [--verbose,-v] [--trusted] [--security #0] [action] [arg] [subArg]
    Manage peer mesh network for multi-machine agent distribution

  skillkit message [--body,-b #0] [--subject,-s #0] [--priority,-p #0] [--type,-t #0] [--unread,-u] [--limit,-l #0] [--agent,-a #0] [--json,-j] [--verbose,-v] [action] [arg] [arg2]
    Inter-agent messaging system

  skillkit methodology [--agent,-a #0] [--dry-run] [--verbose,-v] <action> [target]
    Manage methodology packs for AI coding agents

  skillkit pattern approve <id>
    Approve a pending pattern

  skillkit pattern cluster [--generate,-g] [--min-confidence #0]
    Cluster similar patterns and generate skills

  skillkit pattern export [--output,-o #0] [--format,-f #0] [--approved]
    Export patterns to a file

  skillkit pattern feedback [--success,-s] [--failure,-f] <id>
    Provide feedback on a pattern to evolve its confidence

  skillkit pattern import <file>
    Import patterns from a file

  skillkit pattern reject <id>
    Reject and remove a pattern

  skillkit pattern status [--category,-c #0] [--json,-j]
    Show status of learned patterns

  skillkit pause [--path,-p #0]
    Pause current skill execution for later resumption

  skillkit plugin [--source,-s #0] [--name,-n #0] [--global,-g] <action>
    Manage SkillKit plugins

  skillkit primer [--agent,-a #0] [--all-agents,-A] [--output,-o #0] [--dry-run,-n] [--analyze-only] [--verbose,-v] [--examples] [--json,-j] [--dir,-d #0] [--learn,-l] [--commits #0]
    Analyze codebase and generate AI instruction files for agents

  skillkit profile [name]
    Manage operational profiles (dev, review, research modes)

  skillkit profile create <--name,-n #0> <--description,-d #0> [--focus,-f #0]
    Create a custom profile

  skillkit profile list [--json,-j]
    List available profiles

  skillkit profile remove <name>
    Remove a custom profile

  skillkit publish [--output,-o #0] [--dry-run,-n] [--format #0] [path]
    Generate well-known skills structure for hosting

  skillkit publish submit [--name,-n #0] [--dry-run] [path]
    Submit skill to SkillKit marketplace (requires review)

  skillkit quick
    Zero-friction skill setup: detect agents, analyze project, recommend and install

  skillkit read [--verbose,-v] <skills>
    Read skill content for AI agent consumption

  skillkit recommend [--limit,-l #0] [--min-score #0] [--category,-c #0] [--verbose,-v] [--update,-u] [--search,-s #0] [--task,-t #0] [--include-installed] [--json,-j] [--path,-p #0] [--quiet,-q] [--explain,-e] [--reasoning,-r] [--show-path] [--hybrid,-H] [--expand,-x] [--rerank] [--build-index]
    Get skill recommendations based on your project

  skillkit remove [--force,-f] <skills> ...
    Remove installed skills

  skillkit resume [--path,-p #0]
    Resume a paused skill execution

  skillkit run [--agent,-a #0] [--dry-run,-n] [--verify] [--auto-commit] [--continue-on-error] [--verbose,-v] [--json,-j] [--path,-p #0] <skillRef>
    Execute a skill with task-based orchestration

  skillkit save [--name,-n #0] [--agent,-a #0] [--global,-g] [--text,-t #0] [--file,-f #0] [url]
    Save content from a URL, text, or file as a reusable skill

  skillkit scan [--format,-f #0] [--fail-on #0] [--skip-rules #0] <path>
    Scan a skill directory for security vulnerabilities

  skillkit serve [--port,-p #0] [--host,-H #0] [--cors #0] [--cache-ttl #0]
    Start the SkillKit REST API server for skill discovery

  skillkit session
    Manage session state for context preservation

  skillkit session complete <task>
    Mark task as completed

  skillkit session explain [--json,-j] [--no-git]
    Explain what happened in the current session

  skillkit session handoff [--to #0] [--out,-o #0] [--json,-j]
    Generate agent-to-agent session handoff document

  skillkit session list [--limit,-l #0] [--json,-j]
    List recent sessions

  skillkit session load [date]
    Load session from specific date

  skillkit session note <note>
    Add note to current session

  skillkit session snapshot delete <name>
    Delete a session snapshot

  skillkit session snapshot list [--json,-j]
    List all session snapshots

  skillkit session snapshot restore <name>
    Restore session state from a snapshot

  skillkit session snapshot save [--desc,-d #0] <name>
    Save current session state as a named snapshot

  skillkit session start [--agent,-a #0]
    Start a new session

  skillkit session status [--json,-j]
    Show current session state

  skillkit session wip <task>
    Mark task as in progress

  skillkit settings [--set,-s #0] [--get,-g #0] [--json,-j] [--global] [--reset]
    View and modify SkillKit settings

  skillkit skillmd check [--verbose,-v] [path]
    Check all SKILL.md files in the project for compliance

  skillkit skillmd init [--name,-n #0] [--force,-f]
    Create a template SKILL.md in the current directory

  skillkit skillmd validate [--verbose,-v] [--json] [path]
    Validate a SKILL.md file against the standard

  skillkit status [--history,-h] [--limit,-l #0] [--json,-j] [--path,-p #0]
    Show current session state and execution progress

  skillkit sync [--output,-o #0] [--agent,-a #0] [--enabled-only,-e] [--yes,-y] [--quiet,-q]
    Sync skills to agent configuration file

  skillkit team [--name #0] [--registry #0] [--description,-d #0] [--tags,-t #0] [--skills #0] [--output,-o #0] [--source,-s #0] [--overwrite] [--dry-run] <action>
    Manage team skill sharing and collaboration

  skillkit test [--verbose,-v] [--bail,-b] [--tags,-t #0] [--skip-tags #0] [--json,-j] [--path,-p #0] [--timeout #0] [skill]
    Run skill tests

  skillkit timeline [--type,-t #0] [--skill,-s #0] [--since #0] [--limit,-l #0] [--json,-j]
    Show unified session event timeline

  skillkit translate [--to,-t #0] [--from,-f #0] [--output,-o #0] [--all,-a] [--dry-run,-n] [--metadata,-m] [--force] [--list,-l] [--compat,-c] [source]
    Translate skills between different AI agent formats

  skillkit tree [--depth,-d #0] [--generate,-g] [--markdown,-m] [--stats,-s] [--json,-j] [--quiet,-q] [treePath]
    Browse skills in a hierarchical tree structure

  skillkit ui
    Launch the interactive TUI (Terminal User Interface)

  skillkit update [--force,-f] ...
    Update skills from their original sources

  skillkit validate [--verbose,-v] [--quality,-q] [--issues,-i] [--min-score,-m #0] [--json] [--all,-a] [--benchmark,-b] [--strict,-s] [--fix] ...
    Validate skill format and quality

  skillkit workflow create [--description,-d #0] [--stdout] [--path,-p #0] <workflowName>
    Create a new workflow

  skillkit workflow list [--verbose,-v] [--json,-j] [--path,-p #0]
    List available workflows

  skillkit workflow pipeline [--dry-run,-n] [pipeline]
    Run a built-in agent pipeline

  skillkit workflow pipeline list [--json,-j]
    List available pipelines

  skillkit workflow run [--file,-f #0] [--dry-run,-n] [--verbose,-v] [--continue-on-error] [--json,-j] [--path,-p #0] [--agent,-a #0] [--simulate] [workflowName]
    Execute a skill workflow

━━━ Commands ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  skillkit command [--skill,-s #0] [--name,-n #0] [--description,-d #0] [--agent,-a #0] [--output,-o #0] [--input,-i #0] [--category,-c #0] [--all] [--json] [--dry-run] <action>
    Manage slash commands and agent integration

  skillkit command available [--category,-c #0] [--json,-j]
    List available bundled command templates

  skillkit command install <id>
    Install a bundled command template

━━━ Development ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  skillkit issue list [--repo,-r #0] [--label,-l #0] [--limit #0] [--json]
    List open GitHub Issues

  skillkit issue plan [--agent,-a #0] [--output,-o #0] [--no-tests] [--json] [--tech-stack #0] <ref>
    Generate a structured plan from a GitHub Issue

  skillkit plan [--file,-f #0] [--output,-o #0] [--name,-n #0] [--goal,-g #0] [--tasks,-t #0] [--template #0] [--tech-stack #0] [--dry-run] [--strict] [--stop-on-error] [--verbose,-v] [--json] <action>
    Manage structured development plans

You can also print more details about any of these commands by calling them with 
the `-h,--help` flag right after the command name.

```
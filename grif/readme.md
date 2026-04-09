# graphify

* https://graphify.net
* [skill extracted from diff](./SKILL.md)

Knowledge Graphs for AI Coding Assistants

## usage

```
# Build a knowledge graph for any project folder
/graphify ./raw

# Outputs land in graphify-out/
graphify-out/
├── graph.html        # interactive visualization
├── GRAPH_REPORT.md   # core nodes, surprises, suggested questions
├── graph.json        # persistent, queryable graph
└── cache/            # incremental cache

```

## install
```

pip install graphifyy

[grif] user:~$ /home/user/.local/bin/graphify 
Usage: graphify <command>

Commands:
  install [--platform P]  copy skill to platform config dir (claude|windows|codex|opencode|claw|droid)
  query "<question>"       BFS traversal of graph.json for a question
    --dfs                   use depth-first instead of breadth-first
    --budget N              cap output at N tokens (default 2000)
    --graph <path>          path to graph.json (default graphify-out/graph.json)
  benchmark [graph.json]  measure token reduction vs naive full-corpus approach
  hook install            install post-commit/post-checkout git hooks (all platforms)
  hook uninstall          remove git hooks
  hook status             check if git hooks are installed
  claude install          write graphify section to CLAUDE.md + PreToolUse hook (Claude Code)
  claude uninstall        remove graphify section from CLAUDE.md + PreToolUse hook
  codex install           write graphify section to AGENTS.md (Codex)
  codex uninstall         remove graphify section from AGENTS.md
  opencode install        write graphify section to AGENTS.md (OpenCode)
  opencode uninstall      remove graphify section from AGENTS.md
  claw install            write graphify section to AGENTS.md (OpenClaw)
  claw uninstall          remove graphify section from AGENTS.md
  droid install           write graphify section to AGENTS.md (Factory Droid)
  droid uninstall         remove graphify section from AGENTS.md

[grif] user:~$ /home/user/.local/bin/graphify install --platform claude
  skill installed  ->  /home/user/.claude/skills/graphify/SKILL.md
  CLAUDE.md        ->  created at /home/user/.claude/CLAUDE.md

Done. Open your AI coding assistant and type:

  /graphify .

```
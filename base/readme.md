# base layer

Ubuntu 22.04 + Node 20 + Claude Code CLI.
This is the foundation all other layers build on.

## Build

```
make base           # from root (build image + spin container)
```

## Contents

- `Dockerfile` — installs system deps, Node 20, Claude Code CLI, creates `user`
- `entrypoint.sh` — copies `claude_tilda_base/` template into container on first start

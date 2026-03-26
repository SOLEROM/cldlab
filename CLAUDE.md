# Claude Overlay Lab — Project Context

## What this project is

A Docker-based lab for running isolated Claude Code CLI environments. Uses OverlayFS to track filesystem changes inside containers. Each environment is a named container that can be diffed, merged into an image, and branched from.

---

## Folder structure

```
cldlab/
├── Makefile              ← single entry point for all operations
├── CLAUDE.md             ← this file
├── readme.md             ← user-facing docs
├── aliases               ← mounted live as ~/.aliases in every container
├── .env                  ← ANTHROPIC_API_KEY + proj path (gitignored)
├── diffs/                ← output of `make diff` exports (gitignored)
├── base/                 ← base layer: Ubuntu + Node 20 + Claude Code CLI
│   ├── Dockerfile
│   ├── entrypoint.sh     ← copies claude_tilda_base → ~/.claude on first start
│   ├── Makefile          ← builds cldimg-base
│   ├── claude_tilda_base/← template for ~/.claude and ~/.claude.json
│   └── readme.md
├── login/                ← login layer: persistent auth sessions
│   ├── Dockerfile        ← FROM cldimg-base
│   ├── Makefile          ← builds cldimg-login
│   └── readme.md
└── plug-template/        ← template for new plugin layers
    ├── Dockerfile        ← FROM cldimg-base (edit to add plugins)
    ├── Makefile          ← builds cldimg-plug-template
    └── readme.md
```

---

## Naming conventions

| Type | Pattern | Example |
|------|---------|---------|
| Images | `cldimg-<name>` | `cldimg-base`, `cldimg-login` |
| Containers | `cldcon-<name>` | `cldcon-base`, `cldcon-login` |
| Plugin folders | `plug-<name>/` | `plug-mcp/` |
| Plugin images | `cldimg-plug-<name>` | `cldimg-plug-mcp` |

---

## Makefile — key design decisions

**All operations are in the root Makefile only.** Sub-Makefiles (`base/`, `login/`, `plug-*/`) contain only a single `build` target.

**Layer targets** (`base`, `login`, `plug`) chain: build base image → build layer image → `make new` to spin container.

**`make plug NAME=x SRC=img`** copies `plug-template/` → `plug-x/`, patches its Makefile, builds + spins. On re-run the folder already exists so it just rebuilds.

**`claude_tilda` overlay**: if a layer folder contains `claude_tilda/`, it is mounted directly as `/home/user/.claude` (volume mount, overrides base template). Used for plugin layers. NOT used for `login` (login keeps `~/.claude` private inside the container for session isolation).

**Base `~/.claude` seeding**: `base/entrypoint.sh` copies `base/claude_tilda_base/dot_claude → ~/.claude` and `dot_claude.json → ~/.claude.json` on first container start only (guarded by `~/.claude/.initialized`).

**`.env` format**: plain `KEY=VALUE` (no `export`, no quotes needed). Loaded by Make via `-include .env / export` (currently commented out — uncomment if Makefile rules need env vars). Passed to containers via `-e ANTHROPIC_API_KEY=$(ANTHROPIC_API_KEY)`.

**`.PHONY`**: all targets must be listed — layer folder names match Make target names so Make would otherwise think they're up to date.

---

## Full command reference

```
# Layer spin (build image + create container)
make base                        # build cldimg-base + spin cldcon-base
make login                       # build cldimg-login + spin cldcon-login
make plug NAME=<n> SRC=<img>     # create plug-<n>/, build + spin cldcon-plug-<n>
make build                       # build cldimg-base only (no container)

# Container lifecycle
make new   NAME=<n> SRC=<img>    # create container from any image
make run   NAME=<n>              # re-enter stopped container
make merge NAME=<n>              # commit container → cldimg-<n>

# Inspect
make list                        # show all managed images + containers
make cmp  SRC=cldimg-<n> DST=cldcon-<n>          # compare OverlayFS upper dirs
make diff SRC=cldimg-<n> DST=cldcon-<n> [NAME=x]  # export DST upperdir → diffs/
make diff.meta NAME=<n>          # docker diff metadata

# Cleanup
make stop  [NAME=<n>]            # stop one or all containers
make clean [NAME=<n>]            # remove containers only (one or all)
make clear [NAME=<n>]            # remove containers + images (one or all)
```

---

## Typical workflows

**New experiment from base:**
```
make base
# inside: do stuff
make merge NAME=base
make new NAME=exp1 SRC=cldimg-base
make diff SRC=cldimg-base DST=cldcon-exp1
```

**Login / auth session:**
```
make login
# inside: claude login, gh auth, etc.
make merge NAME=login            # save session → cldimg-login
make run NAME=login              # resume later
```

**New plugin layer:**
```
make plug NAME=mcp SRC=cldimg-login
# plug-mcp/ created from plug-template/
# edit plug-mcp/Dockerfile to add plugins, then re-run make plug NAME=mcp SRC=...
```

---

## What NOT to change without understanding

- `base/entrypoint.sh` — guards first-start init with `.initialized` flag; changing copy logic affects all containers
- `plug-template/` — source of truth for all `make plug` copies; changes here affect all future plugs
- `.PHONY` line — must include every target that shares a name with a folder (`base`, `login`, `plug-template`, `plug`)
- `login` target — intentionally has no `TILDA` mount so `~/.claude` stays private in the container

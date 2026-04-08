# Claude Overlay Lab

Isolated Docker environments for experimenting with Claude Code CLI — with full filesystem visibility via OverlayFS.

---

## Structure

```
cldlab/
├── Makefile              ← all commands live here
├── .env                  ← env vars (ANTHROPIC_API_KEY, etc) — auto-loaded
├── aliases               ← mounted live as ~/.aliases in every container
├── diffs/                ← diff/export output (never deleted by clean)
├── base/                 ← base layer (Ubuntu + Node + Claude Code CLI)
├── login/                ← login layer (persistent auth sessions, isolated ~/.claude)
└── _template/            ← template for new custom layers
```

---

## Layers

Each layer folder has its own `Dockerfile` and `Makefile` (build only).
All container operations and layer targets are in the root `Makefile`.

| Command | Description |
| ------- | ----------- |
| `make base` | Build base image + spin container |
| `make login` | Build base+login images + spin container |
| `make new NAME=<n>` | Copy `_template/` → `<n>/`, build image, spin container; auto-adds entry to `config.yaml` |

### Plugin `claude_tilda` override

If a layer folder contains a `claude_tilda/` directory, it is mounted directly as `~/.claude` inside the container, overriding the base template. Not used for `login` (kept private).

---

## Environments

| Command | Description |
| ------- | ----------- |
| `make spin NAME=<n> SRC=<img>` | Spin throwaway container from any image |
| `make run NAME=<n>` | Re-enter existing container |
| `make stop [NAME=<n>]` | Stop one container or all |
| `make merge NAME=<n>` | Commit container → image (`cldimg-<n>`) |

---

## Inspect

| Command | Description |
| ------- | ----------- |
| `make list` | List all managed images and containers (names only, no prefix) |
| `make cmp BASE=<n> CON=<n>` | Compare OverlayFS trees (base image vs container) |
| `make diff BASE=<n> CON=<n> [NAME=<folder>]` | Export container changes to `diffs/` |
| `make diff.meta NAME=<n>` | `docker diff` metadata |

---

## Cleanup

| Command | Description |
| ------- | ----------- |
| `make clean [NAME=<n>]` | Remove containers only (one or all) |
| `make clear [NAME=<n>]` | Remove containers + images (one or all, with confirmation) |

---

## Naming

| Type | Prefix | Example |
| ---- | ------ | ------- |
| Images | `cldimg-` | `cldimg-base`, `cldimg-login` |
| Containers | `cldcon-` | `cldcon-base`, `cldcon-login` |

---

## Typical Workflow

```
make base                          # spin base container
make spin NAME=envA SRC=base       # throwaway container from base image
make diff BASE=base CON=envA       # export envA changes
make merge NAME=envA               # snapshot → cldimg-envA
make spin NAME=envB SRC=envA       # branch from snapshot

make login                         # spin login container
# authenticate inside, then:
make merge NAME=login              # save session → cldimg-login

make new NAME=mcp                  # create mcp/ from template, build + spin
# edit mcp/Dockerfile, then re-run make new NAME=mcp
```

---

## Notes

- `.env` is auto-loaded — put `ANTHROPIC_API_KEY=...` there
- `aliases` is mounted as `~/.aliases` in every container and auto-sourced by `.bashrc`
- `base/claude_tilda_base/` is copied to `~/.claude` + `~/.claude.json` on first container start
- If a layer has `claude_tilda/`, it is mounted directly as `~/.claude` (overrides base template)
- `login` layer keeps `~/.claude` private inside the container — credentials never touch the host
- If `$proj` is set in the environment, it is mounted as `/proj` with trust pre-accepted
- `cld` alias = `cd /proj && claude --dangerously-skip-permissions`
- `ANTHROPIC_API_KEY` is injected at container creation — recreate if it changes
- OverlayFS inspection requires `sudo` on the host
- `diffs/` is never deleted by `clean` or `clear`

---

## Adding a new layer

```
make new NAME=<n>
```

This copies `_template/` → `<n>/`, patches the Makefile, builds the image, spins the container, and adds an entry to `config.yaml`. Then edit `<n>/Dockerfile` as needed and re-run `make new NAME=<n>`.

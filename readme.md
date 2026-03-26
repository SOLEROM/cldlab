# Claude Overlay Lab

Isolated Docker environments for experimenting with Claude Code CLI — with full filesystem visibility via OverlayFS.

---

## Structure

```
cldlab/
├── Makefile              ← all commands live here
├── aliases               ← mounted live as ~/.aliases in every container
├── claude_tilda_base/    ← template copied into container on first start
├── diffs/                 ← diff/export output (never deleted by clean)
├── base/                 ← base layer (Ubuntu + Node + Claude Code CLI)
└── plug-template/                ← plug-template layer (extends base)
```

---

## Layers

Each layer folder has its own `Dockerfile` and `Makefile` (build only).
All container operations and layer targets are in the root `Makefile`.

| Command | Description |
| ------- | ----------- |
| `make base [cmd]` | Build base image + spin container |
| `make plug-template [cmd]` | Build base+plug-template images + spin container |
| `make build` | Build base image only (`cldimg-base`) |

The optional `[cmd]` runs inside the container on boot:
```
make plug-template cld      # spin plug-template container and run cld immediately
```

---

## Environments

| Command | Description |
| ------- | ----------- |
| `make new NAME=<n> SRC=<img>` | Create container from image |
| `make run NAME=<n>` | Re-enter existing container |
| `make stop NAME=<n>` | Stop running container |
| `make stop.all` | Stop all running `cldcon-*` containers |
| `make merge NAME=<n>` | Commit container → image |

---

## Inspect

| Command | Description |
| ------- | ----------- |
| `make list` | List all managed images and containers |
| `make cmp SRC=cldimg-<n> DST=cldcon-<n>` | Compare OverlayFS trees |
| `make diff SRC=cldimg-<n> DST=cldcon-<n> [NAME=<folder>]` | Export DST upperdir to `diffs/` |
| `make diff.meta NAME=<n>` | `docker diff` metadata |

---

## Cleanup

| Command | Description |
| ------- | ----------- |
| `make clean NAME=<n>` | Remove container + image by name |
| `make clean.all` | Remove all containers + images (with confirmation) |

---

## Naming

| Type | Prefix | Example |
| ---- | ------ | ------- |
| Images | `cldimg-` | `cldimg-base`, `cldimg-plug-template` |
| Containers | `cldcon-` | `cldcon-base`, `cldcon-plug-template` |

---

## Typical Workflow

```
make base                                # spin base container
make new NAME=envA SRC=cldimg-base       # experiment from base
make diff SRC=cldimg-base DST=cldcon-envA
make merge NAME=envA                     # snapshot → cldimg-envA
make new NAME=envB SRC=cldimg-envA       # branch from snapshot
```

---

## Notes

- `aliases` is mounted as `~/.aliases` in every container and auto-sourced by `.bashrc`
- `claude_tilda_base/` is copied to `~/.claude.json` + `~/.claude/` on first container start
- Each container gets its own private copy — writes inside never affect the host template
- If `$proj` is set in the environment, it is mounted as `/proj` with trust pre-accepted
- `cld` alias = `cd /proj && claude --dangerously-skip-permissions`
- `ANTHROPIC_API_KEY` is injected at container creation — recreate if it changes
- OverlayFS inspection requires `sudo` on the host
- `diffs/` is never deleted by `clean` or `clean.all`

---

## Adding a new layer

1. Create `<name>/Dockerfile` with `FROM cldimg-base` (or another layer)
2. Create `<name>/Makefile` — copy `plug-template/Makefile`, change image name
3. Add a target in root `Makefile` following the `plug-template` pattern
4. Create `<name>/readme.md`

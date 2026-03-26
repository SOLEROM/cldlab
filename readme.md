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
└── plug-template/        ← template for new plugin layers
```

---

## Layers

Each layer folder has its own `Dockerfile` and `Makefile` (build only).
All container operations and layer targets are in the root `Makefile`.

| Command | Description |
| ------- | ----------- |
| `make base` | Build base image + spin container |
| `make login` | Build base+login images + spin container |
| `make plug-template` | Build base+plug-template images + spin container |
| `make build` | Build base image only (`cldimg-base`) |

### Plugin `claude_tilda` override

If a layer folder contains a `claude_tilda/` directory, it is mounted directly as `~/.claude` inside the container, overriding the base template. Not used for `login` (kept private).

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
| Images | `cldimg-` | `cldimg-base`, `cldimg-login` |
| Containers | `cldcon-` | `cldcon-base`, `cldcon-login` |

---

## Typical Workflow

```
make base                                # spin base container
make new NAME=envA SRC=cldimg-base       # experiment from base
make diff SRC=cldimg-base DST=cldcon-envA
make merge NAME=envA                     # snapshot → cldimg-envA
make new NAME=envB SRC=cldimg-envA       # branch from snapshot

make login                               # spin login container
# authenticate inside, then:
make merge NAME=login                    # save session → cldimg-login
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
- `diffs/` is never deleted by `clean` or `clean.all`

---

## Adding a new layer

1. Create `<name>/Dockerfile` with `FROM cldimg-base` (or another layer)
2. Create `<name>/Makefile` — copy `plug-template/Makefile`, change image name
3. Add a target in root `Makefile` following the `plug-template` pattern
4. Add `.PHONY: <name>` to the `.PHONY` line
5. Create `<name>/readme.md`

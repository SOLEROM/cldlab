# Claude Overlay Lab

Isolated Docker environments for experimenting with Claude Code CLI — with full filesystem visibility via OverlayFS.

---

## Setup

```
export ANTHROPIC_API_KEY=sk-ant-...
make build
```

---

## Commands

| Command | Description |
| ------- | ----------- |
| `make build` | Build base image (`cldimg-base`) |
| `make new NAME=<n> SRC=<img>` | Create container from image |
| `make run NAME=<n>` | Re-enter existing container |
| `make stop NAME=<n>` | Stop running container |
| `make stop.all` | Stop all running `cldcon-*` containers |
| `make merge NAME=<n>` | Commit container → image |
| `make list` | List all managed images and containers |
| `make cmp SRC=cldimg-<n> DST=cldcon-<n>` | Compare OverlayFS trees |
| `make diff SRC=cldimg-<n> DST=cldcon-<n> [NAME=<folder>]` | Export DST upperdir to `envs/<folder>` or `envs/<dst>_minus_<src>_<date>` |
| `make diff.meta NAME=<n>` | `docker diff` metadata |
| `make clean NAME=<n>` | Remove container + image by name |
| `make clean.all` | Remove all containers + images (with confirmation) |

---

## Naming

| Type | Prefix | Example |
| ---- | ------ | ------- |
| Images | `cldimg-` | `cldimg-base`, `cldimg-envA` |
| Containers | `cldcon-` | `cldcon-envA` |

---

## Typical Workflow

```
make new NAME=clean SRC=cldimg-base      # baseline
make new NAME=envA  SRC=cldimg-base      # experiment

# inside: run claude, install plugins, etc.

make diff SRC=cldimg-base DST=cldcon-envA
make merge NAME=envA                     # snapshot → cldimg-envA
make new NAME=envB SRC=cldimg-envA       # branch from snapshot
```

---

## Notes

- `cmp` and `diff` require `SRC` to be a `cldimg-*` image and `DST` to be a `cldcon-*` container — images give a zero-noise baseline (empty upperdir), containers hold the real mutations
- `aliases` is mounted as `~/.aliases` in every container and auto-sourced by `.bashrc` — edit on host, changes are live
- `claude_tilda_base/dot_claude.json` is copied to `~/.claude.json` on first container start — controls dark mode, skips onboarding prompts
- `claude_tilda_base/dot_claude/` is copied to `~/.claude/` on first container start — add files here for future Claude config needs
- Each container gets its own private copy of the above — writes inside the container never affect the host templates
- If `$proj` is set in the environment, it is mounted as `/proj` inside the container and the trust dialog is pre-accepted via `/proj/.claude/settings.json`
- The `cld` alias (`cd /proj && claude --dangerously-skip-permissions`) starts Claude in `/proj` with no permission prompts
- `ANTHROPIC_API_KEY` is injected at container creation — recreate if it changes
- OverlayFS inspection requires `sudo` on the host
- `envs/` is never deleted by `clean` or `clean.all`

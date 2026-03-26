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
| `make merge NAME=<n>` | Commit container → image |
| `make list` | List all managed images and containers |
| `make cmp SRC=<e> DST=<e>` | Compare OverlayFS trees |
| `make diff SRC=<e> DST=<e>` | Export DST upperdir to `envs/` |
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

make diff SRC=cldcon-clean DST=cldcon-envA
make merge NAME=envA                     # snapshot → cldimg-envA
make new NAME=envB SRC=cldimg-envA       # branch from snapshot
```

---

## Notes

- `~/aliases` on the host is mounted read-only as `~/.aliases` in every container and auto-sourced by `.bashrc`
- `ANTHROPIC_API_KEY` is injected at container creation — recreate if it changes
- OverlayFS inspection requires `sudo` on the host
- `envs/` is never deleted by `clean` or `clean.all`

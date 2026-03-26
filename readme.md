# Claude Overlay Lab

A minimal, reproducible environment lab for experimenting with Claude Code CLI, plugins, and agent frameworks — with full filesystem visibility using Docker OverlayFS.

---

## Overview

Claude Overlay Lab provides:

* **Isolated environments** (per container)
* **Full filesystem diffing** (via OverlayFS upper layer)
* **Reproducible snapshots** (container → image)
* **Explicit environment comparison** (container ↔ image ↔ container)

This solves a core problem:

> Claude tools and plugins mutate global state unpredictably.

Instead of guessing what changed, this system lets you:

* observe **all filesystem mutations**
* compare environments deterministically
* export diffs for inspection or reuse

---

## Architecture

Each environment is:

* a **Docker container** (`cldcon-*`)
* based on a **clean base image** (`cldimg-base`)
* tracked via OverlayFS (`upperdir`)

```
Base Image (cldimg-base)
        +
Container (cldcon-envX)
        +
OverlayFS (upperdir = all changes)
```

The base image ships with:

* `claude` CLI (`@anthropic-ai/claude-code`) pre-installed globally via npm
* a `user` account with passwordless `sudo`
* standard tooling: `git`, `curl`, `jq`, `tree`, `python3`, `nodejs`

---

## Naming Convention

| Type       | Prefix    | Example     |
| ---------- | --------- | ----------- |
| Images     | `cldimg-` | cldimg-envA |
| Containers | `cldcon-` | cldcon-envA |

---

## Setup

### 1. Set your API key

```
export ANTHROPIC_API_KEY=sk-ant-...
```

This is passed into containers automatically at creation time.

### 2. Build base image

```
make build
```

---

## Usage

### Create new environment

```
make new NAME=envA SRC=cldimg-base
```

`SRC` is any image — `cldimg-base` for a fresh start, or a previously merged image (e.g. `cldimg-envA`) to branch from an existing environment. Creates `cldcon-envA` with `ANTHROPIC_API_KEY` injected.

Inside the container:

* run `claude` to start the CLI
* install plugins / MCP servers
* clone repos, run install scripts

---

### Re-enter environment

```
make run NAME=envA
```

### Stop a running container

```
make stop NAME=envA
```

---

## Inspect Changes

### Show filesystem changes (OverlayFS)

```
make cmp SRC=cldcon-clean DST=cldcon-envA
```

Shows the full tree of mutations in both environments based on OverlayFS `upperdir`.

---

### Export diff to host

```
make diff SRC=cldcon-clean DST=cldcon-envA
```

Output:

```
envs/cldcon-envA_minus_cldcon-clean/
```

Contains:

* binaries
* configs
* plugin files
* any filesystem mutations

---

### Quick metadata diff

```
make diff.meta NAME=envA
```

Example:

```
A /usr/local/bin/toolX
C /home/user/.bashrc
```

---

## Freeze Environment

### Merge container into image

```
make merge NAME=envA
```

Creates `cldimg-envA`. Use it as:

```
docker run -it cldimg-envA
```

---

## Compare Any Environments

Supports:

* container ↔ container
* image ↔ container
* image ↔ image

### Example

```
make cmp SRC=cldimg-envA DST=cldcon-envB
make diff SRC=cldimg-envA DST=cldcon-envB
```

---

## List All Environments

```
make list
```

Output:

```
Images:
  cldimg-base
  cldimg-envA

Containers:
  cldcon-clean
  cldcon-envA
```

---

## Cleanup

### Remove a specific environment

```
make clean NAME=envA
```

Removes `cldcon-envA` and `cldimg-envA`. The `envs/` directory is preserved.

### Remove everything

```
make clean.all
```

Prompts for confirmation, then removes all `cldcon-*` containers and `cldimg-*` images. The `envs/` directory is preserved.

---

## Key Concepts

### OverlayFS = Source of Truth

All changes made inside a container are stored in `upperdir`. This includes:

* new files
* modified files (copy-on-write)
* deletions (whiteouts)

---

### Containers vs Images

| Type      | Role                  |
| --------- | --------------------- |
| Container | Mutable environment   |
| Image     | Snapshot / checkpoint |

---

### Diff Strategy

* OverlayFS gives **full mutation visibility**
* No need to track install paths
* No reliance on plugin behavior

---

## Notes

* Accessing OverlayFS requires root (`sudo`) on the host
* `ANTHROPIC_API_KEY` is injected at container creation — re-export and recreate if it changes
* `merge` creates a snapshot, not a clean build
* exported diffs may include cache / temp files
* no volumes are used → ensures full visibility

---

## Typical Workflow

```
export ANTHROPIC_API_KEY=sk-ant-...

make build

make new NAME=clean SRC=cldimg-base
# verify: claude --version

make new NAME=envA SRC=cldimg-base
# inside: claude, install plugins, etc.

make diff SRC=cldcon-clean DST=cldcon-envA

make merge NAME=envA

docker run -it cldimg-envA
```

---

## Future Extensions

* automatic diff classification (bin/config/cache)
* Dockerfile generation from diffs
* environment lineage graph
* CLI wrapper (`cld`)

---

## Summary

Claude Overlay Lab turns uncontrolled Claude CLI environments into:

* isolated
* inspectable
* reproducible systems

It replaces guesswork with:

> **filesystem-level truth via OverlayFS**

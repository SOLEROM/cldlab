# Claude Overlay Lab

A minimal, reproducible environment lab for experimenting with Claude CLI tools, plugins, and agent frameworks — with full filesystem visibility using Docker OverlayFS.

---

## 🧠 Overview

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

## 🏗 Architecture

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

---

## 📦 Naming Convention

| Type       | Prefix    | Example     |
| ---------- | --------- | ----------- |
| Images     | `cldimg-` | cldimg-envA |
| Containers | `cldcon-` | cldcon-envA |

---

## ⚙️ Setup

### 1. Build base image

```
make build
```

---

## 🚀 Usage

### Run clean baseline

```
make run.clean
```

Creates:

```
cldcon-clean
```

---

### Create new environment

```
make new NAME=envA
```

Creates:

```
cldcon-envA
```

Inside container:

* install plugins
* clone repos
* run install scripts

---

### Re-enter environment

```
make run NAME=envA
```

---

## 🔍 Inspect Changes

### Show filesystem changes (OverlayFS)

```
make cmp SRC=cldcon-clean DST=cldcon-envA
```

Shows:

* full tree of changes in both environments
* based on OverlayFS upperdir

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

## 🧱 Freeze Environment

### Merge container into image

```
make merge NAME=envA
```

Creates:

```
cldimg-envA
```

Use it as:

```
docker run -it cldimg-envA
```

---

## 🔁 Compare Any Environments

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

## 📋 List All Environments

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

## 🧹 Cleanup

Remove all managed resources:

```
make clean
```

---

## 🧠 Key Concepts

### OverlayFS = Source of Truth

All changes made inside a container are stored in:

```
upperdir
```

This includes:

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

## ⚠️ Notes

* Accessing OverlayFS requires root (`sudo`)
* `merge` creates a snapshot, not a clean build
* exported diffs may include cache / temp files
* no volumes are used → ensures full visibility

---

## 🧪 Typical Workflow

```
make run.clean

make new NAME=envA
# install plugin

make diff SRC=cldcon-clean DST=cldcon-envA

make merge NAME=envA

docker run -it cldimg-envA
```

---

## 🚀 Future Extensions

* automatic diff classification (bin/config/cache)
* Dockerfile generation from diffs
* environment lineage graph
* CLI wrapper (`cld`)

---

## 🏁 Summary

Claude Overlay Lab turns uncontrolled plugin environments into:

* isolated
* inspectable
* reproducible systems

It replaces guesswork with:

> **filesystem-level truth via OverlayFS**

---


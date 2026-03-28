# config.yaml Reference

This file lives at the **repo root** next to the Makefile. It is the single source of truth for the control plane and all agent definitions. You can edit it directly or via the **✎ config** button in the web UI.

---

## Top-level structure

```yaml
app:
  ...

agents:
  - ...
  - ...
```

---

## `app` section

Global server settings.

| Key | Default | Description |
|-----|---------|-------------|
| `host` | `127.0.0.1` | Host the server binds to. Use `0.0.0.0` to expose on all interfaces (LAN access). |
| `port` | `5080` | TCP port the control plane listens on. |
| `tmux_socket` | `claude-control` | Name of the tmux socket file (creates `/tmp/tmux-<uid>/<socket>`). Keeps cldlab sessions isolated from any other tmux sessions on the machine. |
| `tmux_prefix` | `cldcc-` | Prefix prepended to every tmux session name created by the control plane (e.g. `cldcc-base-shell`). Must end with `-`. Change this if you run multiple instances of the control plane. |
| `scrollback_limit` | `10000` | Number of lines tmux keeps in each terminal's scrollback buffer. Higher values use more RAM. |

### Example

```yaml
app:
  host: 127.0.0.1
  port: 5080
  tmux_socket: claude-control
  tmux_prefix: "cldcc-"
  scrollback_limit: 10000
```

---

## `agents` section

A list of agent definitions. Each entry becomes one item in the sidebar.

### Common fields (all agent types)

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `name` | yes | — | Unique identifier. Alphanumeric + hyphens/underscores only (`[a-zA-Z0-9_-]`). Used in tmux session names and API paths. |
| `type` | no | `local_shell` | Agent type. Either `docker` or `local_shell`. |
| `path` | no | `../agents/<name>` | Directory shown as the agent's working folder. Path is relative to the repo root (where this config file lives). Used as cwd when opening terminal sessions and as the root for README files. |
| `readme` | no | `README.md` | Path to the README file shown in the right panel, relative to `path`. |
| `auto_start` | no | `false` | Reserved for future use. Not currently acted on at startup. |
| `tags` | no | `[]` | Free-form list of labels shown in the Config tab. No functional effect. |

### `docker` agent fields

Used when `type: docker`. The control plane manages the container lifecycle via `docker start/stop/restart` and opens shells with `docker exec`.

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `container` | no | `cldcon-<name>` | Docker container name. Must match exactly what `docker ps -a` shows. |
| `make_run` | no | `""` | Informational only — shown in the Config tab. The make command used to initially create/build this container. Not executed by the control plane. |
| `make_stop` | no | `""` | Informational only — shown in the Config tab. |

### `local_shell` agent fields

Used when `type: local_shell`. Opens a plain shell in `path` on the host machine. No docker involvement. Always shows as `running`.

No extra fields beyond the common ones.

---

## Full example

```yaml
app:
  host: 127.0.0.1
  port: 5080
  tmux_socket: claude-control
  tmux_prefix: "cldcc-"
  scrollback_limit: 10000

agents:
  # Docker-managed agent
  - name: base
    type: docker
    path: .                          # repo root is the working dir
    container: cldcon-base           # matches 'docker ps -a' name
    make_run: "make run NAME=base"   # informational, shown in Config tab
    make_stop: "make stop NAME=base"
    readme: base/readme.md           # relative to path
    auto_start: false
    tags: [base, ubuntu, node]

  # Agent in its own subfolder
  - name: plug-affaan
    type: docker
    path: plug-affaan                # relative to repo root
    container: cldcon-plug-affaan
    make_run: "make run NAME=plug-affaan"
    make_stop: "make stop NAME=plug-affaan"
    readme: readme.md
    auto_start: false
    tags: [plugin, affaan]

  # Host shell (no docker)
  - name: cldlab-shell
    type: local_shell
    path: .
    readme: readme.md
    auto_start: false
    tags: [host, utility]
```

---

## Notes

- **Paths** are always relative to the directory that contains `config.yaml` (the repo root). Use `.` for the repo root itself.
- **Agent names** must be unique and contain only `[a-zA-Z0-9_-]`. The name appears in tmux session IDs, so avoid spaces or special characters.
- **Editing via UI** — the **✎ config** button opens a YAML editor. Changes take effect on the next server restart (the registry is loaded once at boot).
- **Multiple instances** — if running two control planes on the same machine, give each a different `tmux_socket` and `tmux_prefix` to avoid session name collisions.

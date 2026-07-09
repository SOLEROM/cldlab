# cldLAB — systemd Service Setup

Installs the cldLAB Claude Control Plane as a **systemd user service** so it starts automatically at boot and can be managed without root.

---

## Prerequisites

- Ubuntu 20.04 or later (or any Debian-based distro with systemd ≥ 245)
- Python 3.8+
- tmux (control plane drives Claude sessions through tmux)
- docker (optional — needed for containerized agents)

Install/check host dependencies first:

```bash
cd /path/to/repo
./deps.sh            # or: ./deps.sh --check
```

---

## Quick Install

```bash
cd /path/to/repo/deploy/systemd
chmod +x install.sh
./install.sh
```

The script will:
1. Resolve the port (see **Port selection** below — defaults to the `.port` file)
2. Generate the service file from the template with the correct path and port
3. Place it in `~/.config/systemd/user/cldlab.service`
4. Enable the service (auto-start on boot)
5. Run `loginctl enable-linger` so the service starts at boot even before you log in
6. Start the service immediately

---

## Port selection

Most specific wins:

1. `--port N` passed to `install.sh`.
2. The `.port` file at the repo root (one line, just the number — this repo ships `.port` = `6002`).
3. Otherwise falls back to `5080` (the `config.yaml` default).

The resolved port is baked into the unit's `ExecStart` as `run.sh --public --port N`. To change it later, edit `.port` (or pass `--port`) and re-run `install.sh`, then `systemctl --user restart cldlab`.

---

## Manual Install

If you prefer to do it step by step:

```bash
# 1. Create the user systemd directory
mkdir -p ~/.config/systemd/user

# 2. Generate the service file (replace path and port to match your system)
PROJECT_PATH="/path/to/repo"
PORT="$(tr -d '[:space:]' < "$PROJECT_PATH/.port")"   # or set explicitly

sed \
  -e "s|__PROJECT_PATH__|${PROJECT_PATH}|g" \
  -e "s|__PORT__|${PORT}|g" \
  cldlab.service.template > ~/.config/systemd/user/cldlab.service

# 3. Reload systemd and enable the service
systemctl --user daemon-reload
systemctl --user enable cldlab

# 4. Allow the service to start at boot without an active login session
sudo loginctl enable-linger $USER

# 5. Start it now
systemctl --user start cldlab
```

---

## Managing the Service

```bash
systemctl --user status  cldlab       # check if running
systemctl --user start   cldlab       # start
systemctl --user stop    cldlab       # stop
systemctl --user restart cldlab       # restart
journalctl --user -u cldlab -f        # follow live logs
journalctl --user -u cldlab --since today   # logs from today
```

---

## Uninstall

```bash
./install.sh --uninstall
```

Or manually:

```bash
systemctl --user stop cldlab
systemctl --user disable cldlab
rm ~/.config/systemd/user/cldlab.service
systemctl --user daemon-reload
```

---

## Files in This Directory

| File | Purpose |
|------|---------|
| `cldlab.service.template` | Service file template with `__PROJECT_PATH__` and `__PORT__` placeholders |
| `install.sh` | Install/uninstall script — resolves the port, fills placeholders, registers, and starts the service |
| `README.md` | This file |

---

## Troubleshooting

**Service binds to the wrong port**

The port is fixed at install time from `.port` (or `--port`). After changing `.port`, re-run `install.sh` and `systemctl --user restart cldlab`. Check what the unit is actually running with:

```bash
systemctl --user cat cldlab
```

**`loginctl enable-linger` requires sudo**

On some Ubuntu setups linger requires elevated privileges:

```bash
sudo loginctl enable-linger $USER
```

**Service fails to start — check the logs**

```bash
journalctl --user -u cldlab -n 50 --no-pager
```

#!/usr/bin/env bash
# Start the Claude Control Plane server
# Usage: ./run.sh [--fresh] [--debug] [--public] [--port N] [--help]
set -e
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

# solBench checkout: $SOLBENCH_HOME (other layouts) › sibling ../solBench (the bench layout)
SOLBENCH_HOME="${SOLBENCH_HOME:-$(dirname "$REPO_ROOT")/solBench}"
if [[ ! -f "$SOLBENCH_HOME/webterm/pyproject.toml" ]]; then
  echo "[warn] solBench not found at $SOLBENCH_HOME (set SOLBENCH_HOME on a host with another layout)" \
       "— the terminal uses the legacy stack this run." >&2
  SOLBENCH_HOME=""
fi

# Parse flags
FRESH=0
SERVER_ARGS=()
for arg in "$@"; do
  case "$arg" in
    --help|-h)
      cat <<'EOF'
Claude Control Plane — run.sh

USAGE
  ./run.sh [options]

OPTIONS
  --fresh       Stop all running docker containers (make stop) and kill all
                tmux sessions before starting. Use this for a clean slate.

  --debug       Skip docker status checks on each /api/agents poll (instant
                response instead of running docker inspect). Also enables
                verbose Python logging (DEBUG level). Useful during frontend
                development — docker lifecycle buttons still work normally.

  --public      Bind the server to 0.0.0.0 instead of 127.0.0.1, making it
                reachable from other machines on the network.

  --port N      Override the port set in config.yaml (default: 5080).

  --config PATH Path to a custom config.yaml. Defaults to config.yaml in the
                repo root (next to this script).

  --help, -h    Show this help and exit.

EXAMPLES
  ./run.sh                        Normal start
  ./run.sh --fresh                Clean start: stop dockers + wipe tmux sessions
  ./run.sh --fresh --debug        Clean start with verbose logging
  ./run.sh --public --port 8080   Expose on all interfaces at port 8080
EOF
      exit 0
      ;;
    --fresh)
      FRESH=1
      ;;
    *)
      SERVER_ARGS+=("$arg")
      ;;
  esac
done

if [[ $FRESH -eq 1 ]]; then
  echo "[fresh] Stopping all docker containers..."
  make -C "$REPO_ROOT" stop 2>/dev/null || true

  echo "[fresh] Killing tmux sessions..."
  tmux -L claude-control kill-server 2>/dev/null || true

  echo "[fresh] Done. Starting clean."
fi

mkdir -p "$REPO_ROOT/control-plane/runtime/logs"

VENV="$REPO_ROOT/.venv"
if [[ ! -x "$VENV/bin/python3" ]]; then
  echo "[setup] No virtualenv found at $VENV — creating one..."
  python3 -m venv "$VENV"
  "$VENV/bin/python3" -m pip install -q -U pip
  "$VENV/bin/python3" -m pip install -q -r "$REPO_ROOT/control-plane/requirements.txt"
fi

# Shared webterm terminal library: editable install from $SOLBENCH_HOME, repaired
# on every start (a moved solBench leaves a stale editable finder behind).
# Without it the server falls back to the legacy shell.
webterm_ok() {  # cwd / and -I: from inside a solBench parent, cwd would shadow the install (webterm/install.sh:62-65)
  [[ -n "$SOLBENCH_HOME" ]] || return 0
  (cd / && "$VENV/bin/python3" -I - "$SOLBENCH_HOME/webterm/webterm" <<'PY'
import os, sys
try:
    import webterm
except Exception:
    sys.exit(1)
sys.exit(0 if os.path.samefile(os.path.dirname(webterm.__file__), sys.argv[1]) else 1)
PY
  ) 2>/dev/null
}
if ! webterm_ok; then
  echo "[setup] installing webterm from $SOLBENCH_HOME ..."
  "$SOLBENCH_HOME/webterm/install.sh" "$VENV" >/dev/null \
    || echo "[warn] webterm install failed — the terminal uses the legacy stack this run." >&2
fi

echo "Starting Claude Control Plane..."
"$VENV/bin/python3" "$REPO_ROOT/control-plane/server.py" --config "$REPO_ROOT/config.yaml" "${SERVER_ARGS[@]}"

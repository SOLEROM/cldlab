#!/usr/bin/env bash
# Start the Claude Control Plane server
# Usage: ./run.sh [--fresh] [--debug] [--public] [--port N] [--help]
set -e
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

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
  "$VENV/bin/pip" install -q -U pip
  "$VENV/bin/pip" install -q -r "$REPO_ROOT/control-plane/requirements.txt"
fi

echo "Starting Claude Control Plane..."
"$VENV/bin/python3" "$REPO_ROOT/control-plane/server.py" --config "$REPO_ROOT/config.yaml" "${SERVER_ARGS[@]}"

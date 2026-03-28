#!/usr/bin/env bash
# deps.sh — install all host dependencies for cldlab
# Usage: ./deps.sh [--check]
#   --check   only report what is missing, do not install anything
set -e

CHECK_ONLY=0
[[ "${1:-}" == "--check" ]] && CHECK_ONLY=1

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[ok]${NC}    $*"; }
warn() { echo -e "${YELLOW}[warn]${NC}  $*"; }
miss() { echo -e "${RED}[miss]${NC}  $*"; }

MISSING=()

# ── helpers ────────────────────────────────────────────────────────────────────

need_cmd() {
  local cmd=$1 label=${2:-$1}
  if command -v "$cmd" &>/dev/null; then
    ok "$label ($(command -v "$cmd"))"
  else
    miss "$label — not found"
    MISSING+=("$label")
  fi
}

need_python_pkg() {
  local pkg=$1
  if python3 -c "import $pkg" &>/dev/null 2>&1; then
    local ver
    ver=$(python3 -c "import importlib.metadata; print(importlib.metadata.version('$pkg'))" 2>/dev/null || echo "?")
    ok "python: $pkg ($ver)"
  else
    miss "python: $pkg — not installed"
    MISSING+=("py:$pkg")
  fi
}

# ── system tools ───────────────────────────────────────────────────────────────

echo ""
echo "=== System tools ==="
need_cmd python3    "Python 3"
need_cmd pip3       "pip3"
need_cmd docker     "Docker"
need_cmd tmux       "tmux"
need_cmd make       "make"
need_cmd jq         "jq"
need_cmd git        "git"

# ── Python packages ────────────────────────────────────────────────────────────

echo ""
echo "=== Python packages ==="
need_python_pkg flask
need_python_pkg flask_socketio
need_python_pkg flask_cors
need_python_pkg yaml          # pyyaml
need_python_pkg eventlet

# ── Docker daemon ──────────────────────────────────────────────────────────────

echo ""
echo "=== Docker daemon ==="
if command -v docker &>/dev/null; then
  if docker info &>/dev/null 2>&1; then
    ok "Docker daemon is running"
  else
    warn "Docker is installed but daemon is not running (start with: sudo systemctl start docker)"
    MISSING+=("docker-daemon")
  fi
fi

# ── summary / install ──────────────────────────────────────────────────────────

echo ""
if [[ ${#MISSING[@]} -eq 0 ]]; then
  echo -e "${GREEN}All dependencies satisfied.${NC}"
  exit 0
fi

echo -e "${RED}Missing: ${MISSING[*]}${NC}"

if [[ $CHECK_ONLY -eq 1 ]]; then
  echo "Run without --check to install missing deps."
  exit 1
fi

echo ""
echo "=== Installing ==="

# System packages via apt (best-effort, skip if no apt)
APT_PKGS=()
for m in "${MISSING[@]}"; do
  case "$m" in
    jq)     APT_PKGS+=(jq) ;;
    git)    APT_PKGS+=(git) ;;
    make)   APT_PKGS+=(make) ;;
    tmux)   APT_PKGS+=(tmux) ;;
    Docker) echo "  Docker: follow https://docs.docker.com/engine/install/ for your distro" ;;
  esac
done

if [[ ${#APT_PKGS[@]} -gt 0 ]] && command -v apt-get &>/dev/null; then
  echo "apt-get install: ${APT_PKGS[*]}"
  sudo apt-get update -qq && sudo apt-get install -y "${APT_PKGS[@]}"
fi

# Python packages via requirements.txt
HAS_PY_MISSING=0
for m in "${MISSING[@]}"; do [[ "$m" == py:* ]] && HAS_PY_MISSING=1 && break; done

if [[ $HAS_PY_MISSING -eq 1 ]]; then
  REQ="$(dirname "$0")/control-plane/requirements.txt"
  if [[ -f "$REQ" ]]; then
    echo "pip3 install -r $REQ"
    pip3 install -r "$REQ"
  else
    echo "requirements.txt not found at $REQ — falling back to individual install"
    pip3 install flask flask-socketio flask-cors pyyaml eventlet
  fi
fi

# Final check
echo ""
echo "=== Re-checking ==="
MISSING=()
need_cmd python3; need_cmd pip3; need_cmd docker; need_cmd tmux
need_cmd make; need_cmd jq; need_cmd git
need_python_pkg flask; need_python_pkg flask_socketio
need_python_pkg flask_cors; need_python_pkg yaml; need_python_pkg eventlet

echo ""
if [[ ${#MISSING[@]} -eq 0 ]]; then
  echo -e "${GREEN}All dependencies satisfied.${NC}"
else
  echo -e "${RED}Still missing: ${MISSING[*]}${NC}"
  echo "Some items may require manual installation (Docker, tmux via conda, etc)."
  exit 1
fi

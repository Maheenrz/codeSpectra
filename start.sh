#!/bin/bash
# =============================================================================
# CodeSpectra — start.sh
# Use this instead of docker-compose directly.
# Requires Docker Desktop with Compose v2 (docker compose, not docker-compose).
# =============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# ── Colour helpers ────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${GREEN}[CS]${NC} $1"; }
warn()  { echo -e "${YELLOW}[CS]${NC} $1"; }
error() { echo -e "${RED}[CS]${NC} $1"; exit 1; }

# ── Guard: must use docker compose v2 (space, not hyphen) ────────────────────
if ! docker compose version &>/dev/null; then
    error "docker compose v2 not found. Open Docker Desktop → update to latest version."
fi
COMPOSE_VERSION=$(docker compose version --short 2>/dev/null | head -1)
info "Docker Compose v2: $COMPOSE_VERSION"

# ── Parse arguments ───────────────────────────────────────────────────────────
CMD="${1:-up}"       # up | down | restart | rebuild | engine
shift 2>/dev/null || true

case "$CMD" in

  # ── Full startup (default) ─────────────────────────────────────────────────
  up)
    info "Starting all services…"
    docker compose up -d --build "$@"
    info "All services started."
    echo ""
    echo "  Frontend  → http://localhost:5173"
    echo "  Backend   → http://localhost:3000"
    echo "  Engine    → http://localhost:5000"
    echo "  pgAdmin   → http://localhost:5050"
    ;;

  # ── Rebuild only the analysis engine (fast, skips other services) ──────────
  engine)
    info "Rebuilding analysis engine only…"
    docker compose build --no-cache analysis-engine
    docker compose up -d --no-deps analysis-engine
    info "Analysis engine restarted."
    ;;

  # ── Rebuild any single service: ./start.sh rebuild backend ────────────────
  rebuild)
    SVC="${1:-analysis-engine}"
    info "Rebuilding $SVC…"
    docker compose build --no-cache "$SVC"
    docker compose up -d --no-deps "$SVC"
    info "$SVC restarted."
    ;;

  # ── Stop everything (preserves volumes) ───────────────────────────────────
  down)
    info "Stopping all services (volumes preserved)…"
    docker compose down --remove-orphans
    ;;

  # ── Full reset: stop + remove volumes (wipes DB) ──────────────────────────
  reset)
    warn "This will DELETE all data (postgres, redis volumes). Continue? [y/N]"
    read -r CONFIRM
    [[ "$CONFIRM" =~ ^[Yy]$ ]] || { info "Aborted."; exit 0; }
    docker compose down -v --remove-orphans
    info "All containers and volumes removed."
    ;;

  # ── Restart a service: ./start.sh restart backend ─────────────────────────
  restart)
    SVC="${1:-}"
    if [[ -z "$SVC" ]]; then
        docker compose restart
    else
        docker compose restart "$SVC"
        info "$SVC restarted."
    fi
    ;;

  # ── Show logs: ./start.sh logs analysis-engine ────────────────────────────
  logs)
    SVC="${1:-}"
    if [[ -z "$SVC" ]]; then
        docker compose logs -f --tail=100
    else
        docker compose logs -f --tail=100 "$SVC"
    fi
    ;;

  # ── Status ────────────────────────────────────────────────────────────────
  status)
    docker compose ps
    ;;

  *)
    echo "Usage: ./start.sh [up|down|reset|engine|rebuild <svc>|restart <svc>|logs <svc>|status]"
    echo ""
    echo "  up              Start everything (default)"
    echo "  engine          Rebuild + restart analysis engine only"
    echo "  rebuild <svc>   Rebuild + restart any service"
    echo "  down            Stop all (keeps data)"
    echo "  reset           Stop all + DELETE all data"
    echo "  restart <svc>   Restart a running service"
    echo "  logs <svc>      Tail logs"
    echo "  status          Show container status"
    ;;
esac

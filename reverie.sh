#!/bin/bash

set -euo pipefail

MODE="${1:-reverie}"

case "$MODE" in
  reverie)
    docker compose up -d --build backend webui
    echo "Started backend(core+api) and webui containers."
    echo "WebUI: http://localhost:5173"
    echo "API:   http://localhost:8000/health"
    ;;
  lucid)
    exec docker compose run --rm \
      -e REVERIE_RUN_MODE=Lucid \
      -e REVERIE_ENABLE_API=0 \
      -e REVERIE_SESSION_ID=lucid \
      backend python3 -m reverie.cli --mode Lucid --session-id lucid
    ;;
  murmur)
    exec docker compose run --rm \
      -e REVERIE_RUN_MODE=Murmur \
      -e REVERIE_ENABLE_API=0 \
      -e REVERIE_SESSION_ID=murmur \
      backend python3 -m reverie.cli --mode Murmur --session-id murmur
    ;;
  down)
    docker compose down
    ;;
  logs)
    docker compose logs -f backend webui
    ;;
  *)
    echo "Usage: ./reverie.sh [reverie|lucid|murmur|logs|down]"
    exit 1
    ;;
esac

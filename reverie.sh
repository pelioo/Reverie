#!/bin/bash

set -euo pipefail

MODE="${1:-reverie}"

case "$MODE" in
  reverie)
    SERVICE="reverie"
    docker compose up -d "$SERVICE"
    ;;
  lucid)
    SERVICE="lucid"
    docker compose up "$SERVICE"
    ;;
  murmur)
    SERVICE="murmur"
    docker compose up "$SERVICE"
    ;;
  *)
    echo "Usage: ./reverie.sh [reverie|lucid|murmur]"
    exit 1
    ;;
esac
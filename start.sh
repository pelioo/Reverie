#!/bin/bash

set -euo pipefail

# Start backend(core+api) and webui together
docker compose up -d

echo "Reverie backend(core+api) and webui are starting..."
echo "WebUI: http://localhost:5173"
echo "API:   http://localhost:8000/health"

# Keep original behavior: directly enter a Lucid interactive session
exec docker compose exec \
  backend python3 -m reverie.cli --mode Lucid --session-id lucid

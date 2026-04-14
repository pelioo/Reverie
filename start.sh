#!/bin/bash

set -euo pipefail

# 1) Start the Reverie (dream mode) container in the background
docker compose up -d reverie

# 2) Enter the same container and start a Lucid (dialog mode) session
exec docker compose exec reverie python3 -m reverie.cli --mode Lucid --session-id lucid

#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate
export $(grep -v '^#' .env | xargs)
python -m flask --app app.main run --debug --port=${PORT:-5000}

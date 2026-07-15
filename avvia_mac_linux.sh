#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"

FIRST_INSTALL=0
if [ ! -d .venv ]; then
  echo "Prima installazione: preparo l'ambiente Python..."
  python3 -m venv .venv
  FIRST_INSTALL=1
fi

. .venv/bin/activate
MARKER=".venv/.briscola5_installata"

# Install only on the first run, after dependency changes, or when
# the virtual environment is incomplete or damaged.
if [ "$FIRST_INSTALL" -eq 1 ] || [ ! -f "$MARKER" ] || [ pyproject.toml -nt "$MARKER" ] || \
   ! python -c "import fastapi, uvicorn, briscola5" >/dev/null 2>&1; then
  echo "Installazione/aggiornamento delle dipendenze (solo quando necessario)..."
  python -m pip install -e .
  touch "$MARKER"
fi

python -m briscola5.web.main

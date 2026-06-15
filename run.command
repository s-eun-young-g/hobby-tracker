#!/bin/bash
# Double-click this file in Finder to start tally and open it in your browser.
cd "$(dirname "$0")" || exit 1

if [ ! -x ".venv/bin/tally" ]; then
  echo "First run: setting up..."
  if command -v uv >/dev/null 2>&1; then
    uv venv .venv && VIRTUAL_ENV="$PWD/.venv" uv pip install -e .
  else
    python3 -m venv .venv && ./.venv/bin/pip install -e .
  fi
fi

# open the browser once the server is up
( sleep 2; open "http://localhost:8000" ) &

echo "tally is running at http://localhost:8000  (close this window to stop)"
exec ./.venv/bin/tally

#!/usr/bin/env bash
# Start local PostgreSQL (project-local install) and run all tests.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export PATH="$ROOT/.local/pgsql/bin:$PATH"
export DB_PORT=5433
export DB_USER=postgres
export DB_PASSWORD=
export DB_NAME=CS166_AUCTION_AND_BIDDING_DATABASE

# Start postgres if not running
if ! pg_isready -p 5433 -q 2>/dev/null; then
  pg_ctl -D "$ROOT/.local/pgdata" -o "-p 5433" -l "$ROOT/.local/postgres.log" start
  sleep 2
fi

source "$ROOT/venv/bin/activate"
python "$ROOT/test_full_project.py"
python "$ROOT/test_streamlit_ui.py"
echo ""
echo "All tests passed."

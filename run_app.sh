#!/usr/bin/env bash
# Start the CS166 Auction Streamlit app (database + UI).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# Use project-local PostgreSQL if installed
if [ -d "$ROOT/.local/pgsql/bin" ]; then
  export PATH="$ROOT/.local/pgsql/bin:$PATH"
  export DB_PORT="${DB_PORT:-5433}"
  export DB_USER="${DB_USER:-postgres}"
  export DB_PASSWORD="${DB_PASSWORD:-}"
  export DB_NAME="${DB_NAME:-CS166_AUCTION_AND_BIDDING_DATABASE}"

  if ! pg_isready -p "$DB_PORT" -q 2>/dev/null; then
    echo "Starting PostgreSQL on port $DB_PORT..."
    pg_ctl -D "$ROOT/.local/pgdata" -o "-p $DB_PORT" -l "$ROOT/.local/postgres.log" start
    sleep 2
  fi

  if ! psql -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" >/dev/null 2>&1; then
    echo "Setting up database (first run)..."
    createdb -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" 2>/dev/null || true
    psql -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$ROOT/AUCTION_AND_BIDDING_SCHEMA.sql" -q
    psql -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$ROOT/SAMPLE_AUCTION_AND_BIDDING_DATA.sql" -q
    echo "Database ready."
  fi
else
  echo "No local PostgreSQL found in .local/"
  echo "Set DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME if using your own Postgres."
fi

if [ ! -d "$ROOT/venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
  source "$ROOT/venv/bin/activate"
  pip install -q streamlit psycopg2-binary
else
  source "$ROOT/venv/bin/activate"
fi

echo ""
echo "Starting Streamlit at http://localhost:8501"
echo "Press Ctrl+C to stop."
echo ""

exec streamlit run "$ROOT/MAIN_STREAMLIT_UI.py" --server.headless true

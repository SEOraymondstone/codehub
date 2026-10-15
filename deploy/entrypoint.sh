#!/usr/bin/env bash
set -euo pipefail

# Apply database migrations (can be skipped for one-off containers).
if [ "${SKIP_MIGRATIONS:-0}" != "1" ]; then
  echo "[codehub] applying migrations..."
  python manage.py migrate --noinput
fi

# Build the hashed static manifest used by WhiteNoise.
echo "[codehub] collecting static files..."
python manage.py collectstatic --noinput

# Optional first-run bootstrap: create demo accounts when SEED_DEMO=1.
if [ "${SEED_DEMO:-0}" = "1" ]; then
  echo "[codehub] seeding demo data..."
  python manage.py seed_codehub || true
fi

exec "$@"

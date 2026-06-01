#!/bin/sh

set -e

echo "Waiting for PostgreSQL..."

while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 1
done

echo "PostgreSQL is ready."

echo "Running Alembic migrations..."
alembic upgrade head

if [ "$RUN_SEEDERS" = "true" ]; then
  echo "Running QA seeders..."

  if [ -f "scripts/seed_users.py" ]; then
    python -m scripts.seed_users --password "$SEED_DEFAULT_PASSWORD"
  fi

  if [ -f "scripts/seed_patients.py" ]; then
    python -m scripts.seed_patients --count 25
  fi

  if [ -f "scripts/seed_services.py" ]; then
    python -m scripts.seed_services
  fi

  echo "QA seeders completed."
fi

echo "Starting FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
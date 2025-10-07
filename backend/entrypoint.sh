#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."

# Wait for the database to be ready
while ! pg_isready -h db -p 5432 -q -U "$POSTGRES_USER"; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "PostgreSQL is up - executing command"

# --- INTELLIGENT COMMAND EXECUTION ---

# If the command is 'uvicorn' (the default for starting the app),
# then we first try to apply any existing migrations.
if [ "$1" = 'uvicorn' ]; then
    # Only run migrations if the migrations directory exists
    if [ -d "migrations" ]; then
        echo "Running database migrations..."
        alembic upgrade head
    fi
fi

# Execute the command passed to the container.
# This will be 'uvicorn...' when starting the app normally,
# or 'alembic...' when you run it manually.
exec "$@"
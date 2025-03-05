#!/bin/sh
# Wait for the PostgreSQL server to be available
./wait-for-it.sh db:5432 --timeout=30 --strict -- echo "Postgres is up - continuing"

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port 8000


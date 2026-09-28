#!/bin/sh
set -e

mkdir -p /app/data

echo "Running migrations..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput 2>/dev/null || true

exec "$@"

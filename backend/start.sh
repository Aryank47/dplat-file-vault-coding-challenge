#!/bin/sh

# Ensure data directory exists and has proper permissions
mkdir -p /app/data
chmod -R 777 /app/data

# Run migrations
echo "Running migrations..."
if [ "$RUN_MAKEMIGRATIONS" = "1" ]; then
  echo "Running makemigrations..."
  python manage.py makemigrations
fi

# Start server
echo "Starting server..."
gunicorn --bind 0.0.0.0:8000 core.wsgi:application 
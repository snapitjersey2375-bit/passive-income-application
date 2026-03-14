#!/bin/bash
set -e

# Use PORT env var if set, otherwise default to 8000
PORT=${PORT:-8000}

echo "Starting gunicorn on port $PORT..."
exec gunicorn -w 4 -b 0.0.0.0:$PORT apps.engine.main:app

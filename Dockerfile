# BACKUP DOCKERFILE - Ultra minimal, no complex config
FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y gcc postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY apps/engine/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY apps/engine /app/apps/engine

# Expose port
EXPOSE 8000

# Direct command - no entrypoint, no variables, no complexity
CMD python -m uvicorn apps.engine.main:app --host 0.0.0.0 --port 8000

# Build stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY apps/engine/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY apps/engine /app/apps/engine
COPY apps/web /app/apps/web
COPY packages /app/packages

# Create necessary directories
RUN mkdir -p /app/logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Expose port
EXPOSE 8000

# Run gunicorn with dynamic port
CMD ["sh", "-c", "gunicorn -w 4 -b 0.0.0.0:${PORT:-8000} apps.engine.main:app"]

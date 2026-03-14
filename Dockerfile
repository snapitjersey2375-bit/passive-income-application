# Ultra minimal, production-ready Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy entire apps directory (preserves __init__.py and structure)
COPY apps /app/apps
COPY packages /app/packages

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/apps/engine/requirements.txt

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set Python path to allow imports from /app
ENV PYTHONPATH=/app

# Expose port 8000
EXPOSE 8000

# Health check disabled - will add back after deployment
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the application from the correct working directory
CMD ["python", "-m", "uvicorn", "apps.engine.main:app", "--host", "0.0.0.0", "--port", "8000"]

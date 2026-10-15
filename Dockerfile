FROM python:3.13-slim

WORKDIR /app

# Install system dependencies (build-essential, libpq for PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create unprivileged user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/uploads /app/data && \
    chown -R appuser:appuser /app

# Copy application source code
COPY --chown=appuser:appuser app/ /app/app/
COPY --chown=appuser:appuser backend/ /app/backend/
COPY --chown=appuser:appuser frontend/ /app/frontend/
COPY --chown=appuser:appuser data/ /app/data/
COPY --chown=appuser:appuser run.py /app/run.py
COPY --chown=appuser:appuser wsgi.py /app/wsgi.py

USER appuser

EXPOSE 5000

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --threads 2 --timeout 120 wsgi:app"]

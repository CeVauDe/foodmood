# Use Python 3.13 slim image as base
FROM python:3.13-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_HOME="/opt/poetry" \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

# Set work directory
WORKDIR /app

# Copy Poetry files
COPY pyproject.toml poetry.lock ./

# Configure Poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-root \
    && rm -rf "$POETRY_CACHE_DIR"

# Copy only the necessary application files
COPY foodmood/ ./foodmood/
COPY gunicorn.conf.py ./
COPY scripts/entrypoint.prod.sh ./foodmood



# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app


# Allow user to use /var/www/
RUN groupadd varwwwusers \
    && adduser appuser varwwwusers \
    && mkdir /var/www \
    && chgrp -R varwwwusers /var/www/ \
    && chmod -R 770 /var/www

USER appuser

# Set working directory to the Django project
WORKDIR /app/foodmood

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

RUN chmod +x entrypoint.prod.sh

# Run the application
CMD ["./entrypoint.prod.sh"]

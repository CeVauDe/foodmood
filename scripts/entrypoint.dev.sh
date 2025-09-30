#!/usr/bin/env bash

# Install/sync dependencies (including dev dependencies)
uv sync --frozen

# Run migrations
python manage.py migrate --noinput

# Start development server
python manage.py runserver 0.0.0.0:8000

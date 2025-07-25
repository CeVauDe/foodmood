#!/bin/bash

# FoodMood Docker Development Scripts

set -e

case "$1" in
    "dev")
        echo "🚀 Starting development environment..."
        docker compose up --build
        ;;
    "dev-d")
        echo "🚀 Starting development environment in background..."
        docker compose up -d --build
        ;;
    "prod")
        echo "🚀 Starting production environment..."
        docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build
        ;;
    "prod-d")
        echo "🚀 Starting production environment in background..."
        docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
        ;;
    "stop")
        echo "🛑 Stopping all services..."
        docker compose down
        ;;
    "clean")
        echo "🧹 Cleaning up containers, images, and volumes..."
        docker compose down -v --rmi all --remove-orphans
        ;;
    "logs")
        echo "📋 Showing logs..."
        docker compose logs -f
        ;;
    "shell")
        echo "🐚 Opening Django shell..."
        docker compose exec web python foodmood/manage.py shell
        ;;
    "db-shell")
        echo "🗄️ Opening PostgreSQL shell..."
        docker compose exec db psql -U foodmood -d foodmood
        ;;
    "migrate")
        echo "📊 Running migrations..."
        docker compose exec web python foodmood/manage.py migrate
        ;;
    "makemigrations")
        echo "📊 Creating migrations..."
        docker compose exec web python foodmood/manage.py makemigrations
        ;;
    "collectstatic")
        echo "📁 Collecting static files..."
        docker compose exec web python foodmood/manage.py collectstatic --noinput
        ;;
    "test")
        echo "🧪 Running tests..."
        docker compose exec web python foodmood/manage.py test
        ;;
    "build")
        echo "🔨 Building Docker image..."
        docker compose build
        ;;
    *)
        echo "🤖 FoodMood Docker Helper"
        echo ""
        echo "Usage: ./scripts/docker.sh [command]"
        echo ""
        echo "Commands:"
        echo "  dev           Start development environment"
        echo "  dev-d         Start development environment in background"
        echo "  prod          Start production environment"
        echo "  prod-d        Start production environment in background"
        echo "  stop          Stop all services"
        echo "  clean         Clean up everything (containers, images, volumes)"
        echo "  logs          Show service logs"
        echo "  shell         Open Django shell"
        echo "  db-shell      Open PostgreSQL shell"
        echo "  migrate       Run database migrations"
        echo "  makemigrations Create new migrations"
        echo "  collectstatic Collect static files"
        echo "  test          Run tests"
        echo "  build         Build Docker image"
        echo ""
        ;;
esac

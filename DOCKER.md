# Docker Setup for FoodMood

This guide explains how to run FoodMood using Docker for both development and production environments.

## Quick Start

### Development with Docker Compose

1. **Start the development environment:**
   ```bash
   ./scripts/docker.sh dev
   # or manually: docker-compose up --build
   ```

2. **Access the application:**
   - Web app: http://localhost:8000
   - PostgreSQL: localhost:5432
   - Redis: localhost:6379

3. **Stop the environment:**
   ```bash
   ./scripts/docker.sh stop
   ```

### Production with Docker Compose

1. **Copy and configure environment variables:**
   ```bash
   cp .env.docker .env.prod
   # Edit .env.prod with your production values
   ```

2. **Start production environment:**
   ```bash
   ./scripts/docker.sh prod
   ```

## Services

- **web**: Django application (port 8000)
- **db**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)

## Helper Scripts

Use the `./scripts/docker.sh` script for common operations:

```bash
# Development
./scripts/docker.sh dev          # Start development environment
./scripts/docker.sh dev-d        # Start in background
./scripts/docker.sh logs         # View logs

# Database operations
./scripts/docker.sh migrate      # Run migrations
./scripts/docker.sh makemigrations  # Create migrations
./scripts/docker.sh shell        # Django shell

# Testing and maintenance
./scripts/docker.sh test         # Run tests
./scripts/docker.sh clean        # Clean up everything
./scripts/docker.sh build        # Rebuild images
```

## VS Code Dev Containers

For the best development experience with VS Code:

1. Install the "Dev Containers" extension
2. Open the project in VS Code
3. Click "Reopen in Container" when prompted
4. VS Code will build and start the development environment automatically

## Environment Variables

### Development (.env or .env.docker)
- `DJANGO_SECRET_KEY`: Django secret key
- `DJANGO_DEBUG`: Set to "true" for development

### Production (.env.prod)
- `DJANGO_SECRET_KEY`: Strong secret key for production
- `DJANGO_DEBUG`: Set to "false"
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: Database credentials

## Database

- **Development**: Uses PostgreSQL in Docker
- **Local fallback**: Falls back to SQLite if no PostgreSQL environment variables
- **Production**: Uses PostgreSQL with environment-specific credentials

## Volumes

- `postgres_data`: Persistent PostgreSQL data
- Development: Source code is mounted for live editing

## Health Checks

The web container includes health checks that verify the application is responding on port 8000.

## Troubleshooting

### Reset everything:
```bash
./scripts/docker.sh clean
./scripts/docker.sh dev
```

### View logs:
```bash
./scripts/docker.sh logs
# or for specific service:
docker-compose logs web
```

### Access container shell:
```bash
docker-compose exec web bash
```

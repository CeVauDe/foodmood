# foodmood


[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
[![Tests](https://github.com/CeVauDe/foodmood/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/CeVauDe/foodmood/actions/workflows/test.yml)
![MyPy](https://img.shields.io/badge/mypy-checked-blue.svg)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=CeVauDe_foodmood&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=CeVauDe_foodmood)

FoodMood is a webpage that lets you track your meals and your wellbeing to look for correlations.

## Features

- **User Authentication**: Complete registration and login system with Django's built-in authentication
- **Edible Tracking**: Track food items with support for recursive ingredient relationships
- **Quick-Create API**: Dynamically add new ingredients with duplicate detection
- **Admin Interface**: Django admin panel for managing users and edibles

## Getting Started

### Installation

1. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

2. Run database migrations:
   ```bash
   poetry run python foodmood/manage.py migrate
   ```

3. Start the development server:
   ```bash
   poetry run python foodmood/manage.py runserver
   ```

4. Access the application at http://localhost:8000

For Docker setup, see [DOCKER.md](DOCKER.md).

## Project Structure

### Edible Model
The core model is `Edible`, which represents any food item. Edibles can contain other edibles as ingredients, creating a flexible hierarchical structure:
- A simple ingredient (e.g., "tomato")
- A complex meal with multiple ingredients (e.g., "pasta with tomato sauce")

### Available Routes
- `/` - Home page
- `/users/register/` - User registration
- `/users/login/` - User login
- `/users/logout/` - User logout
- `/edibles/` - Edibles tracking page
- `/edibles/api/quick-create/` - API endpoint for creating ingredients
- `/health/` - Health check endpoint
- `/admin/` - Django admin interface

## Development

### Running Tests

To run tests locally:

```bash
# Run all tests
poetry run python foodmood/manage.py test

# Run tests with coverage
poetry run coverage run --source='.' foodmood/manage.py test
poetry run coverage report

# Run specific app tests
poetry run python foodmood/manage.py test users
```

### Code Quality

This project uses several tools to maintain code quality:

- **Ruff**: For linting and formatting
- **MyPy**: For type checking
- **Coverage**: For test coverage reporting

```bash
# Run linting
poetry run ruff check .

# Run formatting
poetry run ruff format .

# Run type checking
poetry run mypy foodmood --disallow-untyped-calls
```

### Continuous Integration

GitHub Actions automatically runs tests and linting on every push and pull request. The CI pipeline includes:

- Running the full test suite with Django's test runner (using SQLite for speed)
- Code linting with Ruff
- Type checking with MyPy
- Coverage reporting
- Testing against Python 3.13

All pull requests must pass the CI checks before they can be merged.

# foodmood


[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
[![Tests](https://github.com/CeVauDe/foodmood/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/CeVauDe/foodmood/actions/workflows/test.yml)
![MyPy](https://img.shields.io/badge/mypy-checked-blue.svg)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=CeVauDe_foodmood&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=CeVauDe_foodmood)

FoodMood is a webpage that lets you track your meals and your wellbeing to look for correlations.

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

# diabeateeze

A simple Django app for monitoring glucose levels and meals for managing diabetes.

## Development

This project uses a Python virtual environment located at `.venv/`.

### Setup

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
make migrate

# Create a superuser
.venv/bin/python manage.py createsuperuser
```

### Running the Development Server

```bash
make dev
# or
.venv/bin/python manage.py runserver
```

### Running Tests

```bash
make test
# or
.venv/bin/pytest

# Run specific test file
.venv/bin/pytest tests/entries/test_views.py

# Run specific test class
.venv/bin/pytest tests/entries/test_views.py::TestGlucoseReadingsListView

# Run with verbose output
.venv/bin/pytest -v
```

### Common Commands

```bash
# Run database migrations
make migrate

# Create new migrations
.venv/bin/python manage.py makemigrations

# Format code
.venv/bin/black src/

# Check for issues
make check
```

### Project Structure

- `src/` - Django application source code
  - `entries/` - Glucose readings, insulin doses, and meal tracking
  - `users/` - User management
  - `dashboard/` - Dashboard views
  - `base/` - Base models and utilities
- `tests/` - Test suite
- `templates/` - HTML templates
- `staticfiles/` - Static assets
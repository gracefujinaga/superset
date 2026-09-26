# Backend Development

Start the Superset Flask backend development server.

## Usage

```
/backend-dev
```

## What it does

- Activates the Python virtual environment
- Sets up Flask environment variables
- Starts the Flask development server
- Handles database connections and migrations

## Context

The Superset backend uses Flask with SQLAlchemy. The development server typically runs on port 8088. Ensure the database is configured and migrations are up to date before starting.
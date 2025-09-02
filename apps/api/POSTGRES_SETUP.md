# PostgreSQL Setup for Fantasy Edge API

This document provides instructions for setting up PostgreSQL for the Fantasy Edge API.

## Configuration

### Local Development (Docker)

For local development, use the Docker Compose setup which includes PostgreSQL:

```bash
docker-compose -f infra/docker-compose.dev.yml up
```

The database will be available at `postgresql://ff:ff@db:5432/ff`.

### Neon (Production)

For production, use Neon (serverless PostgreSQL):

1. Create a Neon project
2. Get the connection string from the Neon dashboard
3. Update the `DATABASE_URL` environment variable in your deployment configuration

Example connection string:
```
postgresql+psycopg://USER:PASSWORD@ep-xxxx.us-xx-x.aws.neon.tech/DB?sslmode=require
```

## Database Migrations

### Running Migrations

To run migrations, use the Alembic CLI:

```bash
cd apps/api
alembic upgrade head
```

### Creating Migrations

To create a new migration:

```bash
cd apps/api
alembic revision --autogenerate -m "description"
```

## Testing Database Connectivity

Use the verification script to test database connectivity:

```bash
cd apps/api
python verify_db.py
```

This script will test the connection using the `DATABASE_URL` environment variable.

## Running Tests

Run the database tests:

```bash
cd apps/api
python run_tests.py
```

## Health Check

The API includes a health check endpoint at `/health` that verifies database connectivity.

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
  - Local: `postgresql+psycopg://ff:ff@db:5432/ff`
  - Neon: `postgresql+psycopg://USER:PASSWORD@ep-xxxx.us-xx-x.aws.neon.tech/DB?sslmode=require`

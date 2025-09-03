#!/bin/bash
# Pre-start script for Fantasy Edge API

set -e

# Validate required environment variables
if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL is not set"
    exit 1
fi

if [ -z "$TOKEN_CRYPTO_KEY" ]; then
    echo "Error: TOKEN_CRYPTO_KEY is not set"
    exit 1
fi

# Validate the Fernet key (masked print)
echo "Validating TOKEN_CRYPTO_KEY..."
if ! python3 -c "from cryptography.fernet import Fernet; Fernet('$TOKEN_CRYPTO_KEY')" 2>/dev/null; then
    echo "Error: TOKEN_CRYPTO_KEY is not a valid 32-byte urlsafe base64 key"
    exit 1
fi
echo "TOKEN_CRYPTO_KEY is valid"

# Run database migrations
echo "Running database migrations..."
cd /app
alembic upgrade head

# Start the application
echo "Starting the application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000

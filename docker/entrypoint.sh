#!/bin/bash
set -e

echo "========================================"
echo "SmartSupport AI - Docker Entrypoint"
echo "========================================"

# Wait for database to be ready (if using PostgreSQL)
if [ "$DATABASE_URL" != "" ] && [[ "$DATABASE_URL" == *"postgresql"* ]]; then
    echo "Waiting for PostgreSQL..."

    # Extract host and port from DATABASE_URL
    DB_HOST=$(echo $DATABASE_URL | sed -r 's|.*@([^:/]+).*|\1|')
    DB_PORT=$(echo $DATABASE_URL | sed -r 's|.*:([0-9]+)/.*|\1|')

    until pg_isready -h ${DB_HOST:-postgres} -p ${DB_PORT:-5432} -U smartsupport_user; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 2
    done

    echo "PostgreSQL is up - continuing..."
fi

# Wait for Redis to be ready (if using Redis)
if [ "$REDIS_URL" != "" ]; then
    echo "Waiting for Redis..."

    # Extract host and port from REDIS_URL
    REDIS_HOST=$(echo $REDIS_URL | sed -r 's|.*://([^:/]+).*|\1|')
    REDIS_PORT=$(echo $REDIS_URL | sed -r 's|.*:([0-9]+).*|\1|')

    until redis-cli -h ${REDIS_HOST:-redis} -p ${REDIS_PORT:-6379} ping; do
        echo "Redis is unavailable - sleeping"
        sleep 2
    done

    echo "Redis is up - continuing..."
fi

# Initialize database
echo "Initializing database..."
python -c "from src.database import init_db; init_db()"

# Initialize knowledge base if not exists
if [ ! -f "./data/knowledge_base/faqs.json" ]; then
    echo "Initializing knowledge base..."
    if [ -f "./initialize_kb.py" ]; then
        python initialize_kb.py
    else
        echo "Warning: initialize_kb.py not found, skipping KB initialization"
    fi
else
    echo "Knowledge base already initialized"
fi

# Create log directory if it doesn't exist
mkdir -p logs

echo "========================================"
echo "Starting application..."
echo "Environment: ${ENVIRONMENT:-development}"
echo "========================================"

# Execute the main command
exec "$@"

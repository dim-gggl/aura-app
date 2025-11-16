#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  Aura Art - Docker Entrypoint${NC}"
echo -e "${GREEN}======================================${NC}"

# Function to wait for PostgreSQL
wait_for_postgres() {
    echo -e "${YELLOW}[1/6] Waiting for PostgreSQL...${NC}"

    if [ -z "$DATABASE_URL" ]; then
        echo -e "${RED}ERROR: DATABASE_URL not set${NC}"
        exit 1
    fi

    # Extract host and port from DATABASE_URL
    # Format: postgresql://user:pass@host:port/db
    POSTGRES_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    POSTGRES_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')

    # Default to localhost:5432 if extraction failed
    POSTGRES_HOST=${POSTGRES_HOST:-db}
    POSTGRES_PORT=${POSTGRES_PORT:-5432}

    echo "Checking PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT}..."

    max_attempts=30
    attempt=0

    until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U postgres > /dev/null 2>&1; do
        attempt=$((attempt + 1))
        if [ $attempt -eq $max_attempts ]; then
            echo -e "${RED}ERROR: PostgreSQL did not become ready in time${NC}"
            exit 1
        fi
        echo "PostgreSQL is unavailable - sleeping (attempt $attempt/$max_attempts)"
        sleep 2
    done

    echo -e "${GREEN}PostgreSQL is ready!${NC}"
}

# # Function to setup PostgreSQL schema
# setup_schema() {
#     echo -e "${YELLOW}[2/6] Setting up PostgreSQL schema...${NC}"

#     # Try to create the aura schema if it doesn't exist
#     python manage.py setup_aura_schema || {
#         echo -e "${YELLOW}Warning: Could not setup schema (may already exist)${NC}"
#     }

#     echo -e "${GREEN}Schema setup complete!${NC}"
# }

# Function to run migrations
run_migrations() {
    echo -e "${YELLOW}[3/6] Running database migrations...${NC}"

    python manage.py migrate --noinput

    echo -e "${GREEN}Migrations complete!${NC}"
}

# Function to collect static files
collect_static() {
    echo -e "${YELLOW}[4/6] Collecting static files...${NC}"

    # Always collect static files in production
    python manage.py collectstatic --noinput --clear
    echo -e "${GREEN}Static files collected!${NC}"
}

# Function to create superuser (optional, for first deployment)
create_superuser() {
    echo -e "${YELLOW}[5/6] Checking for superuser...${NC}"

    if [ "$CREATE_SUPERUSER" = "true" ] && [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
        echo "Creating superuser..."
        python manage.py createsuperuser \
            --noinput \
            --username "$DJANGO_SUPERUSER_USERNAME" \
            --email "${DJANGO_SUPERUSER_EMAIL:-admin@example.com}" \
            2>/dev/null || echo -e "${YELLOW}Superuser may already exist${NC}"
    else
        echo -e "${YELLOW}Skipping superuser creation${NC}"
    fi
}

# Function to run health check
health_check() {
    echo -e "${YELLOW}[6/6] Running system checks...${NC}"

    python manage.py check --deploy || {
        echo -e "${RED}WARNING: Some deployment checks failed${NC}"
    }

    echo -e "${GREEN}System checks complete!${NC}"
}

# Main execution
main() {
    wait_for_postgres
    # setup_schema
    run_migrations
    collect_static
    create_superuser
    health_check

    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}  Initialization Complete!${NC}"
    echo -e "${GREEN}  Starting application...${NC}"
    echo -e "${GREEN}======================================${NC}"

    # Execute the main command (Gunicorn)
    exec "$@"
}

# Run main function
main "$@"

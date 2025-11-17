#!/bin/bash
# Script to reset Railway PostgreSQL database
# This removes all tables and allows migrations to run from scratch

set -e

echo "======================================="
echo "  Railway Database Reset Script"
echo "======================================="
echo ""
echo "WARNING: This will DELETE ALL DATA in your Railway database!"
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable is not set"
    echo "Please set it first:"
    echo "  export DATABASE_URL='your-railway-postgres-url'"
    exit 1
fi

echo ""
echo "Connecting to database..."
echo ""

# Drop all tables in the public schema
psql "$DATABASE_URL" <<EOF
-- Drop all tables
DO \$\$ DECLARE
    r RECORD;
BEGIN
    -- Drop all tables
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'DROP TABLE IF EXISTS public.' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;

    -- Drop all sequences
    FOR r IN (SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public') LOOP
        EXECUTE 'DROP SEQUENCE IF EXISTS public.' || quote_ident(r.sequence_name) || ' CASCADE';
    END LOOP;

    -- Drop all views
    FOR r IN (SELECT table_name FROM information_schema.views WHERE table_schema = 'public') LOOP
        EXECUTE 'DROP VIEW IF EXISTS public.' || quote_ident(r.table_name) || ' CASCADE';
    END LOOP;
END \$\$;

-- Verify cleanup
SELECT 'Tables remaining: ' || COUNT(*)::text FROM pg_tables WHERE schemaname = 'public';
EOF

echo ""
echo "======================================="
echo "  Database reset complete!"
echo "======================================="
echo ""
echo "Next steps:"
echo "1. Trigger a new deployment on Railway"
echo "2. Migrations will run from scratch with the correct settings"
echo ""

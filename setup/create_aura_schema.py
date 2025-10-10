#!/usr/bin/env python3
"""
Script to create the 'aura' schema in PostgreSQL database.
This script should be run before running Django migrations.
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aura_app.settings.dev')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line


def create_aura_schema():
    """
    Create the 'aura' schema in the PostgreSQL database.
    """
    with connection.cursor() as cursor:
        try:
            # Check if schema already exists
            cursor.execute("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name = 'aura'
            """)
            
            if cursor.fetchone():
                print("✅ Schema 'aura' already exists.")
                return
            
            # Create the schema
            cursor.execute('CREATE SCHEMA IF NOT EXISTS aura;')
            print("✅ Schema 'aura' created successfully.")
            
            # Grant permissions to the database user
            cursor.execute("""
                GRANT USAGE ON SCHEMA aura TO aura_user;
                GRANT CREATE ON SCHEMA aura TO aura_user;
                GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA aura TO aura_user;
                GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA aura TO aura_user;
            """)
            print("✅ Permissions granted to 'aura_user' for schema 'aura'.")
            
        except Exception as e:
            print(f"❌ Error creating schema: {e}")
            return False
    
    return True


def set_search_path():
    """
    Set the search_path to include 'aura' schema first.
    """
    with connection.cursor() as cursor:
        try:
            cursor.execute("ALTER DATABASE aura_db SET search_path TO aura, public;")
            print("✅ Search path set to 'aura, public' for database 'aura_db'.")
        except Exception as e:
            print(f"⚠️  Warning: Could not set search_path: {e}")


if __name__ == "__main__":
    print("🚀 Creating 'aura' schema in PostgreSQL...")
    
    if create_aura_schema():
        set_search_path()
        print("\n✅ Schema setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Run: python manage.py makemigrations")
        print("2. Run: python manage.py migrate")
    else:
        print("\n❌ Schema setup failed!")
        sys.exit(1)

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    """
    Django management command to create the 'aura' schema in PostgreSQL.

    Usage:
        python manage.py setup_aura_schema
    """

    help = "Create the aura schema in PostgreSQL database"

    def handle(self, *args, **options):
        """
        Create the 'aura' schema and set up permissions.
        """
        self.stdout.write("🚀 Creating 'aura' schema in PostgreSQL...")

        with connection.cursor() as cursor:
            try:
                # Check if schema already exists
                cursor.execute(
                    """
                    SELECT schema_name
                    FROM information_schema.schemata
                    WHERE schema_name = 'aura'
                """
                )

                if cursor.fetchone():
                    self.stdout.write(
                        self.style.SUCCESS("✅ Schema 'aura' already exists.")
                    )
                    return

                # Create the schema
                cursor.execute("CREATE SCHEMA IF NOT EXISTS aura;")
                self.stdout.write(
                    self.style.SUCCESS("✅ Schema 'aura' created successfully.")
                )

                # Grant permissions to the database user
                cursor.execute(
                    """
                    GRANT USAGE ON SCHEMA aura TO aura_user;
                    GRANT CREATE ON SCHEMA aura TO aura_user;
                    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA aura TO aura_user;
                    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA aura TO aura_user;
                """
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        "✅ Permissions granted to 'aura_user' for schema 'aura'."
                    )
                )

                # Set search path for the database
                cursor.execute(
                    "ALTER DATABASE aura_db SET search_path TO aura, public;"
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        "✅ Search path set to 'aura, public' for database 'aura_db'."
                    )
                )

                self.stdout.write(
                    self.style.SUCCESS("\n✅ Schema setup completed successfully!")
                )
                self.stdout.write("\n📝 Next steps:")
                self.stdout.write("1. Run: python manage.py makemigrations")
                self.stdout.write("2. Run: python manage.py migrate")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error creating schema: {e}"))
                raise

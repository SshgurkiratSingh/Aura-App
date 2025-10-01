from sqlalchemy import text, inspect
from database import engine

def main():
    """
    Connects to the database and applies all necessary schema updates in a robust way.
    This is the single source of truth for the database structure.
    """
    print("Connecting to the database to apply all schema updates...")

    # A list of all schema update commands that are safe to run multiple times
    schema_commands = [
        "CREATE EXTENSION IF NOT EXISTS postgis;",
        
        """
        CREATE TABLE IF NOT EXISTS air_quality_data (
            time TIMESTAMPTZ NOT NULL, latitude DOUBLE PRECISION NOT NULL, longitude DOUBLE PRECISION NOT NULL,
            source TEXT, aqi INTEGER, pm25 DOUBLE PRECISION, no2 DOUBLE PRECISION, o3 DOUBLE PRECISION
        );
        """,
        
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL, health_conditions JSONB,
            created_at TIMESTAMPTZ DEFAULT NOW(), age_group VARCHAR(50), persona VARCHAR(100)
        );
        """,

        """
        CREATE TABLE IF NOT EXISTS weather_forecasts (
            time TIMESTAMPTZ NOT NULL, latitude DOUBLE PRECISION NOT NULL, longitude DOUBLE PRECISION NOT NULL,
            temperature_2m DOUBLE PRECISION, relative_humidity_2m DOUBLE PRECISION,
            precipitation DOUBLE PRECISION, wind_speed_10m DOUBLE PRECISION,
            PRIMARY KEY (time, latitude, longitude)
        );
        """,
        
        # --- THIS IS THE FIX ---
        # Added the CREATE TABLE command for the citizen_reports table
        """
        CREATE TABLE IF NOT EXISTS citizen_reports (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            latitude DOUBLE PRECISION NOT NULL,
            longitude DOUBLE PRECISION NOT NULL,
            description TEXT,
            image_url VARCHAR(255),
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """,

        "ALTER TABLE air_quality_data ADD COLUMN IF NOT EXISTS pm10 DOUBLE PRECISION;",
        "ALTER TABLE air_quality_data ADD COLUMN IF NOT EXISTS so2 DOUBLE PRECISION;",
        "ALTER TABLE air_quality_data ADD COLUMN IF NOT EXISTS co DOUBLE PRECISION;",
        "ALTER TABLE air_quality_data ADD COLUMN IF NOT EXISTS terrain_height DOUBLE PRECISION;",
        "ALTER TABLE air_quality_data ADD COLUMN IF NOT EXISTS surface_pressure DOUBLE PRECISION;",
        "ALTER TABLE air_quality_data ADD COLUMN IF NOT EXISTS wind_speed DOUBLE PRECISION;",
        "ALTER TABLE air_quality_data ADD COLUMN IF NOT EXISTS quality_flag INTEGER;",

        "ALTER TABLE users ADD COLUMN IF NOT EXISTS age_group VARCHAR(50);",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS persona VARCHAR(100);"
    ]

    # This command is handled separately because it doesn't support "IF NOT EXISTS"
    add_constraint_sql = text("""
        ALTER TABLE air_quality_data 
        ADD CONSTRAINT unique_measurement UNIQUE (time, latitude, longitude);
    """)

    with engine.connect() as connection:
        with connection.begin() as transaction:
            try:
                print("- Applying schema updates (extensions, tables, columns)...")
                for command in schema_commands:
                    connection.execute(text(command))
                print("  ...Schema updates applied.")

                try:
                    print("- Adding unique constraint (if it doesn't exist)...")
                    connection.execute(add_constraint_sql)
                    print("  ...Constraint 'unique_measurement' added successfully.")
                except Exception as e:
                    if 'relation "unique_measurement" already exists' in str(e):
                        print("  ...Constraint already exists. Skipping.")
                    else:
                        raise e

                print("\n✅ Schema is now fully up to date.")
            except Exception as e:
                print(f"An error occurred during the main transaction: {e}")
                transaction.rollback()

if __name__ == "__main__":
    main()


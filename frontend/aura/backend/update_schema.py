from sqlalchemy import text
from database import engine

def main():
    """
    Connects to the database and applies all schema updates one by one
    to ensure every command is executed correctly.
    """
    print("Connecting to the database to apply all schema updates...")
    
    # We use a single connection for all operations
    with engine.connect() as connection:
        # Each command will be in its own transaction
        try:
            print("\n--- Step 1: Enabling Extensions ---")
            with connection.begin():
                connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            print("✅ PostGIS extension enabled.")

            print("\n--- Step 2: Creating Tables ---")
            with connection.begin():
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL,
                        health_conditions JSONB, created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                """))
                connection.execute(text("""
                    CREATE TABLE IF NOT EXISTS air_quality_data (
                        time TIMESTAMPTZ NOT NULL, latitude DOUBLE PRECISION NOT NULL,
                        longitude DOUBLE PRECISION NOT NULL, source TEXT, aqi INTEGER,
                        pm25 DOUBLE PRECISION, no2 DOUBLE PRECISION, o3 DOUBLE PRECISION,
                        pm10 DOUBLE PRECISION, so2 DOUBLE PRECISION, co DOUBLE PRECISION
                    );
                """))
            print("✅ Tables 'users' and 'air_quality_data' are present.")

            print("\n--- Step 3: Updating 'users' Table Columns ---")
            with connection.begin():
                connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS age_group VARCHAR(50);"))
                connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS persona VARCHAR(100);"))
            print("✅ 'users' table columns are up to date.")

            print("\n--- Step 4: Updating 'air_quality_data' Table Columns ---")
            with connection.begin():
                connection.execute(text("ALTER TABLE air_quality_data ADD COLUMN IF NOT EXISTS terrain_height DOUBLE PRECISION;"))
                connection.execute(text("ALTER TABLE air_quality_data ADD COLUMN IF NOT EXISTS surface_pressure DOUBLE PRECISION;"))
                connection.execute(text("ALTER TABLE air_quality_data ADD COLUMN IF NOT EXISTS wind_speed DOUBLE PRECISION;"))
                connection.execute(text("ALTER TABLE air_quality_data ADD COLUMN IF NOT EXISTS quality_flag INTEGER;"))
            print("✅ 'air_quality_data' table columns are up to date.")

            print("\n--- Step 5: Adding Unique Constraint ---")
            try:
                with connection.begin():
                    connection.execute(text("""
                        ALTER TABLE air_quality_data 
                        ADD CONSTRAINT unique_measurement UNIQUE (time, latitude, longitude);
                    """))
                print("✅ Constraint 'unique_measurement' added successfully.")
            except Exception as e:
                if 'relation "unique_measurement" already exists' in str(e):
                    print("✅ Constraint already exists. Skipping.")
                else:
                    raise e
            
            print("\n🚀 All schema updates completed successfully!")

        except Exception as e:
            print(f"\n❌ A critical error occurred during the update process: {e}")

if __name__ == "__main__":
    main()


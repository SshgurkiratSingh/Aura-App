from sqlalchemy import text
from database import engine

# This SQL command is specifically for creating the weather_forecasts table.
create_weather_table_sql = text("""
    CREATE TABLE IF NOT EXISTS weather_forecasts (
        time TIMESTAMPTZ NOT NULL,
        latitude DOUBLE PRECISION NOT NULL,
        longitude DOUBLE PRECISION NOT NULL,
        temperature_2m DOUBLE PRECISION,
        relative_humidity_2m DOUBLE PRECISION,
        precipitation DOUBLE PRECISION,
        wind_speed_10m DOUBLE PRECISION,
        PRIMARY KEY (time, latitude, longitude)
    );
""")

def main():
    """ Connects to the database and ensures the 'weather_forecasts' table exists. """
    print("Connecting to the database to create the 'weather_forecasts' table...")
    try:
        with engine.connect() as connection:
            with connection.begin() as transaction:
                connection.execute(create_weather_table_sql)
        print("✅ SUCCESS: The 'weather_forecasts' table is now guaranteed to exist.")
    except Exception as e:
        print("❌ FAILED: An error occurred while creating the table.")
        print(e)

if __name__ == "__main__":
    main()

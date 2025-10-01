import requests
import os
from sqlalchemy import text
from database import SessionLocal
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://data.opendatasoft.com/api/explore/v2.1/catalog/datasets/openaq@public/records?where=country%20%3D%20%22KR%22&order_by=measurements_lastupdated%20DESC&limit=100"

API_KEY = os.getenv("OPENDATASOFT_API_KEY")
ACCEPTED_PARAMS = ['pm25', 'no2', 'o3', 'pm10', 'so2', 'co']

def fetch_and_store_data():
    if not API_KEY:
        raise ValueError("OPENDATASOFT_API_KEY not found. Please add it to your .env file.")
    print(f"Fetching data from: {API_URL}")
    headers = {"Authorization": f"ApiKey {API_KEY}"}
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return

    db = SessionLocal()
    insert_count = 0
    skipped_count = 0

    try:
        if not data.get('results'):
            print("API did not return any results.")
            return
        print(f"Found {len(data['results'])} records. Processing...")

        for record in data['results']:
            param = record.get('measurements_parameter')
            if not record.get('coordinates') or not param:
                skipped_count += 1
                continue
            param = param.lower()
            if param in ACCEPTED_PARAMS:
                latitude = record['coordinates']['lat']
                longitude = record['coordinates']['lon']
                value = record['measurements_value']
                last_updated = record['measurements_lastupdated']
                insert_query = text(f"""
                    INSERT INTO air_quality_data (time, latitude, longitude, source, {param})
                    VALUES (:time, :lat, :lon, :source, :value)
                    ON CONFLICT (time, latitude, longitude) DO UPDATE SET {param} = :value;
                """)
                db.execute(insert_query, {
                    "time": last_updated,
                    "lat": latitude,
                    "lon": longitude,
                    "source": "OpenDataSoft-OpenAQ",
                    "value": value
                })
                insert_count += 1
            else:
                skipped_count += 1

        db.commit()
        print(f"Successfully processed records. Inserted/Updated: {insert_count}. Skipped: {skipped_count}.")

    except Exception as e:
        print(f"An error occurred during database insertion: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fetch_and_store_data()

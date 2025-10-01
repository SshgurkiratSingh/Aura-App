from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from pydantic import BaseModel, Field
from typing import List, Optional
import json
import os
import requests
from dotenv import load_dotenv

# Load all environment variables from .env
load_dotenv()

from database import get_db, engine
from lib.mockData import mockLocationForecast
from personalization_engine import generate_alert
from ai_guide import get_gemini_response

app = FastAPI()

# --- Environment API Keys ---
WAQI_API_KEY = os.getenv("WAQI_API_KEY")
MAPTILER_API_KEY = os.getenv("MAPTILER_API_KEY")

# --- CORS SETTINGS ---
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://10.104.236.87:3000",
    "http://10.202.253.162:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class UserProfile(BaseModel):
    name: str
    age_group: Optional[str] = None
    persona: Optional[str] = None
    healthConditions: Optional[List[str]] = Field(default_factory=list, alias='healthConditions')

class ChatRequest(BaseModel):
    userId: int
    question: str
    lat: float
    lon: float

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"message": "AURA Backend is running!"}

@app.post("/api/v1/users/register")
def register_user(profile: UserProfile, db: Session = Depends(get_db)):
    query = text("""
        INSERT INTO users (name, health_conditions, age_group, persona)
        VALUES (:name, :health_conditions, :age_group, :persona)
        RETURNING id;
    """)
    try:
        health_conditions_json = json.dumps(profile.healthConditions)
        result = db.execute(query, {
            "name": profile.name,
            "health_conditions": health_conditions_json,
            "age_group": profile.age_group,
            "persona": profile.persona
        })
        user_id = result.scalar()
        db.commit()
        return {"message": "User profile created successfully", "user_id": user_id}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@app.get("/api/v1/pollutants/available")
def get_available_pollutants(db: Session = Depends(get_db)):
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('air_quality_data')]
    available = []
    for pollutant in ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']:
        if pollutant in columns:
            query = text(f"SELECT EXISTS (SELECT 1 FROM air_quality_data WHERE {pollutant} IS NOT NULL)")
            if db.execute(query).scalar():
                available.append(pollutant.upper())
    return available

@app.get("/api/v1/grid/current")
def get_current_grid_data(
    db: Session = Depends(get_db),
    pollutant: str = 'auto',
    time_offset: int = 0
):
    pollutant_to_query = "COALESCE(pm25, pm10, o3, no2, so2, co)"
    if pollutant != 'auto':
        safe_pollutant = "".join(filter(str.isalnum, pollutant)).lower()
        if safe_pollutant in ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co']:
            pollutant_to_query = safe_pollutant

    query = text(f"""
        SELECT
            latitude as lat,
            longitude as lon,
            {pollutant_to_query} as aqi
        FROM 
            air_quality_data
        WHERE 
            {pollutant_to_query} IS NOT NULL
            AND time BETWEEN 
                ((SELECT MAX(time) FROM air_quality_data) + (INTERVAL '1 hour' * :time_offset) - INTERVAL '3 hours')
                AND 
                ((SELECT MAX(time) FROM air_quality_data) + (INTERVAL '1 hour' * :time_offset) + INTERVAL '3 hours')
        LIMIT 2000;
    """)
    
    result = db.execute(query, {"time_offset": time_offset}).mappings().all()
    return list(result)

@app.get("/api/v1/users/{user_id}/personalized_alert")
def get_personalized_alert(user_id: int, lat: float, lon: float, db: Session = Depends(get_db)):
    user_profile_query = text("SELECT name, health_conditions, persona, age_group FROM users WHERE id = :user_id")
    user_profile = db.execute(user_profile_query, {"user_id": user_id}).mappings().first()

    if not user_profile:
        return {"error": "User not found"}

    air_quality_query = text("""
        WITH recent_data AS (
            SELECT * FROM air_quality_data
            WHERE time > (SELECT MAX(time) FROM air_quality_data) - INTERVAL '12 hours'
            AND COALESCE(pm25, pm10, o3, no2, so2, co) IS NOT NULL
        )
        SELECT COALESCE(pm25, pm10, o3, no2, so2, co) as aqi
        FROM recent_data
        ORDER BY ST_Distance(ST_MakePoint(longitude, latitude), ST_MakePoint(:lon, :lat))
        LIMIT 1;
    """)
    air_quality = db.execute(air_quality_query, {"lat": lat, "lon": lon}).mappings().first()
    
    if not air_quality:
        return {"risk_level": "Unknown", "recommendation": "No recent air quality data found..."}

    alert = generate_alert(dict(user_profile), dict(air_quality))
    return alert

@app.post("/api/v1/ai_guide/chat")
def chat_with_ai_guide(request: ChatRequest, db: Session = Depends(get_db)):
    user_query = text("SELECT name, health_conditions, persona FROM users WHERE id = :user_id")
    user_profile = db.execute(user_query, {"user_id": request.userId}).mappings().first()

    aq_query = text("""
        WITH recent_data AS (
            SELECT * FROM air_quality_data
            WHERE time > (SELECT MAX(time) FROM air_quality_data) - INTERVAL '12 hours'
            AND COALESCE(pm25, pm10, o3, no2, so2, co) IS NOT NULL
        )
        SELECT COALESCE(pm25, pm10, o3, no2, so2, co) as aqi
        FROM recent_data
        ORDER BY ST_Distance(ST_MakePoint(longitude, latitude), ST_MakePoint(:lon, :lat))
        LIMIT 1;
    """)
    air_quality = db.execute(aq_query, {"lat": request.lat, "lon": request.lon}).mappings().first()

    if not user_profile or not air_quality:
        return {"error": "Could not retrieve context for the AI."}

    ai_response = get_gemini_response(dict(user_profile), dict(air_quality), request.question)
    return {"response": ai_response}

@app.get("/api/v1/point/details")
def get_point_details(lat: float, lon: float):
    return mockLocationForecast

@app.get("/api/v1/location/name")
def get_location_name(lat: float, lon: float):
    if not MAPTILER_API_KEY:
        return {"name": "Location lookup unavailable"}
    
    url = f"https://api.maptiler.com/geocoding/{lon},{lat}.json?key={MAPTILER_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        place_name = data['features'][0]['place_name'] if data.get('features') else "Unknown Location"
        return {"name": place_name}
    except Exception:
        return {"name": "Location lookup failed"}

@app.post("/api/v1/users/{user_id}/generate_podcast")
def generate_podcast_for_user(user_id: int):
    print(f"Podcast generation requested for user {user_id}. Feature not yet implemented.")
    return {
        "status": "in_progress", 
        "message": "Your personalized audio briefing is being generated."
    }

@app.post("/api/v1/hooks/google/location")
def receive_google_location_data(data: dict):
    print("Received Google Location data:", data)
    return {"status": "received"}

@app.get("/api/v1/stations/live")
def get_live_station_data():
    """
    Fetches live data for all stations in a region from the WAQI API.
    """
    if not WAQI_API_KEY:
        return {"error": "WAQI API key not configured."}
    
    bounds = "8.0,68.0,37.0,97.0" # Bounding box for India
    url = f"https://api.waqi.info/map/bounds/?latlng={bounds}&token={WAQI_API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') != 'ok':
            return {"error": "Failed to fetch data from WAQI API."}
        
        valid_stations = []
        for station in data.get('data', []):
            try:
                aqi_value = int(station.get('aqi'))
                if station.get('lat') is not None and station.get('lon') is not None:
                    valid_stations.append({
                        "uid": station.get('uid'),
                        "lat": station.get('lat'),
                        "lon": station.get('lon'),
                        "aqi": aqi_value,
                        "name": station.get('station', {}).get('name')
                    })
            except (ValueError, TypeError):
                continue
        
        return valid_stations
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

@app.get("/api/v1/stations/details/{station_id}")
def get_station_details(station_id: int):
    """
    Fetches detailed, real-time data for a single station from the WAQI API.
    """
    if not WAQI_API_KEY:
        return {"error": "WAQI API key not configured."}
    
    url = f"https://api.waqi.info/feed/@{station_id}/?token={WAQI_API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') != 'ok':
            return {"error": "Failed to fetch station details from WAQI API."}
        
        station_data = data.get('data', {})
        
        cleaned_data = {
            "placeName": station_data.get('city', {}).get('name'),
            "currentAQI": station_data.get('aqi'),
            "dominantPollutant": station_data.get('dominentpol'),
            "pollutantDetails": station_data.get('iaqi', {}),
            "forecast": station_data.get('forecast', {}).get('daily', {})
        }
        return cleaned_data
        
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


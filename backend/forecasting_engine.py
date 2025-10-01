from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional

def generate_forecast(
    db: Session, 
    lat: float, 
    lon: float, 
    hours: int = 48,
    simulation: Optional[dict] = None
) -> list:
    """
    Generates an AQI forecast. If a simulation is provided, it adjusts the baseline AQI.
    """
    
    # 1. Get the most recent, real AQI and all individual pollutant values
    latest_aqi_query = text("""
        SELECT aqi, pm25, pm10, o3, no2, so2, co
        FROM air_quality_data
        WHERE COALESCE(aqi, pm25, pm10, o3, no2, so2, co) IS NOT NULL
        ORDER BY time DESC, ST_Distance(ST_MakePoint(longitude, latitude), ST_MakePoint(:lon, :lat))
        LIMIT 1;
    """)
    latest_aqi_result = db.execute(latest_aqi_query, {"lat": lat, "lon": lon}).mappings().first()
    
    if not latest_aqi_result:
        return []

    # --- SIMULATION LOGIC ---
    # 2. Adjust the baseline data if a simulation is active
    base_pollutants = dict(latest_aqi_result)
    if simulation and simulation.get('pollutant') in base_pollutants:
        pollutant_to_reduce = simulation['pollutant']
        reduction_factor = 1 - (simulation['reduction'] / 100.0)
        
        # Apply the reduction to the specific pollutant
        if base_pollutants[pollutant_to_reduce] is not None:
            base_pollutants[pollutant_to_reduce] *= reduction_factor
            
            # Recalculate the overall 'aqi' as the new highest value after the reduction
            pollutant_values = [v for k, v in base_pollutants.items() if v is not None and k != 'aqi']
            base_pollutants['aqi'] = max(pollutant_values) if pollutant_values else 0
            
    base_aqi = float(base_pollutants.get('aqi', 0))

    # 3. Get the weather forecast from the database
    weather_forecast_query = text("""
        SELECT temperature_2m, precipitation, wind_speed_10m
        FROM weather_forecasts
        WHERE time > NOW()
        ORDER BY time
        LIMIT :hours;
    """)
    weather_forecast = db.execute(weather_forecast_query, {"hours": hours}).mappings().all()

    # If no weather data, return a simple "persistence" forecast
    if not weather_forecast:
        return [{"hour": f"+{i+1}h", "predicted_aqi": round(base_aqi)} for i in range(hours)]

    # 4. Apply simple rules to generate the AQI forecast based on weather
    forecast = []
    current_aqi = base_aqi
    
    for i, hourly_weather in enumerate(weather_forecast):
        # Rule: Rain and high wind clean the air
        if hourly_weather['precipitation'] > 0.5 or hourly_weather['wind_speed_10m'] > 20:
            current_aqi *= 0.95 # 5% improvement
        
        # Rule: High temperatures can worsen some pollutants
        if hourly_weather['temperature_2m'] > 30:
            current_aqi *= 1.02 # 2% worsening
            
        current_aqi = max(current_aqi, 10)
        
        forecast.append({"hour": f"+{i+1}h", "predicted_aqi": round(current_aqi)})

    return forecast


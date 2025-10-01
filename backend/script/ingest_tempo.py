import xarray as xr
import os
import numpy as np
from sqlalchemy import text
from database import SessionLocal
from tqdm import tqdm

# --- CONFIGURATION ---
# Update this to the exact name of the file you have downloaded
FILE_NAME = "TEMPO_NO2_L2_V03_20250916T214329Z_S012G07.nc"
FILE_PATH = os.path.join("data", FILE_NAME)
DOWNSAMPLE_FACTOR = 10 # Increase this number for faster testing, decrease for higher resolution

def get_variable_safely(dataset, var_name, shape_reference):
    """
    A helper function to safely get a variable from the dataset.
    If the variable doesn't exist, it returns an array of NaNs.
    """
    if var_name in dataset:
        return dataset[var_name].values
    else:
        print(f"Warning: Variable '{var_name}' not found. Using NaN as a placeholder.")
        return np.full_like(shape_reference, np.nan)

def process_tempo_file():
    """
    Opens a TEMPO NetCDF file, extracts main and supporting data,
    and inserts it into the database using a fast, bulk method.
    """
    if not os.path.exists(FILE_PATH):
        print(f"Error: Data file not found at {FILE_PATH}")
        return
        
    print(f"Opening TEMPO data file: {FILE_PATH}")
    db = SessionLocal()
    
    try:
        ds_geo = xr.open_dataset(FILE_PATH, group='geolocation')
        ds_prod = xr.open_dataset(FILE_PATH, group='product')
        ds_support = xr.open_dataset(FILE_PATH, group='support_data')

        # --- Extract all necessary data arrays ---
        latitude = ds_geo['latitude'].values
        longitude = ds_geo['longitude'].values
        time_data = ds_geo['time'].values
        no2_data = ds_prod['vertical_column_troposphere'].values
        
        # --- ROBUST DATA EXTRACTION ---
        # Use our safe helper function to prevent crashes if a variable is missing
        quality_flag = get_variable_safely(ds_prod, 'main_data_quality_flag', latitude)
        terrain_height = get_variable_safely(ds_support, 'terrain_height', latitude)
        surface_pressure = get_variable_safely(ds_support, 'surface_pressure', latitude)
        wind_speed = get_variable_safely(ds_support, 'wind_speed', latitude)
        
        print("Preparing records for bulk insert...")
        records_to_insert = []

        for lat_idx in tqdm(range(0, latitude.shape[0], DOWNSAMPLE_FACTOR), desc="Processing TEMPO Scanlines"):
            time_for_scanline = np.datetime_as_string(time_data[lat_idx])
            for lon_idx in range(0, latitude.shape[1], DOWNSAMPLE_FACTOR):
                # Quality Check (skip if flag is not 0 or is NaN)
                q_flag = quality_flag[lat_idx, lon_idx]
                if np.isnan(q_flag) or int(q_flag) != 0:
                    continue

                no2_value = float(no2_data[lat_idx, lon_idx])
                if np.isnan(no2_value) or no2_value < -1e10:
                    continue

                records_to_insert.append({
                    "time": time_for_scanline,
                    "lat": float(latitude[lat_idx, lon_idx]),
                    "lon": float(longitude[lat_idx, lon_idx]),
                    "source": "NASA-TEMPO",
                    "no2": no2_value,
                    "terrain_height": float(terrain_height[lat_idx, lon_idx]),
                    "surface_pressure": float(surface_pressure[lat_idx, lon_idx]),
                    # Use None if wind_speed is NaN
                    "wind_speed": float(wind_speed[lat_idx, lon_idx]) if not np.isnan(wind_speed[lat_idx, lon_idx]) else None,
                    "quality_flag": int(q_flag)
                })

        if not records_to_insert:
            print("No valid, high-quality records found to insert.")
            return

        print(f"\nList prepared with {len(records_to_insert)} high-quality records. Executing bulk insert...")

        insert_query = text("""
            INSERT INTO air_quality_data (
                time, latitude, longitude, source, no2, terrain_height, 
                surface_pressure, wind_speed, quality_flag
            )
            VALUES (
                :time, :lat, :lon, :source, :no2, :terrain_height, 
                :surface_pressure, :wind_speed, :quality_flag
            )
            ON CONFLICT (time, latitude, longitude) DO UPDATE SET 
                no2 = EXCLUDED.no2,
                terrain_height = EXCLUDED.terrain_height,
                surface_pressure = EXCLUDED.surface_pressure,
                wind_speed = EXCLUDED.wind_speed,
                quality_flag = EXCLUDED.quality_flag;
        """)
        
        db.execute(insert_query, records_to_insert)
        db.commit()
        
        print(f"✅ Successfully processed and inserted/updated {len(records_to_insert)} records from the TEMPO file.")

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        if 'db' in locals() and db.is_active: db.close()
        if 'ds_geo' in locals(): ds_geo.close()
        if 'ds_prod' in locals(): ds_prod.close()
        if 'ds_support' in locals(): ds_support.close()

if __name__ == "__main__":
    process_tempo_file()


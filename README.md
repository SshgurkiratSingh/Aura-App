# AURA - Air Quality & Health Co-Pilot

An intelligent air quality and health co-pilot application that leverages NASA TEMPO (Tropospheric Emissions: Monitoring of Pollution) satellite data, combined with ground-based sensors and AI-powered personalization, to provide real-time air quality monitoring, forecasting, and personalized health recommendations.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Data Ingestion Scripts](#data-ingestion-scripts)
- [Environment Variables](#environment-variables)
- [Development](#development)

## 🌟 Overview

AURA is a comprehensive air quality monitoring and health advisory platform that:
- Visualizes real-time air quality data from NASA satellites and ground stations
- Provides personalized health alerts based on user profiles and health conditions
- Offers AI-powered guidance through an interactive chatbot
- Generates air quality forecasts
- Enables citizen science through community reporting
- Supports policy simulation for environmental planning

## ✨ Features

- **Real-time Air Quality Visualization**: Interactive map displaying PM2.5, PM10, NO2, O3, SO2, and CO levels
- **NASA TEMPO Data Integration**: Satellite-based air quality monitoring
- **Personalized Health Alerts**: Customized recommendations based on age, health conditions, and activity preferences
- **AI Guide**: Gemini-powered chatbot for air quality questions and advice
- **Forecasting Engine**: Predict future air quality trends
- **Citizen Science Module**: Community-driven environmental reporting
- **Policy Simulator**: Model the impact of environmental policies
- **Time-series Analysis**: Historical data visualization and analysis

## 🛠 Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with PostGIS extension
- **AI/ML**: Google Gemini API
- **Data Processing**: 
  - xarray (NetCDF data handling)
  - numpy (numerical computations)
  - SQLAlchemy (ORM)
- **APIs**: 
  - WAQI (World Air Quality Index)
  - MapTiler
  - OpenAQ
  - OpenMeteo

### Frontend
- **Framework**: Next.js 15 (React 19)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **Mapping**: 
  - deck.gl 9.1
  - MapLibre GL
  - react-map-gl
- **Charts**: Recharts
- **Icons**: Lucide React

### Data Sources
- NASA TEMPO satellite data (NO2, O3)
- NASA AIRS satellite data
- WAQI ground station network
- OpenAQ measurements
- OpenMeteo weather data
- Korea environmental data

## 📁 Project Structure

```
Aura-App/
├── backend/                          # FastAPI backend application
│   ├── script/                       # Data ingestion scripts
│   │   ├── check_netcdf.py          # NetCDF file structure inspector
│   │   ├── ingest_airs.py           # NASA AIRS data ingestion
│   │   ├── ingest_korea_data.py     # Korea environmental data
│   │   ├── ingest_openaq.py         # OpenAQ data ingestion
│   │   ├── ingest_openmeteo.py      # Weather data ingestion
│   │   ├── ingest_tempo.py          # NASA TEMPO data ingestion
│   │   └── ingest_waqi.py           # WAQI ground station data
│   ├── lib/
│   │   └── mockData.py              # Mock data for testing
│   ├── ai_guide.py                  # Gemini AI chatbot integration
│   ├── check_file_structure.py      # NetCDF file inspector
│   ├── create_tables.py             # Database table creation
│   ├── create_user_table.py         # User table setup
│   ├── database.py                  # Database configuration
│   ├── forecasting_engine.py        # Air quality forecasting
│   ├── intelligent_ingestor.py      # Smart data ingestion coordinator
│   ├── main.py                      # FastAPI application entry point
│   ├── personalization_engine.py    # Personalized alert generation
│   ├── reset_and_create_schema.py   # Database schema management
│   ├── update_schema.py             # Schema migration utilities
│   └── verify_tables.py             # Database verification
│
├── frontend/                         # Next.js frontend application
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx           # Root layout component
│   │   │   └── page.tsx             # Main page component
│   │   ├── components/
│   │   │   ├── AuraGuideButton.tsx  # AI chatbot button
│   │   │   ├── AuraGuideChat.tsx    # AI chatbot interface
│   │   │   ├── CitizenScienceModal.tsx  # Community reporting
│   │   │   ├── DataPanel.tsx        # Data visualization panel
│   │   │   ├── Forecast_modal.tsx   # Forecast display modal
│   │   │   ├── Header.tsx           # Application header
│   │   │   ├── LeftSidebar.tsx      # Layer selection sidebar
│   │   │   ├── MapContainer.tsx     # Main map component
│   │   │   ├── PolicySimulatorModal.tsx  # Policy simulation
│   │   │   ├── ProfileModal.tsx     # User profile management
│   │   │   ├── RegistrationModal.tsx # User registration
│   │   │   └── TimeScrubber.tsx     # Time navigation control
│   │   └── lib/
│   │       └── mockData.ts          # Frontend mock data
│   ├── public/                      # Static assets
│   ├── eslint.config.mjs           # ESLint configuration
│   ├── next.config.ts              # Next.js configuration
│   ├── package.json                # Frontend dependencies
│   ├── postcss.config.mjs          # PostCSS configuration
│   └── tsconfig.json               # TypeScript configuration
│
└── README.md                        # This file
```

## ⚙️ Prerequisites

### Required Software
- **Node.js**: v20.x or higher
- **npm**: v10.x or higher (comes with Node.js)
- **Python**: 3.9 or higher
- **PostgreSQL**: 14.x or higher with PostGIS extension
- **pip**: Python package installer

### API Keys
You'll need to obtain API keys for:
- Google Gemini API (for AI chatbot)
- WAQI API (for ground station data)
- MapTiler API (for map tiles)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/SshgurkiratSingh/Aura-App.git
cd Aura-App
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend

# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv requests xarray netCDF4 numpy tqdm google-generativeai
```

#### Setup Database

1. Install PostgreSQL with PostGIS extension:
```bash
# On Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib postgis

# On macOS with Homebrew:
brew install postgresql postgis
```

2. Create the database:
```sql
sudo -u postgres psql
CREATE DATABASE aura_db;
\c aura_db
CREATE EXTENSION postgis;
CREATE USER aura_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE aura_db TO aura_user;
\q
```

3. Initialize database schema:
```bash
python create_tables.py
# or
python reset_and_create_schema.py
```

#### Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# Database Configuration
DB_USER=aura_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=aura_db

# API Keys
WAQI_API_KEY=your_waqi_api_key
MAPTILER_API_KEY=your_maptiler_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Frontend Setup

#### Install Node.js Dependencies

```bash
cd ../frontend
npm install
```

#### Configure Frontend Environment (Optional)

Create a `.env.local` file in the `frontend` directory if needed:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🏃 Running the Application

### Development Mode

#### Start Backend Server

```bash
cd backend
# Activate virtual environment if not already active
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Run the FastAPI server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The backend API will be available at `http://localhost:8000`
- API documentation (Swagger): `http://localhost:8000/docs`
- Alternative API docs (ReDoc): `http://localhost:8000/redoc`

#### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

#### Run Both Concurrently (from frontend directory)

```bash
cd frontend
npm run dev:backend  # Starts backend
npm run dev          # Starts frontend
```

### Production Mode

#### Backend
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm run build
npm start
```

## 📡 API Documentation

### Base URL
`http://localhost:8000/api/v1`

### Core Endpoints

#### User Management
- `POST /users/register` - Register new user with health profile
- `GET /users/{user_id}/personalized_alert` - Get personalized health alert

#### Air Quality Data
- `GET /` - Health check endpoint
- `GET /pollutants/available` - List available pollutants
- `GET /grid/current` - Get current air quality grid data
  - Query params: `pollutant`, `time_offset`
- `GET /point/details` - Get air quality details for specific coordinates
  - Query params: `lat`, `lon`
- `GET /stations/live` - Get live data from all ground stations
- `GET /stations/details/{station_id}` - Get detailed station data

#### Forecasting
- `GET /forecast/point` - Get forecast for specific location
  - Query params: `lat`, `lon`
- `GET /forecast/simulate` - Simulate policy impact on air quality
  - Query params: `lat`, `lon`, `pollutant`, `reduction`

#### AI Guide
- `POST /ai_guide/chat` - Chat with AI assistant
  - Body: `{ userId, question, lat, lon }`

#### Citizen Science
- `POST /reports/submit` - Submit citizen science report
  - Form data: `lat`, `lon`, `description`, `user_id`, optional `image`
- `GET /reports/verified` - Get verified community reports

#### Utilities
- `GET /location/name` - Get location name from coordinates
  - Query params: `lat`, `lon`
- `POST /users/{user_id}/generate_podcast` - Generate audio briefing (placeholder)
- `POST /hooks/google/location` - Receive location updates from Google

## 📊 Data Ingestion Scripts

Located in `backend/script/`, these scripts populate the database with air quality data:

### NASA TEMPO Data
```bash
cd backend
python script/ingest_tempo.py
```
Processes NASA TEMPO satellite NetCDF files containing NO2 and O3 measurements.

### NASA AIRS Data
```bash
python script/ingest_airs.py
```
Ingests Atmospheric Infrared Sounder data.

### WAQI Ground Stations
```bash
python script/ingest_waqi.py
```
Fetches real-time data from World Air Quality Index ground stations.

### OpenAQ Network
```bash
python script/ingest_openaq.py
```
Pulls data from the OpenAQ open-source air quality platform.

### Weather Data
```bash
python script/ingest_openmeteo.py
```
Retrieves meteorological data from OpenMeteo API.

### Korea Environmental Data
```bash
python script/ingest_korea_data.py
```
Imports air quality measurements from Korean monitoring stations.

### NetCDF File Inspector
```bash
python script/check_netcdf.py
```
Utility to inspect the structure of NetCDF data files.

**Note**: Update the `FILE_NAME` and `FILE_PATH` variables in each script to match your downloaded data files.

## 🔐 Environment Variables

### Backend (.env)

| Variable | Description | Required |
|----------|-------------|----------|
| `DB_USER` | PostgreSQL username | Yes |
| `DB_PASSWORD` | PostgreSQL password | Yes |
| `DB_HOST` | Database host (usually localhost) | Yes |
| `DB_PORT` | Database port (usually 5432) | Yes |
| `DB_NAME` | Database name | Yes |
| `WAQI_API_KEY` | World Air Quality Index API key | Yes |
| `MAPTILER_API_KEY` | MapTiler API key for map tiles | Yes |
| `GEMINI_API_KEY` | Google Gemini API key for AI chat | Yes |

### Frontend (.env.local)

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | No (defaults to localhost:8000) |

## 🔧 Development

### Code Structure

- **Backend**: RESTful API built with FastAPI, following a modular architecture
- **Frontend**: Component-based React application using Next.js App Router
- **Database**: PostgreSQL with PostGIS for geospatial queries

### Key Features Implementation

1. **Real-time Visualization**: Uses deck.gl HeatmapLayer and ScatterplotLayer for rendering air quality data
2. **Personalization**: SQLAlchemy queries match user health profiles with air quality thresholds
3. **AI Integration**: Google Gemini API provides contextual air quality guidance
4. **Time Navigation**: TimeScrubber component allows historical data exploration
5. **Forecasting**: Statistical models predict future air quality based on historical patterns

### Running Tests

```bash
# Backend tests (if available)
cd backend
pytest

# Frontend tests (if available)
cd frontend
npm test
```

### Linting

```bash
# Frontend linting
cd frontend
npm run lint
```

## 📝 Notes

- The application requires NASA TEMPO NetCDF data files to be placed in the `backend/data/` directory
- Initial data ingestion may take significant time depending on data volume
- The DOWNSAMPLE_FACTOR in ingestion scripts can be adjusted for faster testing (higher value = lower resolution)
- Some features like podcast generation are placeholders for future implementation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is part of a NASA Space Apps Challenge submission.

## 🙏 Acknowledgments

- NASA for TEMPO and AIRS satellite data
- WAQI for ground station data
- OpenAQ for open air quality data
- MapTiler for map tiles
- Google for Gemini AI API

---

**Built with ❤️ for cleaner air and healthier communities**

# Copilot Instructions for Aura-App

## Project Overview

Aura-App is an intelligent air quality and health co-pilot leveraging NASA TEMPO data. The codebase is split into two main components:

- **backend/**: Python scripts for data ingestion, processing, and database management.
- **frontend/**: Next.js (TypeScript) web application for user interaction and visualization.

## Architecture & Data Flow

- **Data Ingestion**: Scripts in `backend/script/` handle importing data from various sources (e.g., AIRS, TEMPO, OpenAQ, WAQI, Korea data).
- **Database Management**: Core database logic is in `backend/database.py` and related table creation/verification scripts.
- **AI & Personalization**: `backend/ai_guide.py` and `backend/personalization_engine.py` provide intelligent features and user-specific recommendations.
- **Frontend Integration**: The frontend does not directly call backend scripts; integration is expected via API endpoints (not present in this repo, but implied by structure).

## Developer Workflows

- **Backend**:
  - Install dependencies: `pip install -r backend/requirements.txt`
  - Run scripts directly for ingestion or schema management (e.g., `python backend/create_tables.py`)
  - Data files for ingestion are in `backend/data/`
- **Frontend**:
  - Install dependencies: `npm install` (in `frontend/`)
  - Start dev server: `npm run dev` (Next.js, port 3000)
  - Edit UI in `frontend/src/components/` and pages in `frontend/src/app/`

## Conventions & Patterns

- **Backend**:
  - Each ingestion source has a dedicated script in `backend/script/`
  - Database schema is managed via explicit scripts (not migrations)
  - AI logic is modularized in separate files
- **Frontend**:
  - Uses Next.js app directory structure
  - Components are colocated in `frontend/src/components/`
  - Mock data for frontend is in `frontend/src/lib/mockData.ts`

## Integration Points

- Data files: `backend/data/` (HDF, NetCDF, etc.)
- No explicit API layer in repo; backend scripts are run manually or scheduled
- Frontend expects backend data to be available, but integration is not hardcoded

## External Dependencies

- **Backend**: Python, requirements in `backend/requirements.txt`
- **Frontend**: Next.js, TypeScript, npm packages in `frontend/package.json`

## Examples

- To ingest AIRS data: `python backend/script/ingest_airs.py backend/data/AIRS.2025.09.28.076.L2.RetStd_IR.v6.0.34.0.R25271044911.hdf`
- To start frontend: `cd frontend && npm run dev`

## Key Files & Directories

- `backend/ai_guide.py`, `backend/personalization_engine.py`: AI logic
- `backend/database.py`: DB logic
- `backend/script/`: Data ingestion scripts
- `frontend/src/components/`: UI components
- `frontend/src/app/`: Next.js pages

---

_If any section is unclear or missing, please provide feedback to improve these instructions._

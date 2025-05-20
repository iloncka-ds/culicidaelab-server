# Culicidae Lab API

Backend API for the Culicidae Lab mosquito tracking and analysis platform.

## Setup Instructions

1. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn lancedb pandas
   ```

2. **Initialize the database**:
   ```bash
   python -m backend.scripts.initialize_db
   ```
   This will:
   - Set up the LanceDB database
   - Populate species data
   - Populate disease data

3. **Run the API server**:
   ```bash
   uvicorn backend.main:app --reload
   ```

4. **Access the API documentation**:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Species Endpoints

- `GET /species` - Get a list of mosquito species
- `GET /species/{species_id}` - Get detailed information about a specific species

### Disease Endpoints

- `GET /diseases` - Get a list of vector-borne diseases
- `GET /diseases/{disease_id}` - Get detailed information about a specific disease

## Database Structure

The application uses LanceDB, a vector database that supports fast similarity searches:

1. **Species Table** - Contains information about mosquito species
2. **Diseases Table** - Contains information about vector-borne diseases

Each disease entry includes references to the associated vector species that can transmit the disease.
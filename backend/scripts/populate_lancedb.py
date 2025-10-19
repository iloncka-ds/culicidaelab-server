"""LanceDB database population script for Culicidae Lab.

This script provides functionality to populate a LanceDB database with sample data
for the Culicidae Lab application. It creates and populates various tables including
species, diseases, observations, regions, data sources, and map layers.

The script reads JSON and GeoJSON files from the sample data directory and
transforms them according to predefined schemas before inserting into the database.

Tables populated by this script:
    - species: Mosquito species information
    - diseases: Disease information and vectors
    - observations: Field observations with geolocation data
    - regions: Geographic regions and boundaries
    - data_sources: Sources of observation data
    - map_layers: Geographic layers for visualization

Example:
    To populate the database with sample data:

        python backend/scripts/populate_lancedb.py

    The script will automatically create the database directory if it doesn't exist
    and populate all tables with sample data from the data/sample_data directory.
"""

import json
import asyncio
import os
from pathlib import Path
import pyarrow as pa
from backend.database_utils.lancedb_manager import (
    LanceDBManager,
    SPECIES_SCHEMA,
    DISEASES_SCHEMA,
    OBSERVATIONS_SCHEMA,
    REGIONS_SCHEMA,
    DATA_SOURCES_SCHEMA,
    MAP_LAYERS_SCHEMA,
)
from backend.config import settings

BASE_DIR = Path(__file__).resolve().parent
JSON_FILES_DIR = (BASE_DIR / "../data/sample_data").resolve()
DATA_DIR = (BASE_DIR / "../data").resolve()


async def populate_regions_table(manager: LanceDBManager):
    """Populate the regions table with geographic region data.

    Reads region data from sample_regions.json and creates or overwrites
    the regions table in LanceDB using the predefined REGIONS_SCHEMA.

    Args:
        manager: The LanceDBManager instance to use for database operations.

    Returns:
        None

    Raises:
        FileNotFoundError: If the sample_regions.json file is not found.

    Example:
        >>> manager = LanceDBManager(uri="/path/to/database")
        >>> await manager.connect()
        >>> await populate_regions_table(manager)
    """
    file_path = os.path.join(JSON_FILES_DIR, "sample_regions.json")
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
    with open(file_path, encoding="utf-8") as f:
        regions_data = json.load(f)
    await manager.create_or_overwrite_table("regions", regions_data, REGIONS_SCHEMA)


async def populate_data_sources_table(manager: LanceDBManager):
    """Populate the data_sources table with information about data sources.

    Reads data source information from sample_data_sources.json and creates
    or overwrites the data_sources table in LanceDB using DATA_SOURCES_SCHEMA.
    Only populates the table if data is available in the source file.

    Args:
        manager: The LanceDBManager instance to use for database operations.

    Returns:
        None

    Example:
        >>> manager = LanceDBManager(uri="/path/to/database")
        >>> await manager.connect()
        >>> await populate_data_sources_table(manager)
    """
    file_path = os.path.join(JSON_FILES_DIR, "sample_data_sources.json")
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
    with open(file_path, encoding="utf-8") as f:
        data_sources = json.load(f)
    if data_sources:
        await manager.create_or_overwrite_table("data_sources", data_sources, DATA_SOURCES_SCHEMA)


async def populate_species_table(manager: LanceDBManager):
    """Populate the species table with mosquito species information.

    Reads species data from sample_species.json and creates or overwrites
    the species table in LanceDB using SPECIES_SCHEMA. Performs field validation
    to ensure all required schema fields are present, adding empty lists for
    missing list-type fields.

    Args:
        manager: The LanceDBManager instance to use for database operations.

    Returns:
        None

    Raises:
        FileNotFoundError: If the sample_species.json file is not found.

    Example:
        >>> manager = LanceDBManager(uri="/path/to/database")
        >>> await manager.connect()
        >>> await populate_species_table(manager)
    """
    file_path = os.path.join(JSON_FILES_DIR, "sample_species.json")
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
    with open(file_path, encoding="utf-8") as f:
        species_data = json.load(f)

    for s in species_data:
        for field_name in SPECIES_SCHEMA.names:
            if field_name not in s:
                field_obj = SPECIES_SCHEMA.field(field_name)
                if pa.types.is_list(field_obj.type):
                    s[field_name] = []

    await manager.create_or_overwrite_table("species", species_data, SPECIES_SCHEMA)


async def populate_map_layers_table(manager: LanceDBManager):
    """Populate the map_layers table with geographic layer data.

    Reads observation data from sample_observations.geojson and creates
    or overwrites the map_layers table in LanceDB using MAP_LAYERS_SCHEMA.
    Extracts species information from features and creates layer metadata.

    The function processes GeoJSON feature collections and identifies
    contained species for each layer type.

    Args:
        manager: The LanceDBManager instance to use for database operations.

    Returns:
        None

    Note:
        This table is kept for compatibility but is no longer the primary
        source for observations data.

    Example:
        >>> manager = LanceDBManager(uri="/path/to/database")
        >>> await manager.connect()
        >>> await populate_map_layers_table(manager)
    """
    layer_files_info = {
        "observations": "sample_observations.geojson",
    }

    all_map_layer_data = []
    for layer_type, filename in layer_files_info.items():
        file_path = os.path.join(JSON_FILES_DIR, filename)
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found. Skipping {layer_type} layer.")
            continue
        with open(file_path, encoding="utf-8") as f:
            geojson_collection = json.load(f)

        contained_species_set = set()
        if geojson_collection and "features" in geojson_collection:
            for feature in geojson_collection["features"]:
                species = feature.get("properties", {}).get("species")
                if species:
                    contained_species_set.add(species)

        all_map_layer_data.append(
            {
                "layer_type": layer_type,
                "layer_name": f"Default {layer_type.title()} Layer",
                "geojson_data": json.dumps(geojson_collection),
                "contained_species": sorted(list(contained_species_set)),
            },
        )

    if all_map_layer_data:
        # This table is no longer the primary source for observations but is kept for compatibility.
        await manager.create_or_overwrite_table("map_layers", all_map_layer_data, MAP_LAYERS_SCHEMA)


async def populate_observations_table(manager: LanceDBManager):
    """Populate the observations table with field observation data.

    Reads observation data from sample_observations.geojson and creates
    or overwrites the observations table in LanceDB using OBSERVATIONS_SCHEMA.
    Processes GeoJSON features and transforms them into observation records
    with proper field mapping and type handling.

    The function extracts properties from GeoJSON features and creates
    structured observation records suitable for database storage.

    Args:
        manager: The LanceDBManager instance to use for database operations.

    Returns:
        None

    Raises:
        FileNotFoundError: If the sample_observations.geojson file is not found.

    Example:
        >>> manager = LanceDBManager(uri="/path/to/database")
        >>> await manager.connect()
        >>> await populate_observations_table(manager)
        Observations table populated successfully.
    """
    file_path = os.path.join(JSON_FILES_DIR, "sample_observations.geojson")
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
    with open(file_path, encoding="utf-8") as f:
        geojson_data = json.load(f)

    observations_records = []
    if "features" in geojson_data:
        for feature in geojson_data.get("features", []):
            props = feature.get("properties", {})
            geom = feature.get("geometry", {})
            record = {
                "type": feature.get("type"),
                "id": props.get("id"),
                "species_scientific_name": props.get("species_scientific_name"),
                "observed_at": props.get("observed_at"),
                "count": props.get("count"),
                "observer_id": props.get("observer_id"),
                "data_source": json.dumps(props.get("data_source")),
                "location_accuracy_m": props.get("location_accuracy_m"),
                "notes": props.get("notes"),
                "geometry_type": geom.get("type"),
                # Ensure coordinates is a non-empty list of floats to avoid NullType issues
                "coordinates": geom.get("coordinates"),
                "image_filename": props.get("image_filename"),
                "model_id": props.get("model_id"),
                "confidence": props.get("confidence"),
                "metadata": json.dumps(props.get("metadata", {})),
            }

            observations_records.append(record)

    if observations_records:
        await manager.create_or_overwrite_table("observations", observations_records, OBSERVATIONS_SCHEMA)
        print("Observations table populated successfully.")


async def populate_diseases_table(manager: LanceDBManager):
    file_path = JSON_FILES_DIR / "sample_diseases.json"
    if not file_path.exists():
        print(f"Error: {file_path} not found.")
        return
    with open(file_path, encoding="utf-8") as f:
        diseases_data = json.load(f)

    for d in diseases_data:
        for field in DISEASES_SCHEMA.names:
            if field not in d:
                if DISEASES_SCHEMA.field(field).type == pa.list_(pa.string()):
                    d[field] = []
                elif DISEASES_SCHEMA.field(field).type == pa.string():
                    d[field] = None

    await manager.create_or_overwrite_table("diseases", diseases_data, DISEASES_SCHEMA)
    print("Diseases table populated.")


async def main():
    if not os.path.exists(settings.DATABASE_PATH):
        os.makedirs(settings.DATABASE_PATH, exist_ok=True)

    manager = LanceDBManager(uri=settings.DATABASE_PATH)
    await manager.connect()

    print("Populating LanceDB...")
    await populate_species_table(manager)
    await populate_regions_table(manager)
    await populate_data_sources_table(manager)
    await populate_map_layers_table(manager)
    await populate_diseases_table(manager)
    await populate_observations_table(manager)

    print("LanceDB population complete.")


if __name__ == "__main__":
    asyncio.run(main())

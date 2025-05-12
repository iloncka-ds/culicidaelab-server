import json
import asyncio
import os
from lancedb_manager import LanceDBManager, SPECIES_SCHEMA, FILTER_OPTIONS_SCHEMA, MAP_LAYERS_SCHEMA

# Adjust paths if your JSON files are elsewhere relative to this script
DATA_DIR = "../../data"  # Assuming JSON files are in culicidaelab_server/data/
# If running from culicidaelab_server/backend/database:
# DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
# For script to be run from culicidaelab_server/ (where sample files are generated)
# This assumes `generate_sample_data.py` was run from the project root.
JSON_FILES_DIR = "."


async def populate_species_table(manager: LanceDBManager):
    file_path = os.path.join(JSON_FILES_DIR, "sample_species.json")
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
    with open(file_path, "r") as f:
        species_data = json.load(f)

    # Ensure data matches schema (e.g., lists for list fields)
    for s in species_data:
        s["key_characteristics"] = s.get("key_characteristics", [])
        s["geographic_regions"] = s.get("geographic_regions", [])
        s["related_diseases"] = s.get("related_diseases", [])
        s["habitat_preferences"] = s.get("habitat_preferences", [])

    await manager.create_or_overwrite_table("species", species_data, SPECIES_SCHEMA)


async def populate_filter_options_tables(manager: LanceDBManager):
    file_path = os.path.join(JSON_FILES_DIR, "sample_filter_options.json")
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
    with open(file_path, "r") as f:
        options_data = json.load(f)

    regions = [{"name": r} for r in options_data.get("regions", [])]
    data_sources = [{"name": ds} for ds in options_data.get("data_sources", [])]
    # Species for filter options will be read directly from the 'species' table by the API

    if regions:
        await manager.create_or_overwrite_table("regions", regions, FILTER_OPTIONS_SCHEMA)
    if data_sources:
        await manager.create_or_overwrite_table("data_sources", data_sources, FILTER_OPTIONS_SCHEMA)


async def populate_map_layers_table(manager: LanceDBManager):
    layer_files_info = {
        "distribution": "sample_distribution.geojson",
        "observations": "sample_observations.geojson",
        "modeled": "sample_modeled.geojson",
        "breeding_sites": "sample_breeding_sites.geojson",
    }

    all_map_layer_data = []
    for layer_type, filename in layer_files_info.items():
        file_path = os.path.join(JSON_FILES_DIR, filename)
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found. Skipping {layer_type} layer.")
            continue
        with open(file_path, "r") as f:
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
                "layer_name": f"Default {layer_type.title()} Layer",  # Or generate a more specific name
                "geojson_data": json.dumps(geojson_collection),  # Store as string
                "contained_species": sorted(list(contained_species_set)),  # Store as list of strings
            }
        )

    if all_map_layer_data:
        await manager.create_or_overwrite_table("map_layers", all_map_layer_data, MAP_LAYERS_SCHEMA)


async def main():
    # Ensure the .lancedb directory exists or adjust LANCEDB_URI
    lancedb_dir = ".lancedb"  # Default, relative to where this script is run
    if not os.path.exists(lancedb_dir):
        os.makedirs(lancedb_dir, exist_ok=True)

    manager = LanceDBManager(uri=lancedb_dir)  # Use local directory for DB files
    await manager.connect()  # Explicit connect for setup script

    print("Populating LanceDB...")
    await populate_species_table(manager)
    await populate_filter_options_tables(manager)
    await populate_map_layers_table(manager)
    print("LanceDB population complete.")
    # No explicit close needed for current LanceDB versions for local FS


if __name__ == "__main__":
    # First, ensure generate_sample_data.py has been run in the project root
    # to create the .json files.
    # This script should ideally be run from the `culicidaelab_server/backend/database` directory
    # or adjust JSON_FILES_DIR accordingly.
    # For simplicity, let's assume it's run from project root after generate_sample_data.py
    # For this example, let's assume you run this from the project root `culicidaelab-server/`
    # $ python backend/database/populate_lancedb.py
    asyncio.run(main())

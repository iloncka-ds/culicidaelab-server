import json
import asyncio
import os
import pyarrow as pa
from backend.database_utils.lancedb_manager import (
    LanceDBManager,
    SPECIES_SCHEMA,
    DISEASES_SCHEMA,
    REGIONS_SCHEMA,
    DATA_SOURCES_SCHEMA,

    MAP_LAYERS_SCHEMA,
)
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
JSON_FILES_DIR = (BASE_DIR / "../data/sample_data").resolve()
DATA_DIR = (BASE_DIR / "../data").resolve()

async def populate_regions_table(manager: LanceDBManager):
    file_path = os.path.join(JSON_FILES_DIR, "sample_regions.json")
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
    with open(file_path, "r") as f:
        regions_data = json.load(f)
    await manager.create_or_overwrite_table("regions", regions_data, REGIONS_SCHEMA)


async def populate_data_sources_table(manager: LanceDBManager):
    file_path = os.path.join(JSON_FILES_DIR, "sample_data_sources.json")
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
    with open(file_path, "r") as f:
        data_sources = json.load(f)
    if data_sources:
        await manager.create_or_overwrite_table("data_sources", data_sources, DATA_SOURCES_SCHEMA)

async def populate_species_table(manager: LanceDBManager):
    file_path = os.path.join(JSON_FILES_DIR, "sample_species.json")
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
    with open(file_path, "r") as f:
        species_data = json.load(f)

    # Ensure all list fields exist to match schema
    for s in species_data:
        for field_name in SPECIES_SCHEMA.names:
            if field_name not in s:
                field_obj = SPECIES_SCHEMA.field(field_name)
                if pa.types.is_list(field_obj.type):
                    s[field_name] = []

    await manager.create_or_overwrite_table("species", species_data, SPECIES_SCHEMA)


async def populate_map_layers_table(manager: LanceDBManager):
    layer_files_info = {
        # "distribution": "sample_distribution.geojson",
        "observations": "sample_observations.geojson",
        # "modeled": "sample_modeled.geojson",
        # "breeding_sites": "sample_breeding_sites.geojson",
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
                "layer_name": f"Default {layer_type.title()} Layer",
                "geojson_data": json.dumps(geojson_collection),
                "contained_species": sorted(list(contained_species_set)),
            }
        )

    if all_map_layer_data:
        await manager.create_or_overwrite_table("map_layers", all_map_layer_data, MAP_LAYERS_SCHEMA)


async def populate_diseases_table(manager: LanceDBManager):
    file_path = JSON_FILES_DIR / "sample_diseases.json"
    if not file_path.exists():
        print(f"Error: {file_path} not found.")
        return
    with open(file_path, "r") as f:
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
    lancedb_dir = DATA_DIR / ".lancedb"
    if not os.path.exists(lancedb_dir):
        os.makedirs(lancedb_dir, exist_ok=True)

    manager = LanceDBManager(uri=str(lancedb_dir))
    await manager.connect()

    print("Populating LanceDB...")
    await populate_species_table(manager)
    await populate_regions_table(manager)
    await populate_data_sources_table(manager)
    await populate_map_layers_table(manager)
    await populate_diseases_table(manager)

    print("LanceDB population complete.")


if __name__ == "__main__":
    asyncio.run(main())

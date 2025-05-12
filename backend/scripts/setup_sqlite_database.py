import sqlite3
import json
import os

DB_NAME = "culicidae_lab.db"


def create_tables(conn):
    cursor = conn.cursor()

    # Species Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS species (
        id TEXT PRIMARY KEY,
        scientific_name TEXT UNIQUE NOT NULL,
        common_name TEXT,
        vector_status TEXT,
        image_url TEXT,
        description TEXT,
        key_characteristics TEXT, -- JSON list
        geographic_regions TEXT,  -- JSON list
        related_diseases TEXT,    -- JSON list
        habitat_preferences TEXT  -- JSON list
    )
    """)

    # Filter Options Tables (simple lists for now)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS regions (
        name TEXT PRIMARY KEY
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS data_sources (
        name TEXT PRIMARY KEY
    )
    """)
    # Species list for filters will be derived from the species table itself

    # Map Layers Table
    # layer_type: 'distribution', 'observations', 'modeled', 'breeding_sites'
    # species_filter: comma-separated list of species this layer applies to, or NULL if general
    # geojson_data: The full GeoJSON FeatureCollection as TEXT
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS map_layers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        layer_type TEXT NOT NULL,
        layer_name TEXT NOT NULL UNIQUE, -- e.g., "Aedes albopictus Distribution Q1 2023"
        species_filter TEXT,             -- Can be NULL if layer is not species-specific (e.g. all breeding sites)
                                         -- or specific species ID(s) comma-separated
        geojson_data TEXT NOT NULL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    # Index for faster layer lookup by type and species
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_map_layers_type_species ON map_layers (layer_type, species_filter)")

    conn.commit()
    print("Tables created successfully.")


def populate_species(conn, species_data_file="sample_species.json"):
    with open(species_data_file, "r") as f:
        species_list = json.load(f)

    cursor = conn.cursor()
    for s in species_list:
        try:
            cursor.execute(
                """
            INSERT INTO species (id, scientific_name, common_name, vector_status, image_url,
                                 description, key_characteristics, geographic_regions, related_diseases, habitat_preferences)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    s["id"],
                    s["scientific_name"],
                    s.get("common_name"),
                    s.get("vector_status"),
                    s.get("image_url"),
                    s.get("description"),
                    json.dumps(s.get("key_characteristics", [])),
                    json.dumps(s.get("geographic_regions", [])),
                    json.dumps(s.get("related_diseases", [])),
                    json.dumps(s.get("habitat_preferences", [])),
                ),
            )
        except sqlite3.IntegrityError as e:
            print(f"Skipping duplicate species '{s['scientific_name']}': {e}")
    conn.commit()
    print(f"Populated {len(species_list)} species.")


def populate_filter_options(conn, filter_options_file="sample_filter_options.json"):
    with open(filter_options_file, "r") as f:
        options = json.load(f)

    cursor = conn.cursor()
    # Regions
    for region_name in options.get("regions", []):
        try:
            cursor.execute("INSERT INTO regions (name) VALUES (?)", (region_name,))
        except sqlite3.IntegrityError:
            pass  # Skip duplicates
    # Data Sources
    for ds_name in options.get("data_sources", []):
        try:
            cursor.execute("INSERT INTO data_sources (name) VALUES (?)", (ds_name,))
        except sqlite3.IntegrityError:
            pass  # Skip duplicates
    conn.commit()
    print("Populated filter options (regions, data_sources).")


def populate_map_layers(conn):
    cursor = conn.cursor()
    layer_files = {
        "distribution": "sample_distribution.geojson",
        "observations": "sample_observations.geojson",
        "modeled": "sample_modeled.geojson",
        "breeding_sites": "sample_breeding_sites.geojson",
    }

    for layer_type, filename in layer_files.items():
        if not os.path.exists(filename):
            print(f"Warning: {filename} not found. Skipping {layer_type} layer.")
            continue
        with open(filename, "r") as f:
            geojson_collection = json.load(f)

        # For simplicity, we store the entire FeatureCollection as one entry per layer type.
        # A more granular approach might store individual features or group by species.
        # Here, if the GeoJSON contains multiple species, the species_filter needs thought.
        # Let's assume for now that each file is either general or implicitly for all species within it.
        # For our API, we'll likely filter the features within the GeoJSON based on species param.

        # Extract all unique species from the features in this layer file if properties.species exists
        all_species_in_layer = set()
        if geojson_collection and "features" in geojson_collection:
            for feature in geojson_collection["features"]:
                if "properties" in feature and "species" in feature["properties"] and feature["properties"]["species"]:
                    all_species_in_layer.add(feature["properties"]["species"])

        # Convert set to comma-separated string or None if empty
        species_filter_str = ",".join(sorted(list(all_species_in_layer))) if all_species_in_layer else None

        try:
            cursor.execute(
                """
            INSERT INTO map_layers (layer_type, layer_name, species_filter, geojson_data)
            VALUES (?, ?, ?, ?)
            """,
                (layer_type, f"Default {layer_type.title()} Layer", species_filter_str, json.dumps(geojson_collection)),
            )
            print(f"Inserted {layer_type} layer from {filename}.")
        except sqlite3.IntegrityError as e:
            print(f"Could not insert layer {layer_type}: {e}")

    conn.commit()
    print("Populated map layers.")


def main():
    # Remove old DB if it exists to start fresh
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Removed old database {DB_NAME}.")

    conn = sqlite3.connect(DB_NAME)
    try:
        create_tables(conn)
        populate_species(conn)
        populate_filter_options(conn)
        populate_map_layers(conn)
        print(f"Database '{DB_NAME}' created and populated successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

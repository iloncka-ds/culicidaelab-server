import lancedb
import pyarrow as pa
import json
import os
from shapely.geometry import shape, Point, Polygon, MultiPolygon  # For geometry handling
import time
import uuid  # Used only if sample data generation includes it

# --- Configuration ---
# Assumes script is run from backend/ directory
DB_PATH = "./backend/data/.lancedb"
SAMPLE_DATA_DIR = "./backend/data/sample_data"
SPECIES_FILE = os.path.join(SAMPLE_DATA_DIR, "sample_species.json")
DIST_FILE = os.path.join(SAMPLE_DATA_DIR, "sample_distribution.geojson")
OBS_FILE = os.path.join(SAMPLE_DATA_DIR, "sample_observations.geojson")
MOD_FILE = os.path.join(SAMPLE_DATA_DIR, "sample_modeled.geojson")
BREED_FILE = os.path.join(SAMPLE_DATA_DIR, "sample_breeding_sites.geojson")


# --- Helper Functions ---
def read_json(filepath):
    if not os.path.exists(filepath):
        print(f"Warning: File not found - {filepath}")
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading JSON file {filepath}: {e}")
        return None


def get_geometry_type(geom_dict):
    """Safely gets geometry type"""
    return geom_dict.get("type", "Unknown") if isinstance(geom_dict, dict) else "Invalid"


def geojson_features_to_lance(features, layer_type):
    """
    Converts a list of GeoJSON features to a list of dicts for LanceDB,
    storing full geometry and properties as JSON strings.
    Optionally extracts coordinates for simple filtering.
    """
    data = []
    # Define expected properties for different layers (can be adjusted)
    required_prop_fields = {
        "distribution": ["species"],
        "observations": ["species"],
        "modeled": ["species"],
        "breeding_sites": [],  # No single property is strictly required for filtering ALL breeding sites
    }.get(layer_type, [])

    optional_prop_fields = {  # Map properties key to lance column name
        "observation_date": "obs_date",
        "count": "count",
        "data_source": "data_source",
        "distribution_status": "dist_status",
        "probability": "probability",
        "site_type": "site_type",
        "larvae_present": "larvae_present",
    }

    print(f"  Processing {len(features)} features for layer type: {layer_type}")
    processed_count = 0
    skipped_count = 0

    for i, feature in enumerate(features):
        if feature.get("type") != "Feature" or not feature.get("geometry"):
            # print(f"  Skipping feature {i+1}: Invalid type or missing geometry.")
            skipped_count += 1
            continue

        props = feature.get("properties", {})
        geom_dict = feature["geometry"]
        geom_type = get_geometry_type(geom_dict)

        # Basic validation of geometry dictionary
        if geom_type == "Unknown" or "coordinates" not in geom_dict:
            # print(f"  Skipping feature {i+1}: Invalid geometry dictionary: {geom_dict}")
            skipped_count += 1
            continue

        # Check for required properties
        missing_required = False
        for prop_key in required_prop_fields:
            if props.get(prop_key) is None:
                # Allow None species specifically for breeding sites if needed by design
                if not (prop_key == "species" and layer_type == "breeding_sites"):
                    # print(f"  Skipping feature {i+1}: Missing required property '{prop_key}'. Props: {props}")
                    missing_required = True
                    break
        if missing_required:
            skipped_count += 1
            continue

        record = {
            "layer_type": layer_type,
            "geometry_type": geom_type,
            "geometry_json": json.dumps(geom_dict),  # Store original geometry as JSON string
            "properties_json": json.dumps(props),  # Store original properties as JSON string
            # Initialize optional fields to None
            "species": None,
            "lon": None,
            "lat": None,
            "minx": None,
            "miny": None,
            "maxx": None,
            "maxy": None,
            "obs_date": None,
            "count": None,
            "data_source": None,
            "dist_status": None,
            "probability": None,
            "site_type": None,
            "larvae_present": None,
        }

        # Populate species field explicitly
        record["species"] = props.get("species")

        # Extract coordinates for potential simple filtering (optional)
        try:
            # Use shapely to parse geometry and extract derived info
            geom_shapely = shape(geom_dict)
            if isinstance(geom_shapely, Point):
                record["lon"] = geom_shapely.x
                record["lat"] = geom_shapely.y
            elif isinstance(geom_shapely, (Polygon, MultiPolygon)):
                # Store bounds for bbox filtering
                bounds = geom_shapely.bounds
                if len(bounds) == 4:
                    record["minx"], record["miny"], record["maxx"], record["maxy"] = bounds
        except Exception as e:
            # print(f"  Warning: Could not parse geometry or extract coords for feature {i+1}. Error: {e}")
            pass  # Continue processing record even if coord extraction fails

        # Add optional properties from the defined mapping
        for prop_key, lance_key in optional_prop_fields.items():
            # Check type compatibility (e.g., larvae_present should be bool)
            raw_value = props.get(prop_key)
            if lance_key == "larvae_present" and raw_value is not None:
                record[lance_key] = bool(raw_value)  # Ensure boolean type
            elif lance_key == "count" and raw_value is not None:
                try:
                    record[lance_key] = int(raw_value)
                except (ValueError, TypeError):
                    record[lance_key] = None  # Set to None if conversion fails
            elif lance_key == "probability" and raw_value is not None:
                try:
                    record[lance_key] = float(raw_value)
                except (ValueError, TypeError):
                    record[lance_key] = None
            else:
                record[lance_key] = raw_value

        data.append(record)
        processed_count += 1

    print(f"  Finished processing for {layer_type}: {processed_count} added, {skipped_count} skipped.")
    return data


# --- Main Setup Logic ---
def setup_database():
    print(f"Connecting to LanceDB at: {DB_PATH}")
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = lancedb.connect(DB_PATH)

    # --- 1. Species Table ---
    print("\nProcessing 'species' data...")
    species_data = read_json(SPECIES_FILE)
    if species_data:
        print("Setting up 'species' table...")
        species_schema = pa.schema(
            [
                pa.field("id", pa.string(), nullable=False),
                pa.field("scientific_name", pa.string()),
                pa.field("common_name", pa.string()),
                pa.field("vector_status", pa.string()),
                pa.field("image_url", pa.string()),
                pa.field("description", pa.string()),
                pa.field("key_characteristics", pa.string()),  # JSON list stored as string
                pa.field("geographic_regions", pa.string()),  # JSON list stored as string
                pa.field("related_diseases", pa.string()),  # JSON list stored as string
                pa.field("habitat_preferences", pa.string()),  # JSON list stored as string
            ]
        )
        # Convert list fields to JSON strings for insertion
        processed_species_data = []
        for item in species_data:
            # Ensure basic fields exist
            if not item.get("id") or not item.get("scientific_name"):
                print(f"Warning: Skipping species record due to missing id or scientific_name: {item}")
                continue
            new_item = item.copy()  # Avoid modifying original dict
            for key in ["key_characteristics", "geographic_regions", "related_diseases", "habitat_preferences"]:
                new_item[key] = json.dumps(new_item.get(key, []))
            processed_species_data.append(new_item)

        if processed_species_data:
            try:
                db.drop_table("species", ignore_missing=True)
                print("  Existing 'species' table dropped (if any).")
                tbl = db.create_table("species", schema=species_schema, mode="overwrite")
                tbl.add(processed_species_data)
                print(f"  Added {len(processed_species_data)} records to 'species' table.")
                # Consider creating index on 'id' or 'scientific_name' if needed frequently
                # tbl.create_index("scientific_name")
            except Exception as e:
                print(f"Error setting up 'species' table: {e}")
        else:
            print("No valid species data processed.")
    else:
        print("Skipping 'species' table: No data found.")

    # --- 2. Geo Layers Table ---
    # REVISED SCHEMA to include geometry_json
    geo_schema = pa.schema(
        [
            pa.field("layer_type", pa.string(), nullable=False),
            pa.field("species", pa.string()),  # Nullable
            pa.field("geometry_type", pa.string()),
            pa.field("geometry_json", pa.string(), nullable=False),  # Store full geometry JSON
            # Optional extracted coords for simple filtering
            pa.field("lon", pa.float64()),
            pa.field("lat", pa.float64()),
            pa.field("minx", pa.float64()),
            pa.field("miny", pa.float64()),
            pa.field("maxx", pa.float64()),
            pa.field("maxy", pa.float64()),
            # Extracted properties for filtering/display
            pa.field("obs_date", pa.string()),  # Keep as string for filtering simplicity
            pa.field("count", pa.int64()),
            pa.field("data_source", pa.string()),
            pa.field("dist_status", pa.string()),
            pa.field("probability", pa.float64()),
            pa.field("site_type", pa.string()),
            pa.field("larvae_present", pa.bool_()),
            # Full properties backup
            pa.field("properties_json", pa.string(), nullable=False),
        ]
    )

    all_geo_data = []
    layer_files = {
        "distribution": DIST_FILE,
        "observations": OBS_FILE,
        "modeled": MOD_FILE,
        "breeding_sites": BREED_FILE,
    }
    print("\nProcessing GeoJSON files for 'geo_features' table...")
    for layer_type, filepath in layer_files.items():
        geojson_data = read_json(filepath)
        if (
            geojson_data
            and isinstance(geojson_data, dict)
            and "features" in geojson_data
            and isinstance(geojson_data["features"], list)
        ):
            features = geojson_data["features"]
            lance_records = geojson_features_to_lance(features, layer_type)
            all_geo_data.extend(lance_records)
        else:
            print(f" - No valid features found or invalid format in {filepath}")

    if all_geo_data:
        print(f"\nSetting up 'geo_features' table with {len(all_geo_data)} total records...")
        try:
            db.drop_table("geo_features", ignore_missing=True)
            print("  Existing 'geo_features' table dropped (if any).")
            # Create table first
            tbl_geo = db.create_table("geo_features", schema=geo_schema, mode="overwrite")
            # Add data in batches if very large
            batch_size = 10000
            num_batches = (len(all_geo_data) + batch_size - 1) // batch_size
            print(f"  Adding data in {num_batches} batches of size {batch_size}...")
            for i in range(0, len(all_geo_data), batch_size):
                batch = all_geo_data[i : i + batch_size]
                tbl_geo.add(batch)
                # print(f"  - Added batch {i//batch_size + 1}/{num_batches}")
            print(f"  Data added ({len(all_geo_data)} records).")

            print("  Creating indexes...")
            start_time = time.time()
            # Create indexes for common filter fields
            # Indexing nullable fields like 'species' might behave differently based on LanceDB version.
            try:
                # Indexing on string fields helps with exact matches ('=').
                tbl_geo.create_scalar_index("layer_type")
                tbl_geo.create_scalar_index("species")  # Index even if nullable
                tbl_geo.create_scalar_index("data_source")
                # Scalar quantization index might help with bbox ranges, but requires careful config.
                # For now, stick to basic indexes.
                print(f"  Indexes created successfully (took {time.time() - start_time:.2f}s).")
            except Exception as idx_e:
                print(f"Warning: Could not create all indexes. Error: {idx_e}")

            print("'geo_features' table created and populated.")
        except Exception as e:
            print(f"Error setting up 'geo_features' table: {e}")
            import traceback

            traceback.print_exc()
    else:
        print("No valid geo data found to populate 'geo_features' table.")

    print("\nDatabase setup complete.")


if __name__ == "__main__":
    # Ensure sample data exists before proceeding
    if not os.path.exists(SAMPLE_DATA_DIR):
        print(f"Error: Sample data directory not found at '{os.path.abspath(SAMPLE_DATA_DIR)}'")
        print(
            "Please run the generate_sample_data.py script first or place sample files in the 'data/sample_data/' directory relative to where this script is run."
        )
    else:
        # Check if essential files exist
        essential_files = [SPECIES_FILE, DIST_FILE, OBS_FILE, MOD_FILE, BREED_FILE]
        missing_files = [f for f in essential_files if not os.path.exists(f)]
        if missing_files:
            print("Error: The following essential sample data files are missing:")
            for f in missing_files:
                print(f" - {f}")
            print("Please ensure all sample files are generated and present in the 'data/sample_data/' directory.")
        else:
            print("All essential sample data files found. Proceeding with database setup.")
            setup_database()

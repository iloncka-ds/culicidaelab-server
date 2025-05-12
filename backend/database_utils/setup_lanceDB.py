import lancedb
import pyarrow as pa
import json
import os
from shapely.geometry import shape, Point, Polygon, MultiPolygon  # For geometry handling
import time

# --- Configuration ---
# Assumes script is run from backend/ directory
DB_PATH = "data/.lancedb"
SAMPLE_DATA_DIR = "data/sample_data"
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
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_geometry_type(geom_dict):
    """Safely gets geometry type"""
    return geom_dict.get("type", "Unknown") if isinstance(geom_dict, dict) else "Invalid"


def parse_geometry(geom_dict):
    """Parses GeoJSON geometry into Shapely object (basic support)"""
    if not isinstance(geom_dict, dict) or "type" not in geom_dict or "coordinates" not in geom_dict:
        return None
    try:
        # Shapely can directly load GeoJSON-like dicts
        return shape(geom_dict)
    except Exception as e:
        # print(f"Warning: Could not parse geometry: {geom_dict}. Error: {e}")
        return None  # Handle potential errors in geometry data


def geojson_features_to_lance(features, layer_type):
    """Converts a list of GeoJSON features to a list of dicts for LanceDB"""
    data = []
    required_prop_fields = ["species"]  # Fields we expect in properties for filtering later
    optional_prop_fields = {  # Map properties key to lance column name
        "observation_date": "obs_date",
        "count": "count",
        "data_source": "data_source",
        "distribution_status": "dist_status",
        "probability": "probability",
        "site_type": "site_type",
        "larvae_present": "larvae_present",
    }

    for feature in features:
        if feature.get("type") != "Feature" or not feature.get("geometry"):
            continue

        props = feature.get("properties", {})
        geom_dict = feature["geometry"]
        geom_type = get_geometry_type(geom_dict)
        geom_shapely = parse_geometry(geom_dict)

        if geom_shapely is None:  # Skip if geometry is invalid/unparseable
            continue

        record = {
            "layer_type": layer_type,
            # Store geometry directly if LanceDB supports it well enough for basic ops
            # For points, store x, y separately for easier bbox filtering without spatial index yet
            "geometry_type": geom_type,
            # "geometry_wkb": geom_shapely.wkb_hex if geom_shapely else None, # Store Well-Known Binary
        }

        # Extract coordinates for simple filtering
        if isinstance(geom_shapely, Point):
            record["lon"] = geom_shapely.x
            record["lat"] = geom_shapely.y
        elif isinstance(geom_shapely, (Polygon, MultiPolygon)):
            # Store centroid for rough filtering, or rely on bbox of full dataset later
            centroid = geom_shapely.centroid
            record["centroid_lon"] = centroid.x
            record["centroid_lat"] = centroid.y
            # Alternatively store bounds minx, miny, maxx, maxy
            bounds = geom_shapely.bounds
            record["minx"] = bounds[0]
            record["miny"] = bounds[1]
            record["maxx"] = bounds[2]
            record["maxy"] = bounds[3]

        # Add required properties
        missing_required = False
        for prop_key in required_prop_fields:
            if props.get(prop_key) is None:
                # Handle layers like breeding sites where species might be None
                if prop_key == "species" and layer_type in ["breeding_sites"]:
                    record[prop_key] = None
                else:
                    # print(f"Warning: Feature missing required property '{prop_key}'. Skipping. Props: {props}")
                    missing_required = True
                    break
            record[prop_key] = props.get(prop_key)
        if missing_required:
            continue

        # Add optional (but useful for API) properties
        for prop_key, lance_key in optional_prop_fields.items():
            record[lance_key] = props.get(prop_key)  # Will be None if not present

        # Store all properties as a JSON string for full retrieval
        record["properties_json"] = json.dumps(props)

        data.append(record)
    return data


# --- Main Setup Logic ---
def setup_database():
    print(f"Connecting to LanceDB at: {DB_PATH}")
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = lancedb.connect(DB_PATH)

    # --- 1. Species Table ---
    species_data = read_json(SPECIES_FILE)
    if species_data:
        print("Setting up 'species' table...")
        # Simple schema, store complex fields as JSON strings
        species_schema = pa.schema(
            [
                pa.field("id", pa.string()),
                pa.field("scientific_name", pa.string()),
                pa.field("common_name", pa.string()),
                pa.field("vector_status", pa.string()),
                pa.field("image_url", pa.string()),
                pa.field("description", pa.string()),
                pa.field("key_characteristics", pa.string()),  # JSON list
                pa.field("geographic_regions", pa.string()),  # JSON list
                pa.field("related_diseases", pa.string()),  # JSON list
                pa.field("habitat_preferences", pa.string()),  # JSON list
            ]
        )
        # Convert lists to JSON strings for insertion
        for item in species_data:
            for key in ["key_characteristics", "geographic_regions", "related_diseases", "habitat_preferences"]:
                item[key] = json.dumps(item.get(key, []))

        try:
            db.drop_table("species", ignore_missing=True)
            tbl = db.create_table("species", schema=species_schema, mode="overwrite")
            tbl.add(species_data)
            print(f"Added {len(species_data)} records to 'species' table.")
        except Exception as e:
            print(f"Error setting up 'species' table: {e}")

    # --- 2. Geo Layers Tables ---
    layer_files = {
        "distribution": DIST_FILE,
        "observations": OBS_FILE,
        "modeled": MOD_FILE,
        "breeding_sites": BREED_FILE,
    }

    geo_schema = pa.schema(
        [
            pa.field("layer_type", pa.string()),
            pa.field("species", pa.string()),  # Nullable for some layers
            pa.field("geometry_type", pa.string()),
            # Point coords
            pa.field("lon", pa.float64()),
            pa.field("lat", pa.float64()),
            # Polygon coords (centroid / bbox)
            pa.field("centroid_lon", pa.float64()),
            pa.field("centroid_lat", pa.float64()),
            pa.field("minx", pa.float64()),
            pa.field("miny", pa.float64()),
            pa.field("maxx", pa.float64()),
            pa.field("maxy", pa.float64()),
            # Extracted properties
            pa.field("obs_date", pa.string()),  # Keep as string for simplicity
            pa.field("count", pa.int64()),
            pa.field("data_source", pa.string()),
            pa.field("dist_status", pa.string()),
            pa.field("probability", pa.float64()),
            pa.field("site_type", pa.string()),
            pa.field("larvae_present", pa.bool_()),
            # Full properties backup
            pa.field("properties_json", pa.string()),
            # pa.field("geometry_wkb", pa.string()) # Optional WKB storage
        ]
    )

    all_geo_data = []
    print("\nProcessing GeoJSON files for 'geo_features' table...")
    for layer_type, filepath in layer_files.items():
        geojson_data = read_json(filepath)
        if geojson_data and "features" in geojson_data:
            features = geojson_data["features"]
            lance_records = geojson_features_to_lance(features, layer_type)
            all_geo_data.extend(lance_records)
            print(f" - Parsed {len(lance_records)} features from {layer_type} ({filepath})")
        else:
            print(f" - No valid features found in {filepath}")

    if all_geo_data:
        print(f"\nSetting up 'geo_features' table with {len(all_geo_data)} total records...")
        try:
            db.drop_table("geo_features", ignore_missing=True)
            # If creating index takes too long on large data, do it after adding
            # Create table first
            tbl_geo = db.create_table("geo_features", schema=geo_schema, mode="overwrite")
            # Add data in batches if very large
            batch_size = 10000
            for i in range(0, len(all_geo_data), batch_size):
                batch = all_geo_data[i : i + batch_size]
                tbl_geo.add(batch)
                print(f"  - Added batch {i//batch_size + 1}/{(len(all_geo_data) + batch_size - 1)//batch_size}")

            print("Data added. Creating indexes...")
            start_time = time.time()
            # Create indexes for common filter fields
            try:
                tbl_geo.create_index("layer_type")
                tbl_geo.create_index("species")
                print(f"Indexes created successfully (took {time.time() - start_time:.2f}s).")
            except Exception as idx_e:
                print(f"Warning: Could not create all indexes. Error: {idx_e}")

            print("'geo_features' table created and populated.")
        except Exception as e:
            print(f"Error setting up 'geo_features' table: {e}")
    else:
        print("No geo data found to populate 'geo_features' table.")

    print("\nDatabase setup complete.")


if __name__ == "__main__":
    # Ensure sample data exists
    if not os.path.exists(SAMPLE_DATA_DIR):
        print(f"Error: Sample data directory not found at {SAMPLE_DATA_DIR}")
        print("Please run the generate_sample_data.py script first or place sample files here.")
    else:
        setup_database()

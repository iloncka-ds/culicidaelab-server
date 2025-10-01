"""Sample data generation utilities for Culicidae lab server backend data directory.

This module provides functions and data structures for generating sample data files
including species information, regional data, disease information, and observation data.
The generated data is used for testing and demonstration purposes.

The module generates the following sample data files:
- sample_species.json: Species information and characteristics
- sample_regions.json: Geographic regions data
- sample_data_sources.json: Data source information
- sample_diseases.json: Disease information and vectors
- sample_filter_options.json: Filter options for frontend
- sample_observations.geojson: Sample observation data with geographic coordinates

Example:
    Running this module as a script generates all sample data files:
    ```python
    python generate_sample_data.py
    ```
"""

import json
import random
from datetime import datetime, timedelta
from typing import TypedDict
from uuid import uuid4

from backend.data.sample_data.species import species_list
from backend.data.sample_data.diseases import diseases_data_list


with open("sample_species.json", "w", encoding="utf-8") as f:
    json.dump(species_list, f, indent=2, ensure_ascii=False)
print("Generated sample_species.json")


class BoundingBox(TypedDict):
    """Bounding box coordinates for geographic regions.

    This TypedDict defines the structure for bounding box coordinates used to
    constrain random geographic point generation within specific regions.

    Attributes:
        min_lon (float): Minimum longitude value in decimal degrees.
        max_lon (float): Maximum longitude value in decimal degrees.
        min_lat (float): Minimum latitude value in decimal degrees.
        max_lat (float): Maximum latitude value in decimal degrees.

    Example:
        >>> europe_bbox: BoundingBox = {
        ...     "min_lon": -10, "max_lon": 40,
        ...     "min_lat": 35, "max_lat": 70
        ... }
    """

    min_lon: float
    max_lon: float
    min_lat: float
    max_lat: float


# Define bounding boxes for different regions
europe_bbox: BoundingBox = {"min_lon": -10, "max_lon": 40, "min_lat": 35, "max_lat": 70}
se_asia_bbox: BoundingBox = {"min_lon": 90, "max_lon": 140, "min_lat": -10, "max_lat": 30}

# Map species to their regions
species_regions_map: dict[str, BoundingBox] = {
    "Aedes albopictus": europe_bbox,
    "Aedes aegypti": se_asia_bbox,
    "Culex pipiens": europe_bbox,
    "Anopheles gambiae": {"min_lon": -20, "max_lon": 50, "min_lat": -35, "max_lat": 15},
    "Culiseta annulata": europe_bbox,
}

# --- REGIONS DATA ---
regions_data = [
    {"id": "asia", "name_en": "Asia", "name_ru": "Азия"},
    {"id": "europe", "name_en": "Europe", "name_ru": "Европа"},
    {"id": "americas", "name_en": "Americas", "name_ru": "Америка"},
    {"id": "africa", "name_en": "Africa", "name_ru": "Африка"},
    {"id": "oceania", "name_en": "Oceania", "name_ru": "Океания"},
    {"id": "sub_saharan_africa", "name_en": "Sub-Saharan Africa", "name_ru": "Африка к югу от Сахары"},
]
with open("sample_regions.json", "w", encoding="utf-8") as f:
    json.dump(regions_data, f, indent=2, ensure_ascii=False)
print("Generated sample_regions.json")

# --- DATA SOURCES DATA ---
data_sources = [
    {"id": "gbif", "name_en": "GBIF", "name_ru": "GBIF"},
    {"id": "inatuarlist", "name_en": "iNaturalist", "name_ru": "iNaturalist"},
    {"id": "vectorbase", "name_en": "VectorBase", "name_ru": "VectorBase"},
    {"id": "local_survey_a", "name_en": "Local Survey Team A", "name_ru": "Местная исследовательская группа А"},
    {"id": "research_xyz", "name_en": "Research Study XYZ", "name_ru": "Научное исследование XYZ"},
]
with open("sample_data_sources.json", "w", encoding="utf-8") as f:
    json.dump(data_sources, f, indent=2, ensure_ascii=False)
print("Generated sample_data_sources.json")

# --- DISEASES DATA ---
with open("sample_diseases.json", "w", encoding="utf-8") as f:
    json.dump(diseases_data_list, f, indent=2, ensure_ascii=False)
print(f"Generated {'sample_diseases.json'}")

filter_options = {
    "species": [s["scientific_name"] for s in species_list],
    "regions": [r["id"] for r in regions_data],
    "data_sources": data_sources,
}
with open("sample_filter_options.json", "w") as f:
    json.dump(filter_options, f, indent=2)
print("Generated sample_filter_options.json")


def random_point_in_bbox(bbox: BoundingBox) -> list[float]:
    """Generate a random point within the given bounding box.

    Args:
        bbox: A BoundingBox TypedDict containing the coordinate boundaries
            with min_lon, max_lon, min_lat, and max_lat values.

    Returns:
        list[float]: A list containing [latitude, longitude] coordinates
            randomly selected within the bounding box boundaries.

    Example:
        >>> bbox = {"min_lon": -10, "max_lon": 40, "min_lat": 35, "max_lat": 70}
        >>> point = random_point_in_bbox(bbox)
        >>> len(point) == 2
        True
        >>> bbox["min_lat"] <= point[0] <= bbox["max_lat"]
        True
        >>> bbox["min_lon"] <= point[1] <= bbox["max_lon"]
        True
    """
    return [
        random.uniform(bbox["min_lat"], bbox["max_lat"]),
        random.uniform(bbox["min_lon"], bbox["max_lon"]),
    ]


def random_date(start_days_ago: int = 365, end_days_ago: int = 0) -> str:
    """Generate a random date within the specified range.

    Args:
        start_days_ago: Number of days ago to start the random date range.
            Defaults to 365 (1 year ago).
        end_days_ago: Number of days ago to end the random date range.
            Defaults to 0 (today).

    Returns:
        str: A date string in ISO format (YYYY-MM-DD) randomly selected
            between start_days_ago and end_days_ago from the current date.

    Example:
        >>> date_str = random_date(365, 0)
        >>> len(date_str) == 10
        True
        >>> date_str.count('-') == 2
        True
        >>> # Date should be within the last year
        >>> from datetime import datetime, timedelta
        >>> today = datetime.now().date()
        >>> start_date = today - timedelta(days=365)
        >>> end_date = today
        >>> # The generated date should fall within this range
    """
    return (datetime.now() - timedelta(days=random.randint(end_days_ago, start_days_ago))).strftime("%Y-%m-%d")


# --- OBSERVATIONS DATA ---
observations_data = []
for _ in range(100):
    species_obj = random.choice(species_list)
    species_name = str(species_obj["scientific_name"])
    bbox = species_regions_map.get(species_name, europe_bbox)
    point = random_point_in_bbox(bbox)
    observations_data.append(
        {
            "type": "Feature",
            "properties": {
                "id": str(uuid4()),
                "species_scientific_name": species_name,
                "observed_at": random_date(),
                "count": random.randint(1, 20),
                "observer_id": str(uuid4()),
                "location_accuracy_m": random.choice([None, 5, 10, 50, 100]),
                "notes": random.choice(["", "Near standing water.", "Adult female found.", "Larvae collected."]),
                "data_source": random.choice(data_sources),
                "image_filename": f"obs_{random.randint(100,999)}.jpg",
                "model_id": random.choice([None, "model_1", "model_2"]),
                "confidence": random.uniform(0, 1),
                "metadata": {
                    "model_id": random.choice([None, "model_1", "model_2"]),
                    "confidence": random.uniform(0, 1),
                    "species_scientific_name": species_name,
                },
            },
            "geometry": {
                "type": "Point",
                "coordinates": point,
            },
        },
    )
with open("sample_observations.geojson", "w") as f:
    json.dump({"type": "FeatureCollection", "features": observations_data}, f, indent=2)
print("Generated sample_observations.geojson")

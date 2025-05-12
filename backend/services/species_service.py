import json
from typing import List, Optional
import lancedb
from ..database import get_table
from ..models import SpeciesDetail, SpeciesBase


def _parse_json_field(json_string: Optional[str]) -> Optional[List[str]]:
    if json_string is None:
        return None
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        return None  # Or return [] or log error


def _db_record_to_species_detail(record: dict) -> SpeciesDetail:
    return SpeciesDetail(
        id=record.get("id", ""),
        scientific_name=record.get("scientific_name", ""),
        common_name=record.get("common_name"),
        vector_status=record.get("vector_status"),
        image_url=record.get("image_url"),
        description=record.get("description"),
        key_characteristics=_parse_json_field(record.get("key_characteristics")),
        geographic_regions=_parse_json_field(record.get("geographic_regions")),
        related_diseases=_parse_json_field(record.get("related_diseases")),
        habitat_preferences=_parse_json_field(record.get("habitat_preferences")),
    )


def get_all_species(db: lancedb.DBConnection, search: Optional[str] = None, limit: int = 100) -> List[SpeciesBase]:
    """Gets a list of species, optionally filtered by search term."""
    try:
        tbl = get_table(db, "species")
        query = tbl.search().limit(limit)  # Start with limit

        if search:
            # LanceDB FTS or simple filtering (case-insensitive requires lower usually)
            # Simple SQL-like filter (might be case-sensitive depending on backend)
            # Adjust field names if needed
            search_lower = search.lower()
            # NOTE: LanceDB filtering on strings might be basic. FTS is better.
            # For now, approximate with SQL 'like' idea if supported or filter in Python
            # Let's try filtering in Python for simplicity now
            all_species_raw = tbl.to_pydantic(SpeciesDetail)  # Fetch more details for filtering
            filtered_species = [
                s
                for s in all_species_raw
                if (s.scientific_name and search_lower in s.scientific_name.lower())
                or (s.common_name and search_lower in s.common_name.lower())
            ][:limit]  # Apply limit after Python filter
            # Convert back to SpeciesBase for list response
            return [SpeciesBase(**s.model_dump()) for s in filtered_species]

        else:
            # No search, just get base info
            # Select specific columns for efficiency if possible
            selected_columns = ["id", "scientific_name", "common_name", "vector_status", "image_url"]
            # Check if select works as expected
            try:
                results = query.select(selected_columns).to_list()
                return [SpeciesBase(**r) for r in results]
            except:  # Fallback if select causes issues
                print("Warning: Column selection failed, fetching full records for species list.")
                results = query.to_list()
                return [
                    SpeciesBase(
                        id=r.get("id"),
                        scientific_name=r.get("scientific_name"),
                        common_name=r.get("common_name"),
                        vector_status=r.get("vector_status"),
                        image_url=r.get("image_url"),
                    )
                    for r in results
                ]

    except Exception as e:
        print(f"Error getting all species: {e}")
        return []


def get_species_by_id(db: lancedb.DBConnection, species_id: str) -> Optional[SpeciesDetail]:
    """Gets detailed information for a single species by its ID."""
    try:
        tbl = get_table(db, "species")
        result = tbl.search().where(f"id = '{species_id}'").limit(1).to_list()
        if result:
            return _db_record_to_species_detail(result[0])
        return None
    except Exception as e:
        print(f"Error getting species by ID '{species_id}': {e}")
        return None

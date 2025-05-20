import json
from typing import List, Optional, Dict, Any
import lancedb
from backend.services.database import get_table
from backend.models import SpeciesDetail, SpeciesBase
from backend.services import disease_service


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


def get_all_species(db: lancedb.DBConnection, search: Optional[str] = None, limit: int = 10) -> List[SpeciesBase]:
    """Gets a list of species, optionally filtered by search term."""
    try:
        tbl = get_table(db, "species")

        if search:
            search_lower = search.lower()
            # Try using LanceDB's vector search with metadata filtering if possible
            try:
                # This would be the preferred approach if supported by your LanceDB version
                query = (
                    tbl.search()
                    .where(
                        f"LOWER(scientific_name) LIKE '%{search_lower}%' OR LOWER(common_name) LIKE '%{search_lower}%'"
                    )
                    .limit(limit)
                )
                results = query.to_list()
                return [SpeciesBase(**_extract_base_fields(r)) for r in results]
            except Exception as e:
                # Fallback to Python filtering if LanceDB's WHERE clause doesn't work as expected
                print(f"Warning: LanceDB filtering failed, using Python filtering: {e}")
                all_species_raw = tbl.to_list()  # Get all records
                filtered_species = [
                    r
                    for r in all_species_raw
                    if (r.get("scientific_name") and search_lower in str(r.get("scientific_name")).lower())
                    or (r.get("common_name") and search_lower in str(r.get("common_name")).lower())
                ][:limit]  # Apply limit after filtering
                return [SpeciesBase(**_extract_base_fields(r)) for r in filtered_species]
        else:
            # No search term, just get the limited list
            results = tbl.search().limit(limit).to_list()
            return [SpeciesBase(**_extract_base_fields(r)) for r in results]

    except Exception as e:
        print(f"Error getting all species: {e}")
        # Consider logging the full exception with traceback for debugging
        import traceback

        traceback.print_exc()
        return []


def _extract_base_fields(record: dict) -> dict:
    """Helper function to extract only the fields needed for SpeciesBase."""
    return {
        "id": record.get("id"),
        "scientific_name": record.get("scientific_name"),
        "common_name": record.get("common_name"),
        "vector_status": record.get("vector_status"),
        "image_url": record.get("image_url"),
    }


def get_species_by_id(db: lancedb.DBConnection, species_id: str) -> Optional[SpeciesDetail]:
    """Gets detailed information for a single species by its ID."""
    try:
        tbl = get_table(db, "species")
        # Sanitize the input to prevent injection
        sanitized_id = species_id.replace("'", "''")  # Basic SQL injection protection
        result = tbl.search().where(f"id = '{sanitized_id}'").limit(1).to_list()

        if result and len(result) > 0:
            return _db_record_to_species_detail(result[0])
        return None
    except Exception as e:
        print(f"Error getting species by ID '{species_id}': {e}")
        # Consider logging the full exception with traceback for debugging
        import traceback

        traceback.print_exc()
        return None


def _db_record_to_species_detail(record: dict) -> SpeciesDetail:
    """Convert a database record to a SpeciesDetail model.
    This function centralizes the logic for mapping DB fields to the model."""
    # Add any field transformations or enrichment here
    return SpeciesDetail(
        id=record.get("id"),
        scientific_name=record.get("scientific_name"),
        common_name=record.get("common_name"),
        vector_status=record.get("vector_status"),
        image_url=record.get("image_url"),
        taxonomy=record.get("taxonomy"),
        conservation_status=record.get("conservation_status"),
        habitat=record.get("habitat"),
        description=record.get("description"),
        # Add other fields as needed
    )

def get_vector_species(db: lancedb.DBConnection, disease_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get species that are disease vectors, optionally filtered by a specific disease.
    """
    # If a disease ID is provided, get its vectors
    if disease_id:
        disease = disease_service.get_disease_by_id(db, disease_id)
        if not disease or "vectors" not in disease:
            return []

        vector_ids = disease.get("vectors", [])
        if not vector_ids:
            return []

        # Get species details for each vector ID
        table = db.open_table("species")
        vector_species = []

        for vector_id in vector_ids:
            result = table.search(f"id = '{vector_id}'").limit(1).to_pandas()
            if not result.empty:
                vector_species.append(result.to_dict("records")[0])

        return vector_species

    # Otherwise, get all species with vector_status not "None"
    else:
        table = db.open_table("species")
        result = table.search("vector_status != 'None'").to_pandas()
        return result.to_dict("records")
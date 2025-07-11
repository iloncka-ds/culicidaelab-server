import json
from typing import List, Optional, Dict, Any
import lancedb
from backend.services.database import get_table

from backend.schemas.species_schemas import SpeciesDetail, SpeciesBase
from backend.services import disease_service


def _parse_json_field(json_string: Optional[str]) -> Optional[List[str]]:
    if json_string is None:
        return None
    try:
        data = json.loads(json_string)
        if isinstance(data, list):
            return [str(item) for item in data]
        return None
    except (json.JSONDecodeError, TypeError):
        return None

def _get_list_field_from_record(value: Any) -> Optional[List[str]]:
    """
    Helper to safely extract a list of strings from a record value.
    The value might already be a list, or None.
    Pydantic models (like SpeciesBase) expect Optional[List[str]].
    """
    if value is None:
        return None
    if isinstance(value, list):
        return [str(item) for item in value]

    if isinstance(value, str):
        try:
            parsed_value = json.loads(value)
            if isinstance(parsed_value, list):
                return [str(item) for item in parsed_value]
        except json.JSONDecodeError:
            print(f"Warning: Field value was a string but not valid JSON list: {value}")
            return None

    print(f"Warning: Expected list for field, but received type {type(value)}. Value: {value}")
    return []
def _db_record_to_species_detail(record: dict) -> SpeciesDetail:
    """
    Converts a raw dictionary record from LanceDB to a SpeciesDetail Pydantic model.
    Handles fields that are expected to be lists of strings.
    """



    species_detail_data = {
        "id": str(record.get("id", "")),
        "scientific_name": record.get("scientific_name"),
        "common_name": record.get("common_name"),
        "vector_status": record.get("vector_status"),
        "image_url": record.get("image_url"),
        "description": record.get("description"),
        "key_characteristics": _get_list_field_from_record(record.get("key_characteristics")),
        "geographic_regions": _get_list_field_from_record(record.get("geographic_regions")),
        "related_diseases": _get_list_field_from_record(record.get("related_diseases")),
        "habitat_preferences": _get_list_field_from_record(record.get("habitat_preferences")),
    }


    return SpeciesDetail(**species_detail_data)


def get_all_species(
    db: lancedb.DBConnection, search: Optional[str] = None, limit: int = 100
) -> List[SpeciesBase]:
    """
    Gets a list of species, optionally filtered by search term.
    
    Args:
        db: LanceDB connection
        search: Optional search term to filter species by name
        limit: Maximum number of results to return (default: 100)
        
    Returns:
        List of SpeciesBase objects. Returns an empty list on error.
    """
    try:
        tbl = get_table(db, "species")
        if tbl is None:
            print("Error: 'species' table not found in the database")
            return []

        try:
            if search:
                search_lower = search.lower()
                # First try with search optimization
                try:
                    query = tbl.search().limit(limit * 5)
                    all_potential_species = query.to_list()
                    
                    filtered_species = [
                        r for r in all_potential_species
                        if (r.get("scientific_name") and search_lower in str(r.get("scientific_name")).lower())
                        or (r.get("common_name") and search_lower in str(r.get("common_name")).lower())
                    ][:limit]
                    return [SpeciesBase(**_extract_base_fields(r)) for r in filtered_species]
                except Exception as e:
                    print(f"Warning: Search optimization failed, falling back to full table scan: {e}")
                    all_species_raw = tbl.to_list()
                    filtered_species = [
                        r for r in all_species_raw
                        if (r.get("scientific_name") and search_lower in str(r.get("scientific_name")).lower())
                        or (r.get("common_name") and search_lower in str(r.get("common_name")).lower())
                    ][:limit]
                    return [SpeciesBase(**_extract_base_fields(r)) for r in filtered_species]
            else:
                # No search term, just get all species up to limit
                results = tbl.search().limit(limit).to_list()
                return [SpeciesBase(**_extract_base_fields(r)) for r in results]
                
        except Exception as e:
            print(f"Error querying species data: {e}")
            return []
            
    except Exception as e:
        print(f"Critical error in get_all_species: {e}")
        import traceback
        traceback.print_exc()
        return []
        return []


def _extract_base_fields(record: dict) -> dict:
    """Helper function to extract only the fields needed for SpeciesBase."""
    return {
        "id": str(record.get("id")),
        "scientific_name": record.get("scientific_name"),
        "common_name": record.get("common_name"),
        "vector_status": record.get("vector_status"),
        "image_url": record.get("image_url"),
        "description": record.get("description"),
    }


def get_species_by_id(db: lancedb.DBConnection, species_id: str) -> Optional[SpeciesDetail]:
    """Gets detailed information for a single species by its ID."""
    try:
        tbl = get_table(db, "species")
        result = (
            tbl.search().where(f"id = '{species_id}'").limit(1).to_list()
        )

        if result and len(result) > 0:
            return _db_record_to_species_detail(result[0])
        return None
    except Exception as e:
        print(f"Error getting species by ID '{species_id}': {e}")
        import traceback

        traceback.print_exc()
        return None




def get_vector_species(db: lancedb.DBConnection, disease_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get species that are disease vectors, optionally filtered by a specific disease.
    """
    if disease_id:
        disease_obj = disease_service.get_disease_by_id(db, disease_id)

        if not disease_obj:
            return []

        vector_ids = []
        if isinstance(disease_obj, dict):
            vector_ids = disease_obj.get("vectors", [])
        else:
            vector_ids = getattr(disease_obj, "vectors", [])

        if not vector_ids:
            return []

        table = get_table(db, "species")
        vector_species_list = []

        for vector_id in vector_ids:
            results = table.search().where(f"id = '{str(vector_id)}'").limit(1).to_list()
            if results:
                raw_species_data = results[0]
                processed_species_data = {
                    **raw_species_data,
                    "key_characteristics": _get_list_field_from_record(raw_species_data.get("key_characteristics")),
                    "geographic_regions": _get_list_field_from_record(raw_species_data.get("geographic_regions")),
                    "related_diseases": _get_list_field_from_record(raw_species_data.get("related_diseases")),
                    "habitat_preferences": _get_list_field_from_record(raw_species_data.get("habitat_preferences")),
                }
                vector_species_list.append(processed_species_data)
        return vector_species_list
    else:
        table = get_table(db, "species")
        results = (
            table.search().where("vector_status != 'None' AND vector_status != 'Unknown'").limit(200).to_list()
        )

        processed_results = []
        for r in results:
            processed_results.append(
                {
                    **r,
                    "key_characteristics": _get_list_field_from_record(r.get("key_characteristics")),
                    "geographic_regions": _get_list_field_from_record(r.get("geographic_regions")),
                    "related_diseases": _get_list_field_from_record(r.get("related_diseases")),
                    "habitat_preferences": _get_list_field_from_record(r.get("habitat_preferences")),
                }
            )
        return processed_results

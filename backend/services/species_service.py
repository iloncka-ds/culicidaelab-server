import json
from typing import List, Optional, Dict, Any
import lancedb
from backend.services.database import get_table

# Ensure SpeciesDetail is correctly imported and defined (e.g., inherits from SpeciesBase or is similar)
from backend.models import SpeciesDetail, SpeciesBase
from backend.services import disease_service  # Imported but not directly used in the functions changed below


# This function can remain if other parts of your system might store JSON strings
# that need parsing into lists. However, for the specific fields from your example,
# if they are already Python lists from LanceDB, it won't be directly used by the modified
# _db_record_to_species_detail for those fields.
def _parse_json_field(json_string: Optional[str]) -> Optional[List[str]]:
    if json_string is None:
        return None
    try:
        data = json.loads(json_string)
        if isinstance(data, list):
            return [str(item) for item in data]  # Ensure items are strings
        return None  # Parsed, but not a list
    except (json.JSONDecodeError, TypeError):  # TypeError if json_string is not a string
        return None

def _get_list_field_from_record(value: Any) -> Optional[List[str]]:
    """
    Helper to safely extract a list of strings from a record value.
    The value might already be a list, or None.
    Pydantic models (like SpeciesBase) expect Optional[List[str]].
    """
    if value is None:
        return None  # Will default to [] if model has ` = []`
    if isinstance(value, list):
        return [str(item) for item in value]  # Ensure all items are strings

    # If the value is a string, we can attempt to parse it as JSON.
    # This provides fallback if data is inconsistently stored.
    if isinstance(value, str):
        try:
            parsed_value = json.loads(value)
            if isinstance(parsed_value, list):
                return [str(item) for item in parsed_value]
        except json.JSONDecodeError:
            print(f"Warning: Field value was a string but not valid JSON list: {value}")
            return None  # Or handle as appropriate

    print(f"Warning: Expected list for field, but received type {type(value)}. Value: {value}")
    return []
# This is the _db_record_to_species_detail function that should be used.
# The second, conflicting definition later in the original file should be REMOVED.
def _db_record_to_species_detail(record: dict) -> SpeciesDetail:
    """
    Converts a raw dictionary record from LanceDB to a SpeciesDetail Pydantic model.
    Handles fields that are expected to be lists of strings.
    """

      # Or an empty list: []

    # Constructing the SpeciesDetail object.
    # Ensure field names match your SpeciesDetail Pydantic model.
    # SpeciesBase includes: scientific_name, common_name, vector_status, image_url,
    # description, key_characteristics, geographic_regions, related_diseases, habitat_preferences.
    # SpeciesDetail would add 'id' and potentially other fields like 'taxonomy'.

    species_detail_data = {
        "id": str(record.get("id", "")),  # Ensure ID is string
        "scientific_name": record.get("scientific_name"),
        "common_name": record.get("common_name"),
        "vector_status": record.get("vector_status"),
        "image_url": record.get("image_url"),
        "description": record.get("description"),
        "key_characteristics": _get_list_field_from_record(record.get("key_characteristics")),
        "geographic_regions": _get_list_field_from_record(record.get("geographic_regions")),
        "related_diseases": _get_list_field_from_record(record.get("related_diseases")),
        "habitat_preferences": _get_list_field_from_record(record.get("habitat_preferences")),
        # Add any other fields specific to SpeciesDetail that are not in SpeciesBase
        # For example, if 'taxonomy', 'conservation_status', 'habitat' are part of SpeciesDetail:
        # "taxonomy": record.get("taxonomy"),
        # "conservation_status": record.get("conservation_status"),
        # "habitat": record.get("habitat"), # Note: example JSON has 'habitat_preferences' (list)
        # if 'habitat' (singular) is a simple string, direct get is fine.
    }

    # Filter out None values for fields that are optional and not explicitly set,
    # to rely on Pydantic model defaults if any, or to keep them as None.
    # This step might be optional depending on how your Pydantic models handle None vs. missing keys.
    # Pydantic generally handles `None` correctly for `Optional` fields.

    return SpeciesDetail(**species_detail_data)


def get_all_species(
    db: lancedb.DBConnection, search: Optional[str] = None, limit: int = 100
) -> List[SpeciesBase]:  # Increased limit for example
    """Gets a list of species, optionally filtered by search term."""
    try:
        tbl = get_table(db, "species")

        if search:
            search_lower = search.lower()
            # LanceDB FTS or more robust filtering might be available depending on version/setup.
            # The example uses a basic string matching, which can be inefficient.
            # For simplicity, retaining the existing fallback logic if direct WHERE fails.
            try:
                # Attempting a simplified WHERE clause for text search
                # Note: LOWER() might not be directly supported in all LanceDB WHERE clauses.
                # Consider pre-processing data or using vector search for better text matching.
                query = (
                    tbl.search()
                    # This specific SQL-like WHERE with LOWER might not work.
                    # .where(f"CONTAINS(scientific_name, '{search_lower}') OR CONTAINS(common_name, '{search_lower}')") # Example of a hypothetical FTS
                    # Fallback to fetching more and filtering in Python if complex WHERE is not supported
                    .limit(limit * 5)  # Fetch more to filter client-side if necessary
                )
                all_potential_species = query.to_list()

                filtered_species = [
                    r
                    for r in all_potential_species
                    if (r.get("scientific_name") and search_lower in str(r.get("scientific_name")).lower())
                    or (r.get("common_name") and search_lower in str(r.get("common_name")).lower())
                ][:limit]
                return [SpeciesBase(**_extract_base_fields(r)) for r in filtered_species]

            except Exception as e:
                print(f"Warning: LanceDB search/filtering might have issues, falling back to broader fetch: {e}")
                all_species_raw = tbl.to_list()  # Potentially very large, use with caution
                filtered_species = [
                    r
                    for r in all_species_raw
                    if (r.get("scientific_name") and search_lower in str(r.get("scientific_name")).lower())
                    or (r.get("common_name") and search_lower in str(r.get("common_name")).lower())
                ][:limit]
                return [SpeciesBase(**_extract_base_fields(r)) for r in filtered_species]
        else:
            results = tbl.search().limit(limit).to_list()
            return [SpeciesBase(**_extract_base_fields(r)) for r in results]

    except Exception as e:
        print(f"Error getting all species: {e}")
        import traceback

        traceback.print_exc()
        return []


def _extract_base_fields(record: dict) -> dict:
    """Helper function to extract only the fields needed for SpeciesBase."""
    # This ensures that only fields defined in SpeciesBase are passed,
    # and list fields like 'related_diseases' are not included in the summary view if not in SpeciesBase.
    # Your SpeciesBase model does include 'related_diseases', so if you want it in summary, add it here.
    return {
        "id": str(record.get("id")),  # Add id if SpeciesBase needs it (Species extends SpeciesBase with id)
        "scientific_name": record.get("scientific_name"),
        "common_name": record.get("common_name"),
        "vector_status": record.get("vector_status"),
        "image_url": record.get("image_url"),
        # If SpeciesBase schema is exactly as provided, it also includes:
        # description, key_characteristics, geographic_regions, related_diseases, habitat_preferences
        # You might want to include some of these in the base representation or keep it minimal.
        # For example, if description is part of the card summary:
        "description": record.get("description"),
        # For list fields in base, use the helper but be mindful of data size for list views
        # "related_diseases": _get_list_field_from_record(record.get("related_diseases")) # If needed in base
    }


def get_species_by_id(db: lancedb.DBConnection, species_id: str) -> Optional[SpeciesDetail]:
    """Gets detailed information for a single species by its ID."""
    try:
        tbl = get_table(db, "species")
        # Ensure species_id is a string and properly formatted for a 'where' clause if not using parameterized queries.
        # LanceDB's where clause might be sensitive to exact string matching.
        result = (
            tbl.search().where(f"id = '{species_id}'").limit(1).to_list()
        )  # Basic sanitization might be needed for species_id if it can contain special chars

        if result and len(result) > 0:
            return _db_record_to_species_detail(result[0])  # This will use the corrected function
        return None
    except Exception as e:
        print(f"Error getting species by ID '{species_id}': {e}")
        import traceback

        traceback.print_exc()
        return None


# The second definition of _db_record_to_species_detail that was here should be DELETED.
# It was:
# def _db_record_to_species_detail(record: dict) -> SpeciesDetail:
#     """Convert a database record to a SpeciesDetail model.
#     This function centralizes the logic for mapping DB fields to the model."""
#     # Add any field transformations or enrichment here
#     return SpeciesDetail(
#         id=record.get("id"),
#         ...
#         taxonomy=record.get("taxonomy"), # This version was missing list parsing
#         ...
#     )


def get_vector_species(db: lancedb.DBConnection, disease_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get species that are disease vectors, optionally filtered by a specific disease.
    """
    # (This function's logic seems okay as it returns dicts, which SpeciesCard can handle,
    # but ensure the field names in the dicts match what SpeciesCard expects,
    # especially for list-like fields if SpeciesCard renders them from these dicts.)
    # ... (existing implementation of get_vector_species) ...
    # If a disease ID is provided, get its vectors
    if disease_id:
        # Assuming disease_service.get_disease_by_id returns a Pydantic model or a dict
        disease_obj = disease_service.get_disease_by_id(db, disease_id)  # Ensure this call is correct

        if not disease_obj:
            return []

        # Accessing 'vectors' field - adapt if disease_obj is a Pydantic model (disease_obj.vectors)
        # or a dict (disease_obj.get("vectors"))
        vector_ids = []
        if isinstance(disease_obj, dict):
            vector_ids = disease_obj.get("vectors", [])
        else:  # Assuming Pydantic model
            vector_ids = getattr(disease_obj, "vectors", [])  # Or disease_obj.vectors if always present

        if not vector_ids:
            return []

        table = get_table(db, "species")  # Use get_table for consistency
        vector_species_list = []

        for vector_id in vector_ids:
            # Ensure vector_id is a string for the where clause
            results = table.search().where(f"id = '{str(vector_id)}'").limit(1).to_list()
            if results:
                # Convert to SpeciesBase or ensure dict structure is what SpeciesCard expects
                # For now, appending the raw dict from LanceDB
                raw_species_data = results[0]
                # Optionally transform to a common structure if SpeciesCard relies on it.
                # For example, making sure list fields are actual lists:
                processed_species_data = {
                    **raw_species_data,  # spread existing fields
                    "key_characteristics": _get_list_field_from_record(raw_species_data.get("key_characteristics")),
                    "geographic_regions": _get_list_field_from_record(raw_species_data.get("geographic_regions")),
                    "related_diseases": _get_list_field_from_record(raw_species_data.get("related_diseases")),
                    "habitat_preferences": _get_list_field_from_record(raw_species_data.get("habitat_preferences")),
                }
                vector_species_list.append(processed_species_data)
        return vector_species_list
    else:
        # Get all species with vector_status not "None" (or other relevant statuses)
        table = get_table(db, "species")
        # Adjust WHERE clause for what LanceDB supports, e.g., vector_status != 'Unknown' and vector_status IS NOT NULL
        # This might need to be a broader query + Python filter if complex WHERE not supported.
        results = (
            table.search().where("vector_status != 'None' AND vector_status != 'Unknown'").limit(200).to_list()
        )  # Example limit

        # Process these results to ensure list fields are correctly formatted if used by SpeciesCard directly
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

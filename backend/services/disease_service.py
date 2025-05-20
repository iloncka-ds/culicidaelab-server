import lancedb
from typing import List, Dict, Any, Optional
import json  # For _parse_json_field, though not directly used for diseases unless a field is JSON string
import traceback

# Assuming get_table is available through a shared database utility module
# If it's directly in services.database, adjust the import
from backend.services.database import get_table
from backend.schemas.diseases_schemas import Disease  # Using the schema for API consistency


# Helper function to convert a raw database record (dictionary) to a Disease Pydantic model
def _db_record_to_disease_model(record: Dict[str, Any]) -> Disease:
    """Converts a database dictionary record to a Disease Pydantic model."""
    return Disease(
        id=record.get("id", ""),  # Ensure ID is present
        name=record.get("name"),
        description=record.get("description"),
        symptoms=record.get("symptoms"),
        treatment=record.get("treatment"),
        prevention=record.get("prevention"),
        prevalence=record.get("prevalence"),
        image_url=record.get("image_url"),
        vectors=record.get("vectors", []),  # Default to empty list if 'vectors' is missing
    )


def get_all_diseases(db: lancedb.DBConnection, search: Optional[str] = None, limit: int = 50) -> List[Disease]:
    """
    Retrieve a list of diseases, optionally filtered by search term.
    """
    try:
        tbl = get_table(db, "diseases")
        if tbl is None:
            print(f"Error: Table 'diseases' not found or could not be accessed.")
            return []

        query_parts = []
        if search:
            search_lower = search.lower().replace("'", "''")  # Basic sanitization
            # Build search query for multiple fields
            # Note: LanceDB's SQL WHERE clause might have limitations with complex LIKE on non-indexed text.
            # For production, consider FTS or vector embeddings for better text search.
            query_parts.append(f"LOWER(name) LIKE '%{search_lower}%'")
            query_parts.append(f"LOWER(description) LIKE '%{search_lower}%'")
            query_parts.append(f"LOWER(symptoms) LIKE '%{search_lower}%'")

            full_query = " OR ".join(query_parts)
            results_raw = tbl.search().where(full_query).limit(limit).to_list()
        else:
            results_raw = tbl.search().limit(limit).to_list()

        return [_db_record_to_disease_model(r) for r in results_raw]

    except Exception as e:
        print(f"Error getting all diseases: {e}")
        traceback.print_exc()
        return []


def get_disease_by_id(db: lancedb.DBConnection, disease_id: str) -> Optional[Disease]:
    """
    Retrieve detailed information for a specific disease by ID.
    """
    try:
        tbl = get_table(db, "diseases")
        if tbl is None:
            print(f"Error: Table 'diseases' not found or could not be accessed for ID {disease_id}.")
            return None

        sanitized_id = disease_id.replace("'", "''")  # Basic SQL injection protection
        result_raw = tbl.search().where(f"id = '{sanitized_id}'").limit(1).to_list()

        if result_raw and len(result_raw) > 0:
            return _db_record_to_disease_model(result_raw[0])
        return None

    except Exception as e:
        print(f"Error getting disease by ID '{disease_id}': {e}")
        traceback.print_exc()
        return None


def get_diseases_by_vector(db: lancedb.DBConnection, vector_id: str) -> List[Disease]:
    """
    Retrieve a list of diseases associated with a specific vector species ID.
    The 'vectors' field in the 'diseases' table is expected to be a list of strings (species IDs).
    """
    try:
        tbl = get_table(db, "diseases")
        if tbl is None:
            print(f"Error: Table 'diseases' not found or could not be accessed for vector '{vector_id}'.")
            return []

        sanitized_vector_id = vector_id.replace("'", "''")

        # LanceDB's SQL dialect supports array_has(column, value) for checking if an array contains an element.
        # This is generally more efficient and correct than LIKE for array fields.
        # Ensure your LanceDB version supports this.
        # If not, a fallback might be needed (e.g., fetch all and filter in Python, less efficient).
        query = f"array_has(vectors, '{sanitized_vector_id}')"
        # query = f"vectors LIKE '%{sanitized_vector_id}%'" # Less reliable for arrays, use array_has if possible

        results_raw = tbl.search().where(query).to_list()

        return [_db_record_to_disease_model(r) for r in results_raw]

    except Exception as e:
        # Catching potential error if array_has is not supported or other issues
        print(f"Error getting diseases by vector '{vector_id}': {e}")
        print("Attempting fallback with Python-based filtering if array_has failed...")
        traceback.print_exc()

        # Fallback: fetch all and filter in Python (less efficient for large datasets)
        # This part is executed only if the `array_has` query fails.
        try:
            all_diseases_raw = tbl.search().to_list()
            filtered_diseases = [
                _db_record_to_disease_model(r)
                for r in all_diseases_raw
                if r.get("vectors") and vector_id in r["vectors"]
            ]
            return filtered_diseases
        except Exception as fallback_e:
            print(f"Fallback Python filtering also failed for vector '{vector_id}': {fallback_e}")
            traceback.print_exc()
            return []

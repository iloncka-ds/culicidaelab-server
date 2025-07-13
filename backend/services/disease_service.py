import lancedb
from typing import List, Dict, Any, Optional
import traceback

from backend.services.database import get_table
from backend.schemas.diseases_schemas import Disease


def _db_record_to_disease_model(record: Dict[str, Any], lang: str) -> Disease:
    """Converts a database dictionary record to a Disease Pydantic model."""
    fallback_lang = "en"
    return Disease(
        id=record.get("id", ""),
        image_url=record.get("image_url"),
        # Mapped fields
        name=record.get(f"name_{lang}", record.get(f"name_{fallback_lang}")),
        description=record.get(f"description_{lang}", record.get(f"description_{fallback_lang}")),
        symptoms=record.get(f"symptoms_{lang}", record.get(f"symptoms_{fallback_lang}")),
        treatment=record.get(f"treatment_{lang}", record.get(f"treatment_{fallback_lang}")),
        prevention=record.get(f"prevention_{lang}", record.get(f"prevention_{fallback_lang}")),
        prevalence=record.get(f"prevalence_{lang}", record.get(f"prevalence_{fallback_lang}")),
        vectors=record.get("vectors", []),
    )


def get_all_diseases(
    db: lancedb.DBConnection, lang: str, search: Optional[str] = None, limit: int = 50
) -> List[Disease]:
    """
    Retrieve a list of diseases, optionally filtered by search term.
    """
    try:
        tbl = get_table(db, "diseases")
        if tbl is None:
            return []

        query = tbl.search()
        if search:
            search_lower = search.lower().replace("'", "''")
            # Search across all localized text fields
            search_query = (
                f"LOWER(name_en) LIKE '%{search_lower}%' OR "
                f"LOWER(name_es) LIKE '%{search_lower}%' OR "
                f"LOWER(description_en) LIKE '%{search_lower}%' OR "
                f"LOWER(description_es) LIKE '%{search_lower}%'"
            )
            query = query.where(search_query)

        results_raw = query.limit(limit).to_list()
        return [_db_record_to_disease_model(r, lang) for r in results_raw]

    except Exception as e:
        print(f"Error getting all diseases: {e}")
        traceback.print_exc()
        return []


def get_disease_by_id(db: lancedb.DBConnection, disease_id: str, lang: str) -> Optional[Disease]:
    """
    Retrieve detailed information for a specific disease by ID.
    """
    try:
        tbl = get_table(db, "diseases")
        if tbl is None:
            return None

        sanitized_id = disease_id.replace("'", "''")
        result_raw = tbl.search().where(f"id = '{sanitized_id}'").limit(1).to_list()

        if result_raw:
            return _db_record_to_disease_model(result_raw[0], lang)
        return None

    except Exception as e:
        print(f"Error getting disease by ID '{disease_id}': {e}")
        traceback.print_exc()
        return None


def get_diseases_by_vector(db: lancedb.DBConnection, vector_id: str, lang: str) -> List[Disease]:
    """
    Retrieve a list of diseases associated with a specific vector species ID.
    """
    try:
        tbl = get_table(db, "diseases")
        if tbl is None:
            return []
        sanitized_vector_id = vector_id.replace("'", "''")
        query = f"array_has(vectors, '{sanitized_vector_id}')"
        results_raw = tbl.search().where(query).to_list()
        return [_db_record_to_disease_model(r, lang) for r in results_raw]

    except Exception as e:
        print(f"Error getting diseases by vector '{vector_id}': {e}")
        return []

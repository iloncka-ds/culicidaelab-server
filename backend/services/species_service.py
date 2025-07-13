import json
from typing import List, Optional, Dict, Any
import lancedb
from backend.services.database import get_table

from backend.schemas.species_schemas import SpeciesDetail, SpeciesBase
from backend.services import disease_service


def _get_list_field_from_record(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _db_record_to_species_detail(record: dict, lang: str) -> SpeciesDetail:
    """
    Converts a raw dictionary record from LanceDB to a SpeciesDetail Pydantic model.
    """
    fallback_lang = "en"
    return SpeciesDetail(
        id=str(record.get("id", "")),
        scientific_name=record.get("scientific_name"),
        vector_status=record.get("vector_status"),
        image_url=record.get("image_url"),
        # Mapped fields
        common_name=record.get(f"common_name_{lang}", record.get(f"common_name_{fallback_lang}")),
        description=record.get(f"description_{lang}", record.get(f"description_{fallback_lang}")),
        key_characteristics=_get_list_field_from_record(
            record.get(f"key_characteristics_{lang}", record.get(f"key_characteristics_{fallback_lang}"))
        ),
        habitat_preferences=_get_list_field_from_record(
            record.get(f"habitat_preferences_{lang}", record.get(f"habitat_preferences_{fallback_lang}"))
        ),
        # Unchanged fields
        geographic_regions=_get_list_field_from_record(record.get("geographic_regions")),
        related_diseases=_get_list_field_from_record(record.get("related_diseases")),
    )


def _db_record_to_species_base(record: dict, lang: str) -> SpeciesBase:
    """
    Converts a raw dictionary record from LanceDB to a SpeciesBase Pydantic model.
    """
    fallback_lang = "en"
    return SpeciesBase(
        id=str(record.get("id", "")),
        scientific_name=record.get("scientific_name"),
        vector_status=record.get("vector_status"),
        image_url=record.get("image_url"),
        common_name=record.get(f"common_name_{lang}", record.get(f"common_name_{fallback_lang}")),
    )


def get_all_species(
    db: lancedb.DBConnection, lang: str, search: Optional[str] = None, limit: int = 100
) -> List[SpeciesBase]:
    """
    Gets a list of species, optionally filtered by search term.
    """
    try:
        tbl = get_table(db, "species")
        if tbl is None:
            return []

        query = tbl.search()
        if search:
            search_lower = search.lower().replace("'", "''")
            search_query = (
                f"LOWER(scientific_name) LIKE '%{search_lower}%' OR "
                f"LOWER(common_name_en) LIKE '%{search_lower}%' OR "
                f"LOWER(common_name_es) LIKE '%{search_lower}%'"
            )
            query = query.where(search_query)

        results = query.limit(limit).to_list()
        return [_db_record_to_species_base(r, lang) for r in results]
    except Exception as e:
        print(f"Error querying species data: {e}")
        return []


def get_species_by_id(db: lancedb.DBConnection, species_id: str, lang: str) -> Optional[SpeciesDetail]:
    """Gets detailed information for a single species by its ID."""
    try:
        tbl = get_table(db, "species")
        result = tbl.search().where(f"id = '{species_id}'").limit(1).to_list()
        if result:
            return _db_record_to_species_detail(result[0], lang)
        return None
    except Exception as e:
        print(f"Error getting species by ID '{species_id}': {e}")
        return None


def get_vector_species(db: lancedb.DBConnection, lang: str, disease_id: Optional[str] = None) -> List[SpeciesBase]:
    """
    Get species that are disease vectors, optionally filtered by a specific disease.
    """
    vector_ids = []
    if disease_id:
        # We pass the lang param in case we need the disease name for logging, etc.
        disease_obj = disease_service.get_disease_by_id(db, disease_id, lang)
        if not disease_obj or not disease_obj.vectors:
            return []
        vector_ids = disease_obj.vectors

    table = get_table(db, "species")

    if vector_ids:
        # Build a SQL 'IN' clause for the vector IDs
        id_list_str = ", ".join([f"'{v_id}'" for v_id in vector_ids])
        query = table.search().where(f"id IN ({id_list_str})")
    else:
        # Get all species marked as vectors
        query = table.search().where("vector_status != 'None' AND vector_status != 'Unknown'")

    results = query.limit(200).to_list()
    return [_db_record_to_species_base(r, lang) for r in results]

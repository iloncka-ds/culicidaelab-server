import json
from typing import List, Optional, Dict, Any
import lancedb
from fastapi import Request
from backend.services.database import get_table

from backend.schemas.species_schemas import SpeciesDetail, SpeciesBase
from backend.services import disease_service


def _get_list_field_from_record(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _db_record_to_species_detail(
    record: dict, lang: str, region_translations: Dict[str, Dict[str, str]], request: Request
) -> SpeciesDetail:
    """
    Converts a raw dictionary record to a SpeciesDetail Pydantic model.
    It constructs the full image URL dynamically using the request's base URL.

    Args:
        record: The raw data dictionary for the species.
        lang: The target language for translation.
        region_translations: The pre-loaded cache of region translations.
        request: The FastAPI request object, used to get the base URL.
    """
    fallback_lang = "en"
    species_id = record.get("id", "")
    base_url = str(request.base_url)

    image_url = f"{base_url}static/images/species/{species_id}/detail.jpg"

    geographic_region_ids = _get_list_field_from_record(record.get("geographic_regions"))
    lang_specific_translations = region_translations.get(lang, {})
    translated_geographic_regions = [
        lang_specific_translations.get(region_id, region_id) for region_id in geographic_region_ids
    ]
    return SpeciesDetail(
        id=species_id,
        scientific_name=record.get("scientific_name"),
        vector_status=record.get("vector_status"),
        image_url=image_url,  # Use the newly constructed URL
        # Mapped fields
        common_name=record.get(f"common_name_{lang}", record.get(f"common_name_{fallback_lang}")),
        description=record.get(f"description_{lang}", record.get(f"description_{fallback_lang}")),
        key_characteristics=_get_list_field_from_record(
            record.get(f"key_characteristics_{lang}", record.get(f"key_characteristics_{fallback_lang}"))
        ),
        habitat_preferences=_get_list_field_from_record(
            record.get(f"habitat_preferences_{lang}", record.get(f"habitat_preferences_{fallback_lang}"))
        ),
        geographic_regions=translated_geographic_regions,
        related_diseases=_get_list_field_from_record(record.get("related_diseases")),
    )


def _db_record_to_species_base(record: dict, lang: str, request: Request) -> SpeciesBase:
    """
    Converts a raw dictionary record to a SpeciesBase Pydantic model.
    It constructs the full image URL to the thumbnail dynamically.
    """
    fallback_lang = "en"
    species_id = record.get("id", "")
    base_url = str(request.base_url)


    image_url = f"{base_url}static/images/species/{species_id}/thumbnail.jpg"

    return SpeciesBase(
        id=species_id,
        scientific_name=record.get("scientific_name"),
        vector_status=record.get("vector_status"),
        image_url=image_url,  # Use the newly constructed URL
        common_name=record.get(f"common_name_{lang}", record.get(f"common_name_{fallback_lang}")),
    )


def get_all_species(
    db: lancedb.DBConnection, request: Request, lang: str, search: Optional[str] = None, limit: int = 100
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
                f"LOWER(common_name_ru) LIKE '%{search_lower}%'"
            )
            query = query.where(search_query)

        results = query.limit(limit).to_list()
        # Pass the request object to the helper to build the image URL
        return [_db_record_to_species_base(r, lang, request) for r in results]
    except Exception as e:
        print(f"Error querying species data: {e}")
        return []


def get_species_by_id(
    db: lancedb.DBConnection,
    species_id: str,
    lang: str,
    region_translations: Dict[str, Dict[str, str]],
    request: Request,
) -> Optional[SpeciesDetail]:
    """Gets detailed information for a single species by its ID."""
    try:
        tbl = get_table(db, "species")
        result = tbl.search().where(f"id = '{species_id}'").limit(1).to_list()
        if result:
            # Pass the request object to the helper to build the image URL
            return _db_record_to_species_detail(result[0], lang, region_translations, request)
        return None
    except Exception as e:
        print(f"Error getting species by ID '{species_id}': {e}")
        return None


def get_vector_species(
    db: lancedb.DBConnection, request: Request, lang: str, disease_id: Optional[str] = None
) -> List[SpeciesBase]:
    """
    Get species that are disease vectors, optionally filtered by a specific disease.
    """
    vector_ids = []
    if disease_id:

        disease_obj = disease_service.get_disease_by_id(db, disease_id, lang, request)
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
    # Pass the request object to the helper to build the image URL
    return [_db_record_to_species_base(r, lang, request) for r in results]

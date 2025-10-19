"""
Species data service for managing mosquito species information.

This module provides functionality for retrieving and filtering species data
from the database, including support for multiple languages, search functionality,
and vector status filtering. It handles the conversion of raw database records
to properly formatted species models with localized content.

Example:
    >>> from backend.services.species_service import get_all_species
    >>> from backend.services.database import get_db
    >>> from fastapi import Request
    >>> db = get_db()
    >>> species = get_all_species(db, request, "en", search="aedes")
"""

from typing import Any
import os
import lancedb
from fastapi import Request
from backend.services.database import get_table

from backend.schemas.species_schemas import SpeciesDetail, SpeciesBase
from backend.services import disease_service


def _get_list_field_from_record(value: Any) -> list[str]:
    """Convert a database field value to a list of strings.

    This helper function safely converts various database field types to a
    consistent list of strings, handling both list and non-list inputs.

    Args:
        value (Any): The field value from the database record. Can be a list,
            string, or other type.

    Returns:
        list[str]: A list of string representations of the input value.
            Returns an empty list for None or non-list inputs.

    Example:
        >>> _get_list_field_from_record(["item1", "item2"])
        ['item1', 'item2']
        >>> _get_list_field_from_record(None)
        []
    """
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _db_record_to_species_detail(
    record: dict,
    lang: str,
    region_translations: dict[str, dict[str, str]],
    request: Request,
) -> SpeciesDetail:
    """Convert a database record to a detailed SpeciesDetail model with translations.

    This helper function transforms raw database records into SpeciesDetail objects,
    handling language fallbacks, region translations, and dynamic image URL construction.

    Args:
        record (dict): The raw database record containing species data.
        lang (str): The target language code (e.g., 'en', 'ru') for translations.
        region_translations (dict[str, dict[str, str]]): Pre-loaded region
            translations for localizing geographic region names.
        request (Request): The FastAPI request object used to construct image URLs.

    Returns:
        SpeciesDetail: A fully populated SpeciesDetail object with localized
            content, translated region names, and constructed image URL.

    Example:
        >>> record = {
        ...     "id": "aedes_aegypti",
        ...     "scientific_name": "Aedes aegypti",
        ...     "common_name_en": "Yellow fever mosquito"
        ... }
        >>> species = _db_record_to_species_detail(record, "en", regions, request)
    """
    fallback_lang = "en"
    species_id = record.get("id", "")

    # Use environment variable for static URL base, fallback to request base URL
    static_url_base = os.getenv("STATIC_URL_BASE", str(request.base_url).rstrip("/"))
    image_url = f"{static_url_base}/static/images/species/{species_id}/detail.jpg"

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
            record.get(f"key_characteristics_{lang}", record.get(f"key_characteristics_{fallback_lang}")),
        ),
        habitat_preferences=_get_list_field_from_record(
            record.get(f"habitat_preferences_{lang}", record.get(f"habitat_preferences_{fallback_lang}")),
        ),
        geographic_regions=translated_geographic_regions,
        related_diseases=_get_list_field_from_record(record.get("related_diseases")),
    )


def _db_record_to_species_base(record: dict, lang: str, request: Request) -> SpeciesBase:
    """Convert a database record to a basic SpeciesBase model.

    This helper function transforms raw database records into SpeciesBase objects,
    handling language fallbacks and dynamic thumbnail image URL construction.

    Args:
        record (dict): The raw database record containing species data.
        lang (str): The target language code (e.g., 'en', 'ru') for translations.
        request (Request): The FastAPI request object used to construct image URLs.

    Returns:
        SpeciesBase: A SpeciesBase object with localized content and
            constructed thumbnail image URL.

    Example:
        >>> record = {
        ...     "id": "culex_pipiens",
        ...     "scientific_name": "Culex pipiens",
        ...     "common_name_en": "Common house mosquito"
        ... }
        >>> species = _db_record_to_species_base(record, "en", request)
    """
    fallback_lang = "en"
    species_id = record.get("id", "")

    # Use environment variable for static URL base, fallback to request base URL
    static_url_base = os.getenv("STATIC_URL_BASE", str(request.base_url).rstrip("/"))
    image_url = f"{static_url_base}/static/images/species/{species_id}/thumbnail.jpg"
    return SpeciesBase(
        id=species_id,
        scientific_name=record.get("scientific_name"),
        vector_status=record.get("vector_status"),
        image_url=image_url,
        common_name=record.get(f"common_name_{lang}", record.get(f"common_name_{fallback_lang}")),
    )


def get_all_species(
    db: lancedb.DBConnection,
    request: Request,
    lang: str,
    search: str | None = None,
    limit: int = 100,
) -> list[SpeciesBase]:
    """Retrieve a list of species with optional search filtering.

    This function queries the species table and returns species records,
    optionally filtered by search terms across scientific names and common names
    in multiple languages. Results are returned as SpeciesBase objects.

    Args:
        db (lancedb.DBConnection): The database connection object.
        request (Request): The FastAPI request object for image URL construction.
        lang (str): The target language code for localized content.
        search (str | None, optional): Search term to filter species by.
            Searches across scientific names and common names in all languages.
            If None, returns all species.
        limit (int, optional): Maximum number of species to return.
            Defaults to 100.

    Returns:
        list[SpeciesBase]: A list of SpeciesBase objects matching the search
            criteria, or all species if no search term is provided.

    Example:
        >>> from backend.services.database import get_db
        >>> db = get_db()
        >>> # Get all species
        >>> all_species = get_all_species(db, request, "en")
        >>> # Search for Aedes species
        >>> aedes_species = get_all_species(db, request, "en", search="aedes")
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
    region_translations: dict[str, dict[str, str]],
    request: Request,
) -> SpeciesDetail | None:
    """Retrieve detailed information for a specific species by its ID.

    This function queries the species table for a specific species record
    and returns it as a detailed SpeciesDetail object with full information
    including translated region names. Returns None if the species is not found.

    Args:
        db (lancedb.DBConnection): The database connection object.
        species_id (str): The unique identifier for the species to retrieve.
        lang (str): The target language code for localized content.
        region_translations (dict[str, dict[str, str]]): Pre-loaded region
            translations for localizing geographic region names.
        request (Request): The FastAPI request object for image URL construction.

    Returns:
        SpeciesDetail | None: A SpeciesDetail object if found, None if the
            species does not exist in the database.

    Example:
        >>> from backend.services.database import get_db
        >>> db = get_db()
        >>> aedes = get_species_by_id(db, "aedes_aegypti", "en", regions, request)
        >>> if aedes:
        ...     print(f"Species: {aedes.scientific_name}")
        ...     print(f"Regions: {aedes.geographic_regions}")
    """
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
    db: lancedb.DBConnection,
    request: Request,
    lang: str,
    disease_id: str | None = None,
) -> list[SpeciesBase]:
    """Retrieve species that are disease vectors, optionally filtered by disease.

    This function queries the species table for species marked as disease vectors.
    It can filter by a specific disease to find only species that transmit that
    disease, or return all vector species if no disease filter is applied.

    Args:
        db (lancedb.DBConnection): The database connection object.
        request (Request): The FastAPI request object for image URL construction.
        lang (str): The target language code for localized content.
        disease_id (str | None, optional): Specific disease ID to filter by.
            If provided, only species that transmit this disease are returned.
            If None, all vector species are returned.

    Returns:
        list[SpeciesBase]: A list of SpeciesBase objects that are disease vectors,
            optionally filtered by the specified disease.

    Example:
        >>> from backend.services.database import get_db
        >>> db = get_db()
        >>> # Get all vector species
        >>> all_vectors = get_vector_species(db, request, "en")
        >>> # Get species that transmit malaria
        >>> malaria_vectors = get_vector_species(db, request, "en", "malaria")
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

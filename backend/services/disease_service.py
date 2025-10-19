"""
Disease data service for managing mosquito-borne disease information.

This module provides functionality for retrieving and filtering disease data
from the database, including support for multiple languages, search functionality,
and vector-based filtering. It handles the conversion of raw database records
to properly formatted disease models.

Example:
    >>> from backend.services.disease_service import get_all_diseases
    >>> from backend.services.database import get_db
    >>> from fastapi import Request
    >>> db = get_db()
    >>> diseases = get_all_diseases(db, request, "en", search="malaria")
"""

import lancedb
from typing import Any
import traceback
from fastapi import Request
import os

from backend.services.database import get_table
from backend.schemas.diseases_schemas import Disease


def _db_record_to_disease_model(record: dict[str, Any], lang: str, request: Request) -> Disease:
    """Convert a database record to a Disease Pydantic model with localized content.

    This helper function transforms raw database records into properly structured
    Disease objects, handling language fallbacks and dynamic image URL construction
    based on the request's base URL.

    Args:
        record (dict[str, Any]): The raw database record containing disease data.
        lang (str): The target language code (e.g., 'en', 'ru') for translations.
        request (Request): The FastAPI request object used to construct image URLs.

    Returns:
        Disease: A fully populated Disease object with localized content and
            dynamically constructed image URL.

    Example:
        >>> record = {
        ...     "id": "malaria",
        ...     "name_en": "Malaria",
        ...     "description_en": "A mosquito-borne disease..."
        ... }
        >>> disease = _db_record_to_disease_model(record, "en", request)
        >>> print(disease.name)  # "Malaria"
    """
    fallback_lang = "en"
    disease_id = record.get("id", "")

    # Use environment variable for static URL base, fallback to request base URL
    static_url_base = os.getenv("STATIC_URL_BASE", str(request.base_url).rstrip("/"))
    image_url = f"{static_url_base}/static/images/diseases/{disease_id}/detail.jpg"
    return Disease(
        id=disease_id,
        image_url=image_url,  # Use the newly constructed URL
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
    db: lancedb.DBConnection,
    request: Request,
    lang: str,
    search: str | None = None,
    limit: int = 50,
) -> list[Disease]:
    """Retrieve a list of diseases with optional search filtering.

    This function queries the diseases table and returns disease records,
    optionally filtered by search terms across multiple language fields.
    Results are returned as properly formatted Disease objects.

    Args:
        db (lancedb.DBConnection): The database connection object.
        request (Request): The FastAPI request object for image URL construction.
        lang (str): The target language code for localized content.
        search (str | None, optional): Search term to filter diseases by.
            Searches across name and description fields in all languages.
            If None, returns all diseases.
        limit (int, optional): Maximum number of diseases to return.
            Defaults to 50.

    Returns:
        list[Disease]: A list of Disease objects matching the search criteria,
            or all diseases if no search term is provided.

    Example:
        >>> from backend.services.database import get_db
        >>> db = get_db()
        >>> # Get all diseases
        >>> all_diseases = get_all_diseases(db, request, "en")
        >>> # Search for malaria-related diseases
        >>> malaria_diseases = get_all_diseases(db, request, "en", search="malaria")
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
                f"LOWER(name_ru) LIKE '%{search_lower}%' OR "
                f"LOWER(description_en) LIKE '%{search_lower}%' OR "
                f"LOWER(description_ru) LIKE '%{search_lower}%'"
            )
            query = query.where(search_query)

        results_raw = query.limit(limit).to_list()
        # Pass the request object to the helper to build the image URL
        return [_db_record_to_disease_model(r, lang, request) for r in results_raw]

    except Exception as e:
        print(f"Error getting all diseases: {e}")
        traceback.print_exc()
        return []


def get_disease_by_id(db: lancedb.DBConnection, disease_id: str, lang: str, request: Request) -> Disease | None:
    """Retrieve detailed information for a specific disease by its ID.

    This function queries the diseases table for a specific disease record
    and returns it as a properly formatted Disease object. Returns None
    if the disease is not found.

    Args:
        db (lancedb.DBConnection): The database connection object.
        disease_id (str): The unique identifier for the disease to retrieve.
        lang (str): The target language code for localized content.
        request (Request): The FastAPI request object for image URL construction.

    Returns:
        Disease | None: A Disease object if found, None if the disease
            does not exist in the database.

    Example:
        >>> from backend.services.database import get_db
        >>> db = get_db()
        >>> malaria = get_disease_by_id(db, "malaria", "en", request)
        >>> if malaria:
        ...     print(f"Disease: {malaria.name}")
    """
    try:
        tbl = get_table(db, "diseases")
        if tbl is None:
            return None

        sanitized_id = disease_id.replace("'", "''")
        result_raw = tbl.search().where(f"id = '{sanitized_id}'").limit(1).to_list()

        if result_raw:
            # Pass the request object to the helper to build the image URL
            return _db_record_to_disease_model(result_raw[0], lang, request)
        return None

    except Exception as e:
        print(f"Error getting disease by ID '{disease_id}': {e}")
        traceback.print_exc()
        return None


def get_diseases_by_vector(db: lancedb.DBConnection, vector_id: str, lang: str, request: Request) -> list[Disease]:
    """Retrieve diseases associated with a specific mosquito vector species.

    This function queries the diseases table for diseases that are transmitted
    by the specified vector species. The vector relationship is determined
    by checking if the vector_id exists in the disease's vectors array.

    Args:
        db (lancedb.DBConnection): The database connection object.
        vector_id (str): The unique identifier of the vector species to search for.
        lang (str): The target language code for localized content.
        request (Request): The FastAPI request object for image URL construction.

    Returns:
        list[Disease]: A list of Disease objects that are transmitted by the
            specified vector species. Returns an empty list if no diseases
            are found or if the vector species doesn't exist.

    Example:
        >>> from backend.services.database import get_db
        >>> db = get_db()
        >>> # Get diseases transmitted by Aedes aegypti
        >>> aedes_diseases = get_diseases_by_vector(db, "aedes_aegypti", "en", request)
        >>> for disease in aedes_diseases:
        ...     print(f"{disease.name} - transmitted by Aedes aegypti")
    """
    try:
        tbl = get_table(db, "diseases")
        if tbl is None:
            return []
        sanitized_vector_id = vector_id.replace("'", "''")
        query = f"array_has(vectors, '{sanitized_vector_id}')"
        results_raw = tbl.search().where(query).to_list()
        # Pass the request object to the helper to build the image URL
        return [_db_record_to_disease_model(r, lang, request) for r in results_raw]

    except Exception as e:
        print(f"Error getting diseases by vector '{vector_id}': {e}")
        return []

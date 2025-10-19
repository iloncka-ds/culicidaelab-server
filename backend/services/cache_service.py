"""
Data caching service for loading and caching translation data.

This module provides functions for loading translation data from the database
and caching it in memory for improved performance. It handles region translations,
data source translations, and species names with fallback mechanisms for missing
translations.

Example:
    >>> from backend.services.cache_service import load_all_region_translations
    >>> from backend.services.database import get_db
    >>> db = get_db()
    >>> regions = load_all_region_translations(db, ["en", "ru"])
    >>> print(regions["en"]["us"])  # "United States"
"""

from backend.services.database import get_table


def load_all_region_translations(db: object, supported_langs: list[str]) -> dict[str, dict[str, str]]:
    """Load all region translations from the database for multiple languages.

    This function queries the regions table and extracts translations for all
    supported languages, using English as a fallback for missing translations.
    The data is loaded once at application startup for performance.

    Args:
        db (object): The database connection object.
        supported_langs (list[str]): A list of language codes to load
            (e.g., ['en', 'ru', 'es']).

    Returns:
        dict[str, dict[str, str]]: A nested dictionary structured as
            {language_code: {region_id: translated_name}}. Missing translations
            fall back to English or the region ID itself.

    Example:
        >>> db = get_db()
        >>> translations = load_all_region_translations(db, ["en", "ru"])
        >>> print(translations["en"]["us"])  # "United States"
        >>> print(translations["ru"]["us"])  # "Соединенные Штаты"
    """
    print("Executing `load_all_region_translations`: Loading region data into memory...")
    try:
        regions_tbl = get_table(db, "regions")
        lang_columns = [f"name_{lang}" for lang in supported_langs]
        all_columns = ["id"] + lang_columns

        regions_res = regions_tbl.search().select(all_columns).to_list()

        translations: dict[str, dict[str, str]] = {lang: {} for lang in supported_langs}
        fallback_lang = "en"

        for record in regions_res:
            region_id = record.get("id")
            if not region_id:
                continue

            for lang in supported_langs:
                translated_name = record.get(f"name_{lang}") or record.get(f"name_{fallback_lang}", region_id)
                translations[lang][region_id] = translated_name

        print("✅ Region translations loaded successfully.")
        return translations
    except Exception as e:
        print(f"❌ ERROR: Failed to load region translations: {e}")
        return {lang: {} for lang in supported_langs}


def load_all_datasource_translations(db: object, supported_langs: list[str]) -> dict[str, dict[str, str]]:
    """Load all data source translations from the database for multiple languages.

    This function queries the data_sources table and extracts translations for all
    supported languages, using English as a fallback for missing translations.
    Returns an empty dictionary if the query fails.

    Args:
        db (object): The database connection object.
        supported_langs (list[str]): A list of language codes to load
            (e.g., ['en', 'ru', 'es']).

    Returns:
        dict[str, dict[str, str]]: A nested dictionary structured as
            {language_code: {source_id: translated_name}}. Returns an empty
            dictionary if the query fails. Missing translations fall back
            to English or the source ID itself.

    Example:
        >>> db = get_db()
        >>> translations = load_all_datasource_translations(db, ["en", "ru"])
        >>> print(translations["en"]["gbif"])  # "GBIF"
        >>> print(translations["ru"]["gbif"])  # "GBIF"
    """
    print("Executing `load_all_data_source_translations`...")
    try:
        data_sources_tbl = get_table(db, "data_sources")
        lang_columns = [f"name_{lang}" for lang in supported_langs]
        all_columns = ["id"] + lang_columns
        data_sources_res = data_sources_tbl.search().select(all_columns).to_list()

        translations: dict[str, dict[str, str]] = {lang: {} for lang in supported_langs}
        fallback_lang = "en"

        for record in data_sources_res:
            source_id = record.get("id")
            if not source_id:
                continue
            for lang in supported_langs:
                translated_name = record.get(f"name_{lang}") or record.get(f"name_{fallback_lang}", source_id)
                translations[lang][source_id] = translated_name

        print("✅ Data Source translations loaded.")
        return translations
    except Exception as e:
        print(f"❌ ERROR: Failed to load data source translations: {e}")
        return {}


def load_all_species_names(db: object) -> list[str]:
    """Load a sorted list of all unique species scientific names from the database.

    This function queries the species table and extracts all unique scientific
    names, returning them as a sorted list. Returns an empty list if the query fails.

    Args:
        db (object): The database connection object.

    Returns:
        list[str]: A sorted list of unique species scientific names. Returns
            an empty list if the query fails or no species are found.

    Example:
        >>> db = get_db()
        >>> species_names = load_all_species_names(db)
        >>> print(len(species_names))  # Number of species
        >>> print(species_names[:3])  # First 3 species names
    """
    print("Executing `load_all_species_names`...")
    try:
        species_tbl = get_table(db, "species")
        species_results = species_tbl.search().select(["scientific_name"]).to_list()
        species_names = sorted([r["scientific_name"] for r in species_results if r.get("scientific_name")])
        print("✅ Species names loaded.")
        return species_names
    except Exception as e:
        print(f"❌ ERROR: Failed to load species names: {e}")
        return []

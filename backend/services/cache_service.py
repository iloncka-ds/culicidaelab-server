from typing import Dict, List
from backend.services.database import get_table


def load_all_region_translations(db: object, supported_langs: List[str]) -> Dict[str, Dict[str, str]]:
    """
    Loads all region translations from the database for all supported languages.
    This function is intended to be called only once on application startup.

    Args:
        db: The database connection object.
        supported_langs: A list of language codes to load (e.g., ['en', 'ru']).

    Returns:
        A nested dictionary structured as: {lang: {region_id: region_name}}.
    """
    print("Executing `load_all_region_translations`: Loading region data into memory...")
    regions_tbl = get_table(db, "regions")

    lang_columns = [f"name_{lang}" for lang in supported_langs]
    all_columns = ["id"] + lang_columns

    regions_res = regions_tbl.search().select(all_columns).to_list()

    translations = {lang: {} for lang in supported_langs}
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

def load_all_data_source_translations(db: object, supported_langs: List[str]) -> Dict[str, Dict[str, str]]:
    """
    Loads all data source translations from the database for all supported languages.
    """
    print("Executing `load_all_data_source_translations`...")
    try:
        data_sources_tbl = get_table(db, "data_sources")
        lang_columns = [f"name_{lang}" for lang in supported_langs]
        all_columns = ["id"] + lang_columns
        data_sources_res = data_sources_tbl.search().select(all_columns).to_list()

        translations = {lang: {} for lang in supported_langs}
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


def load_all_species_names(db: object) -> List[str]:
    """
    Loads a sorted list of all unique species scientific names.
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
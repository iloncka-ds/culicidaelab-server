from typing import Dict, List
from backend.schemas.filter_schemas import FilterOptions, RegionFilter, DataSourceFilter


def get_filter_options(lang: str,
                       species_names: List[str],
                       region_translations: Dict[str, Dict[str, str]],
                       data_source_translations: Dict[str, Dict[str, str]]) -> FilterOptions:
    """
    Constructs translated filter options from pre-loaded, cached data.
    This function is completely stateless and performs no I/O.

    Args:
        lang: The target language code.
        species_names: The cached list of all species scientific names.
        region_translations: The cached dictionary of all region translations.
        data_source_translations: The cached dictionary of all data source translations.
    """
    lang_specific_regions = region_translations.get(lang, {})
    regions = sorted(
        [
            RegionFilter(id=region_id, name=translated_name)
            for region_id, translated_name in lang_specific_regions.items()
        ],
        key=lambda x: x.name,
    )

    # 3. Process cached data sources for the requested language
    lang_specific_data_sources = data_source_translations.get(lang, {})
    data_sources = sorted(
        [
            DataSourceFilter(id=source_id, name=translated_name)
            for source_id, translated_name in lang_specific_data_sources.items()
        ],
        key=lambda x: x.name,
    )

    return FilterOptions(species=species_names, regions=regions, data_sources=data_sources)

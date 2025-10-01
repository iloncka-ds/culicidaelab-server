"""
Filter options service for generating localized filter data.

This module provides functionality for constructing translated filter options
from cached data sources, regions, and species information. It supports
multiple languages and generates filter objects suitable for frontend
consumption.

Example:
    >>> from backend.services.filter_service import get_filter_options
    >>> options = get_filter_options(
    ...     lang="en",
    ...     species_names=["Aedes aegypti", "Culex pipiens"],
    ...     region_translations={"en": {"reg1": "Region 1"}},
    ...     data_source_translations={"en": {"src1": "Source 1"}}
    ... )
"""

from backend.schemas.filter_schemas import FilterOptions, RegionFilter, DataSourceFilter


def get_filter_options(
    lang: str,
    species_names: list[str],
    region_translations: dict[str, dict[str, str]],
    data_source_translations: dict[str, dict[str, str]],
) -> FilterOptions:
    """Construct translated filter options from pre-loaded, cached data.

    This function processes cached translation data to generate filter options
    for species, regions, and data sources in the specified language. All
    options are sorted alphabetically for consistent presentation.

    Args:
        lang (str): The target language code (e.g., 'en', 'ru') for which
            to generate translated filter options.
        species_names (list[str]): A list of scientific species names to
            include in the filter options.
        region_translations (dict[str, dict[str, str]]): A nested dictionary
            containing region translations structured as {lang: {region_id: name}}.
        data_source_translations (dict[str, dict[str, str]]): A nested dictionary
            containing data source translations structured as {lang: {source_id: name}}.

    Returns:
        FilterOptions: A structured object containing sorted filter options for
            species, regions, and data sources in the specified language.

    Example:
        >>> species = ["Aedes aegypti", "Culex quinquefasciatus"]
        >>> regions = {"en": {"us": "United States", "br": "Brazil"}}
        >>> sources = {"en": {"gbif": "GBIF", "citizen": "Citizen Science"}}
        >>> options = get_filter_options("en", species, regions, sources)
        >>> print(len(options.regions))  # Number of region options
        2
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

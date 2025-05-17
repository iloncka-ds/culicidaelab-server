import lancedb
from backend.services.database import get_table
from backend.models import FilterOptions
import json

def get_filter_options(db: lancedb.DBConnection) -> FilterOptions:
    """Gets filter options (species, regions, data sources)."""
    species_names = []
    regions = set()
    data_sources = set()

    try:
        # Get species names
        species_tbl = get_table(db, "species")
        # Assuming scientific_name is unique and non-null
        species_results = species_tbl.search().select(["scientific_name"]).to_list()
        species_names = sorted([r["scientific_name"] for r in species_results if r.get("scientific_name")])
        regions_tbl = get_table(db, "regions")

        regions_res = regions_tbl.search().select(["name"]).to_list()
        regions = sorted([r.get("name") for r in regions_res])
        data_sources_tbl = get_table(db, "data_sources")
        data_sources_res = data_sources_tbl.search().select(["name"]).to_list()
        data_sources = sorted([r.get("name") for r in data_sources_res])
        # Get distinct regions and data sources from geo_features table
        # geo_tbl = get_table(db, "geo_features")
        # This might be slow on large tables without specific optimizations/indexes in LanceDB for distinct values.
        # Consider alternative storage if performance is critical.
        # Fetch necessary fields (adjust limit if needed, but could be large)
        # geo_results = (
        #     geo_tbl.search().select(["geographic_regions", "data_source"]).limit(5000).to_list()
        # )  # Limit to avoid pulling too much data

        # # We stored geographic_regions as a JSON string in the species table, not geo_features
        # # Let's get regions from the species table instead
        # region_results = species_tbl.search().select(["geographic_regions"]).to_list()
        # for r in region_results:
        #     region_list_str = r.get("geographic_regions")
        #     if region_list_str:
        #         try:
        #             region_list = json.loads(region_list_str)
        #             if isinstance(region_list, list):
        #                 regions.update(region_list)
        #         except Exception:
        #             pass  # Ignore parsing errors

        # # Get data sources from geo_features
        # for r in geo_results:
        #     ds = r.get("data_source")
        #     if ds:
        #         data_sources.add(ds)

    except Exception as e:
        print(f"Error getting filter options: {e}")
        # Return empty lists on error

    return FilterOptions(species=species_names, regions=sorted(regions), data_sources=sorted(data_sources))

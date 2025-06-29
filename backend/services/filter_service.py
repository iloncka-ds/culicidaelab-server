import lancedb
from backend.services.database import get_table
from backend.models import FilterOptions


def get_filter_options(db: lancedb.DBConnection) -> FilterOptions:
    """Gets filter options (species, regions, data sources)."""
    species_names = []
    regions = set()
    data_sources = set()

    try:
        species_tbl = get_table(db, "species")
        species_results = species_tbl.search().select(["scientific_name"]).to_list()
        species_names = sorted([r["scientific_name"] for r in species_results if r.get("scientific_name")])
        regions_tbl = get_table(db, "regions")

        regions_res = regions_tbl.search().select(["name"]).to_list()
        regions = sorted([r.get("name") for r in regions_res if r.get("name")])
        data_sources_tbl = get_table(db, "data_sources")
        data_sources_res = data_sources_tbl.search().select(["name"]).to_list()
        data_sources = sorted([r.get("name") for r in data_sources_res if r.get("name")])



    except Exception as e:
        print(f"Error getting filter options: {e}")

    return FilterOptions(species=species_names, regions=sorted(regions), data_sources=sorted(data_sources))

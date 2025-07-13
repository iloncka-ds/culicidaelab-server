import lancedb
from backend.services.database import get_table
from backend.schemas.filter_schemas import FilterOptions, RegionFilter, DataSourceFilter


def get_filter_options(db: lancedb.DBConnection, lang: str) -> FilterOptions:
    """Gets translated filter options (species, regions, data sources)."""
    fallback_lang = "en"

    species_names = []
    regions = []
    data_sources = []

    try:
        # 1. Get Species (scientific_name is not translated)
        species_tbl = get_table(db, "species")
        species_results = species_tbl.search().select(["scientific_name"]).to_list()
        species_names = sorted([r["scientific_name"] for r in species_results if r.get("scientific_name")])

        # 2. Get Translated Regions
        regions_tbl = get_table(db, "regions")
        regions_res = regions_tbl.search().select(["id", f"name_{lang}", f"name_{fallback_lang}"]).to_list()
        regions = sorted(
            [
                RegionFilter(id=r["id"], name=r.get(f"name_{lang}") or r.get(f"name_{fallback_lang}", r["id"]))
                for r in regions_res
                if r.get("id")
            ],
            key=lambda x: x.name,
        )

        # 3. Get Translated Data Sources
        data_sources_tbl = get_table(db, "data_sources")
        data_sources_res = data_sources_tbl.search().select(["id", f"name_{lang}", f"name_{fallback_lang}"]).to_list()
        data_sources = sorted(
            [
                DataSourceFilter(id=r["id"], name=r.get(f"name_{lang}") or r.get(f"name_{fallback_lang}", r["id"]))
                for r in data_sources_res
                if r.get("id")
            ],
            key=lambda x: x.name,
        )

    except Exception as e:
        print(f"Error getting filter options: {e}")

    return FilterOptions(species=species_names, regions=regions, data_sources=data_sources)

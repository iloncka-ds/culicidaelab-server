from backend.database.lancedb_manager import LanceDBManager
from typing import List, Optional, Dict, Any
import json  # For parsing characteristics etc. if they were stored as JSON strings


class SpeciesService:
    def __init__(self, db_manager: LanceDBManager):
        self.db_manager = db_manager

    async def get_all_species(
        self, search: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        species_table = await self.db_manager.get_table("species")
        if not species_table:
            return []

        query_builder = species_table.search()
        if search:
            # LanceDB full-text search is more complex (e.g., requires FTS index or vectorization)
            # Simple SQL-like WHERE for substring match:
            query_builder = query_builder.where(
                f"LOWER(scientific_name) LIKE '%{search.lower()}%' OR LOWER(common_name) LIKE '%{search.lower()}%'"
            )

        results_df = await query_builder.limit(limit).offset(offset).to_pandas()
        return results_df.to_dict(orient="records")

    async def get_species_by_id(self, species_id: str) -> Optional[Dict[str, Any]]:
        species_table = await self.db_manager.get_table("species")
        if not species_table:
            return None
        try:
            # Assuming 'id' is a primary field used for filtering
            results_df = await species_table.search().where(f"id = '{species_id}'").limit(1).to_pandas()
            if not results_df.empty:
                return results_df.iloc[0].to_dict()
        except Exception as e:
            print(f"Error fetching species by id {species_id}: {e}")
        return None

    async def get_filter_options(self) -> Dict[str, List[str]]:
        species_table = await self.db_manager.get_table("species")
        regions_table = await self.db_manager.get_table("regions")
        data_sources_table = await self.db_manager.get_table("data_sources")

        species_names = []
        if species_table:
            df = await species_table.to_pandas(columns=["scientific_name"])
            species_names = df["scientific_name"].unique().tolist()

        region_names = []
        if regions_table:
            df = await regions_table.to_pandas(columns=["name"])
            region_names = df["name"].unique().tolist()

        ds_names = []
        if data_sources_table:
            df = await data_sources_table.to_pandas(columns=["name"])
            ds_names = df["name"].unique().tolist()

        return {"species": sorted(species_names), "regions": sorted(region_names), "data_sources": sorted(ds_names)}

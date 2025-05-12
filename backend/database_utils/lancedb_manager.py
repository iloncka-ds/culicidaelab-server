import lancedb
import pyarrow as pa
import os
from typing import Optional, List, Dict, Any

LANCEDB_URI = os.environ.get("LANCEDB_URI", ".lancedb")  # Default to local dir

# Define PyArrow schemas for our tables
# These need to match the structure of your data when inserting
SPECIES_SCHEMA = pa.schema(
    [
        pa.field("id", pa.string(), nullable=False),
        pa.field("scientific_name", pa.string()),
        pa.field("common_name", pa.string()),
        pa.field("vector_status", pa.string()),
        pa.field("image_url", pa.string()),
        pa.field("description", pa.string()),
        pa.field("key_characteristics", pa.list_(pa.string())),
        pa.field("geographic_regions", pa.list_(pa.string())),
        pa.field("related_diseases", pa.list_(pa.string())),
        pa.field("habitat_preferences", pa.list_(pa.string())),
    ]
)

FILTER_OPTIONS_SCHEMA = pa.schema(
    [  # Store each option type in its own table for simplicity
        pa.field("name", pa.string(), nullable=False)
    ]
)  # Separate tables for regions, data_sources

MAP_LAYERS_SCHEMA = pa.schema(
    [
        pa.field("layer_type", pa.string(), nullable=False),  # 'distribution', 'observations', etc.
        pa.field("layer_name", pa.string()),  # e.g., "Default Observations Layer"
        # Storing the entire GeoJSON FeatureCollection string.
        # Filtering by species/bbox will happen in Python after retrieval.
        pa.field("geojson_data", pa.string(), nullable=False),
        # We can add a field for all species present in this geojson_data to aid initial filtering
        pa.field("contained_species", pa.list_(pa.string())),
    ]
)


class LanceDBManager:
    def __init__(self, uri: str = LANCEDB_URI):
        self.uri = uri
        self.db = None  # Initialized in connect

    async def connect(self):
        """Connects to the LanceDB database."""
        if self.db is None:
            self.db = await lancedb.connect_async(self.uri)
            print(f"Connected to LanceDB at {self.uri}")

    async def close(self):
        """Closes the LanceDB connection."""
        # LanceDB async connection doesn't have an explicit close in current versions.
        # Connections are typically managed per operation or globally.
        # For now, this method is a placeholder.
        if self.db:
            # await self.db.close() # If future versions support it
            print("LanceDB connection implicitly managed.")
            self.db = None

    async def get_table(self, table_name: str, schema: Optional[pa.Schema] = None) -> Optional[lancedb.aio.LanceTable]:
        """Gets a table, creating it with the schema if it doesn't exist."""
        if not self.db:
            await self.connect()

        try:
            table_names = await self.db.table_names()
            if table_name not in table_names:
                if schema:
                    print(f"Table '{table_name}' not found. Creating with provided schema.")
                    return await self.db.create_table(table_name, schema=schema, mode="create")  # or "overwrite"
                else:
                    print(f"Table '{table_name}' not found and no schema provided for creation.")
                    return None
            return await self.db.open_table(table_name)
        except Exception as e:
            print(f"Error accessing table {table_name}: {e}")
            return None

    async def create_or_overwrite_table(self, table_name: str, data: List[Dict[str, Any]], schema: pa.Schema):
        if not self.db:
            await self.connect()
        try:
            print(f"Creating/overwriting table '{table_name}' with {len(data)} records.")
            tbl = await self.db.create_table(table_name, data=data, schema=schema, mode="overwrite")
            print(f"Table '{table_name}' created/overwritten successfully.")
            return tbl
        except Exception as e:
            print(f"Error creating/overwriting table {table_name}: {e}")
            raise


# Global instance (can be managed with FastAPI lifespan events or dependencies)
lancedb_manager = LanceDBManager()


async def get_lancedb_manager():
    # Ensures connection is established before use in routers
    if not lancedb_manager.db:
        await lancedb_manager.connect()
    return lancedb_manager

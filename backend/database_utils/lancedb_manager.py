import lancedb
import pyarrow as pa
import os
from typing import Optional, List, Dict, Any

LANCEDB_URI = os.environ.get("LANCEDB_URI", ".lancedb")

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
        pa.field("related_diseases_info", pa.list_(pa.string())),
        pa.field("habitat_preferences", pa.list_(pa.string())),
    ]
)

DISEASES_SCHEMA = pa.schema(
    [
        pa.field("id", pa.string(), nullable=False),
        pa.field("name", pa.string()),
        pa.field("description", pa.string()),
        pa.field("symptoms", pa.string()),
        pa.field("treatment", pa.string()),
        pa.field("prevention", pa.string()),
        pa.field("prevalence", pa.string()),
        pa.field("image_url", pa.string()),
        pa.field("vectors", pa.list_(pa.string())),
    ]
)

FILTER_OPTIONS_SCHEMA = pa.schema(
    [
        pa.field("name", pa.string(), nullable=False)
    ]
)

MAP_LAYERS_SCHEMA = pa.schema(
    [
        pa.field("layer_type", pa.string(), nullable=False),
        pa.field("layer_name", pa.string()),
        pa.field("geojson_data", pa.string(), nullable=False),
        pa.field("contained_species", pa.list_(pa.string())),
    ]
)


class LanceDBManager:
    def __init__(self, uri: str = LANCEDB_URI):
        self.uri = uri
        self.db = None

    async def connect(self):
        """Connects to the LanceDB database."""
        if self.db is None:
            self.db = await lancedb.connect_async(self.uri)
            print(f"Connected to LanceDB at {self.uri}")

    async def close(self):
        """Closes the LanceDB connection."""
        if self.db:
            print("LanceDB connection implicitly managed.")
            self.db = None

    async def get_table(
        self, table_name: str, schema: Optional[pa.Schema] = None
    ) -> Optional[lancedb.table.AsyncTable]:
        """Gets a table, creating it with the schema if it doesn't exist."""
        if not self.db:
            await self.connect()

        try:
            table_names = await self.db.table_names()
            if table_name not in table_names:
                if schema:
                    print(f"Table '{table_name}' not found. Creating with provided schema.")
                    return await self.db.create_table(table_name, schema=schema, mode="create")
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


lancedb_manager = LanceDBManager()


async def get_lancedb_manager():
    if not lancedb_manager.db:
        await lancedb_manager.connect()
    return lancedb_manager

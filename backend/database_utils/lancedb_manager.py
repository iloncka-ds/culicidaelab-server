"""LanceDB Manager Module.

This module provides a high-level interface for managing LanceDB database operations.
It includes schema definitions for various data models and a LanceDBManager class
for handling database connections, table operations, and data management.

The module supports:
- Database connection management with automatic reconnection
- Table creation and retrieval with schema validation
- Data insertion and table management for species, diseases, regions,
  data sources, map layers, and observations
"""

from __future__ import annotations

import lancedb
import pyarrow as pa
from typing import Any, cast
from lancedb import AsyncConnection
from backend.config import settings


SPECIES_SCHEMA = pa.schema(
    [
        pa.field("id", pa.string(), nullable=False),
        pa.field("scientific_name", pa.string()),
        pa.field("image_url", pa.string()),
        pa.field("vector_status", pa.string()),
        # Localized fields
        pa.field("common_name_en", pa.string()),
        pa.field("common_name_ru", pa.string()),
        pa.field("description_en", pa.string()),
        pa.field("description_ru", pa.string()),
        pa.field("key_characteristics_en", pa.list_(pa.string())),
        pa.field("key_characteristics_ru", pa.list_(pa.string())),
        pa.field("habitat_preferences_en", pa.list_(pa.string())),
        pa.field("habitat_preferences_ru", pa.list_(pa.string())),
        # Relational and non-translated fields
        pa.field("geographic_regions", pa.list_(pa.string())),
        pa.field("related_diseases", pa.list_(pa.string())),
        pa.field("related_diseases_info", pa.list_(pa.string())),
    ],
)

DISEASES_SCHEMA = pa.schema(
    [
        pa.field("id", pa.string(), nullable=False),
        pa.field("image_url", pa.string()),
        # Localized fields
        pa.field("name_en", pa.string()),
        pa.field("name_ru", pa.string()),
        pa.field("description_en", pa.string()),
        pa.field("description_ru", pa.string()),
        pa.field("symptoms_en", pa.string()),
        pa.field("symptoms_ru", pa.string()),
        pa.field("treatment_en", pa.string()),
        pa.field("treatment_ru", pa.string()),
        pa.field("prevention_en", pa.string()),
        pa.field("prevention_ru", pa.string()),
        pa.field("prevalence_en", pa.string()),
        pa.field("prevalence_ru", pa.string()),
        # Relational field
        pa.field("vectors", pa.list_(pa.string())),
    ],
)

REGIONS_SCHEMA = pa.schema(
    [
        pa.field("id", pa.string(), nullable=False),
        pa.field("name_en", pa.string()),
        pa.field("name_ru", pa.string()),
    ],
)

DATA_SOURCES_SCHEMA = pa.schema(
    [
        pa.field("id", pa.string(), nullable=False),
        pa.field("name_en", pa.string()),
        pa.field("name_ru", pa.string()),
    ],
)


MAP_LAYERS_SCHEMA = pa.schema(
    [
        pa.field("layer_type", pa.string(), nullable=False),
        pa.field("layer_name", pa.string()),
        pa.field("geojson_data", pa.string(), nullable=False),
        pa.field("contained_species", pa.list_(pa.string())),
    ],
)

OBSERVATIONS_SCHEMA = pa.schema(
    [
        pa.field("type", pa.string()),
        pa.field("id", pa.string(), nullable=False),
        pa.field("species_scientific_name", pa.string()),
        pa.field("observed_at", pa.string()),
        pa.field("count", pa.int32()),
        pa.field("observer_id", pa.string()),
        pa.field("location_accuracy_m", pa.float32()),
        pa.field("notes", pa.string()),
        pa.field("data_source", pa.string()),
        pa.field("image_filename", pa.string()),
        pa.field("model_id", pa.string()),
        pa.field("confidence", pa.float32()),
        pa.field("geometry_type", pa.string()),
        pa.field("coordinates", pa.list_(pa.float32())),
        pa.field("metadata", pa.string()),
    ],
)


class LanceDBManager:
    """A high-level manager for LanceDB database operations.

    This class provides methods for connecting to a LanceDB database,
    managing tables with predefined schemas, and performing CRUD operations.
    It handles connection lifecycle and provides utilities for creating
    and managing vector-enabled tables for species, diseases, and observations.

    Attributes:
        uri: The database URI/path.
        db: The active database connection instance.
    """

    def __init__(self, uri: str = settings.DATABASE_PATH):
        """Initialize the LanceDB manager.

        Args:
            uri: The database URI/path to connect to. Defaults to the
                configured database path from settings.
        """
        self.uri = uri
        self.db: AsyncConnection | None = None

    async def connect(self):
        """Establish a connection to the LanceDB database.

        This method creates an async connection to the database if one
        doesn't already exist. The connection is stored in the db attribute.

        Raises:
            RuntimeError: If connection fails.
        """
        if self.db is None:
            self.db = await lancedb.connect_async(self.uri)
            print(f"Connected to LanceDB at {self.uri}")

    async def close(self):
        """Close the LanceDB database connection.

        This method cleans up the database connection. Note that LanceDB
        connections are typically managed implicitly, so this mainly
        clears the local reference.
        """
        if self.db:
            print("LanceDB connection implicitly managed.")
            self.db = None

    async def get_table(
        self,
        table_name: str,
        schema: pa.Schema | None = None,
    ) -> lancedb.table.AsyncTable | None:
        """Get a table from the database, creating it if it doesn't exist.

        Args:
            table_name: Name of the table to retrieve or create.
            schema: Schema to use when creating the table. If None and
                table doesn't exist, returns None.

        Returns:
            The requested table instance, or None if table doesn't exist
            and no schema was provided for creation.

        Raises:
            RuntimeError: If connection fails.
        """
        if self.db is None:
            await self.connect()
            # After connect(), self.db should not be None
            if self.db is None:
                raise RuntimeError("Failed to connect to LanceDB")

        db = cast(AsyncConnection, self.db)  # Now we know self.db is not None

        try:
            table_names = await db.table_names()
            if table_name not in table_names:
                if schema:
                    print(f"Table '{table_name}' not found. Creating with provided schema.")
                    return await db.create_table(table_name, schema=schema, mode="create")
                print(f"Table '{table_name}' not found and no schema provided for creation.")
                return None
            return await db.open_table(table_name)
        except Exception as e:
            print(f"Error accessing table {table_name}: {e}")
            return None

    async def create_or_overwrite_table(self, table_name: str, data: list[dict[str, Any]], schema: pa.Schema):
        """Create or overwrite a table with the provided data.

        Args:
            table_name: Name of the table to create or overwrite.
            data: List of dictionaries containing the data to insert.
            schema: PyArrow schema defining the table structure.

        Returns:
            The created or overwritten table instance.

        Raises:
            RuntimeError: If connection fails.
            Exception: If table creation fails.
        """
        if self.db is None:
            await self.connect()
            if self.db is None:
                raise RuntimeError("Failed to connect to LanceDB")

        db = cast(AsyncConnection, self.db)
        try:
            print(f"Creating/overwriting table '{table_name}' with {len(data)} records.")
            tbl = await db.create_table(table_name, data=data, schema=schema, mode="overwrite")
            print(f"Table '{table_name}' created/overwritten successfully.")
            return tbl
        except Exception as e:
            print(f"Error creating/overwriting table {table_name}: {e}")
            raise


lancedb_manager = LanceDBManager(settings.DATABASE_PATH)


async def get_lancedb_manager() -> LanceDBManager:
    """Get the global LanceDB manager instance.

    This function returns the singleton LanceDB manager instance,
    ensuring it's connected before returning.

    Returns:
        The connected LanceDB manager instance.
    """
    if lancedb_manager.db is None:
        await lancedb_manager.connect()
    return lancedb_manager

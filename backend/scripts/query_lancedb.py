"""LanceDB querying utilities for Culicidae Lab.

This module provides command-line utilities for querying LanceDB tables
and exporting data as JSON. It allows users to fetch records from specific
tables with optional filtering and limiting.

The main functionality includes:
    - Connecting to a LanceDB instance
    - Querying specific tables
    - Limiting result sets
    - Exporting results as formatted JSON

Example:
    Query observations table with a limit:

        python backend/scripts/query_lancedb.py observations --limit 5

    Get all records from species table:

        python backend/scripts/query_lancedb.py species --limit 0

    Available tables typically include:
        - observations: Field observation data
        - species: Mosquito species information
        - diseases: Disease information
        - regions: Geographic regions
        - data_sources: Data source metadata
"""

import argparse
import asyncio

import json
from typing import Any
from backend.config import settings
from backend.database_utils.lancedb_manager import LanceDBManager


async def fetch_records(table_name: str, limit: int | None = None) -> list[dict[str, Any]]:
    """Fetch records from a LanceDB table.

    Connects to the LanceDB instance and retrieves records from the specified
    table. The function handles database connection, table validation, and
    data conversion to a convenient dictionary format.

    Args:
        table_name: Name of the LanceDB table to query (e.g., 'observations',
            'species', 'diseases').
        limit: Maximum number of records to return. If None, returns all
            records. If 0, also returns all records.

    Returns:
        A list of dictionaries where each dictionary represents a table row
        with column names as keys and values as the corresponding data.

    Raises:
        RuntimeError: If the specified table does not exist in the database.

    Example:
        >>> records = await fetch_records("observations", limit=10)
        >>> print(f"Retrieved {len(records)} observation records")
        >>> for record in records[:3]:
        ...     print(f"Species: {record.get('species_scientific_name')}")
    """
    # Resolve LanceDB directory relative to this script.
    manager = LanceDBManager(uri=settings.DATABASE_PATH)
    await manager.connect()

    table = await manager.get_table(table_name)
    if table is None:
        raise RuntimeError(f"Table '{table_name}' not found in LanceDB at {settings.DATABASE_PATH}.")

    # Convert to PyArrow table then to list of dicts for convenience.
    arrow_table = await table.to_arrow()
    records: list[dict[str, Any]] = arrow_table.to_pylist()
    if limit is not None:
        records = records[:limit]
    await manager.close()
    return records


async def main() -> None:
    """Main entry point for the LanceDB query script.

    Parses command line arguments and executes the table query operation.
    Supports querying any table in the LanceDB instance with optional
    result limiting.

    The script accepts the following arguments:
        table: Name of the table to query (required)
        --limit, -n: Maximum number of records to return (optional)

    Returns:
        None

    Example:
        >>> # Query first 5 records from observations table
        >>> python backend/scripts/query_lancedb.py observations --limit 5
        >>>
        >>> # Get all records from species table
        >>> python backend/scripts/query_lancedb.py species --limit 0
    """
    parser = argparse.ArgumentParser(description="Query a LanceDB table and print its records as JSON.")
    parser.add_argument(
        "table",
        help="Name of the LanceDB table to query (e.g., 'observations').",
    )
    parser.add_argument(
        "--limit",
        "-n",
        type=int,
        default=10,
        help="Maximum number of rows to print (default: 10). Use 0 for all rows.",
    )
    args = parser.parse_args()

    limit = None if args.limit == 0 else args.limit
    records = await fetch_records(args.table, limit=limit)

    print(json.dumps(records, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())

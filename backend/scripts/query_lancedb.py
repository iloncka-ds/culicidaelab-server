import argparse
import asyncio

import json
import os
from typing import Any, List

import pyarrow as pa

from backend.database_utils.lancedb_manager import LanceDBManager


async def fetch_records(table_name: str, limit: int | None = None) -> List[dict[str, Any]]:
    """Connects to LanceDB and fetches records from the specified table.

    Args:
        table_name: Name of the table to query.
        limit: Maximum number of rows to return. ``None`` fetches all rows.

    Returns:
        A list of dictionaries representing table rows.
    """
    # Resolve LanceDB directory relative to this script.
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.abspath(os.path.join(base_dir, "../data"))
    lancedb_dir = os.path.join(data_dir, ".lancedb")

    manager = LanceDBManager(uri=lancedb_dir)
    await manager.connect()

    table = await manager.get_table(table_name)
    if table is None:
        raise RuntimeError(f"Table '{table_name}' not found in LanceDB at {lancedb_dir}.")

    # Convert to PyArrow table then to list of dicts for convenience.
    arrow_table = await table.to_arrow()
    records: list[dict[str, Any]] = arrow_table.to_pylist()
    if limit is not None:
        records = records[:limit]
    await manager.close()
    return records


async def main() -> None:
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

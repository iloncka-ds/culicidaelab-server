"""
Database connection and table management utilities.

This module provides functions for establishing connections to the LanceDB database
and retrieving specific tables. It includes error handling for connection failures
and table access issues.

Example:
    >>> from backend.services.database import get_db, get_table
    >>> db = get_db()
    >>> species_table = get_table(db, "species")
"""

import lancedb
from backend.config import settings
from functools import lru_cache


@lru_cache
def get_db():
    """Establish a connection to the LanceDB database.

    This function creates a cached connection to the LanceDB database using
    the path specified in the application settings. The connection is cached
    to avoid repeated connection overhead.

    Returns:
        lancedb.DBConnection: A connection object to the LanceDB database.

    Raises:
        Exception: If the database connection fails, the original exception
            is re-raised after logging the error.

    Example:
        >>> db_connection = get_db()
        >>> print(f"Connected to: {db_connection}")
    """
    try:
        db = lancedb.connect(settings.DATABASE_PATH)
        print(settings.DATABASE_PATH)
        print(f"DB Connection Success: {settings.DATABASE_PATH}")
        return db
    except Exception as e:
        print(f"Error connecting to LanceDB at {settings.DATABASE_PATH}: {e}")
        raise


def get_table(db: lancedb.DBConnection, table_name: str):
    """Retrieve a specific table from the LanceDB database.

    Opens and returns a reference to the specified table in the database.
    This function validates that the table exists and is accessible.

    Args:
        db (lancedb.DBConnection): The database connection object.
        table_name (str): The name of the table to retrieve.

    Returns:
        lancedb.table.Table: A table object for the specified table name.

    Raises:
        ValueError: If the table is not found or cannot be opened.

    Example:
        >>> db = get_db()
        >>> observations_table = get_table(db, "observations")
        >>> results = observations_table.search().limit(10).to_list()
    """
    try:
        return db.open_table(table_name)
    except Exception as e:
        print(f"Error opening table '{table_name}': {e}")
        raise ValueError(f"Table '{table_name}' not found or error opening.")

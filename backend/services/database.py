import lancedb
from backend.config import settings
from functools import lru_cache


@lru_cache()  # Cache the connection per DB path
def get_db():
    """Connects to the LanceDB database."""
    try:
        db = lancedb.connect(settings.DATABASE_PATH)
        print(settings.DATABASE_PATH)
        print(f"DB Connection Success: {settings.DATABASE_PATH}")
        return db
    except Exception as e:
        print(f"Error connecting to LanceDB at {settings.DATABASE_PATH}: {e}")
        raise


def get_table(db: lancedb.DBConnection, table_name: str):
    """Gets a LanceDB table, raises error if not found."""
    try:
        return db.open_table(table_name)
    except Exception as e:
        # Catching generic Exception as LanceDB errors might vary
        print(f"Error opening table '{table_name}': {e}")
        # You might want to check if the error means "table not found" specifically
        # For now, re-raise or return None/handle appropriately in services
        raise ValueError(f"Table '{table_name}' not found or error opening.")

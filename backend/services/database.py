import lancedb
from backend.config import settings
from functools import lru_cache


@lru_cache()
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
        print(f"Error opening table '{table_name}': {e}")
        raise ValueError(f"Table '{table_name}' not found or error opening.")

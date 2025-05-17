from backend.database_utils.lancedb_manager import get_lancedb_manager, LanceDBManager


async def get_db() -> LanceDBManager:
    return await get_lancedb_manager()

from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "CulicidaeLab API"
    API_V1_STR: str = "/api/v1"  # We'll version our API
    LANCEDB_URI: str = os.environ.get("LANCEDB_URI", ".lancedb")  # Matches manager

    class Config:
        case_sensitive = True


settings = Settings()

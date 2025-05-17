# from pydantic_settings import BaseSettings
# import os


# class Settings(BaseSettings):
#     PROJECT_NAME: str = "CulicidaeLab API"
#     API_V1_STR: str = "/api/v1"  # We'll version our API
#     LANCEDB_URI: str = os.environ.get("LANCEDB_URI", ".lancedb")  # Matches manager

#     class Config:
#         case_sensitive = True


# settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import pathlib


# Go up one level to the 'backend' directory
BACKEND_DIR = pathlib.Path(__file__).parent.resolve()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",  # Load from .env file
        case_sensitive=False,  # Environment variables are case-insensitive
        env_prefix="CULICIDAELAB_",  # Only load env vars starting with CULICIDAE_
        extra="ignore",  # Optionally ignore extra fields if needed, but prefix is usually enough
    )

    APP_NAME: str = "CulicidaeLab API"
    API_V1_STR: str = "/api"
    DATABASE_PATH: str = str(BACKEND_DIR / "data" / ".lancedb")
    print(DATABASE_PATH)
    # CORS settings
    # Allow requests from the default Solara dev server port
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:8765", "http://127.0.0.1:8765"]

settings = Settings()

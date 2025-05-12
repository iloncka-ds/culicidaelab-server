# from pydantic_settings import BaseSettings
# import os


# class Settings(BaseSettings):
#     PROJECT_NAME: str = "CulicidaeLab API"
#     API_V1_STR: str = "/api/v1"  # We'll version our API
#     LANCEDB_URI: str = os.environ.get("LANCEDB_URI", ".lancedb")  # Matches manager

#     class Config:
#         case_sensitive = True


# settings = Settings()

from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    APP_NAME: str = "CulicidaeLab API"
    API_V1_STR: str = "/api"
    DATABASE_PATH: str = "backend/data/.lancedb"  # Relative to backend/ directory

    # CORS settings
    # Allow requests from the default Solara dev server port
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:8765", "http://127.0.0.1:8765"]

    class Config:
        # If you use a .env file in the backend/ directory
        env_file = ".env"
        case_sensitive = True


settings = Settings()

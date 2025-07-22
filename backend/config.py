
from pydantic_settings import BaseSettings, SettingsConfigDict
from culicidaelab import get_settings
from dotenv import load_dotenv
import os
import pathlib


load_dotenv()
BACKEND_DIR = pathlib.Path(__file__).parent.resolve()

def get_predictor_model_path():
    settings = get_settings()
    model_path = settings.get_model_weights_path("segmenter")

    return model_path

def get_predictor_settings():
    return get_settings()

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_prefix="CULICIDAELAB_",
        extra="ignore",

    )

    APP_NAME: str = "CulicidaeLab API"
    API_V1_STR: str = "/api"
    DATABASE_PATH: str = os.environ.get("CULICIDAELAB_DATABASE_PATH", ".lancedb")

    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:8765", "http://127.0.0.1:8765"]

    @property
    def classifier_settings(self):
        """Returns the fully initialized settings object from the culicidaelab library."""
        return get_predictor_settings()

    @property
    def classifier_model_path(self) -> str:
        """Returns the path to the classifier model weights."""
        return get_predictor_model_path()

settings = AppSettings()

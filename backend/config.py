
from pydantic_settings import BaseSettings, SettingsConfigDict
from culicidaelab import get_settings

import pathlib


BACKEND_DIR = pathlib.Path(__file__).parent.resolve()

def get_predictor_settings():
    settings = get_settings()
    classifier_conf = settings.get_config("predictors.classifier")
    return classifier_conf
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_prefix="CULICIDAELAB_",
        extra="ignore",
    )

    APP_NAME: str = "CulicidaeLab API"
    API_V1_STR: str = "/api"
    DATABASE_PATH: str = str(BACKEND_DIR / "data" / ".lancedb")
    print(DATABASE_PATH)
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:8765", "http://127.0.0.1:8765"]
    CLASSIFIER_CONFIG: dict = get_predictor_settings()
settings = Settings()

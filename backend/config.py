"""Configuration module for CulicidaeLab API backend.

This module handles application settings, configuration management, and provides
access to model paths and predictor settings for the CulicidaeLab API server.
It uses Pydantic settings for configuration management with environment variable
support and provides centralized access to application-wide settings.

The module includes:
- Application settings (AppSettings class)
- Model path resolution functions
- Environment-based configuration loading

Example:
    >>> from backend.config import settings, get_predictor_model_path
    >>> model_path = get_predictor_model_path()
    >>> app_name = settings.APP_NAME
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from culicidaelab import get_settings
from dotenv import load_dotenv
import os
import pathlib


load_dotenv()
BACKEND_DIR = pathlib.Path(__file__).parent.resolve()


def get_predictor_model_path():
    """Retrieves the path to the predictor model weights.

    This function loads the application settings and extracts the path
    to the segmenter model weights used for species prediction.

    Returns:
        str: Full path to the predictor model weights file.

    Example:
        >>> model_path = get_predictor_model_path()
        >>> print(f"Model located at: {model_path}")
        Model located at: /path/to/models/segmenter_weights.pt
    """
    settings = get_settings()
    model_path = settings.get_model_weights_path("segmenter")

    return model_path


def get_predictor_settings():
    """Retrieves the complete predictor settings from culicidaelab library.

    Returns the fully initialized settings object containing all configuration
    parameters for the culicidaelab prediction models and processing pipeline.

    Returns:
        Settings: Complete settings object with model configuration,
            processing parameters, and prediction settings.

    Example:
        >>> predictor_config = get_predictor_settings()
        >>> threshold = predictor_config.get_confidence_threshold()
    """
    return get_settings()


class AppSettings(BaseSettings):
    """Application settings configuration for CulicidaeLab API backend.

    This class defines all configuration parameters for the CulicidaeLab API server,
    using Pydantic BaseSettings for environment variable support and validation.
    Settings can be overridden via environment variables with the CULICIDAELAB_ prefix.

    Attributes:
        APP_NAME (str): Name of the application displayed in API documentation.
        API_V1_STR (str): Base path prefix for API version 1 endpoints.
        DATABASE_PATH (str): File system path to the LanceDB database directory.
        SAVE_PREDICTED_IMAGES (str | bool): Whether to save predicted images to disk.
        BACKEND_CORS_ORIGINS (list[str]): List of allowed CORS origins for frontend access.

    Example:
        >>> settings = AppSettings()
        >>> print(f"App name: {settings.APP_NAME}")
        App name: CulicidaeLab API
        >>> print(f"Database path: {settings.DATABASE_PATH}")
        Database path: .lancedb
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_prefix="CULICIDAELAB_",
        extra="ignore",
    )

    APP_NAME: str = "CulicidaeLab API"
    API_V1_STR: str = "/api"
    DATABASE_PATH: str = os.environ.get("CULICIDAELAB_DATABASE_PATH", ".lancedb")
    SAVE_PREDICTED_IMAGES: str | bool = os.environ.get("CULICIDAELAB_SAVE_PREDICTED_IMAGES", False)

    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:8765", "http://127.0.0.1:8765"]

    @property
    def classifier_settings(self):
        """Returns the fully initialized settings object from the culicidaelab library.

        This property provides access to the complete predictor configuration including
        model parameters, processing settings, and prediction thresholds.

        Returns:
            Settings: Complete settings object with all culicidaelab configuration.

        Example:
            >>> settings = AppSettings()
            >>> predictor_config = settings.classifier_settings
            >>> threshold = predictor_config.get_confidence_threshold()
        """
        return get_predictor_settings()

    @property
    def classifier_model_path(self) -> str:
        """Returns the path to the classifier model weights.

        This property retrieves the file system path to the trained model weights
        used for species prediction and classification tasks.

        Returns:
            str: Full path to the predictor model weights file.

        Example:
            >>> settings = AppSettings()
            >>> model_path = settings.classifier_model_path
            >>> print(f"Model location: {model_path}")
        """
        return get_predictor_model_path()


settings = AppSettings()

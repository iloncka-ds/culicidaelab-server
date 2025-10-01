"""
Machine learning prediction service for mosquito species identification.

This module provides functionality for predicting mosquito species from images
using a trained MosquitoClassifier model. It handles model loading, image processing,
and prediction with confidence scoring and species identification.

Example:
    >>> from backend.services.prediction_service import prediction_service
    >>> result, error = await prediction_service.predict_species(image_data, "mosquito.jpg")
    >>> if result:
    ...     print(f"Predicted species: {result.scientific_name}")
"""

from __future__ import annotations

import asyncio
import io
from datetime import datetime
from pathlib import Path

import aiofiles
import numpy as np
from PIL import Image
from backend.schemas.prediction_schemas import PredictionResult
from backend.config import settings as app_settings
from culicidaelab import MosquitoClassifier, get_settings


class PredictionService:
    """Service for mosquito species prediction using the MosquitoClassifier.

    This class manages the machine learning model lifecycle, including loading,
    prediction, and image saving functionality. It provides both synchronous
    and asynchronous methods for species identification from images.

    Attributes:
        model: The loaded MosquitoClassifier model instance.
        model_loaded (bool): Whether the model has been successfully loaded.
        lib_settings: Configuration settings from the culicidaelab library.
        save_predicted_images_enabled (bool): Whether to save predicted images.

    Example:
        >>> service = PredictionService()
        >>> await service.load_model()
        >>> result, error = await service.predict_species(image_data, "test.jpg")
    """

    def __init__(self):
        """Initialize the PredictionService with default configuration.

        Sets up the service with model loading state, library settings,
        and image saving configuration from application settings.

        Example:
            >>> service = PredictionService()
            >>> print(service.save_predicted_images_enabled)
        """
        self.model = None
        self.model_loaded = False
        self.lib_settings = get_settings()
        self.save_predicted_images_enabled = app_settings.SAVE_PREDICTED_IMAGES

    async def load_model(self):
        """Load the mosquito classifier model if not already loaded.

        This method loads the MosquitoClassifier model from the culicidaelab library.
        The model is cached after the first load to avoid repeated loading overhead.
        Model architecture and ID information is extracted for logging purposes.

        Raises:
            Exception: If model loading fails, the original exception is re-raised
                after setting model_loaded to False.

        Example:
            >>> service = PredictionService()
            >>> await service.load_model()
            >>> print(f"Model loaded: {service.model_loaded}")
        """
        if self.model_loaded:
            return self.model

        try:
            self.model = MosquitoClassifier(self.lib_settings, load_model=True)
            self.model_loaded = True
            self.model_arch = self.lib_settings.get_config("predictors.classifier").model_arch
            self.model_id = self.lib_settings.get_config("predictors.classifier").filename.split(".")[0]

        except Exception as e:
            self.model_loaded = False
            print(f"Error loading model: {type(e).__name__} - {str(e)}")
            raise

    async def save_predicted_image(self, image_data: bytes, filename: str, quiet: bool = True):
        """Asynchronously save the predicted image in multiple sizes.

        This method saves the original image along with resized versions (224x224
        and 100x100) to the static images directory. Failures are handled silently
        to not disrupt the prediction flow unless quiet mode is disabled.

        Args:
            image_data (bytes): The raw image data to save.
            filename (str): The filename to use for the saved images.
            quiet (bool, optional): If False, exceptions will be raised instead
                of being handled silently. Defaults to True.

        Raises:
            Exception: If quiet=False and an error occurs during image saving,
                the original exception is re-raised.

        Example:
            >>> service = PredictionService()
            >>> await service.save_predicted_image(image_bytes, "mosquito_001.jpg")
        """
        try:
            base_path = Path("backend/static/images/predicted")
            original_path = base_path / "original"
            size_224_path = base_path / "224x224"
            size_100_path = base_path / "100x100"

            # Create directories asynchronously if they don't exist
            await asyncio.gather(
                asyncio.to_thread(lambda p: p.mkdir(parents=True, exist_ok=True), original_path),
                asyncio.to_thread(lambda p: p.mkdir(parents=True, exist_ok=True), size_224_path),
                asyncio.to_thread(lambda p: p.mkdir(parents=True, exist_ok=True), size_100_path),
            )

            image = Image.open(io.BytesIO(image_data))
            image_format = image.format or "JPEG"

            # --- Save original image ---
            original_file_path = original_path / filename
            async with aiofiles.open(original_file_path, "wb") as f:
                await f.write(image_data)

            # --- Resize and save 224x224 version ---
            image.thumbnail((224, 224))
            buffer_224 = io.BytesIO()
            image.save(buffer_224, format=image_format)
            async with aiofiles.open(size_224_path / filename, "wb") as f:
                await f.write(buffer_224.getvalue())

            # --- Resize and save 100x100 version ---
            image.thumbnail((100, 100))
            buffer_100 = io.BytesIO()
            image.save(buffer_100, format=image_format)
            async with aiofiles.open(size_100_path / filename, "wb") as f:
                await f.write(buffer_100.getvalue())

        except Exception as e:
            print(f"Error saving predicted image '{filename}': {type(e).__name__} - {str(e)}")
            if not quiet:
                raise

    async def predict_species(
        self,
        image_data: bytes,
        filename: str,
    ) -> tuple[PredictionResult | None, str | None]:
        """Predict mosquito species from image data.

        This method processes the provided image data using the loaded ML model
        to identify the mosquito species with confidence scores. It optionally
        saves the image if the feature flag is enabled.

        Args:
            image_data (bytes): The raw image data in bytes format (e.g., JPEG, PNG).
            filename (str): The original filename of the image for logging purposes.

        Returns:
            tuple[PredictionResult | None, str | None]: A tuple containing:
                - PredictionResult: The prediction result with species name,
                  confidence scores, and metadata. None if prediction fails.
                - str | None: Error message if prediction fails, None if successful.

        Example:
            >>> service = PredictionService()
            >>> await service.load_model()
            >>> with open("mosquito.jpg", "rb") as f:
            ...     image_data = f.read()
            >>> result, error = await service.predict_species(image_data, "mosquito.jpg")
            >>> if result:
            ...     print(f"Predicted: {result.scientific_name} ({result.confidence:.2%})")
        """
        image_url_species = None
        try:
            if not self.model_loaded:
                try:
                    await self.load_model()
                except Exception as e:
                    error_msg = f"Error loading model: {type(e).__name__} - {str(e)}"
                    return None, error_msg

            image = Image.open(io.BytesIO(image_data)).convert("RGB")
            image_np = np.array(image)

            predictions = self.model.predict(image_np)
            top_species, top_confidence = predictions[0]
            species_id = top_species.replace(" ", "_").lower()
            unique_id = f"{hash(top_species) % 10000:04d}"
            date_str = datetime.now().strftime("%d%m%Y")
            result_id = f"{species_id}_{unique_id}_{date_str}"

            if self.save_predicted_images_enabled:
                extension = Path(filename).suffix or ".jpg"
                new_filename = f"{result_id}{extension}"
                asyncio.create_task(self.save_predicted_image(image_data, new_filename))
                image_url_species = f"/static/images/predicted/224x224/{new_filename}"
            else:
                print("[SERVICE] Feature flag 'SAVE_PREDICTED_IMAGES' is False. Skipping image save.")

            result = PredictionResult(
                scientific_name=top_species,
                probabilities={species: float(conf) for species, conf in predictions[:2]},
                id=species_id,
                model_id=self.model_id,
                confidence=float(top_confidence),
                image_url_species=image_url_species,
            )
            return result, None

        except Exception as e:
            error_msg = f"Error predicting species for file '{filename}': {type(e).__name__} - {str(e)}"

            return None, error_msg


prediction_service = PredictionService()

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
import re
from datetime import datetime
from pathlib import Path

import aiofiles

from PIL import Image
from backend.schemas.prediction_schemas import PredictionResult
from backend.config import settings as app_settings
from culicidaelab.core.settings import get_settings
from culicidaelab.serve import serve


class PredictionService:
    """Service for mosquito species prediction using the CulicidaeLab `serve` API.

    This class provides a high-level interface for species identification from
    images. It is optimized for production use, leveraging an efficient inference
    backend with automatic model caching to ensure low latency.

    Attributes:
        save_predicted_images_enabled (bool): Whether to save predicted images.
        model_id (str): The identifier for the machine learning model being used.

    Example:
        >>> service = PredictionService()
        >>> result, error = await service.predict_species(image_data, "test.jpg")
    """

    def __init__(self):
        """Initialize the PredictionService and retrieve the model configuration.

        Sets up the service based on application settings and fetches the model
        architecture information from the CulicidaeLab library settings to generate
        a descriptive model ID.
        """
        self.save_predicted_images_enabled = app_settings.SAVE_PREDICTED_IMAGES
        self.model_id = self._get_model_id()

    def _get_model_id(self) -> str:
        """Retrieves and formats the model ID from the library's settings.

        This method mirrors the logic from the previous implementation to ensure
        a consistent and descriptive model identifier.

        Returns:
            A sanitized string representing the model architecture.
        """
        try:
            lib_settings = get_settings()
            model_arch = lib_settings.get_config("predictors.classifier").model_arch
            # Sanitize the model architecture string to create a valid ID
            model_id = re.sub(r'[<>:"/\\|?*. ]', "_", model_arch).strip("_")
            return model_id
        except Exception as e:
            print(f"Warning: Could not dynamically determine model ID. Falling back to default. Error: {e}")
            return "classifier_onnx_production"

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
        """Predict mosquito species from image data using the `serve` API.

        This method processes image data using the high-performance `serve`
        function. It translates the library's output into the backend's
        `PredictionResult` schema, including the correct model ID.

        Args:
            image_data (bytes): The raw image data (e.g., JPEG, PNG).
            filename (str): The original filename of the image.

        Returns:
            A tuple containing the `PredictionResult` or None, and an error
            message or None.
        """
        image_url_species = None
        try:
            # The `serve` function is synchronous, so run it in a thread pool
            # to avoid blocking the asyncio event loop.
            predictions = await asyncio.to_thread(
                serve,
                image=image_data,
                predictor_type="classifier",
            )

            top_prediction = predictions.top_prediction()  # type: ignore
            if not top_prediction:
                return None, f"Prediction failed for file '{filename}': Model returned no results."

            top_species = top_prediction.species_name
            top_confidence = top_prediction.confidence
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
                probabilities={p.species_name: float(p.confidence) for p in predictions.predictions[:2]},
                id=species_id,
                model_id=self.model_id,  # Use the dynamically fetched model ID
                confidence=float(top_confidence),
                image_url_species=image_url_species,
            )
            return result, None

        except Exception as e:
            error_msg = f"Error predicting species for file '{filename}': {type(e).__name__} - {str(e)}"
            return None, error_msg


prediction_service = PredictionService()

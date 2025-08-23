from __future__ import annotations

import asyncio
import io
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import aiofiles
import numpy as np
from PIL import Image
import os
import stat
from backend.schemas.prediction_schemas import PredictionResult
from backend.config import settings as app_settings
from culicidaelab import MosquitoClassifier, get_settings


class PredictionService:
    """Service for mosquito species prediction using the MosquitoClassifier."""

    def __init__(self):
        """Initialize the prediction service."""
        self.model = None
        self.model_loaded = False
        self.lib_settings = get_settings()
        self.save_predicted_images_enabled = app_settings.SAVE_PREDICTED_IMAGES

    async def load_model(self):
        """Load the mosquito classifier model if not already loaded."""
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
        """
        Asynchronously save the predicted image in multiple sizes.
        Failures are handled silently to not disrupt the prediction flow.
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
            image_format = image.format or 'JPEG'

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
        self, image_data: bytes, filename: str
    ) -> Tuple[Optional[PredictionResult], Optional[str]]:
        """
        Predict mosquito species from image data.
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
                image_url_species=image_url_species
            )
            return result, None

        except Exception as e:
            error_msg = f"Error predicting species for file '{filename}': {type(e).__name__} - {str(e)}"

            return None, error_msg


prediction_service = PredictionService()

from __future__ import annotations

import re
from backend.config import settings
from culicidaelab import MosquitoClassifier, get_settings
from pydantic import BaseModel
from typing import Dict, Optional, Tuple
from pathlib import Path
from PIL import Image
import io
import numpy as np
from backend.schemas.prediction_schemas import PredictionResult


class PredictionService:
    """Service for mosquito species prediction using the MosquitoClassifier."""

    def __init__(self):
        """Initialize the prediction service."""
        print("\n--- [SERVICE] Initializing PredictionService instance ---")
        self.model = None
        self.model_loaded = False
        self.settings = get_settings()

    async def load_model(self):
        """Load the mosquito classifier model if not already loaded."""
        print("[SERVICE] Attempting to load model...")
        if self.model_loaded:
            print("[SERVICE] Model is already loaded. Skipping.")
            return self.model

        try:
            print("[SERVICE] Model not loaded. Initializing MosquitoClassifier...")
            self.model = MosquitoClassifier(self.settings, load_model=True)
            self.model_loaded = True
            self.model_arch = self.settings.get_config("predictors.classifier").model_arch
            self.model_id = self.settings.get_config("predictors.classifier").filename.split(".")[0]
            print(
                f"[SERVICE] Mosquito classifier model loaded successfully. Arch: '{self.model_arch}', ID: '{self.model_id}'"
            )
        except Exception as e:
            print(f"[SERVICE] CRITICAL ERROR during model loading: {type(e).__name__} - {e}")
            self.model_loaded = False
            # Re-raise the exception to be handled by the caller
            raise

    async def predict_species(
        self, image_data: bytes, filename: str
    ) -> Tuple[Optional[PredictionResult], Optional[str]]:
        """
        Predict mosquito species from image data.
        """
        print("\n--- [SERVICE] predict_species called ---")
        try:
            # --- MODEL LOADING ---
            if not self.model_loaded:
                print("[SERVICE] Model not loaded, calling load_model()...")
                try:
                    await self.load_model()
                except Exception as e:
                    print(f"[SERVICE] ERROR: Could not load model, falling back to mock prediction. Reason: {e}")
                    return await self._mock_prediction()
            else:
                print("[SERVICE] Model already loaded, proceeding with prediction.")


            print("[SERVICE] Opening image data from bytes using PIL...")
            image = Image.open(io.BytesIO(image_data)).convert("RGB")
            print("[SERVICE] Image opened and converted to RGB. Converting to NumPy array...")
            image_np = np.array(image)
            print(f"[SERVICE] Image converted to NumPy array with shape: {image_np.shape}")

            # --- PREDICTION ---
            print("[SERVICE] Calling self.model.predict()...")
            # The model's predict() method might also have internal print statements
            predictions = self.model.predict(image_np)
            print(
                f"[SERVICE] Model prediction received. Type: {type(predictions)}, Content: {predictions[0]}"
            )

            # --- RESULT PROCESSING ---
            print("[SERVICE] Processing prediction results...")
            top_species, top_confidence = predictions[0]
            result = PredictionResult(
                scientific_name=top_species,
                probabilities={species: float(conf) for species, conf in predictions[:2]},
                id=f"species_{hash(top_species) % 10000:04d}",
                model_id=self.model_id,
                confidence=float(top_confidence),
                image_url_species=f"https://via.placeholder.com/300x200.png?text={top_species.replace(' ', '+')}",
            )
            print(f"[SERVICE] Prediction successful. Returning result for '{result.scientific_name}'.")
            return result, None

        except Exception as e:
            # --- ERROR HANDLING ---
            # This is a critical catch-all for any unexpected errors during the process
            error_msg = f"Error predicting species for file '{filename}': {type(e).__name__} - {str(e)}"
            print(f"[SERVICE] CRITICAL ERROR in predict_species: {error_msg}")
            # Returning the error message to the router
            return None, error_msg

    async def _mock_prediction(self) -> Tuple[PredictionResult, None]:
        """
        Generate mock prediction when the model is unavailable.
        """
        print("\n--- [SERVICE] Using MOCK prediction service ---")
        result = PredictionResult(
            scientific_name="Aedes fictus",
            probabilities={"Aedes fictus": 0.95, "Culex pipiens": 0.05},
            id="species_mock_001",
            model_id="model_v1_mock",
            confidence=0.95,
            image_url_species="https://via.placeholder.com/300x200.png?text=Aedes+fictus",
        )
        print("[SERVICE] Mock prediction generated successfully.")
        return result, None


# Initialize the service instance at the end of the module
prediction_service = PredictionService()

from __future__ import annotations


from backend.config import settings
from culicidaelab import MosquitoClassifier

from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from PIL import Image
import io
import numpy as np

class PredictionResult(BaseModel):
    """Model for prediction results."""

    scientific_name: str
    probabilities: Dict[str, float]
    id: str
    model_id: str
    confidence: float
    image_url_species: Optional[str] = None


class PredictionService:
    """Service for mosquito species prediction using the MosquitoClassifier."""

    def __init__(self):
        """Initialize the prediction service."""
        self.model = None
        self.model_loaded = False
        self.model_path = Path(settings.CLASSIFIER_MODEL_PATH) if hasattr(settings, "CLASSIFIER_MODEL_PATH") else None
        self.config_manager = None

    async def load_model(self):
        """Load the mosquito classifier model if not already loaded."""
        if self.model_loaded:
            return self.model

        try:
            self.model = MosquitoClassifier(settings, load_model=True)
            self.model_loaded = True
            print(f"Mosquito classifier model loaded successfully from {self.model_path}")
        except Exception as e:
            print(f"Error loading mosquito classifier model: {e}")
            self.model_loaded = False
        #     from culicidaelab.core.config_manager import ConfigManager
        #     from culicidaelab.classifier.mosquito_classifier import MosquitoClassifier

        #     config_path = Path(settings.CLASSIFIER_CONFIG_PATH) if hasattr(settings, "CLASSIFIER_CONFIG_PATH") else None
        #     if not config_path or not config_path.exists():
        #         raise FileNotFoundError(f"Classifier config not found at {config_path}")

        #     self.config_manager = ConfigManager(config_path)
        #     self.model = MosquitoClassifier(
        #         model_path=self.model_path, config_manager=self.config_manager, load_model=True
        #     )
        #     self.model_loaded = True
        #     print(f"Mosquito classifier model loaded successfully from {self.model_path}")
        # except Exception as e:
        #     print(f"Error loading mosquito classifier model: {e}")
        #     self.model_loaded = False

    async def predict_species(
        self, image_data: bytes, filename: str
    ) -> Tuple[Optional[PredictionResult], Optional[str]]:
        """
        Predict mosquito species from image data.

        Args:
            image_data: Binary image data
            filename: Original filename of the uploaded image

        Returns:
            Tuple containing (prediction_result, error_message)
            If successful, error_message will be None
            If failed, prediction_result will be None and error_message will contain the error
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            image_np = np.array(image)

            if not self.model_loaded:
                try:
                    await self.load_model()
                except Exception as e:
                    print(f"Could not load model, falling back to mock prediction: {e}")
                    return await self._mock_prediction(filename)

            if self.model_loaded:
                predictions = self.model.predict(image_np)

                top_species, top_confidence = predictions[0]
                result = PredictionResult(
                    scientific_name=top_species,
                    probabilities={species: float(conf) for species, conf in predictions},
                    id=f"species_{hash(top_species) % 10000:04d}",
                    model_id=f"model_{self.model.arch}",
                    confidence=float(top_confidence),
                    image_url_species=f"https://via.placeholder.com/300x200.png?text={top_species.replace(' ', '+')}",
                )
                return result, None
            else:
                return await self._mock_prediction(filename)

        except Exception as e:
            error_msg = f"Error predicting species: {str(e)}"
            print(error_msg)
            return None, error_msg

    async def _mock_prediction(self, filename: str) -> Tuple[PredictionResult, None]:
        """
        Generate mock prediction when the model is unavailable.
        This ensures the frontend can still function for testing.
        """
        print("Using mock prediction service")

        result = PredictionResult(
            scientific_name="Aedes fictus",
            probabilities={"Aedes fictus": 0.95, "Culex pipiens": 0.05},
            id="species_mock_001",
            model_id="model_v1_mock",
            confidence=0.95,
            image_url_species="https://via.placeholder.com/300x200.png?text=Aedes+fictus",
        )

        return result, None


prediction_service = PredictionService()

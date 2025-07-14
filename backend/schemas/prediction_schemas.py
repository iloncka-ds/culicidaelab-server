from __future__ import annotations

from pydantic import BaseModel
from typing import Dict, Optional


class PredictionResult(BaseModel):
    """Model for prediction results."""
    id: str
    scientific_name: str
    probabilities: Dict[str, float]
    model_id: str
    confidence: float
    image_url_species: Optional[str] = None

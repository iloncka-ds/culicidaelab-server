from __future__ import annotations

from pydantic import BaseModel


class PredictionResult(BaseModel):
    """Model for prediction results."""

    id: str
    scientific_name: str
    probabilities: dict[str, float]
    model_id: str
    confidence: float
    image_url_species: str | None = None

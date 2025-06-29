"""
Configuration and fixtures for pytest.
"""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from backend.main import app


@pytest.fixture(scope="session")
def client():
    """Create a test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_image_data():
    """Create a mock image file in memory."""
    from PIL import Image
    import io

    img = Image.new('RGB', (10, 10), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()


@pytest.fixture
def mock_prediction_result():
    """Create a mock prediction result."""
    from backend.services.prediction_service import PredictionResult

    return PredictionResult(
        scientific_name="Aedes aegypti",
        probabilities={"Aedes aegypti": 0.95, "Culex pipiens": 0.05},
        id="species_1234",
        model_id="model_v1",
        confidence=0.95,
        image_url_species="https://example.com/aedes_aegypti.jpg"
    )


@pytest.fixture
def mock_species_detail():
    """Create a mock species detail object."""
    from backend.models import SpeciesDetail

    return SpeciesDetail(
        id="aedes_aegypti",
        scientific_name="Aedes aegypti",
        common_names=["Yellow fever mosquito"],
        family="Culicidae",
        genus="Aedes",
        is_disease_vector=True,
        diseases=["dengue", "zika", "chikungunya", "yellow_fever"],
        distribution=["tropical", "subtropical"],
        habitat=["urban", "domestic"],
        description="Aedes aegypti is a known vector of several viruses...",
        image_url="https://example.com/aedes_aegypti.jpg"
    )

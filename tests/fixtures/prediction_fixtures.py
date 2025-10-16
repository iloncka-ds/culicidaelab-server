"""
Fixtures for prediction service testing.

This module provides specialized fixtures for testing the PredictionService,
including mock prediction results, service instances, and external dependencies.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from backend.schemas.prediction_schemas import PredictionResult


@pytest.fixture
def mock_prediction_result_high_confidence():
    """Create a high-confidence prediction result."""
    return PredictionResult(
        id="aedes_aegypti",
        scientific_name="Aedes aegypti",
        probabilities={"Aedes aegypti": 0.95, "Culex pipiens": 0.05},
        model_id="classifier_onnx_production",
        confidence=0.95,
        image_url_species="/static/images/predicted/224x224/aedes_aegypti_1234_15062023.jpg",
    )


@pytest.fixture
def mock_prediction_result_low_confidence():
    """Create a low-confidence prediction result."""
    return PredictionResult(
        id="unknown_species",
        scientific_name="Culex pipiens",
        probabilities={"Culex pipiens": 0.55, "Aedes aegypti": 0.45},
        model_id="classifier_onnx_production",
        confidence=0.55,
        image_url_species="/static/images/predicted/224x224/culex_pipiens_5678_15062023.jpg",
    )


@pytest.fixture
def mock_culicidaelab_predictions():
    """Create mock predictions from culicidaelab library."""
    mock_prediction_1 = MagicMock()
    mock_prediction_1.species_name = "Aedes aegypti"
    mock_prediction_1.confidence = 0.95
    
    mock_prediction_2 = MagicMock()
    mock_prediction_2.species_name = "Culex pipiens"
    mock_prediction_2.confidence = 0.05
    
    mock_predictions = MagicMock()
    mock_predictions.top_prediction.return_value = mock_prediction_1
    mock_predictions.predictions = [mock_prediction_1, mock_prediction_2]
    
    return mock_predictions


@pytest.fixture
def mock_culicidaelab_serve(mock_culicidaelab_predictions):
    """Mock the culicidaelab serve function."""
    with patch('backend.services.prediction_service.serve') as mock_serve:
        mock_serve.return_value = mock_culicidaelab_predictions
        yield mock_serve


@pytest.fixture
def mock_culicidaelab_settings():
    """Mock the culicidaelab settings."""
    mock_settings = MagicMock()
    mock_config = MagicMock()
    mock_config.model_arch = "efficientnet_b0_onnx"
    mock_settings.get_config.return_value = mock_config
    
    with patch('backend.services.prediction_service.get_settings') as mock_get_settings:
        mock_get_settings.return_value = mock_settings
        yield mock_settings


@pytest.fixture
def mock_prediction_service_with_save_enabled():
    """Create a PredictionService mock with image saving enabled."""
    mock_service = MagicMock()
    mock_service.save_predicted_images_enabled = True
    mock_service.model_id = "classifier_onnx_production"
    mock_service._get_model_id.return_value = "classifier_onnx_production"
    
    # Mock async methods
    mock_service.predict_species = AsyncMock()
    mock_service.save_predicted_image = AsyncMock()
    
    return mock_service


@pytest.fixture
def mock_prediction_service_with_save_disabled():
    """Create a PredictionService mock with image saving disabled."""
    mock_service = MagicMock()
    mock_service.save_predicted_images_enabled = False
    mock_service.model_id = "classifier_onnx_production"
    mock_service._get_model_id.return_value = "classifier_onnx_production"
    
    # Mock async methods
    mock_service.predict_species = AsyncMock()
    mock_service.save_predicted_image = AsyncMock()
    
    return mock_service


@pytest.fixture
def mock_pil_image():
    """Create a mock PIL Image object."""
    mock_image = MagicMock()
    mock_image.format = "JPEG"
    mock_image.thumbnail = MagicMock()
    mock_image.save = MagicMock()
    
    with patch('backend.services.prediction_service.Image') as mock_image_class:
        mock_image_class.open.return_value = mock_image
        yield mock_image


@pytest.fixture
def mock_aiofiles():
    """Mock aiofiles for async file operations."""
    mock_file = AsyncMock()
    mock_file.__aenter__ = AsyncMock(return_value=mock_file)
    mock_file.__aexit__ = AsyncMock(return_value=None)
    mock_file.write = AsyncMock()
    
    with patch('backend.services.prediction_service.aiofiles.open') as mock_open:
        mock_open.return_value = mock_file
        yield mock_open


@pytest.fixture
def mock_datetime_now():
    """Mock datetime.now() for consistent timestamps."""
    fixed_datetime = datetime(2023, 6, 15, 10, 30, 0)
    with patch('backend.services.prediction_service.datetime') as mock_dt:
        mock_dt.now.return_value = fixed_datetime
        yield mock_dt


@pytest.fixture
def prediction_error_scenarios():
    """Provide various error scenarios for prediction testing."""
    return {
        "no_predictions": {
            "error": "Model returned no results",
            "mock_predictions": MagicMock(top_prediction=MagicMock(return_value=None))
        },
        "serve_exception": {
            "error": "culicidaelab serve failed",
            "exception": RuntimeError("Model loading failed")
        },
        "image_processing_error": {
            "error": "Image processing failed",
            "exception": ValueError("Invalid image format")
        }
    }
"""Tests for prediction API endpoints.

This module contains tests for the prediction router endpoints,
focusing on image upload and species prediction functionality.
"""

import io
from unittest.mock import AsyncMock, patch
from PIL import Image
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from backend.services.prediction_service import PredictionResult


class TestPredictionAPI:
    """Test cases for prediction API endpoints."""

    def test_predict_species_success(self, client: TestClient, mock_image_data: bytes):
        """Test successful species prediction with valid image."""
        # Mock the prediction service response
        mock_result = PredictionResult(
            id="aedes_aegypti",
            scientific_name="Aedes aegypti",
            probabilities={"aedes_aegypti": 0.95, "culex_pipiens": 0.05},
            model_id="mosquito_classifier_v1",
            confidence=0.95,
            image_url_species="http://testserver/static/predictions/test_image.jpg"
        )

        with patch("backend.routers.prediction.prediction_service") as mock_service:
            mock_service.predict_species = AsyncMock(return_value=(mock_result, None))
            
            response = client.post(
                "/api/predict",
                files={"file": ("test_image.jpg", mock_image_data, "image/jpeg")}
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "aedes_aegypti"
        assert data["scientific_name"] == "Aedes aegypti"
        assert data["confidence"] == 0.95
        assert data["model_id"] == "mosquito_classifier_v1"
        assert "probabilities" in data

    def test_predict_species_invalid_file_type(self, client: TestClient):
        """Test prediction with invalid file type."""
        text_content = b"This is not an image"
        
        response = client.post(
            "/api/predict",
            files={"file": ("test.txt", text_content, "text/plain")}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "File must be an image" in response.json()["detail"]

    def test_predict_species_empty_file(self, client: TestClient):
        """Test prediction with empty file."""
        response = client.post(
            "/api/predict",
            files={"file": ("empty.jpg", b"", "image/jpeg")}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Empty file" in response.json()["detail"]

    def test_predict_species_no_content_type(self, client: TestClient, mock_image_data: bytes):
        """Test prediction with missing content type."""
        # TestClient automatically sets content type based on file extension
        # So we need to test with a file that doesn't have an image extension
        response = client.post(
            "/api/predict",
            files={"file": ("test_file", mock_image_data, None)}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "File must be an image" in response.json()["detail"]

    def test_predict_species_service_error(self, client: TestClient, mock_image_data: bytes):
        """Test prediction when service returns an error."""
        with patch("backend.routers.prediction.prediction_service") as mock_service:
            mock_service.predict_species = AsyncMock(return_value=(None, "Model loading failed"))
            
            response = client.post(
                "/api/predict",
                files={"file": ("test_image.jpg", mock_image_data, "image/jpeg")}
            )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Prediction failed: Model loading failed" in response.json()["detail"]

    def test_predict_species_service_no_result(self, client: TestClient, mock_image_data: bytes):
        """Test prediction when service returns no result and no error."""
        with patch("backend.routers.prediction.prediction_service") as mock_service:
            mock_service.predict_species = AsyncMock(return_value=(None, None))
            
            response = client.post(
                "/api/predict",
                files={"file": ("test_image.jpg", mock_image_data, "image/jpeg")}
            )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Prediction failed with no specific error" in response.json()["detail"]

    def test_predict_species_service_exception(self, client: TestClient, mock_image_data: bytes):
        """Test prediction when service raises an exception."""
        with patch("backend.routers.prediction.prediction_service") as mock_service:
            mock_service.predict_species = AsyncMock(side_effect=Exception("Unexpected error"))
            
            response = client.post(
                "/api/predict",
                files={"file": ("test_image.jpg", mock_image_data, "image/jpeg")}
            )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Prediction failed: Unexpected error" in response.json()["detail"]

    def test_predict_species_large_image(self, client: TestClient):
        """Test prediction with a larger, more realistic image."""
        # Create a larger test image
        img = Image.new("RGB", (224, 224), color="green")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="JPEG")
        large_image_data = img_byte_arr.getvalue()

        mock_result = PredictionResult(
            id="culex_pipiens",
            scientific_name="Culex pipiens",
            probabilities={"culex_pipiens": 0.87, "aedes_aegypti": 0.13},
            model_id="mosquito_classifier_v1",
            confidence=0.87,
            image_url_species=None
        )

        with patch("backend.routers.prediction.prediction_service") as mock_service:
            mock_service.predict_species = AsyncMock(return_value=(mock_result, None))
            
            response = client.post(
                "/api/predict",
                files={"file": ("large_image.jpg", large_image_data, "image/jpeg")}
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["scientific_name"] == "Culex pipiens"
        assert data["confidence"] == 0.87

    def test_predict_species_png_format(self, client: TestClient):
        """Test prediction with PNG format image."""
        # Create PNG image
        img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="PNG")
        png_image_data = img_byte_arr.getvalue()

        mock_result = PredictionResult(
            id="anopheles_gambiae",
            scientific_name="Anopheles gambiae",
            probabilities={"anopheles_gambiae": 0.92, "aedes_aegypti": 0.08},
            model_id="mosquito_classifier_v1",
            confidence=0.92,
            image_url_species="http://testserver/static/predictions/test.png"
        )

        with patch("backend.routers.prediction.prediction_service") as mock_service:
            mock_service.predict_species = AsyncMock(return_value=(mock_result, None))
            
            response = client.post(
                "/api/predict",
                files={"file": ("test_image.png", png_image_data, "image/png")}
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["scientific_name"] == "Anopheles gambiae"
        assert data["image_url_species"] == "http://testserver/static/predictions/test.png"
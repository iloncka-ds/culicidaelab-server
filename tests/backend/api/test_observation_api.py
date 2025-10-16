"""Tests for observation API endpoints.

This module contains tests for the observation router endpoints,
focusing on CRUD operations and geospatial query functionality.
"""

from unittest.mock import AsyncMock, patch
from uuid import uuid4
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from backend.schemas.observation_schemas import (
    Observation, 
    ObservationListResponse, 
    Location
)


class TestObservationAPI:
    """Test cases for observation API endpoints."""

    def test_create_observation_success(self, client: TestClient):
        """Test successful creation of observation."""
        observation_data = {
            "type": "Feature",
            "species_scientific_name": "Aedes aegypti",
            "count": 5,
            "location": {"lat": 40.7128, "lng": -74.0060},
            "observed_at": "2024-01-15T10:30:00Z",
            "notes": "Found near standing water",
            "user_id": "test_user_123",
            "location_accuracy_m": 10,
            "data_source": "field_observation"
        }

        # Create expected response observation
        expected_observation = Observation(
            id=uuid4(),
            **observation_data,
            image_filename="test_image.jpg",
            model_id="mosquito_classifier_v1",
            confidence=0.95,
            metadata={"temperature": 25, "humidity": 80}
        )

        with patch("backend.routers.observation.get_observation_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.create_observation = AsyncMock(return_value=expected_observation)
            mock_get_service.return_value = mock_service
            
            response = client.post("/api/observations", json=observation_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["species_scientific_name"] == "Aedes aegypti"
        assert data["count"] == 5
        assert data["location"]["lat"] == 40.7128
        assert data["location"]["lng"] == -74.0060
        assert data["notes"] == "Found near standing water"
        assert data["user_id"] == "test_user_123"

    def test_create_observation_auto_generate_user_id(self, client: TestClient):
        """Test observation creation with auto-generated user_id."""
        observation_data = {
            "type": "Feature",
            "species_scientific_name": "Culex pipiens",
            "count": 3,
            "location": {"lat": 51.5074, "lng": -0.1278},
            "observed_at": "2024-01-15T14:30:00Z",
            "notes": "Urban environment"
            # No user_id provided
        }

        expected_observation = Observation(
            id=uuid4(),
            user_id="auto_generated_uuid",
            **observation_data
        )

        with patch("backend.routers.observation.get_observation_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.create_observation = AsyncMock(return_value=expected_observation)
            mock_get_service.return_value = mock_service
            
            response = client.post("/api/observations", json=observation_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "user_id" in data
        assert data["user_id"] is not None

    def test_create_observation_validation_error(self, client: TestClient):
        """Test observation creation with invalid data."""
        invalid_observation_data = {
            "type": "Feature",
            "species_scientific_name": "Aedes aegypti",
            "count": -1,  # Invalid: count must be positive
            "location": {"lat": 40.7128, "lng": -74.0060},
            "observed_at": "2024-01-15T10:30:00Z"
        }

        response = client.post("/api/observations", json=invalid_observation_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert response.json()["detail"][0]["type"] == "greater_than"

    def test_create_observation_missing_required_fields(self, client: TestClient):
        """Test observation creation with missing required fields."""
        incomplete_observation_data = {
            "type": "Feature",
            "species_scientific_name": "Aedes aegypti",
            # Missing count, location, observed_at
        }

        response = client.post("/api/observations", json=incomplete_observation_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_observation_service_error(self, client: TestClient):
        """Test observation creation when service raises an error."""
        observation_data = {
            "type": "Feature",
            "species_scientific_name": "Aedes aegypti",
            "count": 5,
            "location": {"lat": 40.7128, "lng": -74.0060},
            "observed_at": "2024-01-15T10:30:00Z"
        }

        with patch("backend.routers.observation.get_observation_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.create_observation = AsyncMock(side_effect=Exception("Database connection failed"))
            mock_get_service.return_value = mock_service
            
            response = client.post("/api/observations", json=observation_data)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to create observation" in response.json()["detail"]

    def test_get_observations_success(self, client: TestClient):
        """Test successful retrieval of observations."""
        mock_observations = [
            Observation(
                id=uuid4(),
                type="Feature",
                species_scientific_name="Aedes aegypti",
                count=5,
                location=Location(lat=40.7128, lng=-74.0060),
                observed_at="2024-01-15T10:30:00Z",
                notes="Urban area",
                user_id="user_123"
            ),
            Observation(
                id=uuid4(),
                type="Feature",
                species_scientific_name="Culex pipiens",
                count=3,
                location=Location(lat=40.7589, lng=-73.9851),
                observed_at="2024-01-15T11:00:00Z",
                notes="Near water source",
                user_id="user_123"
            )
        ]

        mock_response = ObservationListResponse(
            count=2,
            observations=mock_observations
        )

        with patch("backend.routers.observation.get_observation_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_observations = AsyncMock(return_value=mock_response)
            mock_get_service.return_value = mock_service
            
            response = client.get("/api/observations?limit=100&offset=0&user_id=user_123")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 2
        assert len(data["observations"]) == 2
        assert data["observations"][0]["species_scientific_name"] == "Aedes aegypti"
        assert data["observations"][1]["species_scientific_name"] == "Culex pipiens"

    def test_get_observations_with_species_filter(self, client: TestClient):
        """Test observation retrieval filtered by species."""
        mock_observations = [
            Observation(
                id=uuid4(),
                type="Feature",
                species_scientific_name="Aedes aegypti",
                count=5,
                location=Location(lat=40.7128, lng=-74.0060),
                observed_at="2024-01-15T10:30:00Z",
                user_id="user_123"
            )
        ]

        mock_response = ObservationListResponse(
            count=1,
            observations=mock_observations
        )

        with patch("backend.routers.observation.get_observation_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_observations = AsyncMock(return_value=mock_response)
            mock_get_service.return_value = mock_service
            
            response = client.get("/api/observations?species_id=aedes_aegypti&user_id=user_123")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 1
        assert data["observations"][0]["species_scientific_name"] == "Aedes aegypti"
        
        # Verify service was called with correct parameters
        mock_service.get_observations.assert_called_once()
        call_args = mock_service.get_observations.call_args
        assert call_args[1]["species_id"] == "aedes_aegypti"
        assert call_args[1]["user_id"] == "user_123"

    def test_get_observations_pagination(self, client: TestClient):
        """Test observation retrieval with pagination parameters."""
        mock_response = ObservationListResponse(count=0, observations=[])

        with patch("backend.routers.observation.get_observation_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_observations = AsyncMock(return_value=mock_response)
            mock_get_service.return_value = mock_service
            
            response = client.get("/api/observations?limit=50&offset=25&user_id=test_user")

        assert response.status_code == status.HTTP_200_OK
        
        # Verify service was called with correct pagination
        mock_service.get_observations.assert_called_once()
        call_args = mock_service.get_observations.call_args
        assert call_args[1]["limit"] == 50
        assert call_args[1]["offset"] == 25

    def test_get_observations_limit_capping(self, client: TestClient):
        """Test that observation limit is capped at maximum value."""
        mock_response = ObservationListResponse(count=0, observations=[])

        with patch("backend.routers.observation.get_observation_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_observations = AsyncMock(return_value=mock_response)
            mock_get_service.return_value = mock_service
            
            # Request limit higher than maximum (1000)
            response = client.get("/api/observations?limit=2000&user_id=test_user")

        assert response.status_code == status.HTTP_200_OK
        
        # Verify limit was capped at 1000
        mock_service.get_observations.assert_called_once()
        call_args = mock_service.get_observations.call_args
        assert call_args[1]["limit"] == 1000

    def test_get_observations_negative_offset_correction(self, client: TestClient):
        """Test that negative offset is corrected to 0."""
        mock_response = ObservationListResponse(count=0, observations=[])

        with patch("backend.routers.observation.get_observation_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_observations = AsyncMock(return_value=mock_response)
            mock_get_service.return_value = mock_service
            
            response = client.get("/api/observations?offset=-10&user_id=test_user")

        assert response.status_code == status.HTTP_200_OK
        
        # Verify offset was corrected to 0
        mock_service.get_observations.assert_called_once()
        call_args = mock_service.get_observations.call_args
        assert call_args[1]["offset"] == 0

    def test_get_observations_service_error(self, client: TestClient):
        """Test observation retrieval when service raises an error."""
        with patch("backend.routers.observation.get_observation_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_observations = AsyncMock(side_effect=Exception("Database query failed"))
            mock_get_service.return_value = mock_service
            
            response = client.get("/api/observations?user_id=test_user")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to retrieve observations" in response.json()["detail"]

    def test_get_observations_empty_result(self, client: TestClient):
        """Test observation retrieval with no results."""
        mock_response = ObservationListResponse(count=0, observations=[])

        with patch("backend.routers.observation.get_observation_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_service.get_observations = AsyncMock(return_value=mock_response)
            mock_get_service.return_value = mock_service
            
            response = client.get("/api/observations?species_id=nonexistent_species&user_id=test_user")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 0
        assert len(data["observations"]) == 0

    def test_create_observation_geospatial_data(self, client: TestClient):
        """Test observation creation with various geospatial coordinates."""
        # Test with coordinates from different regions
        test_locations = [
            {"lat": -33.8688, "lng": 151.2093},  # Sydney, Australia
            {"lat": 55.7558, "lng": 37.6176},    # Moscow, Russia
            {"lat": -1.2921, "lng": 36.8219},    # Nairobi, Kenya
        ]

        for i, location in enumerate(test_locations):
            observation_data = {
                "type": "Feature",
                "species_scientific_name": f"Test species {i}",
                "count": i + 1,
                "location": location,
                "observed_at": "2024-01-15T10:30:00Z",
                "user_id": f"user_{i}"
            }

            expected_observation = Observation(
                id=uuid4(),
                **observation_data
            )

            with patch("backend.routers.observation.get_observation_service") as mock_get_service:
                mock_service = AsyncMock()
                mock_service.create_observation = AsyncMock(return_value=expected_observation)
                mock_get_service.return_value = mock_service
                
                response = client.post("/api/observations", json=observation_data)

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["location"]["lat"] == location["lat"]
            assert data["location"]["lng"] == location["lng"]
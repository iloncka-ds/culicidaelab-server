"""
Fixtures for observation service testing.

This module provides specialized fixtures for testing the ObservationService,
including mock observations, database connections, and service responses.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime

from backend.schemas.observation_schemas import (
    Observation, 
    ObservationBase, 
    ObservationListResponse, 
    Location
)


@pytest.fixture
def mock_location_nyc():
    """Create a mock location for New York City."""
    return Location(lat=40.7128, lng=-74.0060)


@pytest.fixture
def mock_location_london():
    """Create a mock location for London."""
    return Location(lat=51.5074, lng=-0.1278)


@pytest.fixture
def mock_observation_base():
    """Create a basic observation without system fields."""
    return ObservationBase(
        species_scientific_name="Aedes aegypti",
        count=2,
        location=Location(lat=40.7128, lng=-74.0060),
        observed_at="2023-06-15",
        notes="Found in backyard container",
        user_id="test_user_123",
        location_accuracy_m=5,
        data_source="mobile_app",
    )


@pytest.fixture
def mock_observation_complete():
    """Create a complete observation with all fields."""
    return Observation(
        id=uuid4(),
        species_scientific_name="Aedes aegypti",
        count=3,
        location=Location(lat=40.7128, lng=-74.0060),
        observed_at="2023-06-15",
        notes="Multiple specimens found in water container",
        user_id="test_user_123",
        location_accuracy_m=10,
        data_source="mobile_app",
        image_filename="observation_001.jpg",
        model_id="classifier_onnx_production",
        confidence=0.87,
        metadata={"weather": "sunny", "temperature": 25, "humidity": 65},
    )


@pytest.fixture
def mock_observation_culex():
    """Create an observation for Culex pipiens."""
    return Observation(
        id=uuid4(),
        species_scientific_name="Culex pipiens",
        count=1,
        location=Location(lat=51.5074, lng=-0.1278),
        observed_at="2023-06-16",
        notes="Single specimen near pond",
        user_id="test_user_456",
        location_accuracy_m=15,
        data_source="web_app",
        image_filename="observation_002.jpg",
        model_id="classifier_onnx_production",
        confidence=0.72,
        metadata={"weather": "cloudy", "temperature": 18},
    )


@pytest.fixture
def mock_observation_list():
    """Create a list of mock observations."""
    observations = []
    
    # Aedes aegypti observation
    observations.append(Observation(
        id=uuid4(),
        species_scientific_name="Aedes aegypti",
        count=2,
        location=Location(lat=40.7128, lng=-74.0060),
        observed_at="2023-06-15",
        notes="Found in urban area",
        user_id="user_001",
        location_accuracy_m=5,
        data_source="mobile_app",
        image_filename="obs_001.jpg",
        model_id="classifier_onnx_production",
        confidence=0.89,
        metadata={"temperature": 28},
    ))
    
    # Culex pipiens observation
    observations.append(Observation(
        id=uuid4(),
        species_scientific_name="Culex pipiens",
        count=1,
        location=Location(lat=51.5074, lng=-0.1278),
        observed_at="2023-06-16",
        notes="Near water source",
        user_id="user_002",
        location_accuracy_m=10,
        data_source="web_app",
        image_filename="obs_002.jpg",
        model_id="classifier_onnx_production",
        confidence=0.76,
        metadata={"temperature": 20},
    ))
    
    return observations


@pytest.fixture
def mock_observation_list_response(mock_observation_list):
    """Create a mock ObservationListResponse."""
    return ObservationListResponse(
        count=len(mock_observation_list),
        observations=mock_observation_list
    )


@pytest.fixture
def mock_lancedb_observation_table():
    """Create a mock LanceDB table for observations."""
    mock_table = AsyncMock()
    
    # Mock search chain methods
    mock_table.search.return_value = mock_table
    mock_table.where.return_value = mock_table
    mock_table.limit.return_value = mock_table
    mock_table.offset.return_value = mock_table
    mock_table.to_list = AsyncMock(return_value=[])
    mock_table.to_arrow = AsyncMock()
    mock_table.add = AsyncMock()
    
    return mock_table


@pytest.fixture
def mock_observation_db_records():
    """Create mock database records for observations."""
    return [
        {
            "id": "obs_001",
            "species_scientific_name": "Aedes aegypti",
            "observed_at": "2023-06-15",
            "count": 2,
            "observer_id": "user_001",
            "location_accuracy_m": 5,
            "notes": "Found in urban container",
            "data_source": "mobile_app",
            "image_filename": "obs_001.jpg",
            "model_id": "classifier_onnx_production",
            "confidence": 0.89,
            "geometry_type": "Point",
            "coordinates": [40.7128, -74.0060],
            "metadata": '{"weather": "sunny", "temperature": 28}',
        },
        {
            "id": "obs_002",
            "species_scientific_name": "Culex pipiens",
            "observed_at": "2023-06-16",
            "count": 1,
            "observer_id": "user_002",
            "location_accuracy_m": 10,
            "notes": "Near pond area",
            "data_source": "web_app",
            "image_filename": "obs_002.jpg",
            "model_id": "classifier_onnx_production",
            "confidence": 0.76,
            "geometry_type": "Point",
            "coordinates": [51.5074, -0.1278],
            "metadata": '{"weather": "cloudy", "temperature": 20}',
        },
    ]


@pytest.fixture
def mock_lancedb_manager():
    """Create a mock LanceDB manager."""
    mock_manager = AsyncMock()
    mock_db = MagicMock()
    mock_table = AsyncMock()
    
    # Setup table mock
    mock_table.search.return_value = mock_table
    mock_table.where.return_value = mock_table
    mock_table.limit.return_value = mock_table
    mock_table.offset.return_value = mock_table
    mock_table.to_list = AsyncMock(return_value=[])
    mock_table.add = AsyncMock()
    
    mock_db.open_table = AsyncMock(return_value=mock_table)
    mock_manager.db = mock_db
    
    with patch('backend.services.observation_service.get_lancedb_manager') as mock_get_manager:
        mock_get_manager.return_value = mock_manager
        yield mock_manager


@pytest.fixture
def mock_observation_service_initialized():
    """Create a fully initialized ObservationService mock."""
    mock_service = AsyncMock()
    mock_service.table_name = "observations"
    mock_service.db = MagicMock()
    
    # Mock methods
    mock_service.initialize = AsyncMock(return_value=mock_service)
    mock_service.create_observation = AsyncMock()
    mock_service.get_observations = AsyncMock()
    
    return mock_service


@pytest.fixture
def observation_filter_scenarios():
    """Provide various filtering scenarios for observation testing."""
    return {
        "by_user": {
            "user_id": "test_user_123",
            "species_id": None,
            "expected_filter": "observer_id = 'test_user_123'"
        },
        "by_species": {
            "user_id": None,
            "species_id": "Aedes aegypti",
            "expected_filter": "species_scientific_name = 'Aedes aegypti'"
        },
        "by_user_and_species": {
            "user_id": "test_user_123",
            "species_id": "Aedes aegypti",
            "expected_filter": "observer_id = 'test_user_123' AND species_scientific_name = 'Aedes aegypti'"
        },
        "no_filters": {
            "user_id": None,
            "species_id": None,
            "expected_filter": None
        },
        "default_user": {
            "user_id": "default_user_id",
            "species_id": None,
            "expected_filter": None
        }
    }


@pytest.fixture
def observation_error_scenarios():
    """Provide various error scenarios for observation testing."""
    return {
        "database_connection_error": {
            "error": "Database connection failed",
            "exception": ConnectionError("Cannot connect to LanceDB")
        },
        "invalid_observation_data": {
            "error": "Invalid observation data",
            "exception": ValueError("Missing required fields")
        },
        "table_not_found": {
            "error": "Observations table not found",
            "exception": FileNotFoundError("Table 'observations' does not exist")
        },
        "json_decode_error": {
            "error": "Invalid metadata JSON",
            "exception": ValueError("Invalid JSON in metadata field")
        }
    }


@pytest.fixture
def mock_json_operations():
    """Mock JSON operations for metadata handling."""
    with patch('backend.services.observation_service.json') as mock_json:
        mock_json.dumps.return_value = '{"test": "data"}'
        mock_json.loads.return_value = {"test": "data"}
        yield mock_json
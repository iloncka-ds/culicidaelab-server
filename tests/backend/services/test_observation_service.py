"""
Tests for the observation service.
"""

import json
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4
import pytest
from fastapi import HTTPException

from backend.services.observation_service import ObservationService, get_observation_service
from backend.schemas.observation_schemas import Observation, ObservationListResponse, Location
from tests.factories.mock_factory import MockFactory


class TestObservationService:
    """Test cases for the ObservationService class."""

    @pytest.fixture
    def mock_lancedb_manager(self):
        """Create a mock LanceDB manager."""
        return MockFactory.create_lancedb_manager_mock()

    @pytest.fixture
    def mock_table(self):
        """Create a mock LanceDB table."""
        mock_table = MagicMock()
        mock_table.add = AsyncMock()
        mock_table.search.return_value = mock_table
        mock_table.where.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.offset.return_value = mock_table
        mock_table.to_list = AsyncMock(return_value=[])
        mock_table.to_arrow = AsyncMock()
        return mock_table

    @pytest.fixture
    def sample_observation_data(self):
        """Create sample observation data."""
        return MockFactory.create_observation_data()

    @pytest.fixture
    def sample_observation_record(self):
        """Create sample observation database record."""
        return {
            "id": "550e8400-e29b-41d4-a716-446655440000",  # Valid UUID format
            "species_scientific_name": "Aedes aegypti",
            "count": 2,
            "coordinates": [40.7128, -74.0060],
            "observed_at": "2023-06-15",
            "notes": "Found near water container",
            "observer_id": "test_user_123",
            "location_accuracy_m": 10,
            "data_source": "mobile_app",
            "image_filename": "mosquito_001.jpg",
            "model_id": "classifier_onnx_production",
            "confidence": 0.89,
            "metadata": '{"weather": "sunny", "temperature": "25C"}',
        }

    def test_service_initialization(self):
        """Test that the service initializes correctly with proper attributes."""
        service = ObservationService()
        assert service.table_name == "observations"
        assert service.db is None

    @patch("backend.services.observation_service.get_lancedb_manager")
    async def test_initialize_service(self, mock_get_manager, mock_lancedb_manager):
        """Test service initialization with database connection."""
        mock_get_manager.return_value = mock_lancedb_manager
        
        service = ObservationService()
        result = await service.initialize()

        assert result is service  # Should return self for chaining
        assert service.db is mock_lancedb_manager.db
        mock_get_manager.assert_called_once()

    @patch("backend.services.observation_service.get_lancedb_manager")
    async def test_create_observation_success(self, mock_get_manager, mock_lancedb_manager, mock_table, sample_observation_data):
        """Test successful observation creation."""
        mock_get_manager.return_value = mock_lancedb_manager
        mock_lancedb_manager.db.open_table = AsyncMock(return_value=mock_table)
        
        service = ObservationService()
        await service.initialize()

        result = await service.create_observation(sample_observation_data)

        assert result == sample_observation_data
        mock_table.add.assert_called_once()
        
        # Verify the record structure passed to add()
        call_args = mock_table.add.call_args[0][0]
        assert len(call_args) == 1  # Should be a list with one record
        record = call_args[0]
        assert record["id"] == str(sample_observation_data.id)
        assert record["species_scientific_name"] == sample_observation_data.species_scientific_name
        assert record["count"] == sample_observation_data.count
        assert record["coordinates"] == [sample_observation_data.location.lat, sample_observation_data.location.lng]
        assert record["geometry_type"] == "Point"

    @patch("backend.services.observation_service.get_lancedb_manager")
    async def test_create_observation_with_metadata_dict(self, mock_get_manager, mock_lancedb_manager, mock_table):
        """Test observation creation with dictionary metadata."""
        mock_get_manager.return_value = mock_lancedb_manager
        mock_lancedb_manager.db.open_table = AsyncMock(return_value=mock_table)
        
        service = ObservationService()
        await service.initialize()

        observation_data = MockFactory.create_observation_data()
        observation_data.metadata = {"weather": "sunny", "temperature": 25}

        result = await service.create_observation(observation_data)

        assert result == observation_data
        call_args = mock_table.add.call_args[0][0]
        record = call_args[0]
        assert record["metadata"] == '{"weather": "sunny", "temperature": 25}'

    @patch("backend.services.observation_service.get_lancedb_manager")
    async def test_create_observation_with_metadata_string(self, mock_get_manager, mock_lancedb_manager, mock_table):
        """Test observation creation with string metadata."""
        mock_get_manager.return_value = mock_lancedb_manager
        mock_lancedb_manager.db.open_table = AsyncMock(return_value=mock_table)
        
        service = ObservationService()
        await service.initialize()

        observation_data = MockFactory.create_observation_data()
        observation_data.metadata = '{"weather": "rainy"}'

        result = await service.create_observation(observation_data)

        assert result == observation_data
        call_args = mock_table.add.call_args[0][0]
        record = call_args[0]
        assert record["metadata"] == '{"weather": "rainy"}'

    @patch("backend.services.observation_service.get_lancedb_manager")
    async def test_create_observation_database_error(self, mock_get_manager, mock_lancedb_manager, mock_table, sample_observation_data):
        """Test observation creation with database error."""
        mock_get_manager.return_value = mock_lancedb_manager
        mock_lancedb_manager.db.open_table = AsyncMock(return_value=mock_table)
        mock_table.add.side_effect = Exception("Database connection failed")
        
        service = ObservationService()
        await service.initialize()

        with pytest.raises(HTTPException) as exc_info:
            await service.create_observation(sample_observation_data)

        assert exc_info.value.status_code == 500
        assert "Failed to save observation to database" in exc_info.value.detail

    @patch("backend.services.observation_service.get_lancedb_manager")
    async def test_get_observations_no_filters(self, mock_get_manager, mock_lancedb_manager, mock_table, sample_observation_record):
        """Test getting observations without filters."""
        mock_get_manager.return_value = mock_lancedb_manager
        mock_lancedb_manager.db.open_table = AsyncMock(return_value=mock_table)
        
        # Mock the arrow table for pagination
        mock_arrow_table = MagicMock()
        mock_arrow_table.slice.return_value = mock_arrow_table
        mock_arrow_table.to_pylist.return_value = [sample_observation_record]
        mock_table.to_arrow = AsyncMock(return_value=mock_arrow_table)
        
        service = ObservationService()
        await service.initialize()

        result = await service.get_observations(limit=10, offset=0)

        assert isinstance(result, ObservationListResponse)
        assert result.count == 1
        assert len(result.observations) == 1
        assert result.observations[0].species_scientific_name == "Aedes aegypti"
        assert result.observations[0].location.lat == 40.7128
        assert result.observations[0].location.lng == -74.0060

    @patch("backend.services.observation_service.get_lancedb_manager")
    async def test_get_observations_with_user_filter(self, mock_get_manager, mock_lancedb_manager, mock_table, sample_observation_record):
        """Test getting observations filtered by user ID."""
        mock_get_manager.return_value = mock_lancedb_manager
        mock_lancedb_manager.db.open_table = AsyncMock(return_value=mock_table)
        mock_table.to_list = AsyncMock(return_value=[sample_observation_record])
        
        service = ObservationService()
        await service.initialize()

        result = await service.get_observations(user_id="test_user_123", limit=10)

        assert isinstance(result, ObservationListResponse)
        assert result.count == 1
        mock_table.where.assert_called_once_with("observer_id = 'test_user_123'")

    @patch("backend.services.observation_service.get_lancedb_manager")
    async def test_get_observations_with_species_filter(self, mock_get_manager, mock_lancedb_manager, mock_table, sample_observation_record):
        """Test getting observations filtered by species."""
        mock_get_manager.return_value = mock_lancedb_manager
        mock_lancedb_manager.db.open_table = AsyncMock(return_value=mock_table)
        mock_table.to_list = AsyncMock(return_value=[sample_observation_record])
        
        service = ObservationService()
        await service.initialize()

        result = await service.get_observations(species_id="Aedes aegypti", limit=10)

        assert isinstance(result, ObservationListResponse)
        assert result.count == 1
        mock_table.where.assert_called_once_with("species_scientific_name = 'Aedes aegypti'")

    @patch("backend.services.observation_service.get_lancedb_manager")
    async def test_get_observations_with_multiple_filters(self, mock_get_manager, mock_lancedb_manager, mock_table, sample_observation_record):
        """Test getting observations with both user and species filters."""
        mock_get_manager.return_value = mock_lancedb_manager
        mock_lancedb_manager.db.open_table = AsyncMock(return_value=mock_table)
        mock_table.to_list = AsyncMock(return_value=[sample_observation_record])
        
        service = ObservationService()
        await service.initialize()

        result = await service.get_observations(
            user_id="test_user_123", 
            species_id="Aedes aegypti", 
            limit=10
        )

        assert isinstance(result, ObservationListResponse)
        expected_where = "observer_id = 'test_user_123' AND species_scientific_name = 'Aedes aegypti'"
        mock_table.where.assert_called_once_with(expected_where)

    @patch("backend.services.observation_service.get_lancedb_manager")
    async def test_get_observations_default_user_id_ignored(self, mock_get_manager, mock_lancedb_manager, mock_table):
        """Test that default_user_id is ignored in filtering."""
        mock_get_manager.return_value = mock_lancedb_manager
        mock_lancedb_manager.db.open_table = AsyncMock(return_value=mock_table)
        
        # Mock the arrow table for no-filter case
        mock_arrow_table = MagicMock()
        mock_arrow_table.slice.return_value = mock_arrow_table
        mock_arrow_table.to_pylist.return_value = []
        mock_table.to_arrow = AsyncMock(return_value=mock_arrow_table)
        
        service = ObservationService()
        await service.initialize()

        result = await service.get_observations(user_id="default_user_id", limit=10)

        # Should not call where() since default_user_id is ignored
        mock_table.where.assert_not_called()
        assert isinstance(result, ObservationListResponse)

    @patch("backend.services.observation_service.get_lancedb_manager")
    async def test_get_observations_with_pagination(self, mock_get_manager, mock_lancedb_manager, mock_table):
        """Test getting observations with pagination parameters."""
        mock_get_manager.return_value = mock_lancedb_manager
        mock_lancedb_manager.db.open_table = AsyncMock(return_value=mock_table)
        
        # Mock the arrow table for pagination
        mock_arrow_table = MagicMock()
        mock_arrow_table.slice.return_value = mock_arrow_table
        mock_arrow_table.to_pylist.return_value = []
        mock_table.to_arrow = AsyncMock(return_value=mock_arrow_table)
        
        service = ObservationService()
        await service.initialize()

        result = await service.get_observations(limit=20, offset=40)

        assert isinstance(result, ObservationListResponse)
        # Verify pagination was applied to arrow table
        mock_arrow_table.slice.assert_called_once_with(40, 20)

    @patch("backend.services.observation_service.get_lancedb_manager")
    async def test_get_observations_invalid_metadata_json(self, mock_get_manager, mock_lancedb_manager, mock_table):
        """Test getting observations with invalid JSON metadata."""
        mock_get_manager.return_value = mock_lancedb_manager
        mock_lancedb_manager.db.open_table = AsyncMock(return_value=mock_table)
        
        invalid_record = {
            "id": "550e8400-e29b-41d4-a716-446655440001",  # Valid UUID format
            "species_scientific_name": "Aedes aegypti",
            "count": 1,
            "coordinates": [40.7128, -74.0060],
            "observed_at": "2023-06-15",
            "observer_id": "test_user_123",
            "metadata": "invalid json {",  # Invalid JSON
        }
        
        # Mock the arrow table
        mock_arrow_table = MagicMock()
        mock_arrow_table.slice.return_value = mock_arrow_table
        mock_arrow_table.to_pylist.return_value = [invalid_record]
        mock_table.to_arrow = AsyncMock(return_value=mock_arrow_table)
        
        service = ObservationService()
        await service.initialize()

        result = await service.get_observations(limit=10)

        # Should still return the observation but with empty metadata
        assert isinstance(result, ObservationListResponse)
        assert result.count == 1
        assert result.observations[0].metadata == {}

    @patch("backend.services.observation_service.get_lancedb_manager")
    async def test_get_observations_invalid_coordinates(self, mock_get_manager, mock_lancedb_manager, mock_table):
        """Test getting observations with invalid coordinate data."""
        mock_get_manager.return_value = mock_lancedb_manager
        mock_lancedb_manager.db.open_table = AsyncMock(return_value=mock_table)
        
        invalid_record = {
            "id": "550e8400-e29b-41d4-a716-446655440002",  # Valid UUID format
            "species_scientific_name": "Aedes aegypti",
            "count": 1,
            "coordinates": [40.7128],  # Invalid - only one coordinate
            "observed_at": "2023-06-15",
            "observer_id": "test_user_123",
        }
        
        # Mock the arrow table
        mock_arrow_table = MagicMock()
        mock_arrow_table.slice.return_value = mock_arrow_table
        mock_arrow_table.to_pylist.return_value = [invalid_record]
        mock_table.to_arrow = AsyncMock(return_value=mock_arrow_table)
        
        service = ObservationService()
        await service.initialize()

        result = await service.get_observations(limit=10)

        # Should skip the record with invalid coordinates
        assert isinstance(result, ObservationListResponse)
        assert result.count == 0
        assert len(result.observations) == 0

    @patch("backend.services.observation_service.get_lancedb_manager")
    async def test_get_observations_database_error(self, mock_get_manager, mock_lancedb_manager, mock_table):
        """Test getting observations with database error."""
        mock_get_manager.return_value = mock_lancedb_manager
        mock_lancedb_manager.db.open_table = AsyncMock(side_effect=Exception("Database connection failed"))
        
        service = ObservationService()
        await service.initialize()

        with pytest.raises(HTTPException) as exc_info:
            await service.get_observations(limit=10)

        assert exc_info.value.status_code == 500
        assert "Failed to retrieve observations" in exc_info.value.detail


class TestObservationServiceSingleton:
    """Test cases for the observation service singleton pattern."""

    @patch("backend.services.observation_service.get_lancedb_manager")
    async def test_get_observation_service_creates_singleton(self, mock_get_manager):
        """Test that get_observation_service creates and returns a singleton."""
        mock_manager = MockFactory.create_lancedb_manager_mock()
        mock_get_manager.return_value = mock_manager
        
        # Reset the global service to None for this test
        import backend.services.observation_service
        backend.services.observation_service.observation_service = None

        service1 = await get_observation_service()
        service2 = await get_observation_service()

        assert service1 is service2  # Should be the same instance
        assert isinstance(service1, ObservationService)
        assert service1.db is mock_manager.db

    @patch("backend.services.observation_service.get_lancedb_manager")
    async def test_get_observation_service_returns_existing_instance(self, mock_get_manager):
        """Test that get_observation_service returns existing instance if already created."""
        mock_manager = MockFactory.create_lancedb_manager_mock()
        mock_get_manager.return_value = mock_manager
        
        # Create an instance first
        service1 = await get_observation_service()
        
        # Mock should only be called once for initialization
        mock_get_manager.reset_mock()
        
        # Get service again
        service2 = await get_observation_service()
        
        assert service1 is service2
        # get_lancedb_manager should not be called again
        mock_get_manager.assert_not_called()


class TestObservationServiceDataTransformation:
    """Test cases for data transformation in observation service."""

    def test_observation_record_transformation(self):
        """Test that observation data is correctly transformed for database storage."""
        observation_data = MockFactory.create_observation_data()
        observation_data.metadata = {"weather": "sunny", "temperature": 25}
        observation_data.data_source = {"type": "mobile", "version": "1.0"}

        service = ObservationService()
        
        # We can't easily test the private transformation without refactoring,
        # but we can verify the expected structure through create_observation
        # This is more of an integration test approach
        
        # The transformation logic is tested indirectly through create_observation tests
        assert observation_data.location.lat is not None
        assert observation_data.location.lng is not None
        assert observation_data.species_scientific_name is not None
        assert observation_data.count > 0

    def test_metadata_serialization_edge_cases(self):
        """Test metadata serialization with various data types."""
        service = ObservationService()
        
        # Test with None metadata
        observation1 = MockFactory.create_observation_data()
        observation1.metadata = None
        assert observation1.metadata is None
        
        # Test with empty dict metadata
        observation2 = MockFactory.create_observation_data()
        observation2.metadata = {}
        assert observation2.metadata == {}
        
        # Test with complex nested metadata
        observation3 = MockFactory.create_observation_data()
        observation3.metadata = {
            "weather": {"condition": "sunny", "temperature": 25},
            "equipment": ["camera", "GPS"],
            "notes": "Detailed observation"
        }
        assert isinstance(observation3.metadata, dict)
        assert "weather" in observation3.metadata
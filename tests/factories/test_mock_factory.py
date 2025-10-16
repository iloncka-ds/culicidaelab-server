"""
Test file to validate the MockFactory functionality.

This test file demonstrates the usage of the MockFactory and validates
that all mock creation methods work correctly with current schemas.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock

from tests.factories.mock_factory import MockFactory
from backend.schemas.prediction_schemas import PredictionResult
from backend.schemas.species_schemas import SpeciesBase, SpeciesDetail
from backend.schemas.observation_schemas import Observation, ObservationListResponse
from backend.schemas.diseases_schemas import Disease
from backend.schemas.filter_schemas import FilterOptions
from backend.schemas.geo_schemas import GeoJSONFeatureCollection


class TestMockFactory:
    """Test class for validating MockFactory functionality."""

    def test_create_prediction_service_mock(self):
        """Test that prediction service mock is created correctly."""
        mock_service = MockFactory.create_prediction_service_mock()
        
        assert isinstance(mock_service, MagicMock)
        assert mock_service.save_predicted_images_enabled is True
        assert mock_service.model_id == "classifier_onnx_production"
        assert isinstance(mock_service.save_predicted_image, AsyncMock)
        assert isinstance(mock_service.predict_species, AsyncMock)

    def test_create_species_service_mock(self):
        """Test that species service mock is created correctly."""
        mock_service = MockFactory.create_species_service_mock()
        
        assert isinstance(mock_service, MagicMock)
        assert hasattr(mock_service, 'get_all_species')
        assert hasattr(mock_service, 'get_species_by_id')
        assert hasattr(mock_service, 'get_vector_species')

    def test_create_observation_service_mock(self):
        """Test that observation service mock is created correctly."""
        mock_service = MockFactory.create_observation_service_mock()
        
        assert isinstance(mock_service, MagicMock)
        assert mock_service.table_name == "observations"
        assert isinstance(mock_service.initialize, AsyncMock)
        assert isinstance(mock_service.create_observation, AsyncMock)
        assert isinstance(mock_service.get_observations, AsyncMock)

    def test_create_disease_service_mock(self):
        """Test that disease service mock is created correctly."""
        mock_service = MockFactory.create_disease_service_mock()
        
        assert isinstance(mock_service, MagicMock)
        assert hasattr(mock_service, 'get_all_diseases')
        assert hasattr(mock_service, 'get_disease_by_id')
        assert hasattr(mock_service, 'get_diseases_by_vector')

    def test_create_geo_service_mock(self):
        """Test that geo service mock is created correctly."""
        mock_service = MockFactory.create_geo_service_mock()
        
        assert isinstance(mock_service, MagicMock)
        assert hasattr(mock_service, 'get_geo_layer')
        assert hasattr(mock_service, 'is_valid_date_str')

    def test_create_filter_service_mock(self):
        """Test that filter service mock is created correctly."""
        mock_service = MockFactory.create_filter_service_mock()
        
        assert isinstance(mock_service, MagicMock)
        assert hasattr(mock_service, 'get_filter_options')

    def test_create_prediction_result_data(self):
        """Test that prediction result data conforms to schema."""
        data = MockFactory.create_prediction_result_data()
        
        assert isinstance(data, PredictionResult)
        assert data.scientific_name == "Aedes aegypti"
        assert 0 <= data.confidence <= 1
        assert data.model_id == "classifier_onnx_production"
        assert isinstance(data.probabilities, dict)

    def test_create_species_base_data(self):
        """Test that species base data conforms to schema."""
        data = MockFactory.create_species_base_data()
        
        assert isinstance(data, SpeciesBase)
        assert data.id == "aedes_aegypti"
        assert data.scientific_name == "Aedes aegypti"
        assert data.common_name == "Yellow fever mosquito"

    def test_create_species_detail_data(self):
        """Test that species detail data conforms to schema."""
        data = MockFactory.create_species_detail_data()
        
        assert isinstance(data, SpeciesDetail)
        assert data.id == "aedes_aegypti"
        assert data.scientific_name == "Aedes aegypti"
        assert isinstance(data.key_characteristics, list)
        assert isinstance(data.geographic_regions, list)
        assert isinstance(data.related_diseases, list)

    def test_create_observation_data(self):
        """Test that observation data conforms to schema."""
        data = MockFactory.create_observation_data()
        
        assert isinstance(data, Observation)
        assert data.species_scientific_name == "Aedes aegypti"
        assert data.count > 0
        assert data.location is not None
        assert data.user_id == "test_user_123"

    def test_create_observation_list_response_data(self):
        """Test that observation list response data conforms to schema."""
        data = MockFactory.create_observation_list_response_data(count=3)
        
        assert isinstance(data, ObservationListResponse)
        assert data.count == 3
        assert len(data.observations) == 3
        assert all(isinstance(obs, Observation) for obs in data.observations)

    def test_create_disease_data(self):
        """Test that disease data conforms to schema."""
        data = MockFactory.create_disease_data()
        
        assert isinstance(data, Disease)
        assert data.id == "dengue"
        assert data.name == "Dengue Fever"
        assert isinstance(data.vectors, list)

    def test_create_filter_options_data(self):
        """Test that filter options data conforms to schema."""
        data = MockFactory.create_filter_options_data()
        
        assert isinstance(data, FilterOptions)
        assert isinstance(data.species, list)
        assert isinstance(data.regions, list)
        assert isinstance(data.data_sources, list)

    def test_create_geojson_feature_collection_data(self):
        """Test that GeoJSON feature collection data conforms to schema."""
        data = MockFactory.create_geojson_feature_collection_data(feature_count=2)
        
        assert isinstance(data, GeoJSONFeatureCollection)
        assert data.type == "FeatureCollection"
        assert len(data.features) == 2

    def test_create_lancedb_connection_mock(self):
        """Test that LanceDB connection mock is created correctly."""
        mock_db = MockFactory.create_lancedb_connection_mock()
        
        assert isinstance(mock_db, MagicMock)
        assert isinstance(mock_db.open_table, AsyncMock)

    def test_create_fastapi_request_mock(self):
        """Test that FastAPI request mock is created correctly."""
        mock_request = MockFactory.create_fastapi_request_mock()
        
        assert isinstance(mock_request, MagicMock)
        assert str(mock_request.base_url) == "http://localhost:8000/"

    def test_validate_mock_data_against_schema(self):
        """Test the schema validation utility method."""
        data = MockFactory.create_species_base_data()
        
        # Should validate successfully
        assert MockFactory.validate_mock_data_against_schema(data, SpeciesBase) is True
        
        # Should fail validation with wrong schema
        assert MockFactory.validate_mock_data_against_schema(data, Disease) is False

    def test_custom_parameters(self):
        """Test that mock factories accept custom parameters."""
        # Test custom prediction result
        custom_prediction = MockFactory.create_prediction_result_data(
            scientific_name="Culex pipiens",
            confidence=0.75
        )
        assert custom_prediction.scientific_name == "Culex pipiens"
        assert custom_prediction.confidence == 0.75
        
        # Test custom species data
        custom_species = MockFactory.create_species_base_data(
            species_id="culex_pipiens",
            scientific_name="Culex pipiens",
            common_name="Common house mosquito"
        )
        assert custom_species.id == "culex_pipiens"
        assert custom_species.scientific_name == "Culex pipiens"
        assert custom_species.common_name == "Common house mosquito"
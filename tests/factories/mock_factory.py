"""
Centralized mock factory system for test modernization.

This module provides reusable mock creation methods for all service classes
and schema-based mock data generators using current Pydantic models.
It ensures consistent mocking patterns across all test files.

Example:
    >>> from tests.factories.mock_factory import MockFactory
    >>> prediction_service_mock = MockFactory.create_prediction_service_mock()
    >>> species_data = MockFactory.create_species_detail_data()
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from backend.schemas.prediction_schemas import PredictionResult
from backend.schemas.species_schemas import SpeciesBase, SpeciesDetail
from backend.schemas.observation_schemas import Observation, Location, ObservationListResponse
from backend.schemas.diseases_schemas import Disease
from backend.schemas.filter_schemas import FilterOptions, RegionFilter, DataSourceFilter
from backend.schemas.geo_schemas import GeoJSONFeature, GeoJSONFeatureCollection, GeoJSONGeometry


class MockFactory:
    """Factory class for creating standardized mocks and test data.
    
    This class provides static methods for creating mock objects for all
    service classes and generating realistic test data based on current
    Pydantic schemas.
    """

    # Service Mock Factories
    
    @staticmethod
    def create_prediction_service_mock() -> MagicMock:
        """Create a mock PredictionService with realistic method signatures.
        
        Returns:
            MagicMock: A configured mock PredictionService with proper async methods
                and realistic return values.
        """
        mock_service = MagicMock()
        mock_service.save_predicted_images_enabled = True
        mock_service.model_id = "classifier_onnx_production"
        
        # Mock async methods
        mock_service.save_predicted_image = AsyncMock()
        mock_service.predict_species = AsyncMock()
        
        # Configure predict_species to return realistic data
        mock_result = MockFactory.create_prediction_result_data()
        mock_service.predict_species.return_value = (mock_result, None)
        
        return mock_service

    @staticmethod
    def create_species_service_mock() -> MagicMock:
        """Create a mock for species service functions.
        
        Returns:
            MagicMock: A configured mock with species service functions.
        """
        mock_service = MagicMock()
        
        # Mock service functions
        mock_service.get_all_species = MagicMock()
        mock_service.get_species_by_id = MagicMock()
        mock_service.get_vector_species = MagicMock()
        
        # Configure return values
        mock_service.get_all_species.return_value = [MockFactory.create_species_base_data()]
        mock_service.get_species_by_id.return_value = MockFactory.create_species_detail_data()
        mock_service.get_vector_species.return_value = [MockFactory.create_species_base_data()]
        
        return mock_service

    @staticmethod
    def create_observation_service_mock() -> MagicMock:
        """Create a mock ObservationService with async methods.
        
        Returns:
            MagicMock: A configured mock ObservationService with proper async methods.
        """
        mock_service = MagicMock()
        mock_service.table_name = "observations"
        mock_service.db = MagicMock()
        
        # Mock async methods
        mock_service.initialize = AsyncMock()
        mock_service.create_observation = AsyncMock()
        mock_service.get_observations = AsyncMock()
        
        # Configure return values
        mock_observation = MockFactory.create_observation_data()
        mock_service.create_observation.return_value = mock_observation
        
        mock_response = MockFactory.create_observation_list_response_data()
        mock_service.get_observations.return_value = mock_response
        
        # Make initialize return self for chaining
        mock_service.initialize.return_value = mock_service
        
        return mock_service

    @staticmethod
    def create_disease_service_mock() -> MagicMock:
        """Create a mock for disease service functions.
        
        Returns:
            MagicMock: A configured mock with disease service functions.
        """
        mock_service = MagicMock()
        
        # Mock service functions
        mock_service.get_all_diseases = MagicMock()
        mock_service.get_disease_by_id = MagicMock()
        mock_service.get_diseases_by_vector = MagicMock()
        
        # Configure return values
        mock_service.get_all_diseases.return_value = [MockFactory.create_disease_data()]
        mock_service.get_disease_by_id.return_value = MockFactory.create_disease_data()
        mock_service.get_diseases_by_vector.return_value = [MockFactory.create_disease_data()]
        
        return mock_service

    @staticmethod
    def create_geo_service_mock() -> MagicMock:
        """Create a mock for geo service functions.
        
        Returns:
            MagicMock: A configured mock with geo service functions.
        """
        mock_service = MagicMock()
        
        # Mock service functions
        mock_service.get_geo_layer = MagicMock()
        mock_service.is_valid_date_str = MagicMock()
        
        # Configure return values
        mock_service.get_geo_layer.return_value = MockFactory.create_geojson_feature_collection_data()
        mock_service.is_valid_date_str.return_value = True
        
        return mock_service

    @staticmethod
    def create_filter_service_mock() -> MagicMock:
        """Create a mock for filter service functions.
        
        Returns:
            MagicMock: A configured mock with filter service functions.
        """
        mock_service = MagicMock()
        
        # Mock service functions
        mock_service.get_filter_options = MagicMock()
        
        # Configure return values
        mock_service.get_filter_options.return_value = MockFactory.create_filter_options_data()
        
        return mock_service

    @staticmethod
    def create_cache_service_mock() -> MagicMock:
        """Create a mock for cache service.
        
        Returns:
            MagicMock: A configured mock cache service.
        """
        mock_service = MagicMock()
        
        # Mock common cache methods
        mock_service.get = MagicMock()
        mock_service.set = MagicMock()
        mock_service.delete = MagicMock()
        mock_service.clear = MagicMock()
        
        return mock_service

    # Database Mock Factories
    
    @staticmethod
    def create_lancedb_connection_mock() -> MagicMock:
        """Create a mock LanceDB connection.
        
        Returns:
            MagicMock: A configured mock LanceDB connection.
        """
        mock_db = MagicMock()
        mock_table = MagicMock()
        
        # Mock table operations
        mock_table.search.return_value = mock_table
        mock_table.where.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.offset.return_value = mock_table
        mock_table.to_list.return_value = []
        mock_table.add = AsyncMock()
        mock_table.to_arrow.return_value = MagicMock()
        
        # Mock database operations
        mock_db.open_table = AsyncMock(return_value=mock_table)
        
        return mock_db

    @staticmethod
    def create_lancedb_manager_mock() -> MagicMock:
        """Create a mock LanceDB manager.
        
        Returns:
            MagicMock: A configured mock LanceDB manager.
        """
        mock_manager = MagicMock()
        mock_manager.db = MockFactory.create_lancedb_connection_mock()
        mock_manager.get_table = AsyncMock()
        
        return mock_manager

    # Schema-Based Mock Data Generators
    
    @staticmethod
    def create_prediction_result_data(
        scientific_name: str = "Aedes aegypti",
        confidence: float = 0.95,
        model_id: str = "classifier_onnx_production"
    ) -> PredictionResult:
        """Generate realistic PredictionResult test data.
        
        Args:
            scientific_name: The predicted species name
            confidence: Prediction confidence score
            model_id: Model identifier
            
        Returns:
            PredictionResult: A realistic prediction result object
        """
        species_id = scientific_name.replace(" ", "_").lower()
        unique_id = f"{hash(scientific_name) % 10000:04d}"
        date_str = datetime.now().strftime("%d%m%Y")
        result_id = f"{species_id}_{unique_id}_{date_str}"
        
        return PredictionResult(
            id=species_id,
            scientific_name=scientific_name,
            probabilities={
                scientific_name: confidence,
                "Culex pipiens": 1.0 - confidence
            },
            model_id=model_id,
            confidence=confidence,
            image_url_species=f"/static/images/predicted/224x224/{result_id}.jpg"
        )

    @staticmethod
    def create_species_base_data(
        species_id: str = "aedes_aegypti",
        scientific_name: str = "Aedes aegypti",
        common_name: str = "Yellow fever mosquito"
    ) -> SpeciesBase:
        """Generate realistic SpeciesBase test data.
        
        Args:
            species_id: Unique species identifier
            scientific_name: Scientific name of the species
            common_name: Common name of the species
            
        Returns:
            SpeciesBase: A realistic species base object
        """
        return SpeciesBase(
            id=species_id,
            scientific_name=scientific_name,
            common_name=common_name,
            vector_status="Primary Vector",
            image_url=f"/static/images/species/{species_id}/thumbnail.jpg"
        )

    @staticmethod
    def create_species_detail_data(
        species_id: str = "aedes_aegypti",
        scientific_name: str = "Aedes aegypti",
        common_name: str = "Yellow fever mosquito"
    ) -> SpeciesDetail:
        """Generate realistic SpeciesDetail test data.
        
        Args:
            species_id: Unique species identifier
            scientific_name: Scientific name of the species
            common_name: Common name of the species
            
        Returns:
            SpeciesDetail: A realistic detailed species object
        """
        return SpeciesDetail(
            id=species_id,
            scientific_name=scientific_name,
            common_name=common_name,
            vector_status="Primary Vector",
            image_url=f"/static/images/species/{species_id}/detail.jpg",
            description="A small, dark mosquito with distinctive white markings on its legs and body.",
            key_characteristics=[
                "White bands on legs",
                "Lyre-shaped markings on thorax",
                "Small size (4-7mm)"
            ],
            geographic_regions=["Tropical", "Subtropical", "Urban areas"],
            related_diseases=["dengue", "zika", "yellow_fever", "chikungunya"],
            habitat_preferences=["Container breeding", "Urban environments", "Standing water"]
        )

    @staticmethod
    def create_location_data(lat: float = 40.7128, lng: float = -74.0060) -> Location:
        """Generate realistic Location test data.
        
        Args:
            lat: Latitude coordinate
            lng: Longitude coordinate
            
        Returns:
            Location: A realistic location object
        """
        return Location(lat=lat, lng=lng)

    @staticmethod
    def create_observation_data(
        species_name: str = "Aedes aegypti",
        user_id: str = "test_user_123"
    ) -> Observation:
        """Generate realistic Observation test data.
        
        Args:
            species_name: Scientific name of observed species
            user_id: ID of the observing user
            
        Returns:
            Observation: A realistic observation object
        """
        return Observation(
            id=uuid4(),
            species_scientific_name=species_name,
            count=1,
            location=MockFactory.create_location_data(),
            observed_at="2023-06-15",
            notes="Observed near standing water container",
            user_id=user_id,
            location_accuracy_m=10,
            data_source="citizen_science",
            image_filename="mosquito_obs_001.jpg",
            model_id="classifier_onnx_production",
            confidence=0.89,
            metadata={"weather": "sunny", "temperature": "25C"}
        )

    @staticmethod
    def create_observation_list_response_data(count: int = 1) -> ObservationListResponse:
        """Generate realistic ObservationListResponse test data.
        
        Args:
            count: Number of observations to include
            
        Returns:
            ObservationListResponse: A realistic observation list response
        """
        observations = [MockFactory.create_observation_data() for _ in range(count)]
        return ObservationListResponse(
            count=count,
            observations=observations
        )

    @staticmethod
    def create_disease_data(
        disease_id: str = "dengue",
        name: str = "Dengue Fever"
    ) -> Disease:
        """Generate realistic Disease test data.
        
        Args:
            disease_id: Unique disease identifier
            name: Disease name
            
        Returns:
            Disease: A realistic disease object
        """
        return Disease(
            id=disease_id,
            name=name,
            description="A viral infection transmitted by Aedes mosquitoes.",
            symptoms="Fever, headache, muscle pain, skin rash",
            treatment="Supportive care, pain management, fluid replacement",
            prevention="Mosquito control, eliminate breeding sites",
            prevalence="Endemic in tropical and subtropical regions",
            image_url=f"/static/images/diseases/{disease_id}/detail.jpg",
            vectors=["aedes_aegypti", "aedes_albopictus"]
        )

    @staticmethod
    def create_region_filter_data(
        region_id: str = "tropical",
        name: str = "Tropical Regions"
    ) -> RegionFilter:
        """Generate realistic RegionFilter test data.
        
        Args:
            region_id: Unique region identifier
            name: Region display name
            
        Returns:
            RegionFilter: A realistic region filter object
        """
        return RegionFilter(id=region_id, name=name)

    @staticmethod
    def create_data_source_filter_data(
        source_id: str = "gbif",
        name: str = "GBIF Database"
    ) -> DataSourceFilter:
        """Generate realistic DataSourceFilter test data.
        
        Args:
            source_id: Unique data source identifier
            name: Data source display name
            
        Returns:
            DataSourceFilter: A realistic data source filter object
        """
        return DataSourceFilter(id=source_id, name=name)

    @staticmethod
    def create_filter_options_data() -> FilterOptions:
        """Generate realistic FilterOptions test data.
        
        Returns:
            FilterOptions: A realistic filter options object
        """
        return FilterOptions(
            species=["Aedes aegypti", "Culex pipiens", "Anopheles gambiae"],
            regions=[
                MockFactory.create_region_filter_data("tropical", "Tropical Regions"),
                MockFactory.create_region_filter_data("temperate", "Temperate Regions")
            ],
            data_sources=[
                MockFactory.create_data_source_filter_data("gbif", "GBIF Database"),
                MockFactory.create_data_source_filter_data("citizen_science", "Citizen Science")
            ]
        )

    @staticmethod
    def create_geojson_geometry_data(
        geometry_type: str = "Point",
        coordinates: list[float] = None
    ) -> GeoJSONGeometry:
        """Generate realistic GeoJSONGeometry test data.
        
        Args:
            geometry_type: Type of geometry (Point, Polygon, etc.)
            coordinates: Coordinate array
            
        Returns:
            GeoJSONGeometry: A realistic GeoJSON geometry object
        """
        if coordinates is None:
            coordinates = [40.7128, -74.0060]  # NYC coordinates
            
        return GeoJSONGeometry(
            type=geometry_type,
            coordinates=coordinates
        )

    @staticmethod
    def create_geojson_feature_data() -> GeoJSONFeature:
        """Generate realistic GeoJSONFeature test data.
        
        Returns:
            GeoJSONFeature: A realistic GeoJSON feature object
        """
        return GeoJSONFeature(
            type="Feature",
            properties={
                "id": "obs_001",
                "species_scientific_name": "Aedes aegypti",
                "count": 1,
                "observed_at": "2023-06-15",
                "observer_id": "test_user_123"
            },
            geometry=MockFactory.create_geojson_geometry_data()
        )

    @staticmethod
    def create_geojson_feature_collection_data(feature_count: int = 1) -> GeoJSONFeatureCollection:
        """Generate realistic GeoJSONFeatureCollection test data.
        
        Args:
            feature_count: Number of features to include
            
        Returns:
            GeoJSONFeatureCollection: A realistic GeoJSON feature collection
        """
        features = [MockFactory.create_geojson_feature_data() for _ in range(feature_count)]
        return GeoJSONFeatureCollection(
            type="FeatureCollection",
            features=features
        )

    # External Library Mock Factories
    
    @staticmethod
    def create_culicidaelab_mock() -> MagicMock:
        """Create a mock for the culicidaelab library.
        
        Returns:
            MagicMock: A configured mock culicidaelab module
        """
        mock_lib = MagicMock()
        
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.get_config.return_value = MagicMock(model_arch="EfficientNet-B0")
        mock_lib.core.settings.get_settings.return_value = mock_settings
        
        # Mock serve function
        mock_predictions = MagicMock()
        mock_prediction = MagicMock()
        mock_prediction.species_name = "Aedes aegypti"
        mock_prediction.confidence = 0.95
        
        mock_predictions.top_prediction.return_value = mock_prediction
        mock_predictions.predictions = [mock_prediction]
        
        mock_lib.serve.serve.return_value = mock_predictions
        
        return mock_lib

    @staticmethod
    def create_fastapi_request_mock(base_url: str = "http://localhost:8000/") -> MagicMock:
        """Create a mock FastAPI Request object.
        
        Args:
            base_url: Base URL for the request
            
        Returns:
            MagicMock: A configured mock FastAPI Request
        """
        mock_request = MagicMock()
        mock_request.base_url = base_url
        return mock_request

    @staticmethod
    def create_pil_image_mock() -> MagicMock:
        """Create a mock PIL Image object.
        
        Returns:
            MagicMock: A configured mock PIL Image
        """
        mock_image = MagicMock()
        mock_image.format = "JPEG"
        mock_image.thumbnail = MagicMock()
        mock_image.save = MagicMock()
        return mock_image

    # Utility Methods for Test Data Validation
    
    @staticmethod
    def validate_mock_data_against_schema(data: Any, schema_class: type) -> bool:
        """Validate that mock data conforms to the expected Pydantic schema.
        
        Args:
            data: The mock data to validate
            schema_class: The Pydantic model class to validate against
            
        Returns:
            bool: True if data is valid, False otherwise
        """
        try:
            if isinstance(data, schema_class):
                return True
            schema_class.model_validate(data)
            return True
        except Exception:
            return False

    @staticmethod
    def create_async_context_manager_mock() -> AsyncMock:
        """Create a mock async context manager for file operations.
        
        Returns:
            AsyncMock: A configured async context manager mock
        """
        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_context)
        mock_context.__aexit__ = AsyncMock(return_value=None)
        mock_context.write = AsyncMock()
        mock_context.read = AsyncMock()
        return mock_context
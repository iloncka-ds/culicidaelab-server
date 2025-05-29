"""
Tests for the geo service.
"""
from unittest.mock import MagicMock
import pytest
import lancedb

from backend.models import GeoJSONFeature
from backend.services.geo_service import (
    is_valid_date_str,
    _db_record_to_geojson_feature,
    filter_features,
    get_geo_layer
)


class TestGeoServiceHelpers:
    """Test cases for helper functions in geo service."""
    
    @pytest.mark.parametrize("date_str,expected", [
        ("2023-01-01", True),
        ("2023-12-31", True),
        ("2023-02-30", False),  # Invalid date
        ("2023/01/01", False),  # Wrong format
        ("not-a-date", False),   # Invalid
        ("", False),             # Empty string
        (None, False),           # None
    ])
    def test_is_valid_date_str(self, date_str, expected):
        """Test date string validation."""
        assert is_valid_date_str(date_str) == expected
    
    def test_db_record_to_geojson_feature_valid(self):
        """Test conversion of valid database record to GeoJSON feature."""
        record = {
            "id": "feature_123",
            "properties_json": '{"name": "Test Feature", "value": 42}',
            "geometry_json": '{"type": "Point", "coordinates": [10, 20]}'
        }
        
        result = _db_record_to_geojson_feature(record)
        
        assert isinstance(result, GeoJSONFeature)
        assert result.properties["name"] == "Test Feature"
        assert result.geometry.type == "Point"
        assert result.geometry.coordinates == [10, 20]
    
    @pytest.mark.parametrize("record", [
        {},  # Empty record
        {"id": "feature_123"},  # Missing required fields
        {"id": "feature_123", "properties_json": '{"name": "Test"}'},  # Missing geometry
        {"id": "feature_123", "geometry_json": '{"type": "Point"}'},  # Missing coordinates
        {
            "id": "feature_123",
            "properties_json": 'not-json',
            "geometry_json": '{"type": "Point", "coordinates": [10,20]}'  # Invalid JSON
        }
    ])
    def test_db_record_to_geojson_feature_invalid(self, record):
        """Test conversion of invalid database records to GeoJSON feature."""
        assert _db_record_to_geojson_feature(record) is None


class TestGeoServiceFiltering:
    """Test cases for the filtering functionality in geo service."""
    
    @pytest.fixture
    def sample_features(self):
        """Create sample features for testing filters."""
        return [
            {
                "id": "obs1",
                "species": "aedes_aegypti",
                "geometry_json": '{"type": "Point", "coordinates": [10, 20]}',
                "observation_date": "2023-06-15"
            },
            {
                "id": "obs2",
                "species": "culex_pipiens",
                "geometry_json": '{"type": "Point", "coordinates": [15, 25]}',
                "observation_date": "2023-07-20"
            },
            {
                "id": "obs3",
                "species": "aedes_albopictus",
                "geometry_json": '{"type": "Point", "coordinates": [5, 15]}',
                "observation_date": "2023-08-10"
            }
        ]
    
    def test_filter_features_by_species(self, sample_features):
        """Test filtering features by species."""
        filtered = filter_features(
            sample_features,
            layer_type="observations",
            species=["aedes_aegypti", "aedes_albopictus"]
        )
        
        assert len(filtered) == 2
        assert all(f["species"] in ["aedes_aegypti", "aedes_albopictus"] for f in filtered)
    
    def test_filter_features_by_bbox(self, sample_features):
        """Test filtering features by bounding box."""
        # Bounding box that includes only the first point (10, 20)
        filtered = filter_features(
            sample_features,
            layer_type="observations",
            bbox=(9, 19, 11, 21)  # min_lon, min_lat, max_lon, max_lat
        )
        
        assert len(filtered) == 1
        assert filtered[0]["id"] == "obs1"
    
    def test_filter_features_by_date_range(self, sample_features):
        """Test filtering features by date range."""
        filtered = filter_features(
            sample_features,
            layer_type="observations",
            date_range_str=("2023-07-01", "2023-07-31")  # Only obs2 is in July 2023
        )
        
        assert len(filtered) == 1
        assert filtered[0]["id"] == "obs2"
    
    def test_filter_features_combined(self, sample_features):
        """Test combining multiple filters."""
        filtered = filter_features(
            sample_features,
            layer_type="observations",
            species=["aedes_aegypti", "aedes_albopictus"],
            bbox=(0, 0, 30, 30),  # Include all points
            date_range_str=("2023-06-01", "2023-07-31")  # obs1 and obs2
        )
        
        # Only obs1 matches all criteria (species and date)
        assert len(filtered) == 1
        assert filtered[0]["id"] == "obs1"


class TestGeoServiceIntegration:
    """Test cases for the geo service integration with database."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database connection."""
        mock_conn = MagicMock(spec=lancedb.DBConnection)
        return mock_conn
    
    @pytest.fixture
    def mock_table(self):
        """Create a mock table."""
        mock_table = MagicMock()
        return mock_table
    
    @pytest.fixture
    def mock_database_module(self, monkeypatch):
        """Mock the database module's get_table function."""
        mock_get_table = MagicMock()
        monkeypatch.setattr('backend.services.database.get_table', mock_get_table)
        return mock_get_table
    
    @pytest.fixture
    def mock_filter_features(self, monkeypatch):
        """Mock the filter_features function."""
        mock_filter = MagicMock(return_value=[])
        monkeypatch.setattr('backend.services.geo_service.filter_features', mock_filter)
        return mock_filter
    
    def test_get_geo_layer(self, mock_db, mock_table, mock_database_module, mock_filter_features):
        """Test get_geo_layer function."""
        # Setup mocks
        mock_database_module.return_value = mock_table
        
        # Mock table search results
        mock_results = [
            {
                "id": "obs1",
                "properties_json": '{"name": "Observation 1"}',
                "geometry_json": '{"type": "Point", "coordinates": [10, 20]}',
                "species": "aedes_aegypti",
                "observation_date": "2023-06-15"
            }
        ]
        mock_table.search.return_value.limit.return_value.to_list.return_value = mock_results
        
        # Mock filter_features to return the same features
        mock_filter_features.side_effect = lambda features, **kwargs: features
        
        # Call the function
        result = get_geo_layer(
            db=mock_db,
            layer_type="observations",
            species_list=["aedes_aegypti"],
            bbox_filter=(0, 0, 30, 30),
            start_date_str="2023-01-01",
            end_date_str="2023-12-31",
            limit=100
        )
        
        # Assertions
        assert len(result.features) == 1
        assert result.features[0].properties["name"] == "Observation 1"
        mock_table.search.return_value.limit.assert_called_once_with(100)
        
        # Verify filter_features was called with the correct arguments
        mock_filter_features.assert_called_once()
        args, kwargs = mock_filter_features.call_args
        assert len(args[0]) == 1  # One feature passed to filter
        assert kwargs["layer_type"] == "observations"
        assert kwargs["species"] == ["aedes_aegypti"]
        assert kwargs["bbox"] == (0, 0, 30, 30)
        assert kwargs["date_range_str"] == ("2023-01-01", "2023-12-31")

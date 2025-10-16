"""
Tests for the geo service.
"""

from unittest.mock import MagicMock, patch
import pytest
from datetime import datetime

from backend.schemas.geo_schemas import GeoJSONFeatureCollection, GeoJSONFeature, GeoJSONGeometry
from backend.services.geo_service import (
    is_valid_date_str,
    get_geo_layer,
)
from tests.factories.mock_factory import MockFactory


class TestGeoServiceHelpers:
    """Test cases for helper functions in geo service."""

    @pytest.mark.parametrize(
        "date_str,expected",
        [
            ("2023-07-15", True),
            ("2023-02-28", True),  # Valid leap year date
            ("2023-02-29", False),  # Invalid non-leap year date
            ("2023-02-30", False),  # Invalid date
            ("2023-13-01", False),  # Invalid month
            ("2023-00-01", False),  # Invalid month (zero)
            ("2023-01-32", False),  # Invalid day
            ("2023/07/15", False),  # Wrong format
            ("15-07-2023", False),  # Wrong format
            ("2023-7-15", False),  # Missing zero padding
            ("not-a-date", False),  # Not a date
            ("", False),  # Empty string
            (None, False),  # None
            ("2023-12-31", True),  # Valid end of year
            ("2000-02-29", True),  # Valid leap year date
        ],
    )
    def test_is_valid_date_str(self, date_str, expected):
        """Test date string validation with various formats and edge cases."""
        if date_str is None:
            # Handle None case separately since parametrize doesn't handle None well
            assert is_valid_date_str(None) == False
        else:
            assert is_valid_date_str(date_str) == expected

    def test_is_valid_date_str_type_error(self):
        """Test date validation with non-string input."""
        assert is_valid_date_str(123) == False
        assert is_valid_date_str([]) == False
        assert is_valid_date_str({}) == False


class TestGeoServiceIntegration:
    """Test cases for the geo service integration with database."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database connection."""
        return MockFactory.create_lancedb_connection_mock()

    @pytest.fixture
    def mock_table(self):
        """Create a mock table with proper chaining methods."""
        mock_table = MagicMock()
        # Set up method chaining for search operations
        mock_table.search.return_value = mock_table
        mock_table.where.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.to_list.return_value = []
        return mock_table

    @pytest.fixture
    def sample_observation_records(self):
        """Create sample observation records with geographic data."""
        return [
            {
                "id": "obs_001",
                "species_scientific_name": "Aedes aegypti",
                "count": 1,
                "coordinates": [-74.0060, 40.7128],  # NYC coordinates (lng, lat)
                "geometry_type": "Point",
                "observed_at": "2023-07-15",
                "observer_id": "user_123",
                "notes": "Found near water container",
                "confidence": 0.89,
            },
            {
                "id": "obs_002",
                "species_scientific_name": "Culex pipiens",
                "count": 3,
                "coordinates": [-73.9857, 40.7484],  # Times Square coordinates
                "geometry_type": "Point",
                "observed_at": "2023-07-20",
                "observer_id": "user_456",
                "notes": "Multiple specimens observed",
                "confidence": 0.92,
            },
        ]

    @patch("backend.services.geo_service.get_table")
    def test_get_geo_layer_observations_no_filters(self, mock_get_table, mock_table, sample_observation_records):
        """Test get_geo_layer for observations without any filters."""
        mock_table.to_list.return_value = sample_observation_records
        mock_get_table.return_value = mock_table

        result = get_geo_layer(db=MagicMock(), layer_type="observations")

        assert isinstance(result, GeoJSONFeatureCollection)
        assert result.type == "FeatureCollection"
        assert len(result.features) == 2
        
        # Check first feature
        feature1 = result.features[0]
        assert isinstance(feature1, GeoJSONFeature)
        assert feature1.type == "Feature"
        assert feature1.properties["species_scientific_name"] == "Aedes aegypti"
        assert feature1.properties["id"] == "obs_001"
        assert feature1.geometry.type == "Point"
        assert feature1.geometry.coordinates == [-74.0060, 40.7128]
        
        # Verify database query
        mock_table.search.assert_called_once()
        mock_table.limit.assert_called_once_with(10000)  # Default limit

    @patch("backend.services.geo_service.get_table")
    def test_get_geo_layer_with_species_filter(self, mock_get_table, mock_table, sample_observation_records):
        """Test get_geo_layer with species filtering."""
        # Filter to only return Aedes aegypti records
        filtered_records = [r for r in sample_observation_records if r["species_scientific_name"] == "Aedes aegypti"]
        mock_table.to_list.return_value = filtered_records
        mock_get_table.return_value = mock_table

        result = get_geo_layer(
            db=MagicMock(),
            layer_type="observations",
            species_list=["Aedes aegypti"],
            limit=100
        )

        assert isinstance(result, GeoJSONFeatureCollection)
        assert len(result.features) == 1
        assert result.features[0].properties["species_scientific_name"] == "Aedes aegypti"
        
        # Verify species filter was applied
        mock_table.where.assert_called_once_with("species_scientific_name = 'Aedes aegypti'")
        mock_table.limit.assert_called_once_with(100)

    @patch("backend.services.geo_service.get_table")
    def test_get_geo_layer_with_multiple_species_filter(self, mock_get_table, mock_table, sample_observation_records):
        """Test get_geo_layer with multiple species filtering."""
        mock_table.to_list.return_value = sample_observation_records
        mock_get_table.return_value = mock_table

        result = get_geo_layer(
            db=MagicMock(),
            layer_type="observations",
            species_list=["Aedes aegypti", "Culex pipiens"]
        )

        assert isinstance(result, GeoJSONFeatureCollection)
        assert len(result.features) == 2
        
        # Verify multiple species filter was applied with OR logic
        expected_filter = "species_scientific_name = 'Aedes aegypti' OR species_scientific_name = 'Culex pipiens'"
        mock_table.where.assert_called_once_with(expected_filter)

    @patch("backend.services.geo_service.get_table")
    @patch("backend.services.geo_service.box")
    @patch("backend.services.geo_service.Point")
    def test_get_geo_layer_with_bbox_filter(self, mock_point_class, mock_box, mock_get_table, mock_table, sample_observation_records):
        """Test get_geo_layer with bounding box filtering using Shapely geometry."""
        mock_table.to_list.return_value = sample_observation_records
        mock_get_table.return_value = mock_table
        
        # Mock Shapely geometry operations
        mock_bbox_polygon = MagicMock()
        mock_box.return_value = mock_bbox_polygon
        
        # Mock Point creation and containment check
        mock_point1 = MagicMock()
        mock_point2 = MagicMock()
        mock_point_class.side_effect = [mock_point1, mock_point2]
        
        # First point is inside bbox, second is outside
        mock_bbox_polygon.contains.side_effect = [True, False]

        bbox = (-75.0, 40.0, -73.0, 41.0)  # NYC area bounding box
        result = get_geo_layer(
            db=MagicMock(),
            layer_type="observations",
            bbox_filter=bbox
        )

        assert isinstance(result, GeoJSONFeatureCollection)
        assert len(result.features) == 1  # Only one point should be inside bbox
        assert result.features[0].properties["id"] == "obs_001"
        
        # Verify Shapely operations were called correctly
        mock_box.assert_called_once_with(*bbox)
        assert mock_point_class.call_count == 2
        mock_point_class.assert_any_call([-74.0060, 40.7128])
        mock_point_class.assert_any_call([-73.9857, 40.7484])

    @patch("backend.services.geo_service.get_table")
    def test_get_geo_layer_with_date_range_filter(self, mock_get_table, mock_table, sample_observation_records):
        """Test get_geo_layer with date range filtering."""
        mock_table.to_list.return_value = sample_observation_records
        mock_get_table.return_value = mock_table

        result = get_geo_layer(
            db=MagicMock(),
            layer_type="observations",
            start_date_str="2023-07-16",  # Should exclude first record (2023-07-15)
            end_date_str="2023-07-25"
        )

        assert isinstance(result, GeoJSONFeatureCollection)
        assert len(result.features) == 1  # Only second record should match
        assert result.features[0].properties["observed_at"] == "2023-07-20"

    @patch("backend.services.geo_service.get_table")
    def test_get_geo_layer_with_invalid_date_filter(self, mock_get_table, mock_table, sample_observation_records):
        """Test get_geo_layer with invalid date strings."""
        mock_table.to_list.return_value = sample_observation_records
        mock_get_table.return_value = mock_table

        result = get_geo_layer(
            db=MagicMock(),
            layer_type="observations",
            start_date_str="invalid-date",
            end_date_str="2023-13-45"  # Invalid date
        )

        # Should return all records since date filters are invalid
        assert isinstance(result, GeoJSONFeatureCollection)
        assert len(result.features) == 2

    @patch("backend.services.geo_service.get_table")
    def test_get_geo_layer_with_record_missing_coordinates(self, mock_get_table, mock_table):
        """Test get_geo_layer with records missing coordinate data."""
        records_with_missing_coords = [
            {
                "id": "obs_001",
                "species_scientific_name": "Aedes aegypti",
                "observed_at": "2023-07-15",
                # Missing coordinates
            },
            {
                "id": "obs_002",
                "species_scientific_name": "Culex pipiens",
                "coordinates": [-73.9857, 40.7484],
                "geometry_type": "Point",
                "observed_at": "2023-07-20",
            },
        ]
        mock_table.to_list.return_value = records_with_missing_coords
        mock_get_table.return_value = mock_table

        result = get_geo_layer(
            db=MagicMock(),
            layer_type="observations",
            bbox_filter=(-75.0, 40.0, -73.0, 41.0)
        )

        # Should include both records since bbox filtering only applies to records with coordinates
        assert isinstance(result, GeoJSONFeatureCollection)
        assert len(result.features) == 2

    @patch("backend.services.geo_service.get_table")
    def test_get_geo_layer_with_invalid_observed_at_date(self, mock_get_table, mock_table):
        """Test get_geo_layer with records having invalid observed_at dates."""
        records_with_invalid_dates = [
            {
                "id": "obs_001",
                "species_scientific_name": "Aedes aegypti",
                "coordinates": [-74.0060, 40.7128],
                "geometry_type": "Point",
                "observed_at": "invalid-date",
            },
            {
                "id": "obs_002",
                "species_scientific_name": "Culex pipiens",
                "coordinates": [-73.9857, 40.7484],
                "geometry_type": "Point",
                "observed_at": "2023-07-20",
            },
        ]
        mock_table.to_list.return_value = records_with_invalid_dates
        mock_get_table.return_value = mock_table

        result = get_geo_layer(
            db=MagicMock(),
            layer_type="observations",
            start_date_str="2023-07-15",
            end_date_str="2023-07-25"
        )

        # Should only include the record with valid date
        assert isinstance(result, GeoJSONFeatureCollection)
        assert len(result.features) == 1
        assert result.features[0].properties["observed_at"] == "2023-07-20"

    def test_get_geo_layer_unsupported_layer_type(self):
        """Test get_geo_layer with unsupported layer type."""
        result = get_geo_layer(
            db=MagicMock(),
            layer_type="unsupported_layer"
        )

        assert isinstance(result, GeoJSONFeatureCollection)
        assert result.type == "FeatureCollection"
        assert len(result.features) == 0

    @patch("backend.services.geo_service.get_table")
    def test_get_geo_layer_database_error(self, mock_get_table):
        """Test get_geo_layer with database error."""
        mock_get_table.side_effect = Exception("Database connection failed")

        result = get_geo_layer(
            db=MagicMock(),
            layer_type="observations"
        )

        # Should return empty collection on error
        assert isinstance(result, GeoJSONFeatureCollection)
        assert len(result.features) == 0

    @patch("backend.services.geo_service.get_table")
    def test_get_geo_layer_table_not_found(self, mock_get_table, mock_table):
        """Test get_geo_layer when table is not found."""
        mock_get_table.return_value = None

        result = get_geo_layer(
            db=MagicMock(),
            layer_type="observations"
        )

        # Should handle gracefully and return empty collection
        assert isinstance(result, GeoJSONFeatureCollection)
        assert len(result.features) == 0

    @patch("backend.services.geo_service.get_table")
    def test_get_geo_layer_complex_filtering(self, mock_get_table, mock_table):
        """Test get_geo_layer with multiple filters applied simultaneously."""
        complex_records = [
            {
                "id": "obs_001",
                "species_scientific_name": "Aedes aegypti",
                "coordinates": [-74.0060, 40.7128],  # Inside NYC bbox
                "geometry_type": "Point",
                "observed_at": "2023-07-15",  # Within date range
                "observer_id": "user_123",
            },
            {
                "id": "obs_002",
                "species_scientific_name": "Culex pipiens",  # Different species
                "coordinates": [-74.0060, 40.7128],  # Same location
                "geometry_type": "Point",
                "observed_at": "2023-07-15",
                "observer_id": "user_456",
            },
            {
                "id": "obs_003",
                "species_scientific_name": "Aedes aegypti",
                "coordinates": [-120.0, 35.0],  # Outside bbox (California)
                "geometry_type": "Point",
                "observed_at": "2023-07-15",
                "observer_id": "user_789",
            },
        ]
        
        # Mock only returns Aedes aegypti due to species filter
        filtered_by_species = [r for r in complex_records if r["species_scientific_name"] == "Aedes aegypti"]
        mock_table.to_list.return_value = filtered_by_species
        mock_get_table.return_value = mock_table

        with patch("backend.services.geo_service.box") as mock_box, \
             patch("backend.services.geo_service.Point") as mock_point_class:
            
            # Mock bbox filtering
            mock_bbox_polygon = MagicMock()
            mock_box.return_value = mock_bbox_polygon
            
            mock_point1 = MagicMock()
            mock_point2 = MagicMock()
            mock_point_class.side_effect = [mock_point1, mock_point2]
            
            # First point inside, second outside
            mock_bbox_polygon.contains.side_effect = [True, False]

            result = get_geo_layer(
                db=MagicMock(),
                layer_type="observations",
                species_list=["Aedes aegypti"],
                bbox_filter=(-75.0, 40.0, -73.0, 41.0),
                start_date_str="2023-07-01",
                end_date_str="2023-07-31"
            )

            # Should only return one record that passes all filters
            assert isinstance(result, GeoJSONFeatureCollection)
            assert len(result.features) == 1
            assert result.features[0].properties["id"] == "obs_001"

    @patch("backend.services.geo_service.get_table")
    def test_get_geo_layer_properties_exclude_geometry_fields(self, mock_get_table, mock_table, sample_observation_records):
        """Test that geometry fields are excluded from feature properties."""
        mock_table.to_list.return_value = sample_observation_records
        mock_get_table.return_value = mock_table

        result = get_geo_layer(db=MagicMock(), layer_type="observations")

        assert len(result.features) == 2
        feature = result.features[0]
        
        # Geometry fields should not be in properties
        assert "geometry_type" not in feature.properties
        assert "coordinates" not in feature.properties
        
        # Other fields should be in properties
        assert "id" in feature.properties
        assert "species_scientific_name" in feature.properties
        assert "observed_at" in feature.properties

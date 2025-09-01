"""
Tests for the geo service.
"""

from unittest.mock import MagicMock, patch
import pytest
import lancedb

from backend.schemas.geo_schemas import GeoJSONFeatureCollection
from backend.services.geo_service import (
    is_valid_date_str,
    get_geo_layer,
)


class TestGeoServiceHelpers:
    """Test cases for helper functions in geo service."""

    @pytest.mark.parametrize(
        "date_str,expected",
        [
            ("2023-07-15", True),
            ("2023-02-30", False),  # Invalid date
            ("2023-13-01", False),  # Invalid month
            ("2023/07/15", False),  # Wrong format
            ("not-a-date", False),  # Not a date
            ("", False),  # Empty string
            (None, False),  # None
        ],
    )
    def test_is_valid_date_str(self, date_str, expected):
        """Test date string validation."""
        assert is_valid_date_str(date_str) == expected


class TestGeoServiceIntegration:
    """Test cases for the geo service integration with database."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database connection."""
        return MagicMock(spec=lancedb.DBConnection)

    @pytest.fixture
    def mock_table(self):
        """Create a mock table."""
        table = MagicMock()
        table.search.return_value = table
        table.where.return_value = table
        table.limit.return_value = table
        table.to_list.return_value = []
        return table

    @pytest.fixture
    def mock_database_module(self, monkeypatch, mock_table):
        """Mock the database module's get_table function."""

        def mock_get_table(db, table_name):
            return mock_table

        monkeypatch.setattr("backend.services.geo_service.get_table", mock_get_table)
        return mock_get_table

    @patch("backend.services.geo_service.is_valid_date_str")
    def test_get_geo_layer(self, mock_is_valid_date, mock_db, mock_table, mock_database_module):
        """Test get_geo_layer function."""
        # Setup test data
        test_records = [
            {
                "id": "obs1",
                "species_scientific_name": "Aedes aegypti",
                "geometry_json": '{"type": "Point", "coordinates": [10, 20]}',
                "observation_date": "2023-07-15",
            },
        ]
        mock_table.to_list.return_value = test_records
        mock_is_valid_date.return_value = True

        # Call the function
        result = get_geo_layer(
            db=mock_db,
            layer_type="observations",
            species_list=["Aedes aegypti"],
            bbox_filter=(9, 19, 11, 21),
            start_date_str="2023-07-01",
            end_date_str="2023-07-31",
            limit=10,
        )

        # Assertions
        assert isinstance(result, GeoJSONFeatureCollection)
        assert len(result.features) == 1
        feature = result.features[0]
        assert feature.properties["species_scientific_name"] == "Aedes aegypti"
        assert feature.properties["observation_date"] == "2023-07-15"
        assert feature.geometry.type == "Point"
        assert hasattr(feature.geometry, "coordinates")
        assert feature.geometry.coordinates == [10, 20]

        # Verify the query was constructed correctly
        mock_table.search.assert_called_once()
        mock_table.where.assert_called_once()
        mock_table.limit.assert_called_once_with(10)
        mock_is_valid_date.assert_called()

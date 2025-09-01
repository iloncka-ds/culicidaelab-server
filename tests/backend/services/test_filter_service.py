"""
Tests for the filter service.
"""

from unittest.mock import MagicMock
import pytest
import lancedb

from backend.schemas.filter_schemas import FilterOptions
from backend.services.filter_service import get_filter_options


class TestFilterService:
    """Test cases for the filter service."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database connection."""
        mock_conn = MagicMock(spec=lancedb.DBConnection)
        return mock_conn

    @pytest.fixture
    def mock_species_table(self):
        """Create a mock species table."""
        mock_table = MagicMock()
        return mock_table

    @pytest.fixture
    def mock_regions_table(self):
        """Create a mock regions table."""
        mock_table = MagicMock()
        return mock_table

    @pytest.fixture
    def mock_data_sources_table(self):
        """Create a mock data_sources table."""
        mock_table = MagicMock()
        return mock_table

    @pytest.fixture
    def mock_database_module(self, monkeypatch):
        """Mock the database module's get_table function."""
        mock_get_table = MagicMock()
        monkeypatch.setattr("backend.services.database.get_table", mock_get_table)
        return mock_get_table

    def test_get_filter_options_success(
        self,
        mock_db,
        mock_species_table,
        mock_regions_table,
        mock_data_sources_table,
        mock_database_module,
    ):
        """Test successful retrieval of filter options."""
        mock_database_module.side_effect = [
            mock_species_table,
            mock_regions_table,
            mock_data_sources_table,
        ]

        mock_species_table.search.return_value.select.return_value.to_list.return_value = [
            {"scientific_name": "Aedes aegypti"},
            {"scientific_name": "Culex pipiens"},
            {"scientific_name": "Anopheles gambiae"},
        ]

        mock_regions_table.search.return_value.select.return_value.to_list.return_value = [
            {"name": "North America"},
            {"name": "Europe"},
            {"name": "Asia"},
        ]

        mock_data_sources_table.search.return_value.select.return_value.to_list.return_value = [
            {"name": "WHO"},
            {"name": "CDC"},
            {"name": "ECDC"},
        ]

        result = get_filter_options(mock_db)

        assert isinstance(result, FilterOptions)
        assert len(result.species) == 3
        assert "Aedes aegypti" in result.species
        assert len(result.regions) == 3
        assert "North America" in result.regions
        assert len(result.data_sources) == 3
        assert "WHO" in result.data_sources

        assert mock_database_module.call_count == 3
        mock_database_module.assert_any_call(mock_db, "species")
        mock_database_module.assert_any_call(mock_db, "regions")
        mock_database_module.assert_any_call(mock_db, "data_sources")

    def test_get_filter_options_empty_results(
        self,
        mock_db,
        mock_species_table,
        mock_regions_table,
        mock_data_sources_table,
        mock_database_module,
    ):
        """Test retrieval of filter options with empty results."""
        mock_database_module.side_effect = [
            mock_species_table,
            mock_regions_table,
            mock_data_sources_table,
        ]

        mock_species_table.search.return_value.select.return_value.to_list.return_value = []
        mock_regions_table.search.return_value.select.return_value.to_list.return_value = []
        mock_data_sources_table.search.return_value.select.return_value.to_list.return_value = []

        result = get_filter_options(mock_db)

        assert isinstance(result, FilterOptions)
        assert result.species == []
        assert result.regions == []
        assert result.data_sources == []

    def test_get_filter_options_with_none_values(
        self,
        mock_db,
        mock_species_table,
        mock_regions_table,
        mock_data_sources_table,
        mock_database_module,
    ):
        """Test retrieval of filter options with None values in results."""
        mock_database_module.side_effect = [
            mock_species_table,
            mock_regions_table,
            mock_data_sources_table,
        ]

        mock_species_table.search.return_value.select.return_value.to_list.return_value = [
            {"scientific_name": "Aedes aegypti"},
            {"scientific_name": None},
            {"scientific_name": ""},
        ]

        mock_regions_table.search.return_value.select.return_value.to_list.return_value = [
            {"name": "North America"},
            {"name": None},
            {"name": ""},
        ]

        mock_data_sources_table.search.return_value.select.return_value.to_list.return_value = [
            {"name": "WHO"},
            {"name": None},
            {"name": ""},
        ]

        result = get_filter_options(mock_db)

        assert isinstance(result, FilterOptions)
        assert result.species == ["Aedes aegypti"]
        assert result.regions == ["North America"]
        assert result.data_sources == ["WHO"]

    def test_get_filter_options_database_error(self, mock_db, mock_database_module):
        """Test behavior when database operations raise exceptions."""
        mock_database_module.side_effect = Exception("Database error")

        result = get_filter_options(mock_db)

        assert isinstance(result, FilterOptions)
        assert result.species == []
        assert result.regions == []
        assert result.data_sources == []

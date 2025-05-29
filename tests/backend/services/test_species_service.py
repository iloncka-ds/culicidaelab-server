"""
Tests for the species service.
"""
from unittest.mock import MagicMock
import pytest
import lancedb

from backend.services.species_service import (
    get_all_species,
    get_species_by_id,
    get_vector_species,
    _get_list_field_from_record,
    _extract_base_fields
)


class TestSpeciesServiceHelpers:
    """Test cases for helper functions in species service."""
    
    def test_get_list_field_from_record_with_list(self):
        """Test _get_list_field_from_record with a list input."""
        # Test with a list
        result = _get_list_field_from_record(["item1", "item2"])
        assert result == ["item1", "item2"]
    
    def test_get_list_field_from_record_with_none(self):
        """Test _get_list_field_from_record with None input."""
        # Test with None
        result = _get_list_field_from_record(None)
        assert result is None
    
    def test_get_list_field_from_record_with_json_string(self):
        """Test _get_list_field_from_record with a JSON string input."""
        # Test with a JSON string
        json_str = '["item1", "item2"]'
        result = _get_list_field_from_record(json_str)
        assert result == ["item1", "item2"]
    
    def test_get_list_field_from_record_with_invalid_json(self):
        """Test _get_list_field_from_record with invalid JSON string."""
        # Test with invalid JSON string
        result = _get_list_field_from_record("not a json")
        assert result == []
    
    def test_extract_base_fields(self):
        """Test _extract_base_fields with valid input."""
        # Test with a record containing all fields
        record = {
            "id": "aedes_aegypti",
            "scientific_name": "Aedes aegypti",
            "common_names": ["Yellow fever mosquito"],
            "family": "Culicidae",
            "genus": "Aedes",
            "is_disease_vector": True,
            "diseases": ["dengue", "zika"],
            "distribution": ["tropical", "subtropical"],
            "habitat": ["urban", "domestic"],
            "description": "Test description",
            "image_url": "http://example.com/image.jpg"
        }
        
        result = _extract_base_fields(record)
        assert isinstance(result, dict)
        assert result["id"] == "aedes_aegypti"
        assert result["scientific_name"] == "Aedes aegypti"
        assert "Yellow fever mosquito" in result["common_names"]
        assert "dengue" in result["diseases"]


class TestSpeciesService:
    """Test cases for the species service."""
    
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
    
    def test_get_all_species_no_search(self, mock_db, mock_table):
        """Test get_all_species without search term."""
        # Mock the table and its search method
        mock_table.search.return_value.limit.return_value.to_list.return_value = [
            {"id": "aedes_aegypti", "scientific_name": "Aedes aegypti"},
            {"id": "culex_pipiens", "scientific_name": "Culex pipiens"}
        ]
        mock_db.open_table.return_value = mock_table
        
        # Call the function
        result = get_all_species(mock_db)
        
        # Assertions
        assert len(result) == 2
        assert result[0]["scientific_name"] == "Aedes aegypti"
        assert result[1]["scientific_name"] == "Culex pipiens"
        mock_table.search.assert_called_once()
    
    def test_get_all_species_with_search(self, mock_db, mock_table):
        """Test get_all_species with search term."""
        # Mock the table and its search method
        mock_table.search.return_value.limit.return_value.to_list.return_value = [
            {"id": "aedes_aegypti", "scientific_name": "Aedes aegypti"}
        ]
        mock_db.open_table.return_value = mock_table
        
        # Call the function with search term
        result = get_all_species(mock_db, search="aedes", limit=10)
        
        # Assertions
        assert len(result) == 1
        assert result[0]["scientific_name"] == "Aedes aegypti"
        mock_table.search.assert_called_once()
    
    def test_get_species_by_id_found(self, mock_db, mock_table):
        """Test get_species_by_id when species is found."""
        # Mock the table and its search method
        mock_table.search.return_value.limit.return_value.to_list.return_value = [
            {"id": "aedes_aegypti", "scientific_name": "Aedes aegypti"}
        ]
        mock_db.open_table.return_value = mock_table
        
        # Call the function
        result = get_species_by_id(mock_db, "aedes_aegypti")
        
        # Assertions
        assert result is not None
        assert result["scientific_name"] == "Aedes aegypti"
    
    def test_get_species_by_id_not_found(self, mock_db, mock_table):
        """Test get_species_by_id when species is not found."""
        # Mock the table to return empty results
        mock_table.search.return_value.limit.return_value.to_list.return_value = []
        mock_db.open_table.return_value = mock_table
        
        # Call the function
        result = get_species_by_id(mock_db, "nonexistent_id")
        
        # Assertions
        assert result is None
    
    def test_get_vector_species_no_disease_filter(self, mock_db, mock_table):
        """Test get_vector_species without disease filter."""
        # Mock the table and its search method
        mock_table.search.return_value.limit.return_value.to_list.return_value = [
            {"id": "aedes_aegypti", "scientific_name": "Aedes aegypti", "is_disease_vector": True}
        ]
        mock_db.open_table.return_value = mock_table
        
        # Call the function without disease filter
        result = get_vector_species(mock_db)
        
        # Assertions
        assert len(result) == 1
        assert result[0]["scientific_name"] == "Aedes aegypti"
        assert result[0]["is_disease_vector"] is True
    
    def test_get_vector_species_with_disease_filter(self, mock_db, mock_table):
        """Test get_vector_species with disease filter."""
        # Mock the table and its search method
        mock_table.search.return_value.limit.return_value.to_list.return_value = [
            {
                "id": "aedes_aegypti",
                "scientific_name": "Aedes aegypti",
                "is_disease_vector": True,
                "diseases": ["dengue"]
            }
        ]
        mock_db.open_table.return_value = mock_table
        
        # Call the function with disease filter
        result = get_vector_species(mock_db, disease_id="dengue")
        
        # Assertions
        assert len(result) == 1
        assert result[0]["scientific_name"] == "Aedes aegypti"
        assert "dengue" in result[0]["diseases"]

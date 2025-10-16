"""
Tests for the disease service.
"""

from unittest.mock import MagicMock
import pytest
import lancedb

from backend.schemas.diseases_schemas import Disease
from backend.services.disease_service import (
    get_all_diseases,
    get_disease_by_id,
    get_diseases_by_vector,
    _db_record_to_disease_model,
)


@pytest.fixture
def mock_request():
    """Create a minimal mock request object with base_url attribute."""

    class Req:
        base_url = "http://testserver/"

    return Req()


class TestDiseaseServiceHelpers:
    """Test cases for helper functions in disease service."""

    def test_db_record_to_disease_model(self, mock_request):
        """Test _db_record_to_disease_model with complete data."""
        record = {
            "id": "dengue",
            "name_en": "Dengue Fever",
            "description_en": "Viral disease transmitted by Aedes mosquitoes",
            "symptoms_en": "high fever, rash, muscle and joint pain",
            "treatment": "Supportive care and pain relievers",
            "prevention": "mosquito control, use of repellents",
            "prevalence": "Tropical and subtropical regions",
            "image_url": "http://example.com/dengue.jpg",
            "vectors": ["aedes_aegypti", "aedes_albopictus"],
        }

        # call helper with explicit lang and request to match service signature
        result = _db_record_to_disease_model(record, "en", mock_request)

        assert isinstance(result, Disease)
        assert result.id == "dengue"
        assert result.name == "Dengue Fever"
        assert "Viral disease" in result.description
        assert "high fever" in result.symptoms
        assert "aedes_aegypti" in result.vectors

    def test_db_record_to_disease_model_missing_fields(self, mock_request):
        """Test _db_record_to_disease_model with missing optional fields."""
        record = {
            "id": "dengue",
            "name_en": "Dengue Fever",
        }

        result = _db_record_to_disease_model(record, "en", mock_request)

        assert isinstance(result, Disease)
        assert result.id == "dengue"
        assert result.name == "Dengue Fever"
        assert result.vectors == []
        assert result.description is None


class TestDiseaseService:
    """Test cases for the disease service functions."""

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
        monkeypatch.setattr("backend.services.database.get_table", mock_get_table)
        return mock_get_table

    def test_get_all_diseases_no_search(
        self,
        mock_db,
        mock_table,
        mock_database_module,
        mock_request,
    ):
        """Test get_all_diseases without search term."""
        mock_database_module.return_value = mock_table
        mock_results = [
            {
                "id": "dengue",
                "name_en": "Dengue Fever",
                "description_en": "Viral disease",
                "vectors": ["aedes_aegypti"],
            },
            {"id": "malaria", "name_en": "Malaria", "description_en": "Parasitic disease", "vectors": ["anopheles"]},
        ]
        mock_table.search.return_value.limit.return_value.to_list.return_value = mock_results

        result = get_all_diseases(mock_db, mock_request, "en")

        assert len(result) == 2
        assert result[0].name == "Dengue Fever"
        mock_table.search.return_value.limit.assert_called_once_with(50)

    def test_get_all_diseases_with_search(
        self,
        mock_db,
        mock_table,
        mock_database_module,
        mock_request,
    ):
        """Test get_all_diseases with search term."""
        mock_database_module.return_value = mock_table
        mock_results = [
            {
                "id": "dengue",
                "name_en": "Dengue Fever",
                "description_en": "Viral disease",
                "vectors": ["aedes_aegypti"],
            },
        ]

        mock_query = MagicMock()
        mock_table.search.return_value = mock_query
        mock_query.where.return_value.limit.return_value.to_list.return_value = mock_results

        result = get_all_diseases(mock_db, mock_request, "en", search="dengue", limit=10)

        assert len(result) == 1
        assert result[0].name == "Dengue Fever"
        mock_query.where.assert_called_once()
        mock_query.where.return_value.limit.assert_called_once_with(10)

    def test_get_disease_by_id_found(
        self,
        mock_db,
        mock_table,
        mock_database_module,
        mock_request,
    ):
        """Test get_disease_by_id when disease is found."""
        mock_database_module.return_value = mock_table
        mock_results = [
            {
                "id": "dengue",
                "name_en": "Dengue Fever",
                "description_en": "Viral disease",
                "vectors": ["aedes_aegypti"],
            },
        ]

        mock_query = MagicMock()
        mock_table.search.return_value = mock_query
        mock_query.where.return_value.limit.return_value.to_list.return_value = mock_results

        result = get_disease_by_id(mock_db, "dengue", "en", mock_request)

        assert result is not None
        assert result.id == "dengue"
        mock_query.where.assert_called_once_with("id = 'dengue'")
        mock_query.where.return_value.limit.assert_called_once_with(1)

    def test_get_disease_by_id_not_found(
        self,
        mock_db,
        mock_table,
        mock_database_module,
        mock_request,
    ):
        """Test get_disease_by_id when disease is not found."""
        mock_database_module.return_value = mock_table
        mock_table.search.return_value.where.return_value.limit.return_value.to_list.return_value = []

        result = get_disease_by_id(mock_db, "nonexistent", "en", mock_request)

        assert result is None

    def test_get_diseases_by_vector(
        self,
        mock_db,
        mock_table,
        mock_database_module,
        mock_request,
    ):
        """Test get_diseases_by_vector."""
        mock_database_module.return_value = mock_table
        mock_results = [
            {
                "id": "dengue",
                "name_en": "Dengue Fever",
                "description_en": "Viral disease",
                "vectors": ["aedes_aegypti"],
            },
            {"id": "zika", "name_en": "Zika Virus", "description_en": "Viral disease", "vectors": ["aedes_aegypti"]},
        ]
        mock_query = MagicMock()
        mock_table.search.return_value = mock_query
        mock_query.where.return_value.to_list.return_value = mock_results

        result = get_diseases_by_vector(mock_db, "aedes_aegypti", "en", mock_request)

        assert len(result) == 2
        assert all("aedes_aegypti" in d.vectors for d in result)
        mock_query.where.assert_called_once_with("array_has(vectors, 'aedes_aegypti')")

    def test_get_diseases_by_vector_not_found(
        self,
        mock_db,
        mock_table,
        mock_database_module,
        mock_request,
    ):
        """Test get_diseases_by_vector when no diseases are found for the vector."""
        mock_database_module.return_value = mock_table
        mock_table.search.return_value.where.return_value.to_list.return_value = []

        result = get_diseases_by_vector(
            mock_db,
            "nonexistent_vector",
            "en",
            mock_request,
        )

        assert len(result) == 0

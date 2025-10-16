"""
Tests for the disease service.
"""

from unittest.mock import MagicMock, patch
import pytest

from backend.schemas.diseases_schemas import Disease
from backend.services.disease_service import (
    get_all_diseases,
    get_disease_by_id,
    get_diseases_by_vector,
    _db_record_to_disease_model,
)
from tests.factories.mock_factory import MockFactory


class TestDiseaseServiceHelpers:
    """Test cases for helper functions in disease service."""

    def test_db_record_to_disease_model_complete_data(self, mock_fastapi_request):
        """Test _db_record_to_disease_model with complete data in English."""
        record = {
            "id": "dengue",
            "name_en": "Dengue Fever",
            "name_ru": "Лихорадка денге",
            "description_en": "Viral disease transmitted by Aedes mosquitoes",
            "description_ru": "Вирусное заболевание, передаваемое комарами Aedes",
            "symptoms_en": "High fever, rash, muscle and joint pain",
            "symptoms_ru": "Высокая температура, сыпь, боли в мышцах и суставах",
            "treatment_en": "Supportive care and pain relievers",
            "treatment_ru": "Поддерживающая терапия и обезболивающие",
            "prevention_en": "Mosquito control, use of repellents",
            "prevention_ru": "Контроль комаров, использование репеллентов",
            "prevalence_en": "Tropical and subtropical regions",
            "prevalence_ru": "Тропические и субтропические регионы",
            "vectors": ["aedes_aegypti", "aedes_albopictus"],
        }

        # Test with English
        result_en = _db_record_to_disease_model(record, "en", mock_fastapi_request)

        assert isinstance(result_en, Disease)
        assert result_en.id == "dengue"
        assert result_en.name == "Dengue Fever"
        assert "Viral disease" in result_en.description
        assert "High fever" in result_en.symptoms
        assert "Supportive care" in result_en.treatment
        assert "Mosquito control" in result_en.prevention
        assert "Tropical and subtropical" in result_en.prevalence
        assert "aedes_aegypti" in result_en.vectors
        assert "aedes_albopictus" in result_en.vectors
        assert result_en.image_url.startswith("http://testserver/static/images/diseases/dengue/")

        # Test with Russian
        result_ru = _db_record_to_disease_model(record, "ru", mock_fastapi_request)

        assert result_ru.name == "Лихорадка денге"
        assert "Вирусное заболевание" in result_ru.description
        assert "Высокая температура" in result_ru.symptoms

    def test_db_record_to_disease_model_fallback_to_english(self, mock_fastapi_request):
        """Test _db_record_to_disease_model with fallback to English for missing translations."""
        record = {
            "id": "malaria",
            "name_en": "Malaria",
            "description_en": "Parasitic disease transmitted by Anopheles mosquitoes",
            "symptoms_en": "Fever, chills, headache",
            # No Russian translations available
            "vectors": ["anopheles_gambiae"],
        }

        # Test with Russian language but English fallback
        result = _db_record_to_disease_model(record, "ru", mock_fastapi_request)

        assert isinstance(result, Disease)
        assert result.id == "malaria"
        assert result.name == "Malaria"  # Fallback to English
        assert result.description.startswith("Parasitic disease")  # Fallback to English
        assert result.symptoms == "Fever, chills, headache"  # Fallback to English
        assert "anopheles_gambiae" in result.vectors

    def test_db_record_to_disease_model_minimal_data(self, mock_fastapi_request):
        """Test _db_record_to_disease_model with minimal required data."""
        record = {
            "id": "test_disease",
            "name_en": "Test Disease",
        }

        result = _db_record_to_disease_model(record, "en", mock_fastapi_request)

        assert isinstance(result, Disease)
        assert result.id == "test_disease"
        assert result.name == "Test Disease"
        assert result.vectors == []  # Default empty list
        assert result.description is None
        assert result.symptoms is None
        assert result.treatment is None
        assert result.prevention is None
        assert result.prevalence is None
        assert result.image_url.startswith("http://testserver/static/images/diseases/test_disease/")

    def test_db_record_to_disease_model_empty_vectors(self, mock_fastapi_request):
        """Test _db_record_to_disease_model with empty vectors field."""
        record = {
            "id": "non_vector_disease",
            "name_en": "Non-Vector Disease",
            "vectors": [],
        }

        result = _db_record_to_disease_model(record, "en", mock_fastapi_request)

        assert isinstance(result, Disease)
        assert result.vectors == []

    def test_db_record_to_disease_model_missing_vectors(self, mock_fastapi_request):
        """Test _db_record_to_disease_model with missing vectors field."""
        record = {
            "id": "unknown_disease",
            "name_en": "Unknown Disease",
            # No vectors field
        }

        result = _db_record_to_disease_model(record, "en", mock_fastapi_request)

        assert isinstance(result, Disease)
        assert result.vectors == []  # Default when field is missing


class TestDiseaseService:
    """Test cases for the disease service functions."""

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
    def sample_disease_records(self):
        """Create sample disease database records."""
        return [
            {
                "id": "dengue",
                "name_en": "Dengue Fever",
                "name_ru": "Лихорадка денге",
                "description_en": "Viral disease transmitted by Aedes mosquitoes",
                "description_ru": "Вирусное заболевание, передаваемое комарами Aedes",
                "vectors": ["aedes_aegypti", "aedes_albopictus"],
            },
            {
                "id": "malaria",
                "name_en": "Malaria",
                "name_ru": "Малярия",
                "description_en": "Parasitic disease transmitted by Anopheles mosquitoes",
                "description_ru": "Паразитарное заболевание, передаваемое комарами Anopheles",
                "vectors": ["anopheles_gambiae", "anopheles_funestus"],
            },
        ]

    @patch("backend.services.disease_service.get_table")
    def test_get_all_diseases_no_search(self, mock_get_table, mock_table, sample_disease_records, mock_fastapi_request):
        """Test get_all_diseases without search term."""
        mock_table.to_list.return_value = sample_disease_records
        mock_get_table.return_value = mock_table

        result = get_all_diseases(db=MagicMock(), request=mock_fastapi_request, lang="en")

        assert len(result) == 2
        assert all(isinstance(disease, Disease) for disease in result)
        assert result[0].name == "Dengue Fever"
        assert result[1].name == "Malaria"
        mock_table.search.assert_called_once()
        mock_table.limit.assert_called_once_with(50)  # Default limit

    @patch("backend.services.disease_service.get_table")
    def test_get_all_diseases_with_search(self, mock_get_table, mock_table, mock_fastapi_request):
        """Test get_all_diseases with search term."""
        filtered_records = [
            {
                "id": "dengue",
                "name_en": "Dengue Fever",
                "description_en": "Viral disease transmitted by Aedes mosquitoes",
                "vectors": ["aedes_aegypti"],
            }
        ]
        mock_table.to_list.return_value = filtered_records
        mock_get_table.return_value = mock_table

        result = get_all_diseases(
            db=MagicMock(), 
            request=mock_fastapi_request, 
            lang="en", 
            search="dengue", 
            limit=10
        )

        assert len(result) == 1
        assert result[0].name == "Dengue Fever"
        mock_table.search.assert_called_once()
        mock_table.where.assert_called_once()
        mock_table.limit.assert_called_once_with(10)

    @patch("backend.services.disease_service.get_table")
    def test_get_all_diseases_with_russian_language(self, mock_get_table, mock_table, sample_disease_records, mock_fastapi_request):
        """Test get_all_diseases with Russian language."""
        mock_table.to_list.return_value = sample_disease_records
        mock_get_table.return_value = mock_table

        result = get_all_diseases(db=MagicMock(), request=mock_fastapi_request, lang="ru")

        assert len(result) == 2
        assert result[0].name == "Лихорадка денге"
        assert result[1].name == "Малярия"

    @patch("backend.services.disease_service.get_table")
    def test_get_all_diseases_table_not_found(self, mock_get_table, mock_fastapi_request):
        """Test get_all_diseases when table is not found."""
        mock_get_table.return_value = None

        result = get_all_diseases(db=MagicMock(), request=mock_fastapi_request, lang="en")

        assert result == []

    @patch("backend.services.disease_service.get_table")
    def test_get_all_diseases_exception_handling(self, mock_get_table, mock_table, mock_fastapi_request):
        """Test get_all_diseases exception handling."""
        mock_get_table.return_value = mock_table
        mock_table.search.side_effect = Exception("Database error")

        result = get_all_diseases(db=MagicMock(), request=mock_fastapi_request, lang="en")

        assert result == []

    @patch("backend.services.disease_service.get_table")
    def test_get_disease_by_id_found(self, mock_get_table, mock_table, mock_fastapi_request):
        """Test get_disease_by_id when disease is found."""
        disease_record = {
            "id": "dengue",
            "name_en": "Dengue Fever",
            "description_en": "Viral disease transmitted by Aedes mosquitoes",
            "symptoms_en": "High fever, rash, muscle pain",
            "vectors": ["aedes_aegypti", "aedes_albopictus"],
        }
        mock_table.to_list.return_value = [disease_record]
        mock_get_table.return_value = mock_table

        result = get_disease_by_id(db=MagicMock(), disease_id="dengue", lang="en", request=mock_fastapi_request)

        assert result is not None
        assert isinstance(result, Disease)
        assert result.id == "dengue"
        assert result.name == "Dengue Fever"
        assert "aedes_aegypti" in result.vectors
        mock_table.where.assert_called_once_with("id = 'dengue'")
        mock_table.limit.assert_called_once_with(1)

    @patch("backend.services.disease_service.get_table")
    def test_get_disease_by_id_not_found(self, mock_get_table, mock_table, mock_fastapi_request):
        """Test get_disease_by_id when disease is not found."""
        mock_table.to_list.return_value = []
        mock_get_table.return_value = mock_table

        result = get_disease_by_id(db=MagicMock(), disease_id="nonexistent", lang="en", request=mock_fastapi_request)

        assert result is None

    @patch("backend.services.disease_service.get_table")
    def test_get_disease_by_id_sql_injection_protection(self, mock_get_table, mock_table, mock_fastapi_request):
        """Test get_disease_by_id with SQL injection attempt."""
        mock_table.to_list.return_value = []
        mock_get_table.return_value = mock_table

        # Attempt SQL injection
        malicious_id = "dengue'; DROP TABLE diseases; --"
        result = get_disease_by_id(db=MagicMock(), disease_id=malicious_id, lang="en", request=mock_fastapi_request)

        assert result is None
        # Verify that the ID was sanitized (single quotes escaped)
        expected_sanitized = "dengue''; DROP TABLE diseases; --"
        mock_table.where.assert_called_once_with(f"id = '{expected_sanitized}'")

    @patch("backend.services.disease_service.get_table")
    def test_get_disease_by_id_table_not_found(self, mock_get_table, mock_fastapi_request):
        """Test get_disease_by_id when table is not found."""
        mock_get_table.return_value = None

        result = get_disease_by_id(db=MagicMock(), disease_id="dengue", lang="en", request=mock_fastapi_request)

        assert result is None

    @patch("backend.services.disease_service.get_table")
    def test_get_disease_by_id_exception_handling(self, mock_get_table, mock_table, mock_fastapi_request):
        """Test get_disease_by_id exception handling."""
        mock_get_table.return_value = mock_table
        mock_table.search.side_effect = Exception("Database error")

        result = get_disease_by_id(db=MagicMock(), disease_id="dengue", lang="en", request=mock_fastapi_request)

        assert result is None

    @patch("backend.services.disease_service.get_table")
    def test_get_diseases_by_vector(self, mock_get_table, mock_table, mock_fastapi_request):
        """Test get_diseases_by_vector with valid vector."""
        disease_records = [
            {
                "id": "dengue",
                "name_en": "Dengue Fever",
                "description_en": "Viral disease",
                "vectors": ["aedes_aegypti", "aedes_albopictus"],
            },
            {
                "id": "zika",
                "name_en": "Zika Virus",
                "description_en": "Viral disease",
                "vectors": ["aedes_aegypti"],
            },
        ]
        mock_table.to_list.return_value = disease_records
        mock_get_table.return_value = mock_table

        result = get_diseases_by_vector(db=MagicMock(), vector_id="aedes_aegypti", lang="en", request=mock_fastapi_request)

        assert len(result) == 2
        assert all(isinstance(disease, Disease) for disease in result)
        assert all("aedes_aegypti" in disease.vectors for disease in result)
        mock_table.where.assert_called_once_with("array_has(vectors, 'aedes_aegypti')")

    @patch("backend.services.disease_service.get_table")
    def test_get_diseases_by_vector_not_found(self, mock_get_table, mock_table, mock_fastapi_request):
        """Test get_diseases_by_vector when no diseases are found for the vector."""
        mock_table.to_list.return_value = []
        mock_get_table.return_value = mock_table

        result = get_diseases_by_vector(
            db=MagicMock(), 
            vector_id="nonexistent_vector", 
            lang="en", 
            request=mock_fastapi_request
        )

        assert len(result) == 0

    @patch("backend.services.disease_service.get_table")
    def test_get_diseases_by_vector_sql_injection_protection(self, mock_get_table, mock_table, mock_fastapi_request):
        """Test get_diseases_by_vector with SQL injection attempt."""
        mock_table.to_list.return_value = []
        mock_get_table.return_value = mock_table

        # Attempt SQL injection
        malicious_vector = "aedes'; DROP TABLE diseases; --"
        result = get_diseases_by_vector(
            db=MagicMock(), 
            vector_id=malicious_vector, 
            lang="en", 
            request=mock_fastapi_request
        )

        assert result == []
        # Verify that the vector ID was sanitized
        expected_sanitized = "aedes''; DROP TABLE diseases; --"
        mock_table.where.assert_called_once_with(f"array_has(vectors, '{expected_sanitized}')")

    @patch("backend.services.disease_service.get_table")
    def test_get_diseases_by_vector_table_not_found(self, mock_get_table, mock_fastapi_request):
        """Test get_diseases_by_vector when table is not found."""
        mock_get_table.return_value = None

        result = get_diseases_by_vector(
            db=MagicMock(), 
            vector_id="aedes_aegypti", 
            lang="en", 
            request=mock_fastapi_request
        )

        assert result == []

    @patch("backend.services.disease_service.get_table")
    def test_get_diseases_by_vector_exception_handling(self, mock_get_table, mock_table, mock_fastapi_request):
        """Test get_diseases_by_vector exception handling."""
        mock_get_table.return_value = mock_table
        mock_table.search.side_effect = Exception("Database error")

        result = get_diseases_by_vector(
            db=MagicMock(), 
            vector_id="aedes_aegypti", 
            lang="en", 
            request=mock_fastapi_request
        )

        assert result == []

"""
Tests for the species service.
"""

from unittest.mock import MagicMock, patch
import pytest

from backend.services.species_service import (
    get_all_species,
    get_species_by_id,
    get_vector_species,
    _get_list_field_from_record,
    _db_record_to_species_detail,
    _db_record_to_species_base,
)
from backend.schemas.species_schemas import SpeciesDetail, SpeciesBase
from tests.factories.mock_factory import MockFactory


class TestSpeciesServiceHelpers:
    """Test cases for helper functions in species service."""

    def test_get_list_field_from_record_with_list(self):
        """Test _get_list_field_from_record with a list input."""
        result = _get_list_field_from_record(["item1", "item2"])
        assert result == ["item1", "item2"]

    def test_get_list_field_from_record_with_none(self):
        """Test _get_list_field_from_record with None input."""
        result = _get_list_field_from_record(None)
        assert result == []

    def test_get_list_field_from_record_with_non_list(self):
        """Test _get_list_field_from_record with non-list input."""
        result = _get_list_field_from_record("not a list")
        assert result == []

    def test_get_list_field_from_record_with_mixed_types(self):
        """Test _get_list_field_from_record with mixed type list."""
        result = _get_list_field_from_record([1, "item2", 3.14])
        assert result == ["1", "item2", "3.14"]

    def test_db_record_to_species_detail(self, mock_fastapi_request):
        """Test _db_record_to_species_detail with valid input."""
        record = {
            "id": "aedes_aegypti",
            "scientific_name": "Aedes aegypti",
            "vector_status": "Primary Vector",
            "geographic_regions": ["africa", "americas"],
            "common_name_en": "Yellow fever mosquito",
            "common_name_es": "Mosquito de la fiebre amarilla",
            "description_en": "A mosquito species that transmits diseases...",
            "description_es": "Una especie de mosquito que transmite enfermedades...",
            "key_characteristics_en": ["Black and white stripes", "Lays eggs in water"],
            "key_characteristics_es": ["Rayas negras y blancas", "Pone huevos en el agua"],
            "habitat_preferences_en": ["Urban areas", "Standing water"],
            "habitat_preferences_es": ["Áreas urbanas", "Agua estancada"],
            "related_diseases": ["dengue", "zika", "yellow_fever"],
        }

        region_translations = {
            "en": {"africa": "Africa", "americas": "Americas"},
            "es": {"africa": "África", "americas": "Américas"},
        }

        # Test with English
        result_en = _db_record_to_species_detail(record, "en", region_translations, mock_fastapi_request)
        assert isinstance(result_en, SpeciesDetail)
        assert result_en.id == "aedes_aegypti"
        assert result_en.scientific_name == "Aedes aegypti"
        assert result_en.vector_status == "Primary Vector"
        assert result_en.common_name == "Yellow fever mosquito"
        assert result_en.description.startswith("A mosquito species")
        assert "Black and white stripes" in result_en.key_characteristics
        assert "Africa" in result_en.geographic_regions
        assert result_en.image_url.startswith("http://testserver/static/images/species/aedes_aegypti/")
        assert "dengue" in result_en.related_diseases

        # Test with Spanish
        result_es = _db_record_to_species_detail(record, "es", region_translations, mock_fastapi_request)
        assert result_es.common_name == "Mosquito de la fiebre amarilla"
        assert result_es.description.startswith("Una especie de mosquito")
        assert "África" in result_es.geographic_regions

    def test_db_record_to_species_detail_fallback_to_english(self, mock_fastapi_request):
        """Test _db_record_to_species_detail with fallback to English for missing translations."""
        record = {
            "id": "culex_pipiens",
            "scientific_name": "Culex pipiens",
            "vector_status": "Secondary Vector",
            "geographic_regions": ["temperate"],
            "common_name_en": "Common house mosquito",
            "description_en": "A widespread mosquito species...",
            # No Spanish translations available
        }

        region_translations = {
            "en": {"temperate": "Temperate Regions"},
            "es": {"temperate": "Regiones Templadas"},
        }

        # Test with Spanish language but English fallback
        result = _db_record_to_species_detail(record, "es", region_translations, mock_fastapi_request)
        assert result.common_name == "Common house mosquito"  # Fallback to English
        assert result.description.startswith("A widespread mosquito")  # Fallback to English
        assert "Regiones Templadas" in result.geographic_regions  # Region translation works

    def test_db_record_to_species_base(self, mock_fastapi_request):
        """Test _db_record_to_species_base with valid input."""
        record = {
            "id": "anopheles_gambiae",
            "scientific_name": "Anopheles gambiae",
            "vector_status": "Primary Vector",
            "common_name_en": "African malaria mosquito",
            "common_name_ru": "Африканский малярийный комар",
        }

        # Test with English
        result_en = _db_record_to_species_base(record, "en", mock_fastapi_request)
        assert isinstance(result_en, SpeciesBase)
        assert result_en.id == "anopheles_gambiae"
        assert result_en.scientific_name == "Anopheles gambiae"
        assert result_en.vector_status == "Primary Vector"
        assert result_en.common_name == "African malaria mosquito"
        assert result_en.image_url.startswith("http://testserver/static/images/species/anopheles_gambiae/thumbnail.jpg")

        # Test with Russian
        result_ru = _db_record_to_species_base(record, "ru", mock_fastapi_request)
        assert result_ru.common_name == "Африканский малярийный комар"


class TestSpeciesService:
    """Test cases for the species service."""

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
    def sample_species_records(self):
        """Create sample species database records."""
        return [
            {
                "id": "aedes_aegypti",
                "scientific_name": "Aedes aegypti",
                "vector_status": "Primary Vector",
                "common_name_en": "Yellow fever mosquito",
                "common_name_ru": "Комар жёлтой лихорадки",
            },
            {
                "id": "culex_pipiens",
                "scientific_name": "Culex pipiens",
                "vector_status": "Secondary Vector",
                "common_name_en": "Common house mosquito",
                "common_name_ru": "Обыкновенный комар",
            },
        ]

    @patch("backend.services.species_service.get_table")
    def test_get_all_species_no_search(self, mock_get_table, mock_table, sample_species_records, mock_fastapi_request):
        """Test get_all_species without search term."""
        mock_table.to_list.return_value = sample_species_records
        mock_get_table.return_value = mock_table

        result = get_all_species(db=MagicMock(), request=mock_fastapi_request, lang="en")

        assert len(result) == 2
        assert isinstance(result[0], SpeciesBase)
        assert result[0].scientific_name == "Aedes aegypti"
        assert result[1].scientific_name == "Culex pipiens"
        mock_table.search.assert_called_once()
        mock_table.limit.assert_called_once_with(100)  # Default limit

    @patch("backend.services.species_service.get_table")
    def test_get_all_species_with_search(self, mock_get_table, mock_table, mock_fastapi_request):
        """Test get_all_species with search term."""
        filtered_records = [
            {
                "id": "aedes_aegypti",
                "scientific_name": "Aedes aegypti",
                "vector_status": "Primary Vector",
                "common_name_en": "Yellow fever mosquito",
            }
        ]
        mock_table.to_list.return_value = filtered_records
        mock_get_table.return_value = mock_table

        result = get_all_species(
            db=MagicMock(), 
            request=mock_fastapi_request, 
            lang="en", 
            search="aedes", 
            limit=10
        )

        assert len(result) == 1
        assert result[0].scientific_name == "Aedes aegypti"
        mock_table.search.assert_called_once()
        mock_table.where.assert_called_once()
        mock_table.limit.assert_called_once_with(10)

    @patch("backend.services.species_service.get_table")
    def test_get_all_species_table_not_found(self, mock_get_table, mock_fastapi_request):
        """Test get_all_species when table is not found."""
        mock_get_table.return_value = None

        result = get_all_species(db=MagicMock(), request=mock_fastapi_request, lang="en")

        assert result == []

    @patch("backend.services.species_service.get_table")
    def test_get_all_species_exception_handling(self, mock_get_table, mock_table, mock_fastapi_request):
        """Test get_all_species exception handling."""
        mock_get_table.return_value = mock_table
        mock_table.search.side_effect = Exception("Database error")

        result = get_all_species(db=MagicMock(), request=mock_fastapi_request, lang="en")

        assert result == []

    @patch("backend.services.species_service.get_table")
    def test_get_species_by_id_found(self, mock_get_table, mock_table, mock_fastapi_request):
        """Test get_species_by_id when species is found."""
        species_record = {
            "id": "aedes_aegypti",
            "scientific_name": "Aedes aegypti",
            "vector_status": "Primary Vector",
            "common_name_en": "Yellow fever mosquito",
            "description_en": "A mosquito species that transmits diseases...",
            "geographic_regions": ["tropical", "subtropical"],
            "related_diseases": ["dengue", "zika"],
        }
        mock_table.to_list.return_value = [species_record]
        mock_get_table.return_value = mock_table

        region_translations = {
            "en": {"tropical": "Tropical Regions", "subtropical": "Subtropical Regions"}
        }

        result = get_species_by_id(
            db=MagicMock(),
            species_id="aedes_aegypti",
            lang="en",
            region_translations=region_translations,
            request=mock_fastapi_request,
        )

        assert result is not None
        assert isinstance(result, SpeciesDetail)
        assert result.scientific_name == "Aedes aegypti"
        assert "Tropical Regions" in result.geographic_regions
        mock_table.where.assert_called_once_with("id = 'aedes_aegypti'")

    @patch("backend.services.species_service.get_table")
    def test_get_species_by_id_not_found(self, mock_get_table, mock_table, mock_fastapi_request):
        """Test get_species_by_id when species is not found."""
        mock_table.to_list.return_value = []
        mock_get_table.return_value = mock_table

        result = get_species_by_id(
            db=MagicMock(),
            species_id="nonexistent_id",
            lang="en",
            region_translations={},
            request=mock_fastapi_request,
        )

        assert result is None

    @patch("backend.services.species_service.get_table")
    def test_get_species_by_id_exception_handling(self, mock_get_table, mock_table, mock_fastapi_request):
        """Test get_species_by_id exception handling."""
        mock_get_table.return_value = mock_table
        mock_table.search.side_effect = Exception("Database error")

        result = get_species_by_id(
            db=MagicMock(),
            species_id="aedes_aegypti",
            lang="en",
            region_translations={},
            request=mock_fastapi_request,
        )

        assert result is None

    @patch("backend.services.species_service.disease_service")
    @patch("backend.services.species_service.get_table")
    def test_get_vector_species_no_disease_filter(self, mock_get_table, mock_disease_service, mock_table, mock_fastapi_request):
        """Test get_vector_species without disease filter."""
        vector_records = [
            {
                "id": "aedes_aegypti",
                "scientific_name": "Aedes aegypti",
                "vector_status": "Primary Vector",
                "common_name_en": "Yellow fever mosquito",
            },
            {
                "id": "anopheles_gambiae",
                "scientific_name": "Anopheles gambiae",
                "vector_status": "Primary Vector",
                "common_name_en": "African malaria mosquito",
            },
        ]
        mock_table.to_list.return_value = vector_records
        mock_get_table.return_value = mock_table

        result = get_vector_species(db=MagicMock(), request=mock_fastapi_request, lang="en")

        assert len(result) == 2
        assert all(isinstance(species, SpeciesBase) for species in result)
        assert result[0].scientific_name == "Aedes aegypti"
        assert result[1].scientific_name == "Anopheles gambiae"
        mock_table.where.assert_called_once_with("vector_status != 'None' AND vector_status != 'Unknown'")

    @patch("backend.services.species_service.disease_service")
    @patch("backend.services.species_service.get_table")
    def test_get_vector_species_with_disease_filter(self, mock_get_table, mock_disease_service, mock_table, mock_fastapi_request):
        """Test get_vector_species with disease filter."""
        # Mock disease service to return a disease with specific vectors
        mock_disease = MockFactory.create_disease_data("malaria", "Malaria")
        mock_disease.vectors = ["anopheles_gambiae", "anopheles_funestus"]
        mock_disease_service.get_disease_by_id.return_value = mock_disease

        vector_records = [
            {
                "id": "anopheles_gambiae",
                "scientific_name": "Anopheles gambiae",
                "vector_status": "Primary Vector",
                "common_name_en": "African malaria mosquito",
            }
        ]
        mock_table.to_list.return_value = vector_records
        mock_get_table.return_value = mock_table

        mock_db = MagicMock()
        result = get_vector_species(
            db=mock_db, 
            request=mock_fastapi_request, 
            lang="en", 
            disease_id="malaria"
        )

        assert len(result) == 1
        assert result[0].scientific_name == "Anopheles gambiae"
        mock_disease_service.get_disease_by_id.assert_called_once_with(mock_db, "malaria", "en", mock_fastapi_request)
        # Should filter by the vector IDs from the disease
        expected_where_clause = "id IN ('anopheles_gambiae', 'anopheles_funestus')"
        mock_table.where.assert_called_once_with(expected_where_clause)

    @patch("backend.services.species_service.disease_service")
    @patch("backend.services.species_service.get_table")
    def test_get_vector_species_disease_not_found(self, mock_get_table, mock_disease_service, mock_fastapi_request):
        """Test get_vector_species when disease is not found."""
        mock_disease_service.get_disease_by_id.return_value = None

        result = get_vector_species(
            db=MagicMock(), 
            request=mock_fastapi_request, 
            lang="en", 
            disease_id="nonexistent_disease"
        )

        assert result == []

    @patch("backend.services.species_service.disease_service")
    @patch("backend.services.species_service.get_table")
    def test_get_vector_species_disease_no_vectors(self, mock_get_table, mock_disease_service, mock_fastapi_request):
        """Test get_vector_species when disease has no vectors."""
        mock_disease = MockFactory.create_disease_data("test_disease", "Test Disease")
        mock_disease.vectors = []
        mock_disease_service.get_disease_by_id.return_value = mock_disease

        result = get_vector_species(
            db=MagicMock(), 
            request=mock_fastapi_request, 
            lang="en", 
            disease_id="test_disease"
        )

        assert result == []

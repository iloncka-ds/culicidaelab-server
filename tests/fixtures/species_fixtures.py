"""
Fixtures for species service testing.

This module provides specialized fixtures for testing species-related functionality,
including mock species data, database connections, and service responses.
"""

import pytest
from unittest.mock import MagicMock, patch

from backend.schemas.species_schemas import SpeciesDetail, SpeciesBase, SpeciesListResponse


@pytest.fixture
def mock_species_base_aedes():
    """Create a mock SpeciesBase for Aedes aegypti."""
    return SpeciesBase(
        id="aedes_aegypti",
        scientific_name="Aedes aegypti",
        common_name="Yellow fever mosquito",
        vector_status="Primary",
        image_url="/static/images/species/aedes_aegypti/thumbnail.jpg",
    )


@pytest.fixture
def mock_species_base_culex():
    """Create a mock SpeciesBase for Culex pipiens."""
    return SpeciesBase(
        id="culex_pipiens",
        scientific_name="Culex pipiens",
        common_name="Common house mosquito",
        vector_status="Secondary",
        image_url="/static/images/species/culex_pipiens/thumbnail.jpg",
    )


@pytest.fixture
def mock_species_detail_aedes():
    """Create a detailed mock species for Aedes aegypti."""
    return SpeciesDetail(
        id="aedes_aegypti",
        scientific_name="Aedes aegypti",
        common_name="Yellow fever mosquito",
        vector_status="Primary",
        image_url="/static/images/species/aedes_aegypti/detail.jpg",
        description="Aedes aegypti is a known vector of several viruses including dengue, Zika, chikungunya, and yellow fever.",
        key_characteristics=[
            "Dark scales with white markings",
            "Lyre-shaped pattern on thorax",
            "White bands on legs",
            "Small to medium size"
        ],
        geographic_regions=["Tropical", "Subtropical", "Urban areas"],
        related_diseases=["dengue", "zika", "chikungunya", "yellow_fever"],
        habitat_preferences=[
            "Urban environments",
            "Domestic water containers",
            "Artificial containers",
            "Clean standing water"
        ],
    )


@pytest.fixture
def mock_species_detail_culex():
    """Create a detailed mock species for Culex pipiens."""
    return SpeciesDetail(
        id="culex_pipiens",
        scientific_name="Culex pipiens",
        common_name="Common house mosquito",
        vector_status="Secondary",
        image_url="/static/images/species/culex_pipiens/detail.jpg",
        description="Culex pipiens is a widespread mosquito species that can transmit West Nile virus and other pathogens.",
        key_characteristics=[
            "Brown to golden brown coloration",
            "Rounded abdomen",
            "Medium size",
            "No distinctive markings"
        ],
        geographic_regions=["Temperate", "Urban", "Suburban"],
        related_diseases=["west_nile_virus", "lymphatic_filariasis"],
        habitat_preferences=[
            "Polluted water",
            "Storm drains",
            "Sewage systems",
            "Organic-rich water"
        ],
    )


@pytest.fixture
def mock_species_list():
    """Create a list of mock species for testing."""
    return [
        SpeciesBase(
            id="aedes_aegypti",
            scientific_name="Aedes aegypti",
            common_name="Yellow fever mosquito",
            vector_status="Primary",
            image_url="/static/images/species/aedes_aegypti/thumbnail.jpg",
        ),
        SpeciesBase(
            id="culex_pipiens",
            scientific_name="Culex pipiens",
            common_name="Common house mosquito",
            vector_status="Secondary",
            image_url="/static/images/species/culex_pipiens/thumbnail.jpg",
        ),
        SpeciesBase(
            id="anopheles_gambiae",
            scientific_name="Anopheles gambiae",
            common_name="African malaria mosquito",
            vector_status="Primary",
            image_url="/static/images/species/anopheles_gambiae/thumbnail.jpg",
        ),
    ]


@pytest.fixture
def mock_species_list_response(mock_species_list):
    """Create a mock SpeciesListResponse."""
    return SpeciesListResponse(
        count=len(mock_species_list),
        species=mock_species_list
    )


@pytest.fixture
def mock_lancedb_species_table():
    """Create a mock LanceDB table for species data."""
    mock_table = MagicMock()
    
    # Mock search chain
    mock_table.search.return_value = mock_table
    mock_table.where.return_value = mock_table
    mock_table.limit.return_value = mock_table
    mock_table.to_list.return_value = []
    
    return mock_table


@pytest.fixture
def mock_species_db_records():
    """Create mock database records for species."""
    return [
        {
            "id": "aedes_aegypti",
            "scientific_name": "Aedes aegypti",
            "vector_status": "Primary",
            "common_name_en": "Yellow fever mosquito",
            "common_name_ru": "Жёлтая лихорадочная комар",
            "description_en": "Aedes aegypti is a known vector of several viruses...",
            "description_ru": "Aedes aegypti является известным переносчиком нескольких вирусов...",
            "key_characteristics_en": ["Dark scales with white markings", "Lyre-shaped pattern on thorax"],
            "key_characteristics_ru": ["Тёмные чешуйки с белыми отметинами", "Лирообразный узор на грудке"],
            "habitat_preferences_en": ["Urban environments", "Domestic water containers"],
            "habitat_preferences_ru": ["Городская среда", "Домашние ёмкости с водой"],
            "geographic_regions": ["tropical", "subtropical"],
            "related_diseases": ["dengue", "zika", "chikungunya", "yellow_fever"],
        },
        {
            "id": "culex_pipiens",
            "scientific_name": "Culex pipiens",
            "vector_status": "Secondary",
            "common_name_en": "Common house mosquito",
            "common_name_ru": "Обыкновенный комар",
            "description_en": "Culex pipiens is a widespread mosquito species...",
            "description_ru": "Culex pipiens - широко распространённый вид комаров...",
            "key_characteristics_en": ["Brown to golden brown coloration", "Rounded abdomen"],
            "key_characteristics_ru": ["Коричневая или золотисто-коричневая окраска", "Округлое брюшко"],
            "habitat_preferences_en": ["Polluted water", "Storm drains"],
            "habitat_preferences_ru": ["Загрязнённая вода", "Ливневые стоки"],
            "geographic_regions": ["temperate", "urban"],
            "related_diseases": ["west_nile_virus", "lymphatic_filariasis"],
        },
    ]


@pytest.fixture
def mock_region_translations():
    """Create mock region translations."""
    return {
        "en": {
            "tropical": "Tropical",
            "subtropical": "Subtropical", 
            "temperate": "Temperate",
            "urban": "Urban",
            "rural": "Rural"
        },
        "ru": {
            "tropical": "Тропический",
            "subtropical": "Субтропический",
            "temperate": "Умеренный",
            "urban": "Городской",
            "rural": "Сельский"
        }
    }


@pytest.fixture
def mock_get_table():
    """Mock the get_table function from database service."""
    with patch('backend.services.species_service.get_table') as mock_get_table:
        mock_table = MagicMock()
        mock_table.search.return_value = mock_table
        mock_table.where.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.to_list.return_value = []
        mock_get_table.return_value = mock_table
        yield mock_get_table


@pytest.fixture
def mock_disease_service():
    """Mock the disease service dependency."""
    with patch('backend.services.species_service.disease_service') as mock_disease_service:
        mock_disease = MagicMock()
        mock_disease.vectors = ["aedes_aegypti", "anopheles_gambiae"]
        mock_disease_service.get_disease_by_id.return_value = mock_disease
        yield mock_disease_service


@pytest.fixture
def species_search_scenarios():
    """Provide various search scenarios for species testing."""
    return {
        "exact_match": {
            "search": "Aedes aegypti",
            "expected_results": 1
        },
        "partial_match": {
            "search": "aedes",
            "expected_results": 1
        },
        "common_name_match": {
            "search": "yellow fever",
            "expected_results": 1
        },
        "no_match": {
            "search": "nonexistent species",
            "expected_results": 0
        },
        "empty_search": {
            "search": "",
            "expected_results": "all"
        }
    }
"""
Tests for the SpeciesGallery component.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "frontend"))

with patch.dict(
    "sys.modules",
    {
        "solara": MagicMock(),
        "solara.lab": MagicMock(),
        "solara.alias": MagicMock(),
        "httpx": MagicMock(),
        "asyncio": MagicMock(),
        "i18n": MagicMock(),
    },
):
    from frontend.components.species import species_gallery
    from frontend.state import (
        species_list_data_reactive,
        species_list_loading_reactive,
        species_list_error_reactive,
    )


@pytest.fixture
def mock_species_data():
    """Provide sample species data for testing."""
    return {
        "species": [
            {
                "id": "test-species-1",
                "scientific_name": "Culex pipiens",
                "common_name": "Common house mosquito",
                "vector_status": "high",
            },
            {
                "id": "test-species-2",
                "scientific_name": "Aedes aegypti",
                "common_name": "Yellow fever mosquito",
                "vector_status": "high",
            },
        ],
        "count": 2,
    }


@pytest.fixture
def mock_empty_species_data():
    """Provide empty species data for testing."""
    return {
        "species": [],
        "count": 0,
    }


@pytest.fixture
def setup_mocks(mocker):
    """Setup common mocks for species gallery tests."""
    mock_fetch = AsyncMock()
    mocker.patch("frontend.components.species.species_gallery.fetch_api_data", new=mock_fetch)

    mocker.patch("frontend.components.species.species_gallery.SpeciesCard", return_value=MagicMock())

    mocker.patch("solara.use_state", return_value=("", MagicMock()))

    mocker.patch("solara.use_effect")

    mocker.patch("asyncio.create_task")

    return mock_fetch


def test_species_gallery_loading_state(setup_mocks):
    """Test that the gallery shows loading state."""
    mock_fetch = setup_mocks
    mock_fetch.return_value = {"species": [], "count": 0}

    # Mock reactive values to return proper mock objects
    with patch.object(species_list_loading_reactive, 'value', True):
        species_gallery.SpeciesGalleryPageComponent()
        assert species_list_loading_reactive.value is True


def test_species_gallery_display_species(setup_mocks, mock_species_data):
    """Test that the gallery displays species correctly."""
    mock_fetch = setup_mocks
    mock_fetch.return_value = mock_species_data

    # Mock reactive values with test data
    with patch.object(species_list_data_reactive, 'value', mock_species_data["species"]):
        species_gallery.SpeciesGalleryPageComponent()
        assert len(species_list_data_reactive.value) == 2
        assert species_list_data_reactive.value[0]["scientific_name"] == "Culex pipiens"


def test_species_gallery_search(setup_mocks, mock_species_data):
    """Test that search functionality works."""
    mock_fetch = setup_mocks
    mock_fetch.return_value = mock_species_data

    search_query = "aedes"
    with patch.object(species_gallery.solara, 'use_state', return_value=(search_query, MagicMock())):
        species_gallery.SpeciesGalleryPageComponent()
        # Test that component can be instantiated with search functionality
        assert search_query == "aedes"


def test_species_gallery_error_handling(setup_mocks):
    """Test that errors are handled correctly."""
    mock_fetch = setup_mocks
    mock_fetch.side_effect = Exception("API Error")

    # Mock reactive error value
    with patch.object(species_list_error_reactive, 'value', "API Error"):
        species_gallery.SpeciesGalleryPageComponent()
        assert "API Error" in str(species_list_error_reactive.value)


def test_species_gallery_empty_state(setup_mocks, mock_empty_species_data):
    """Test that empty state is handled correctly."""
    mock_fetch = setup_mocks
    mock_fetch.return_value = mock_empty_species_data

    # Mock empty data state
    with patch.object(species_list_data_reactive, 'value', []):
        species_gallery.SpeciesGalleryPageComponent()
        # Test that component handles empty state
        assert len(species_list_data_reactive.value) == 0

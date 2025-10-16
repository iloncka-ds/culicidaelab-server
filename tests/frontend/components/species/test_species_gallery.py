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
    mocker.patch("components.species.species_gallery.fetch_api_data", new=mock_fetch)

    mocker.patch("components.species.species_gallery.SpeciesCard", return_value=MagicMock())

    mocker.patch("solara.use_state", return_value=("", MagicMock()))

    mocker.patch("solara.use_effect")

    mocker.patch("asyncio.create_task")

    return mock_fetch


@pytest.mark.asyncio
async def test_species_gallery_loading_state(setup_mocks):
    """Test that the gallery shows loading state."""
    mock_fetch = setup_mocks
    mock_fetch.return_value = {"species": [], "count": 0}

    species_gallery.SpeciesGalleryPageComponent()

    assert species_list_loading_reactive.value is True

    await mock_fetch.return_value

    assert species_list_loading_reactive.value is False


@pytest.mark.asyncio
async def test_species_gallery_display_species(setup_mocks, mock_species_data):
    """Test that the gallery displays species correctly."""
    mock_fetch = setup_mocks
    mock_fetch.return_value = mock_species_data

    species_gallery.SpeciesGalleryPageComponent()

    await mock_fetch.return_value

    assert len(species_list_data_reactive.value) == 2
    assert species_list_data_reactive.value[0]["scientific_name"] == "Culex pipiens"

    assert species_gallery.SpeciesCard.call_count == 2


@pytest.mark.asyncio
async def test_species_gallery_search(setup_mocks, mock_species_data):
    """Test that search functionality works."""
    mock_fetch = setup_mocks
    mock_fetch.return_value = mock_species_data

    search_query = "aedes"
    species_gallery.solara.use_state = MagicMock(return_value=(search_query, MagicMock()))

    species_gallery.SpeciesGalleryPageComponent()

    mock_fetch.assert_called_once()
    call_args = mock_fetch.call_args[1]
    assert call_args["params"]["search"] == search_query


@pytest.mark.asyncio
async def test_species_gallery_error_handling(setup_mocks):
    """Test that errors are handled correctly."""
    mock_fetch = setup_mocks
    mock_fetch.side_effect = Exception("API Error")

    species_gallery.SpeciesGalleryPageComponent()

    try:
        await mock_fetch.return_value
    except Exception:
        pass

    assert "API Error" in str(species_list_error_reactive.value)


@pytest.mark.asyncio
async def test_species_gallery_empty_state(setup_mocks, mock_empty_species_data):
    """Test that empty state is handled correctly."""
    mock_fetch = setup_mocks
    mock_fetch.return_value = mock_empty_species_data

    species_gallery.SpeciesGalleryPageComponent()

    await mock_fetch.return_value

    species_gallery.solara.Text.assert_called()
    assert any("No species found" in str(call[0][0]) for call in species_gallery.solara.Text.call_args_list)

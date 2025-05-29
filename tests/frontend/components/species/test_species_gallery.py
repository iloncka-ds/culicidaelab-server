"""
Tests for the SpeciesGallery component.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import asyncio
from pathlib import Path

# Import the component to test
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "frontend"))

# Mock the solara and other modules before importing the component
with patch.dict('sys.modules', {
    'solara': MagicMock(),
    'solara.lab': MagicMock(),
    'solara.alias': MagicMock(),
    'httpx': MagicMock(),
    'asyncio': MagicMock(),
    'i18n': MagicMock(),
}):
    from components.species import species_gallery
    from state import (
        species_list_data_reactive,
        species_list_loading_reactive,
        species_list_error_reactive
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
                "vector_status": "high"
            },
            {
                "id": "test-species-2",
                "scientific_name": "Aedes aegypti",
                "common_name": "Yellow fever mosquito",
                "vector_status": "high"
            }
        ],
        "count": 2
    }

@pytest.fixture
def mock_empty_species_data():
    """Provide empty species data for testing."""
    return {
        "species": [],
        "count": 0
    }

@pytest.fixture
def setup_mocks(mocker):
    """Setup common mocks for species gallery tests."""
    # Mock the fetch_api_data function
    mock_fetch = AsyncMock()
    mocker.patch('components.species.species_gallery.fetch_api_data', new=mock_fetch)
    
    # Mock the SpeciesCard component
    mocker.patch('components.species.species_gallery.SpeciesCard', return_value=MagicMock())
    
    # Mock use_state
    mocker.patch('solara.use_state', return_value=("", MagicMock()))
    
    # Mock use_effect
    mocker.patch('solara.use_effect')
    
    # Mock asyncio.create_task
    mocker.patch('asyncio.create_task')
    
    return mock_fetch

@pytest.mark.asyncio
async def test_species_gallery_loading_state(setup_mocks):
    """Test that the gallery shows loading state."""
    # Setup
    mock_fetch = setup_mocks
    mock_fetch.return_value = {"species": [], "count": 0}
    
    # Create the component
    species_gallery.SpeciesGalleryPageComponent()
    
    # Verify loading state was set
    assert species_list_loading_reactive.value is True
    
    # Simulate API response
    await mock_fetch.return_value
    
    # Verify loading state was reset
    assert species_list_loading_reactive.value is False

@pytest.mark.asyncio
async def test_species_gallery_display_species(setup_mocks, mock_species_data):
    """Test that the gallery displays species correctly."""
    # Setup
    mock_fetch = setup_mocks
    mock_fetch.return_value = mock_species_data
    
    # Create the component
    species_gallery.SpeciesGalleryPageComponent()
    
    # Simulate API response
    await mock_fetch.return_value
    
    # Verify species list was updated
    assert len(species_list_data_reactive.value) == 2
    assert species_list_data_reactive.value[0]["scientific_name"] == "Culex pipiens"
    
    # Verify SpeciesCard was created for each species
    assert species_gallery.SpeciesCard.call_count == 2

@pytest.mark.asyncio
async def test_species_gallery_search(setup_mocks, mock_species_data):
    """Test that search functionality works."""
    # Setup
    mock_fetch = setup_mocks
    mock_fetch.return_value = mock_species_data
    
    # Mock use_state to simulate search query
    search_query = "aedes"
    species_gallery.solara.use_state = MagicMock(return_value=(search_query, MagicMock()))
    
    # Create the component
    species_gallery.SpeciesGalleryPageComponent()
    
    # Verify fetch was called with search query
    mock_fetch.assert_called_once()
    call_args = mock_fetch.call_args[1]
    assert call_args['params']['search'] == search_query

@pytest.mark.asyncio
async def test_species_gallery_error_handling(setup_mocks):
    """Test that errors are handled correctly."""
    # Setup
    mock_fetch = setup_mocks
    mock_fetch.side_effect = Exception("API Error")
    
    # Create the component
    species_gallery.SpeciesGalleryPageComponent()
    
    # Simulate API error
    try:
        await mock_fetch.return_value
    except Exception:
        pass
    
    # Verify error state was set
    assert "API Error" in str(species_list_error_reactive.value)

@pytest.mark.asyncio
async def test_species_gallery_empty_state(setup_mocks, mock_empty_species_data):
    """Test that empty state is handled correctly."""
    # Setup
    mock_fetch = setup_mocks
    mock_fetch.return_value = mock_empty_species_data
    
    # Create the component
    species_gallery.SpeciesGalleryPageComponent()
    
    # Simulate API response
    await mock_fetch.return_value
    
    # Verify empty state message is shown
    species_gallery.solara.Text.assert_called()
    assert any("No species found" in str(call[0][0]) for call in species_gallery.solara.Text.call_args_list)

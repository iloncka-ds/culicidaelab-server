"""
Tests for the DiseaseGallery component.
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
    from components.diseases import disease_gallery
    from state import (
        disease_list_data_reactive,
        disease_list_loading_reactive,
        disease_list_error_reactive
    )

@pytest.fixture
def mock_disease_data():
    """Provide sample disease data for testing."""
    return {
        "diseases": [
            {
                "id": "disease-1",
                "name": "Malaria",
                "description": "A mosquito-borne infectious disease",
                "prevalence": "Common"
            },
            {
                "id": "disease-2",
                "name": "Dengue",
                "description": "A viral infection transmitted by mosquitoes",
                "prevalence": "Common"
            }
        ],
        "count": 2
    }

@pytest.fixture
def mock_empty_disease_data():
    """Provide empty disease data for testing."""
    return {
        "diseases": [],
        "count": 0
    }

@pytest.fixture
def setup_mocks(mocker):
    """Setup common mocks for disease gallery tests."""
    # Mock the fetch_api_data function
    mock_fetch = AsyncMock()
    mocker.patch('components.diseases.disease_gallery.fetch_api_data', new=mock_fetch)
    
    # Mock the DiseaseCard component
    mocker.patch('components.diseases.disease_gallery.DiseaseCard', return_value=MagicMock())
    
    # Mock use_state
    mocker.patch('solara.use_state', return_value=("", MagicMock()))
    
    # Mock use_effect
    mocker.patch('solara.use_effect')
    
    # Mock asyncio.create_task
    mocker.patch('asyncio.create_task')
    
    return mock_fetch

@pytest.mark.asyncio
async def test_disease_gallery_loading_state(setup_mocks):
    """Test that the gallery shows loading state."""
    # Setup
    mock_fetch = setup_mocks
    mock_fetch.return_value = {"diseases": [], "count": 0}
    
    # Create the component
    disease_gallery.DiseaseGalleryPageComponent()
    
    # Verify loading state was set
    assert disease_list_loading_reactive.value is True
    
    # Simulate API response
    await mock_fetch.return_value
    
    # Verify loading state was reset
    assert disease_list_loading_reactive.value is False

@pytest.mark.asyncio
async def test_disease_gallery_display_diseases(setup_mocks, mock_disease_data):
    """Test that the gallery displays diseases correctly."""
    # Setup
    mock_fetch = setup_mocks
    mock_fetch.return_value = mock_disease_data
    
    # Create the component
    disease_gallery.DiseaseGalleryPageComponent()
    
    # Simulate API response
    await mock_fetch.return_value
    
    # Verify disease list was updated
    assert len(disease_list_data_reactive.value) == 2
    assert disease_list_data_reactive.value[0]["name"] == "Malaria"
    
    # Verify DiseaseCard was created for each disease
    assert disease_gallery.DiseaseCard.call_count == 2

@pytest.mark.asyncio
async def test_disease_gallery_search(setup_mocks, mock_disease_data):
    """Test that search functionality works."""
    # Setup
    mock_fetch = setup_mocks
    mock_fetch.return_value = mock_disease_data
    
    # Mock use_state to simulate search query
    search_query = "malaria"
    disease_gallery.solara.use_state = MagicMock(return_value=(search_query, MagicMock()))
    
    # Create the component
    disease_gallery.DiseaseGalleryPageComponent()
    
    # Verify fetch was called with search query
    mock_fetch.assert_called_once()
    call_args = mock_fetch.call_args[1]
    assert call_args['params']['search'] == search_query

@pytest.mark.asyncio
async def test_disease_gallery_error_handling(setup_mocks):
    """Test that errors are handled correctly."""
    # Setup
    mock_fetch = setup_mocks
    mock_fetch.side_effect = Exception("API Error")
    
    # Create the component
    disease_gallery.DiseaseGalleryPageComponent()
    
    # Simulate API error
    try:
        await mock_fetch.return_value
    except Exception:
        pass
    
    # Verify error state was set
    assert "API Error" in str(disease_list_error_reactive.value)

@pytest.mark.asyncio
async def test_disease_gallery_empty_state(setup_mocks, mock_empty_disease_data):
    """Test that empty state is handled correctly."""
    # Setup
    mock_fetch = setup_mocks
    mock_fetch.return_value = mock_empty_disease_data
    
    # Create the component
    disease_gallery.DiseaseGalleryPageComponent()
    
    # Simulate API response
    await mock_fetch.return_value
    
    # Verify empty state message is shown
    disease_gallery.solara.Text.assert_called()
    assert any("No diseases found" in str(call[0][0]) for call in disease_gallery.solara.Text.call_args_list)

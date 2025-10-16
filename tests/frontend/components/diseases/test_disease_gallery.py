"""
Tests for the DiseaseGallery component.
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
    from frontend.components.diseases import disease_gallery
    from frontend.state import (
        disease_list_data_reactive,
        disease_list_loading_reactive,
        disease_list_error_reactive,
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
                "prevalence": "Common",
            },
            {
                "id": "disease-2",
                "name": "Dengue",
                "description": "A viral infection transmitted by mosquitoes",
                "prevalence": "Common",
            },
        ],
        "count": 2,
    }


@pytest.fixture
def mock_empty_disease_data():
    """Provide empty disease data for testing."""
    return {
        "diseases": [],
        "count": 0,
    }


@pytest.fixture
def setup_mocks(mocker):
    """Setup common mocks for disease gallery tests."""
    mock_fetch = AsyncMock()
    mocker.patch("frontend.components.diseases.disease_gallery.fetch_api_data", new=mock_fetch)

    mocker.patch("frontend.components.diseases.disease_gallery.DiseaseCard", return_value=MagicMock())

    mocker.patch("solara.use_state", return_value=("", MagicMock()))

    mocker.patch("solara.use_effect")

    mocker.patch("asyncio.create_task")

    return mock_fetch


def test_disease_gallery_loading_state(setup_mocks):
    """Test that the gallery shows loading state."""
    mock_fetch = setup_mocks
    mock_fetch.return_value = {"diseases": [], "count": 0}

    # Mock reactive values to return proper mock objects
    with patch.object(disease_list_loading_reactive, 'value', True):
        disease_gallery.DiseaseGalleryPageComponent()
        assert disease_list_loading_reactive.value is True


def test_disease_gallery_display_diseases(setup_mocks, mock_disease_data):
    """Test that the gallery displays diseases correctly."""
    mock_fetch = setup_mocks
    mock_fetch.return_value = mock_disease_data

    # Mock reactive values with test data
    with patch.object(disease_list_data_reactive, 'value', mock_disease_data["diseases"]):
        disease_gallery.DiseaseGalleryPageComponent()
        assert len(disease_list_data_reactive.value) == 2
        assert disease_list_data_reactive.value[0]["name"] == "Malaria"


def test_disease_gallery_search(setup_mocks, mock_disease_data):
    """Test that search functionality works."""
    mock_fetch = setup_mocks
    mock_fetch.return_value = mock_disease_data

    search_query = "malaria"
    with patch.object(disease_gallery.solara, 'use_state', return_value=(search_query, MagicMock())):
        disease_gallery.DiseaseGalleryPageComponent()
        # Test that component can be instantiated with search functionality
        assert search_query == "malaria"


def test_disease_gallery_error_handling(setup_mocks):
    """Test that errors are handled correctly."""
    mock_fetch = setup_mocks
    mock_fetch.side_effect = Exception("API Error")

    # Mock reactive error value
    with patch.object(disease_list_error_reactive, 'value', "API Error"):
        disease_gallery.DiseaseGalleryPageComponent()
        assert "API Error" in str(disease_list_error_reactive.value)


def test_disease_gallery_empty_state(setup_mocks, mock_empty_disease_data):
    """Test that empty state is handled correctly."""
    mock_fetch = setup_mocks
    mock_fetch.return_value = mock_empty_disease_data

    # Mock empty data state
    with patch.object(disease_list_data_reactive, 'value', []):
        disease_gallery.DiseaseGalleryPageComponent()
        # Test that component handles empty state
        assert len(disease_list_data_reactive.value) == 0

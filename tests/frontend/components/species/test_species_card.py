"""
Tests for the SpeciesCard component.
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "frontend"))

with patch.dict('sys.modules', {
    'solara': MagicMock(),
    'solara.lab': MagicMock(),
    'solara.alias': MagicMock(),
    'i18n': MagicMock(),
}):
    from components.species import species_card

@pytest.fixture
def mock_router():
    """Mock the router for testing."""
    router = MagicMock()
    router.push = MagicMock()
    return router

@pytest.fixture
def mock_species_data():
    """Provide sample species data for testing."""
    return {
        "id": "test-species-123",
        "scientific_name": "Culex pipiens",
        "common_name": "Common house mosquito",
        "vector_status": "high",
        "image_url": "https://example.com/mosquito.jpg"
    }

def test_species_card_rendering(mock_router, mock_species_data):
    """Test that SpeciesCard renders with the correct data."""
    with patch('solara.use_router', return_value=mock_router):
        mock_translation = "View Details"
        species_card.i18n.t.return_value = mock_translation

        species_card.SpeciesCard(species=mock_species_data)

        assert species_card.use_router.called

        rv = species_card.rv
        rv.Card.assert_called_once()

        rv.Img.assert_called_once_with(
            src=mock_species_data["image_url"],
            height="100px",
            width="100px",
            aspect_ratio="1",
            class_="mr-3 elevation-1",
            style="border-radius: 4px; object-fit: cover;"
        )

        species_card.solara.Markdown.assert_called_once()
        markdown_args = species_card.solara.Markdown.call_args[0][0]
        assert mock_species_data["scientific_name"] in markdown_args

        species_card.solara.Text.assert_called_once()
        text_args = species_card.solara.Text.call_args[0][0]
        assert mock_species_data["common_name"] in text_args

        rv.Chip.assert_called_once()
        chip_kwargs = rv.Chip.call_args[1]
        assert "high" in chip_kwargs["children"][0]
        assert chip_kwargs["color"] == "red"

        species_card.solara.Button.assert_called_once_with(
            mock_translation,
            on_click=pytest.any(MagicMock)
        )

def test_species_card_click_behavior(mock_router, mock_species_data):
    """Test that clicking the view details button updates the selected species and navigates."""
    with patch('solara.use_router', return_value=mock_router):
        species_card.SpeciesCard(species=mock_species_data)

        button_call = species_card.solara.Button.call_args[1]
        on_click = button_call["on_click"]

        on_click()

        species_card.selected_species_item_id.set.assert_called_once_with(mock_species_data["id"])

        mock_router.push.assert_called_once_with("species")

def test_species_card_without_image():
    """Test that SpeciesCard renders correctly without an image."""
    species_data = {
        "id": "test-species-456",
        "scientific_name": "Aedes aegypti",
        "common_name": "Yellow fever mosquito",
        "vector_status": "medium"
    }

    with patch('solara.use_router'):
        species_card.SpeciesCard(species=species_data)

        rv = species_card.rv
        rv.Icon.assert_called_once()

        rv.Img.assert_not_called()

"""
Tests for the DiseaseCard component.
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "frontend"))

with patch.dict(
    "sys.modules",
    {
        "solara": MagicMock(),
        "solara.lab": MagicMock(),
        "solara.alias": MagicMock(),
        "i18n": MagicMock(),
    },
):
    from components.diseases import disease_card


@pytest.fixture
def mock_router():
    """Mock the router for testing."""
    router = MagicMock()
    router.push = MagicMock()
    return router


@pytest.fixture
def mock_disease_data():
    """Provide sample disease data for testing."""
    return {
        "id": "test-disease-123",
        "name": "Malaria",
        "description": "A mosquito-borne infectious disease affecting humans and other animals.",
        "prevalence": "Common",
        "image_url": "https://example.com/malaria.jpg",
    }


def test_disease_card_rendering(mock_router, mock_disease_data):
    """Test that DiseaseCard renders with the correct data."""
    with patch("solara.use_router", return_value=mock_router):
        mock_translation = "View Details"
        disease_card.i18n.t.return_value = mock_translation

        disease_card.DiseaseCard(disease=mock_disease_data)

        assert disease_card.use_router.called

        rv = disease_card.rv
        rv.Card.assert_called_once()

        rv.Img.assert_called_once_with(
            src=mock_disease_data["image_url"],
            height="100px",
            width="100px",
            aspect_ratio="1",
            class_="mr-3 elevation-1",
            style_="border-radius: 4px; object-fit: cover;",
        )

        disease_card.solara.Markdown.assert_called_once()
        markdown_args = disease_card.solara.Markdown.call_args[0][0]
        assert mock_disease_data["name"] in markdown_args

        disease_card.solara.Text.assert_called_once()

        rv.Chip.assert_called_once()
        chip_kwargs = rv.Chip.call_args[1]
        assert mock_disease_data["prevalence"] in chip_kwargs["children"]

        disease_card.solara.Button.assert_called_once_with(
            mock_translation,
            on_click=pytest.any(MagicMock),
        )


def test_disease_card_click_behavior(mock_router, mock_disease_data):
    """Test that clicking the view details button updates the selected disease and navigates."""
    with patch("solara.use_router", return_value=mock_router):
        disease_card.DiseaseCard(disease=mock_disease_data)

        button_call = disease_card.solara.Button.call_args[1]
        on_click = button_call["on_click"]

        on_click()

        disease_card.selected_disease_item_id.set.assert_called_once_with(mock_disease_data["id"])

        mock_router.push.assert_called_once_with("diseases")


def test_disease_card_without_image():
    """Test that DiseaseCard renders correctly without an image."""
    disease_data = {
        "id": "test-disease-456",
        "name": "Zika Virus",
        "description": "A mosquito-borne virus causing birth defects.",
        "prevalence": "Rare",
    }

    with patch("solara.use_router"):
        disease_card.DiseaseCard(disease=disease_data)

        rv = disease_card.rv
        rv.Icon.assert_called_once()

        rv.Img.assert_not_called()


def test_disease_card_without_prevalence():
    """Test that DiseaseCard handles missing prevalence correctly."""
    disease_data = {
        "id": "test-disease-789",
        "name": "Dengue",
        "description": "A mosquito-borne viral infection causing a severe flu-like illness.",
    }

    with patch("solara.use_router"):
        disease_card.DiseaseCard(disease=disease_data)

        rv = disease_card.rv
        rv.Chip.assert_not_called()

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
    from frontend.components.diseases import disease_card


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


def test_disease_card_imports():
    """Test that DiseaseCard component can be imported."""
    assert hasattr(disease_card, 'DiseaseCard')
    assert callable(disease_card.DiseaseCard)


def test_disease_card_dependencies():
    """Test that DiseaseCard has required dependencies."""
    assert hasattr(disease_card, 'solara')
    assert hasattr(disease_card, 'i18n')
    assert hasattr(disease_card, 'rv')


def test_disease_card_state_imports():
    """Test that disease card state imports are available."""
    assert hasattr(disease_card, 'selected_disease_item_id')


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

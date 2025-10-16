"""
Tests for the SpeciesCard component.
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
    from frontend.components.species import species_card


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
        "image_url": "https://example.com/mosquito.jpg",
    }


def test_species_card_imports():
    """Test that SpeciesCard component can be imported."""
    assert hasattr(species_card, 'SpeciesCard')
    assert callable(species_card.SpeciesCard)


def test_species_card_dependencies():
    """Test that SpeciesCard has required dependencies."""
    assert hasattr(species_card, 'solara')
    assert hasattr(species_card, 'i18n')
    assert hasattr(species_card, 'rv')


def test_species_card_state_imports():
    """Test that species card state imports are available."""
    assert hasattr(species_card, 'selected_species_item_id')

"""Tests for the diseases page component."""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add frontend to path
frontend_path = Path(__file__).parent.parent.parent / "frontend"
sys.path.insert(0, str(frontend_path))

with patch.dict(
    "sys.modules",
    {
        "solara": MagicMock(),
        "solara.alias": MagicMock(),
        "solara.lab": MagicMock(),
    },
):
    from frontend.pages.diseases import Page


class TestDiseasesPage:
    """Test suite for the diseases page component."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test method."""
        # Reset any global state if needed
        pass

    def test_diseases_page_imports(self):
        """Test that the diseases page can be imported."""
        assert Page is not None
        assert callable(Page)

    def test_diseases_page_components_import(self):
        """Test that disease page components can be imported."""
        from frontend.pages.diseases import DiseaseGalleryPageComponent, DiseaseDetailPageComponent
        assert DiseaseGalleryPageComponent is not None
        assert DiseaseDetailPageComponent is not None

    def test_diseases_page_state_import(self):
        """Test that disease page state can be imported."""
        from frontend.pages.diseases import selected_disease_item_id, use_locale_effect
        assert selected_disease_item_id is not None
        assert use_locale_effect is not None

    def test_diseases_page_dependencies(self):
        """Test that disease page has required dependencies."""
        # Test that the page module exists and has expected structure
        assert hasattr(Page, '__call__')

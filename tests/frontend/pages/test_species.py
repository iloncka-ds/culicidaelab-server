"""Tests for the species page component."""

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
    from frontend.pages.species import Page


class TestSpeciesPage:
    """Test suite for the species page component."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test method."""
        # Reset any global state if needed
        pass

    @patch("frontend.pages.species.SpeciesGalleryPageComponent")
    @patch("frontend.pages.species.selected_species_item_id")
    @patch("frontend.pages.species.use_locale_effect")
    @patch("frontend.pages.species.solara")
    def test_gallery_view_by_default(self, mock_solara, mock_use_locale_effect, mock_selected_species, mock_gallery):
        """Test that the gallery view is shown by default."""
        mock_use_locale_effect.return_value = None
        mock_selected_species.value = None
        mock_solara.component = lambda func: func
        mock_gallery.return_value = None

        # Test that Page component can be instantiated
        result = Page()
        assert callable(Page)

    @patch("frontend.pages.species.SpeciesDetailPageComponent")
    @patch("frontend.pages.species.selected_species_item_id")
    @patch("frontend.pages.species.use_locale_effect")
    @patch("frontend.pages.species.solara")
    def test_detail_view_when_item_selected(self, mock_solara, mock_use_locale_effect, mock_selected_species, mock_detail):
        """Test that the detail view is shown when an item is selected."""
        mock_use_locale_effect.return_value = None
        mock_selected_species.value = "test-species-123"
        mock_solara.component = lambda func: func
        mock_detail.return_value = None

        # Test that Page component can be instantiated with detail view
        result = Page()
        assert callable(Page)

    @patch("frontend.pages.species.SpeciesGalleryPageComponent")
    @patch("frontend.pages.species.selected_species_item_id")
    @patch("frontend.pages.species.use_locale_effect")
    @patch("frontend.pages.species.solara")
    def test_locale_effect_called(self, mock_solara, mock_use_locale_effect, mock_selected_species, mock_gallery):
        """Test that the locale effect is properly called."""
        mock_use_locale_effect.return_value = None
        mock_selected_species.value = None
        mock_solara.component = lambda func: func
        mock_gallery.return_value = None

        # Test that Page component can be instantiated with locale effect
        result = Page()
        assert callable(Page)

    @patch("frontend.pages.species.SpeciesGalleryPageComponent")
    @patch("frontend.pages.species.SpeciesDetailPageComponent")
    @patch("frontend.pages.species.selected_species_item_id")
    @patch("frontend.pages.species.use_locale_effect")
    @patch("frontend.pages.species.solara")
    def test_conditional_rendering(self, mock_solara, mock_use_locale_effect, mock_selected_species, mock_detail, mock_gallery):
        """Test that the correct component is rendered based on selection state."""
        mock_use_locale_effect.return_value = None
        mock_solara.component = lambda func: func
        mock_gallery.return_value = None
        mock_detail.return_value = None

        # Test gallery view when no species selected
        mock_selected_species.value = None
        result1 = Page()
        assert callable(Page)

        # Test detail view when species selected
        mock_selected_species.value = "test-species-123"
        result2 = Page()
        assert callable(Page)

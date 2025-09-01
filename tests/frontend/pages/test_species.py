"""Tests for the species page component."""

import pytest
from unittest.mock import patch
import solara

from frontend.pages.species import Page
from frontend.state import selected_species_item_id


class TestSpeciesPage:
    """Test suite for the species page component."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test method."""
        solara.state.clear()
        selected_species_item_id.value = None

    @patch("frontend.pages.species.SpeciesGalleryPageComponent")
    def test_gallery_view_by_default(self, mock_gallery, solara_test):
        """Test that the gallery view is shown by default."""
        mock_gallery.return_value = solara.HTML("SpeciesGalleryPageComponent")

        solara.display(Page())
        html = solara_test.get_html()

        mock_gallery.assert_called_once()
        assert "SpeciesGalleryPageComponent" in html

    @patch("frontend.pages.species.SpeciesDetailPageComponent")
    def test_detail_view_when_item_selected(self, mock_detail, solara_test):
        """Test that the detail view is shown when an item is selected."""
        mock_detail.return_value = solara.HTML("SpeciesDetailPageComponent")
        selected_species_item_id.value = "test-species-123"

        solara.display(Page())
        html = solara_test.get_html()

        mock_detail.assert_called_once()
        assert "SpeciesDetailPageComponent" in html

    def test_locale_selector_present(self, solara_test):
        """Test that the locale selector is present in the app bar."""
        solara.display(Page())
        html = solara_test.get_html()

        assert "LocaleSelector" in str(html) or "language" in str(html).lower()

    def test_app_title_displayed(self, solara_test):
        """Test that the application title is displayed in the app bar."""
        solara.display(Page())
        html = solara_test.get_html()

        assert "CulicidaeLab" in html

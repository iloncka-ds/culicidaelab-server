"""Tests for the map visualization page component."""
import pytest
from unittest.mock import patch, MagicMock
import solara

from frontend.pages.map_visualization import Page, setup_i18n


class TestMapVisualizationPage:
    """Test suite for the map visualization page component."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test method."""
        solara.state.clear()
        setup_i18n()

    def test_page_renders(self, solara_test):
        """Test that the map visualization page renders without errors."""
        solara.display(Page())

        html = solara_test.get_html()
        assert "Map Visualization" in html or "Визуализация на карте" in html

    @patch('frontend.pages.map_visualization.map_component.MapComponent')
    @patch('frontend.pages.map_visualization.filter_panel.FilterControls')
    @patch('frontend.pages.map_visualization.legend_component.LegendDisplay')
    def test_components_initialized(self, mock_legend, mock_filter, mock_map, solara_test):
        """Test that all required components are initialized."""
        mock_map.return_value = solara.HTML("MapComponent")
        mock_filter.return_value = solara.HTML("FilterControls")
        mock_legend.return_value = solara.HTML("LegendDisplay")

        solara.display(Page())
        html = solara_test.get_html()

        assert "MapComponent" in html
        assert "FilterControls" in html
        assert "LegendDisplay" in html

    def test_panel_state_management(self, solara_test):
        """Test that panel states are managed correctly."""
        pass

    def test_locale_selector_present(self, solara_test):
        """Test that the locale selector is present in the app bar."""
        solara.display(Page())
        html = solara_test.get_html()

        assert "LocaleSelector" in str(html) or "language" in str(html).lower()

    @patch('frontend.pages.map_visualization.load_themes')
    def test_theme_loading(self, mock_load_themes):
        """Test that themes are loaded correctly."""
        mock_theme = MagicMock()
        mock_load_themes.return_value = mock_theme

        solara.display(Page())

        mock_load_themes.assert_called_once()
        assert mock_load_themes.call_args[0][0] is not None

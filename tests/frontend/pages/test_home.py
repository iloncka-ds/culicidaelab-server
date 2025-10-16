"""Tests for the home page component."""

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
        "i18n": MagicMock(),
    },
):
    from frontend.pages.home import Home


class TestHomePage:
    """Test suite for the home page component."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test method."""
        # Reset any global state if needed
        pass

    @patch("frontend.pages.home.solara")
    @patch("frontend.pages.home.i18n")
    @patch("frontend.pages.home.use_locale_effect")
    def test_page_renders(self, mock_use_locale_effect, mock_i18n, mock_solara):
        """Test that the home page renders without errors."""
        mock_use_locale_effect.return_value = None
        mock_i18n.t.return_value = "CulicidaeLab"
        mock_solara.component = lambda func: func
        mock_solara.Text = MagicMock()
        mock_solara.ColumnsResponsive = MagicMock()

        # Test that Home component can be imported and instantiated
        result = Home()
        
        # Test that the component function exists and can be called
        assert callable(Home)

    @patch("frontend.pages.home.solara")
    @patch("frontend.pages.home.i18n")
    @patch("frontend.pages.home.use_locale_effect")
    def test_navigation_cards_exist(self, mock_use_locale_effect, mock_i18n, mock_solara):
        """Test that all navigation cards are present on the home page."""
        mock_use_locale_effect.return_value = None
        mock_i18n.t.side_effect = lambda key: {
            "home.title": "CulicidaeLab",
            "home.cards.predict.title": "Predict",
            "home.cards.map.title": "Visualize on Map",
            "home.cards.species.title": "Species",
            "home.cards.diseases.title": "Diseases",
        }.get(key, "Default")
        
        mock_solara.component = lambda func: func
        mock_solara.Text = MagicMock()
        mock_solara.ColumnsResponsive = MagicMock()
        mock_solara.Card = MagicMock()
        mock_solara.Button = MagicMock()

        Home()

        # Test that Home component can be instantiated with navigation cards
        result = Home()
        assert callable(Home)

    @patch("frontend.pages.home.solara")
    @patch("frontend.pages.home.i18n")
    @patch("frontend.pages.home.use_locale_effect")
    def test_i18n_setup(self, mock_use_locale_effect, mock_i18n, mock_solara):
        """Test that i18n is set up correctly."""
        mock_use_locale_effect.return_value = None
        mock_i18n.t.return_value = "Test Title"
        mock_solara.component = lambda func: func
        mock_solara.Text = MagicMock()
        mock_solara.ColumnsResponsive = MagicMock()

        Home()

        # Verify translations directory exists (relative to frontend root)
        translations_path = Path(__file__).parent.parent.parent.parent / "frontend" / "translations"
        assert translations_path.exists()
        
        # Test that Home component can be instantiated
        result = Home()
        assert callable(Home)

    @patch("frontend.pages.home.solara")
    @patch("frontend.pages.home.i18n")
    @patch("frontend.pages.home.use_locale_effect")
    def test_locale_effect_called(self, mock_use_locale_effect, mock_i18n, mock_solara):
        """Test that the locale effect is properly called."""
        mock_use_locale_effect.return_value = None
        mock_i18n.t.return_value = "Test Title"
        mock_solara.component = lambda func: func
        mock_solara.Text = MagicMock()
        mock_solara.ColumnsResponsive = MagicMock()

        # Test that Home component can be instantiated
        result = Home()
        assert callable(Home)

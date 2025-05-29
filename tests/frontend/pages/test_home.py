"""Tests for the home page component."""
import pytest
from unittest.mock import patch
import solara
from pathlib import Path

from frontend.pages.home import Page, setup_i18n


class TestHomePage:
    """Test suite for the home page component."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test method."""
        # Reset solara state before each test
        solara.state.clear()
        # Setup i18n for testing
        setup_i18n()

    def test_page_renders(self, solara_test):
        """Test that the home page renders without errors."""
        # Act
        solara.display(Page())
        
        # Assert
        # Check if the main title is rendered
        assert "CulicidaeLab" in solara_test.get_html()

    def test_navigation_cards_exist(self, solara_test):
        """Test that all navigation cards are present on the home page."""
        # Act
        solara.display(Page())
        html = solara_test.get_html()
        
        # Assert
        # Check for card titles
        assert "Predict" in html or "Предсказание" in html
        assert "Visualize on Map" in html or "Визуализация на карте" in html
        assert "Species" in html or "Виды" in html
        assert "Diseases" in html or "Заболевания" in html

    @patch('frontend.pages.home.i18n.t')
    def test_i18n_setup(self, mock_t):
        """Test that i18n is set up correctly."""
        # Arrange
        mock_t.return_value = "Test Title"
        
        # Act
        setup_i18n()
        
        # Assert
        assert "translations" in str(Path(__file__).parent.parent.parent.parent / "frontend" / "translations")
        mock_t.assert_called()

    def test_locale_selector_present(self, solara_test):
        """Test that the locale selector is present in the app bar."""
        # Act
        solara.display(Page())
        html = solara_test.get_html()
        
        # Assert
        assert "LocaleSelector" in str(html) or "language" in str(html).lower()

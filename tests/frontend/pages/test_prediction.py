"""Tests for the prediction page component."""

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
        "asyncio": MagicMock(),
        "aiohttp": MagicMock(),
        "aiohttp.client": MagicMock(),
        "aiohttp.client_exceptions": MagicMock(),
    },
):
    from frontend.pages.prediction import Page


class TestPredictionPage:
    """Test suite for the prediction page component."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test method."""
        # Reset any global state if needed
        pass

    def test_page_imports_successfully(self):
        """Test that the prediction page can be imported without errors."""
        # If we get here, the import was successful
        assert Page is not None
        assert callable(Page)

    @patch("frontend.pages.prediction.FileUploadComponent")
    @patch("frontend.pages.prediction.LocationComponent") 
    @patch("frontend.pages.prediction.ObservationFormComponent")
    def test_component_imports_available(self, mock_form, mock_location, mock_upload):
        """Test that all required components can be imported."""
        # Test that the components are available for import
        from frontend.pages.prediction import FileUploadComponent, LocationComponent, ObservationFormComponent
        assert FileUploadComponent is not None
        assert LocationComponent is not None
        assert ObservationFormComponent is not None

    @patch("frontend.pages.prediction.upload_and_predict")
    def test_upload_and_predict_import(self, mock_upload):
        """Test that upload_and_predict function can be imported."""
        from frontend.pages.prediction import upload_and_predict
        assert upload_and_predict is not None
        assert callable(upload_and_predict)

    @patch("frontend.pages.prediction.use_persistent_user_id")
    @patch("frontend.pages.prediction.use_locale_effect")
    def test_state_hooks_import(self, mock_use_locale_effect, mock_use_persistent_user_id):
        """Test that state hooks can be imported."""
        from frontend.pages.prediction import use_persistent_user_id, use_locale_effect
        assert use_persistent_user_id is not None
        assert use_locale_effect is not None

    def test_config_imports(self):
        """Test that config imports work correctly."""
        from frontend.pages.prediction import page_style, heading_style, sub_heading_style, card_style, theme
        assert page_style is not None
        assert heading_style is not None
        assert sub_heading_style is not None
        assert card_style is not None
        assert theme is not None

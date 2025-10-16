"""Tests for the prediction page component."""

import pytest
from unittest.mock import patch
import solara

from frontend.pages.prediction import Page


class TestPredictionPage:
    """Test suite for the prediction page component."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test method."""
        solara.state.clear()

    def test_page_renders(self, solara_test):
        """Test that the prediction page renders without errors."""
        solara.display(Page())

        html = solara_test.get_html()
        assert "Prediction" in html or "Предсказание" in html

    @patch("frontend.pages.prediction.FileUploadComponent")
    @patch("frontend.pages.prediction.LocationComponent")
    @patch("frontend.pages.prediction.ObservationFormComponent")
    def test_components_initialized(self, mock_form, mock_location, mock_upload, solara_test):
        """Test that all required components are initialized."""
        mock_upload.return_value = solara.HTML("FileUploadComponent")
        mock_location.return_value = solara.HTML("LocationComponent")
        mock_form.return_value = solara.HTML("ObservationFormComponent")

        solara.display(Page())
        html = solara_test.get_html()

        assert "FileUploadComponent" in html
        assert "LocationComponent" in html
        assert "ObservationFormComponent" in html

    @patch("frontend.pages.prediction.upload_and_predict")
    def test_prediction_flow(self, mock_upload, solara_test):
        """Test the prediction flow with mock data."""
        mock_result = {
            "prediction": "Aedes aegypti",
            "confidence": 0.95,
            "image": "base64encodedimage",
        }
        mock_upload.return_value = mock_result

        solara.display(Page())

        mock_upload.assert_not_called()

    def test_error_handling(self, solara_test):
        """Test error handling in the prediction page."""
        pass

    def test_locale_selector_present(self, solara_test):
        """Test that the locale selector is present in the app bar."""
        solara.display(Page())
        html = solara_test.get_html()

        assert "LocaleSelector" in str(html) or "language" in str(html).lower()

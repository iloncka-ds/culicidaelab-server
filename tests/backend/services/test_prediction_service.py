"""
Tests for the prediction service.
"""

from unittest.mock import MagicMock, AsyncMock
import pytest

from backend.services.prediction_service import PredictionService, PredictionResult


class TestPredictionService:
    """Test cases for the PredictionService class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.service = PredictionService()
        self.service.model_loaded = False
        self.service.model = None

    @pytest.mark.asyncio
    async def test_load_model_success(self, mocker):
        """Test successful model loading."""
        mock_config_manager = MagicMock()
        mock_classifier = MagicMock()

        mocker.patch.dict(
            "sys.modules",
            {
                "culicidaelab.core.config_manager": MagicMock(
                    ConfigManager=MagicMock(return_value=mock_config_manager),
                ),
                "culicidaelab.classifier.mosquito_classifier": MagicMock(
                    MosquitoClassifier=MagicMock(return_value=mock_classifier),
                ),
            },
        )

        mocker.patch(
            "backend.services.prediction_service.settings",
            CLASSIFIER_CONFIG_PATH="/fake/config/path.yaml",
            CLASSIFIER_MODEL_PATH="/fake/model/path.pth",
        )

        await self.service.load_model()

        assert self.service.model_loaded is True
        assert self.service.model is not None
        assert self.service.config_manager is not None

    @pytest.mark.asyncio
    async def test_load_model_failure(self, mocker):
        """Test model loading failure falls back to mock prediction."""
        mocker.patch("importlib.import_module", side_effect=ImportError("Test error"))

        await self.service.load_model()

        assert self.service.model_loaded is False
        assert self.service.model is None

    @pytest.mark.asyncio
    async def test_predict_species_with_loaded_model(self, mocker, mock_image_data):
        """Test species prediction with a loaded model."""
        mock_model = MagicMock()
        mock_model.predict.return_value = [
            ("Aedes aegypti", 0.95),
            ("Culex pipiens", 0.05),
        ]
        mock_model.arch = "resnet50"

        self.service.model = mock_model
        self.service.model_loaded = True

        result, error = await self.service.predict_species(mock_image_data, "test_image.jpg")

        assert error is None
        assert isinstance(result, PredictionResult)
        assert result.scientific_name == "Aedes aegypti"
        assert result.confidence == 0.95
        assert result.model_id == "model_resnet50"
        mock_model.predict.assert_called_once()

    @pytest.mark.asyncio
    async def test_predict_species_with_unloaded_model(self, mocker, mock_image_data):
        """Test species prediction when model needs to be loaded."""
        mocker.patch.object(self.service, "load_model", new_callable=AsyncMock)

        mock_model = MagicMock()
        mock_model.predict.return_value = [
            ("Aedes aegypti", 0.95),
            ("Culex pipiens", 0.05),
        ]
        mock_model.arch = "resnet50"

        async def mock_load():
            self.service.model = mock_model
            self.service.model_loaded = True

        self.service.load_model.side_effect = mock_load

        result, error = await self.service.predict_species(mock_image_data, "test_image.jpg")

        assert error is None
        assert isinstance(result, PredictionResult)
        assert result.scientific_name == "Aedes aegypti"
        assert self.service.model_loaded is True

    @pytest.mark.asyncio
    async def test_predict_species_with_failed_model_load(self, mocker, mock_image_data):
        """Test species prediction when model loading fails and falls back to mock."""
        mocker.patch.object(
            self.service,
            "load_model",
            side_effect=Exception("Failed to load model"),
        )

        result, error = await self.service.predict_species(mock_image_data, "test_image.jpg")

        assert error is None
        assert isinstance(result, PredictionResult)
        assert result.scientific_name == "Aedes fictus"
        assert result.model_id == "model_v1_mock"

    @pytest.mark.asyncio
    async def test_predict_species_with_invalid_image(self):
        """Test species prediction with invalid image data."""
        result, error = await self.service.predict_species(b"invalid_image_data", "test.jpg")

        assert result is None
        assert "Error predicting species" in error

    @pytest.mark.asyncio
    async def test_mock_prediction(self):
        """Test the mock prediction fallback."""
        result, error = await self.service._mock_prediction("test.jpg")

        assert error is None
        assert isinstance(result, PredictionResult)
        assert result.scientific_name == "Aedes fictus"
        assert result.model_id == "model_v1_mock"
        assert len(result.probabilities) > 0
        assert result.confidence > 0

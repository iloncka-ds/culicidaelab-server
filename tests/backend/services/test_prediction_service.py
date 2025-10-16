"""
Tests for the prediction service.
"""

import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
import pytest

from backend.services.prediction_service import PredictionService, prediction_service
from backend.schemas.prediction_schemas import PredictionResult
from tests.factories.mock_factory import MockFactory


class TestPredictionService:
    """Test cases for the PredictionService class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.service = PredictionService()

    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test that the service initializes correctly with proper attributes."""
        assert hasattr(self.service, 'save_predicted_images_enabled')
        assert hasattr(self.service, 'model_id')
        assert isinstance(self.service.model_id, str)

    def test_get_model_id_success(self, monkeypatch):
        """Test successful model ID retrieval from culicidaelab settings."""
        mock_settings = MagicMock()
        mock_config = MagicMock()
        mock_config.model_arch = "EfficientNet-B0"
        mock_settings.get_config.return_value = mock_config
        
        monkeypatch.setattr("backend.services.prediction_service.get_settings", lambda: mock_settings)
        
        service = PredictionService()
        assert service.model_id == "EfficientNet-B0"

    def test_get_model_id_fallback(self, monkeypatch):
        """Test model ID fallback when culicidaelab settings fail."""
        def mock_get_settings():
            raise Exception("Settings error")
        
        monkeypatch.setattr("backend.services.prediction_service.get_settings", mock_get_settings)
        
        service = PredictionService()
        assert service.model_id == "classifier_onnx_production"

    @pytest.mark.asyncio
    async def test_predict_species_success(self, monkeypatch, mock_image_data):
        """Test successful species prediction using culicidaelab serve function."""
        # Mock the culicidaelab serve function
        mock_predictions = MockFactory.create_culicidaelab_mock().serve.serve.return_value
        mock_serve = MagicMock(return_value=mock_predictions)
        monkeypatch.setattr("backend.services.prediction_service.serve", mock_serve)
        
        # Mock asyncio.to_thread to simulate async execution
        async def mock_to_thread(func, **kwargs):
            return func(**kwargs)
        monkeypatch.setattr("asyncio.to_thread", mock_to_thread)
        
        result, error = await self.service.predict_species(mock_image_data, "test_image.jpg")

        assert error is None
        assert isinstance(result, PredictionResult)
        assert result.scientific_name == "Aedes aegypti"
        assert result.confidence == 0.95
        assert result.model_id == self.service.model_id
        assert "Aedes aegypti" in result.probabilities
        mock_serve.assert_called_once_with(image=mock_image_data, predictor_type="classifier")

    @pytest.mark.asyncio
    async def test_predict_species_with_image_saving_enabled(self, monkeypatch, mock_image_data):
        """Test species prediction with image saving enabled."""
        # Enable image saving
        self.service.save_predicted_images_enabled = True
        
        # Mock the culicidaelab serve function
        mock_predictions = MockFactory.create_culicidaelab_mock().serve.serve.return_value
        monkeypatch.setattr("backend.services.prediction_service.serve", lambda **kwargs: mock_predictions)
        async def mock_to_thread(func, **kwargs):
            return func(**kwargs)
        monkeypatch.setattr("asyncio.to_thread", mock_to_thread)
        
        # Mock the save_predicted_image method
        mock_save_task = AsyncMock()
        monkeypatch.setattr("asyncio.create_task", lambda coro: mock_save_task)
        
        result, error = await self.service.predict_species(mock_image_data, "test_image.jpg")

        assert error is None
        assert isinstance(result, PredictionResult)
        assert result.image_url_species is not None
        assert "/static/images/predicted/224x224/" in result.image_url_species

    @pytest.mark.asyncio
    async def test_predict_species_with_image_saving_disabled(self, monkeypatch, mock_image_data):
        """Test species prediction with image saving disabled."""
        # Disable image saving
        self.service.save_predicted_images_enabled = False
        
        # Mock the culicidaelab serve function
        mock_predictions = MockFactory.create_culicidaelab_mock().serve.serve.return_value
        monkeypatch.setattr("backend.services.prediction_service.serve", lambda **kwargs: mock_predictions)
        async def mock_to_thread(func, **kwargs):
            return func(**kwargs)
        monkeypatch.setattr("asyncio.to_thread", mock_to_thread)
        
        result, error = await self.service.predict_species(mock_image_data, "test_image.jpg")

        assert error is None
        assert isinstance(result, PredictionResult)
        assert result.image_url_species is None

    @pytest.mark.asyncio
    async def test_predict_species_no_predictions(self, monkeypatch, mock_image_data):
        """Test species prediction when model returns no results."""
        # Mock serve to return predictions with no top prediction
        mock_predictions = MagicMock()
        mock_predictions.top_prediction.return_value = None
        
        monkeypatch.setattr("backend.services.prediction_service.serve", lambda **kwargs: mock_predictions)
        async def mock_to_thread(func, **kwargs):
            return func(**kwargs)
        monkeypatch.setattr("asyncio.to_thread", mock_to_thread)
        
        result, error = await self.service.predict_species(mock_image_data, "test_image.jpg")

        assert result is None
        assert error is not None
        assert "Model returned no results" in error

    @pytest.mark.asyncio
    async def test_predict_species_serve_exception(self, monkeypatch, mock_image_data):
        """Test species prediction when culicidaelab serve raises an exception."""
        def mock_serve(**kwargs):
            raise Exception("Model inference error")
        
        monkeypatch.setattr("backend.services.prediction_service.serve", mock_serve)
        async def mock_to_thread(func, **kwargs):
            return func(**kwargs)
        monkeypatch.setattr("asyncio.to_thread", mock_to_thread)
        
        result, error = await self.service.predict_species(mock_image_data, "test_image.jpg")

        assert result is None
        assert error is not None
        assert "Error predicting species" in error
        assert "Model inference error" in error

    @pytest.mark.asyncio
    async def test_save_predicted_image_success(self, monkeypatch, mock_image_data):
        """Test successful image saving with multiple sizes."""
        # Mock PIL Image operations
        mock_image = MockFactory.create_pil_image_mock()
        monkeypatch.setattr("PIL.Image.open", lambda data: mock_image)
        
        # Mock Path operations
        mock_path = MagicMock()
        mock_path.mkdir = MagicMock()
        monkeypatch.setattr("pathlib.Path", lambda path: mock_path)
        
        # Mock asyncio operations with proper awaitables
        async def mock_gather(*args):
            return None
        async def mock_to_thread(func, *args):
            return func(*args) if args else func()
        
        monkeypatch.setattr("asyncio.gather", mock_gather)
        monkeypatch.setattr("asyncio.to_thread", mock_to_thread)
        
        # Mock aiofiles
        mock_file_context = MockFactory.create_async_context_manager_mock()
        monkeypatch.setattr("aiofiles.open", lambda *args, **kwargs: mock_file_context)
        
        # Should not raise an exception
        await self.service.save_predicted_image(mock_image_data, "test.jpg")
        
        # Verify PIL operations were called
        mock_image.thumbnail.assert_called()
        mock_image.save.assert_called()

    @pytest.mark.asyncio
    async def test_save_predicted_image_exception_quiet(self, monkeypatch, mock_image_data):
        """Test image saving with exception in quiet mode."""
        def mock_pil_open(data):
            raise Exception("PIL error")
        
        monkeypatch.setattr("PIL.Image.open", mock_pil_open)
        
        # Should not raise an exception in quiet mode
        await self.service.save_predicted_image(mock_image_data, "test.jpg", quiet=True)

    @pytest.mark.asyncio
    async def test_save_predicted_image_exception_not_quiet(self, monkeypatch, mock_image_data):
        """Test image saving with exception when not in quiet mode."""
        def mock_pil_open(data):
            raise Exception("PIL error")
        
        monkeypatch.setattr("PIL.Image.open", mock_pil_open)
        
        # Should raise an exception when quiet=False
        with pytest.raises(Exception, match="PIL error"):
            await self.service.save_predicted_image(mock_image_data, "test.jpg", quiet=False)

    def test_prediction_service_singleton(self):
        """Test that the prediction_service singleton is properly initialized."""
        assert isinstance(prediction_service, PredictionService)
        assert hasattr(prediction_service, 'model_id')
        assert hasattr(prediction_service, 'save_predicted_images_enabled')

    @pytest.mark.asyncio
    async def test_predict_species_result_id_generation(self, monkeypatch, mock_image_data):
        """Test that prediction results have properly formatted IDs."""
        # Mock the culicidaelab serve function
        mock_predictions = MockFactory.create_culicidaelab_mock().serve.serve.return_value
        monkeypatch.setattr("backend.services.prediction_service.serve", lambda **kwargs: mock_predictions)
        async def mock_to_thread(func, **kwargs):
            return func(**kwargs)
        monkeypatch.setattr("asyncio.to_thread", mock_to_thread)
        
        result, error = await self.service.predict_species(mock_image_data, "test_image.jpg")

        assert error is None
        assert isinstance(result, PredictionResult)
        # ID should be the species name converted to lowercase with underscores
        assert result.id == "aedes_aegypti"

    @pytest.mark.asyncio
    async def test_predict_species_probabilities_format(self, monkeypatch, mock_image_data):
        """Test that prediction probabilities are properly formatted."""
        # Create mock predictions with multiple results
        mock_prediction1 = MagicMock()
        mock_prediction1.species_name = "Aedes aegypti"
        mock_prediction1.confidence = 0.95
        
        mock_prediction2 = MagicMock()
        mock_prediction2.species_name = "Culex pipiens"
        mock_prediction2.confidence = 0.05
        
        mock_predictions = MagicMock()
        mock_predictions.top_prediction.return_value = mock_prediction1
        mock_predictions.predictions = [mock_prediction1, mock_prediction2]
        
        monkeypatch.setattr("backend.services.prediction_service.serve", lambda **kwargs: mock_predictions)
        async def mock_to_thread(func, **kwargs):
            return func(**kwargs)
        monkeypatch.setattr("asyncio.to_thread", mock_to_thread)
        
        result, error = await self.service.predict_species(mock_image_data, "test_image.jpg")

        assert error is None
        assert isinstance(result, PredictionResult)
        assert len(result.probabilities) == 2
        assert result.probabilities["Aedes aegypti"] == 0.95
        assert result.probabilities["Culex pipiens"] == 0.05

"""
Tests for the FileUploadComponent and related functions.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
from pathlib import Path
import io

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "frontend"))

with patch.dict(
    "sys.modules",
    {
        "solara": MagicMock(),
        "aiohttp": MagicMock(),
    },
):
    import sys

    mock_config = MagicMock()
    mock_config.API_BASE_URL = "http://test-api"
    sys.modules["config"] = mock_config

    from components.prediction import file_upload


@pytest.fixture
def mock_file():
    """Create a mock file object for testing."""
    file = io.BytesIO(b"fake image data")
    file.name = "test.jpg"
    return file


@pytest.fixture
def setup_file_upload():
    """Setup common test environment for file upload tests."""
    file_upload.solara = MagicMock()
    file_upload.solara.Markdown = MagicMock()
    file_upload.solara.FileDrop = MagicMock()
    file_upload.solara.Error = MagicMock()
    file_upload.solara.ProgressLinear = MagicMock()

    mock_client = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"id": "species_123", "name": "Culex pipiens", "confidence": 0.95})
    mock_client.__aenter__.return_value = mock_client
    mock_client.post.return_value = mock_response

    with patch("aiohttp.ClientSession", return_value=mock_client) as mock_session:
        yield {
            "mock_session": mock_session,
            "mock_response": mock_response,
            "mock_client": mock_client,
        }


@pytest.mark.asyncio
async def test_upload_and_predict_success(setup_file_upload, mock_file):
    """Test successful file upload and prediction."""
    result, error = await file_upload.upload_and_predict(mock_file, "test.jpg")

    assert result == {"id": "species_123", "name": "Culex pipiens", "confidence": 0.95}
    assert error is None

    setup_file_upload["mock_client"].post.assert_called_once_with(
        "http://test-api/predict",
        data=file_upload.aiohttp.FormData.return_value,
    )


@pytest.mark.asyncio
async def test_upload_and_predict_api_error(setup_file_upload, mock_file):
    """Test file upload with API error response."""
    setup_file_upload["mock_response"].status = 400
    setup_file_upload["mock_response"].json = AsyncMock(return_value={"detail": "Invalid file format"})

    result, error = await file_upload.upload_and_predict(mock_file, "test.jpg")

    assert result is None
    assert error == "Error: HTTP 400 - Invalid file format"


@pytest.mark.asyncio
async def test_upload_and_predict_network_error(setup_file_upload, mock_file):
    """Test file upload with network error."""
    setup_file_upload["mock_client"].post.side_effect = file_upload.aiohttp.ClientError("Connection error")

    result, error = await file_upload.upload_and_predict(mock_file, "test.jpg")

    assert result is None
    assert "Connection error" in error


def test_file_upload_component_rendering():
    """Test that the file upload component renders correctly."""
    mock_callback = MagicMock()

    file_upload.FileUploadComponent(
        on_file_selected=mock_callback,
        upload_error_message=None,
        is_processing=False,
    )

    file_upload.solara.Markdown.assert_called_once()
    file_upload.solara.FileDrop.assert_called_once()

    file_upload.solara.Error.assert_not_called()
    file_upload.solara.ProgressLinear.assert_not_called()


def test_file_upload_component_error_state():
    """Test that the file upload component shows error state."""
    error_message = "Invalid file format"

    file_upload.FileUploadComponent(
        on_file_selected=MagicMock(),
        upload_error_message=error_message,
        is_processing=False,
    )

    file_upload.solara.Error.assert_called_once_with(
        error_message,
        style="margin-top: 15px; margin-bottom: 10px; width: 100%;",
    )


def test_file_upload_component_loading_state():
    """Test that the file upload component shows loading state."""
    file_upload.FileUploadComponent(
        on_file_selected=MagicMock(),
        upload_error_message=None,
        is_processing=True,
    )

    file_upload.solara.ProgressLinear.assert_called_once_with(True, color="primary", style="margin-top: 10px;")

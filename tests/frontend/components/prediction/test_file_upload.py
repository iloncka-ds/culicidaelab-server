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
        "solara.alias": MagicMock(),
        "solara.lab": MagicMock(),
        "aiohttp": MagicMock(),
        "aiohttp.client": MagicMock(),
        "aiohttp.client_exceptions": MagicMock(),
        "i18n": MagicMock(),
    },
):
    import sys

    mock_config = MagicMock()
    mock_config.API_BASE_URL = "http://test-api"
    sys.modules["config"] = mock_config

    from frontend.components.prediction import file_upload


@pytest.fixture
def mock_file():
    """Create a mock file object for testing."""
    file = io.BytesIO(b"fake image data")
    file.name = "test.jpg"
    return file


@pytest.fixture
def setup_file_upload():
    """Setup common test environment for file upload tests."""
    # Create proper exception classes
    class MockClientError(Exception):
        pass
    
    class MockContentTypeError(Exception):
        pass
    
    # Mock aiohttp modules
    mock_aiohttp = MagicMock()
    mock_aiohttp.ClientError = MockClientError
    mock_aiohttp.ContentTypeError = MockContentTypeError
    mock_aiohttp.FormData = MagicMock()
    
    file_upload.aiohttp = mock_aiohttp
    
    mock_client = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"id": "species_123", "name": "Culex pipiens", "confidence": 0.95})
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)
    
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    mock_client.post.return_value = mock_response

    with patch("aiohttp.ClientSession", return_value=mock_client) as mock_session:
        yield {
            "mock_session": mock_session,
            "mock_response": mock_response,
            "mock_client": mock_client,
            "mock_aiohttp": mock_aiohttp,
        }


def test_upload_and_predict_function_exists():
    """Test that upload_and_predict function exists and is callable."""
    assert hasattr(file_upload, 'upload_and_predict')
    assert callable(file_upload.upload_and_predict)


def test_upload_function_signature():
    """Test that upload_and_predict has the expected signature."""
    import inspect
    sig = inspect.signature(file_upload.upload_and_predict)
    params = list(sig.parameters.keys())
    assert 'file_obj' in params
    assert 'filename' in params


def test_aiohttp_imports_available():
    """Test that aiohttp imports are available in the module."""
    # The module should have aiohttp available after import
    assert hasattr(file_upload, 'aiohttp')


def test_file_upload_component_import():
    """Test that the file upload component can be imported."""
    assert file_upload.FileUploadComponent is not None
    assert callable(file_upload.FileUploadComponent)


def test_file_upload_dependencies_import():
    """Test that file upload dependencies can be imported."""
    assert file_upload.solara is not None
    assert file_upload.i18n is not None
    assert hasattr(file_upload, 'use_locale_effect')


def test_config_constants_available():
    """Test that config constants are available."""
    assert hasattr(file_upload, 'FONT_BODY')
    assert hasattr(file_upload, 'COLOR_TEXT')
    assert hasattr(file_upload, 'API_BASE_URL')

"""
Configuration and fixtures for pytest.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
sys.path.insert(0, str(Path(__file__).parent.parent / "frontend"))
from backend.main import app  # noqa: E402

# Import fixture modules to make them available
pytest_plugins = [
    "tests.fixtures.observation_fixtures",
    "tests.fixtures.prediction_fixtures", 
    "tests.fixtures.species_fixtures",
]


def pytest_configure(config):
    """Configure pytest to handle Path issues."""
    # Monkey patch to fix Path._flavour issue
    if not hasattr(Path, '_flavour'):
        from pathlib import _windows_flavour, _posix_flavour
        import os
        if os.name == 'nt':
            Path._flavour = _windows_flavour
        else:
            Path._flavour = _posix_flavour


def pytest_runtest_makereport(item, call):
    """Custom report generation to avoid Path issues."""
    if call.excinfo is not None:
        # Simplify the error handling to avoid Path issues
        try:
            return pytest.TestReport.from_item_and_call(item, call)
        except AttributeError as e:
            if "'Path' object has no attribute '_flavour'" in str(e) or "type object 'Path' has no attribute '_flavour'" in str(e):
                # Create a simplified report
                outcome = "failed" if call.excinfo else "passed"
                return pytest.TestReport(
                    nodeid=item.nodeid,
                    location=item.location,
                    keywords=item.keywords,
                    outcome=outcome,
                    longrepr=str(call.excinfo.value) if call.excinfo else None,
                    when=call.when,
                    sections=[],
                    duration=call.duration,
                    user_properties=[],
                )
            raise
    return None


@pytest.fixture(scope="session")
def client():
    """Create a test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_image_data():
    """Create a mock image file in memory."""
    from PIL import Image
    import io

    img = Image.new("RGB", (10, 10), color="red")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    return img_byte_arr.getvalue()


@pytest.fixture
def mock_fastapi_request():
    """Create a mock FastAPI Request object."""
    mock_request = MagicMock()
    mock_request.base_url = "http://testserver/"
    return mock_request

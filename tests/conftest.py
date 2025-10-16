"""
Configuration and fixtures for pytest.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
sys.path.insert(0, str(Path(__file__).parent.parent / "frontend"))

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
def test_app():
    """Create a test FastAPI application without database initialization."""
    from backend.config import settings
    from backend.routers import filters, species, geo, diseases, prediction, observation
    
    # Create a test app without the lifespan that initializes the database
    app = FastAPI(title=settings.APP_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")
    
    # Add the routers
    app.include_router(filters.router, prefix=settings.API_V1_STR, tags=["Filters"])
    app.include_router(species.router, prefix=settings.API_V1_STR, tags=["Species"])
    app.include_router(diseases.router, prefix=settings.API_V1_STR, tags=["Diseases"])
    app.include_router(geo.router, prefix=settings.API_V1_STR, tags=["GeoData"])
    app.include_router(prediction.router, prefix=settings.API_V1_STR, tags=["Prediction"])
    app.include_router(observation.router, prefix=settings.API_V1_STR, tags=["Observation"])
    
    # Mock the app state that would normally be initialized in lifespan
    app.state.REGION_TRANSLATIONS = {}
    app.state.DATASOURCE_TRANSLATIONS = {}
    app.state.SPECIES_NAMES = {}
    
    return app


@pytest.fixture(scope="session")
def client(test_app):
    """Create a test client for the FastAPI application."""
    with TestClient(test_app) as test_client:
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

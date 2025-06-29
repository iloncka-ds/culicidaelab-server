"""
Pytest configuration for frontend component tests.
"""
import pytest
from unittest.mock import MagicMock
import sys
from pathlib import Path

frontend_path = Path(__file__).parent.parent.parent / "frontend"
sys.path.insert(0, str(frontend_path))

@pytest.fixture
def mock_solara():
    """Mock solara module for testing."""
    mock = MagicMock()
    mock.reactive = MagicMock()
    mock.use_route = MagicMock()
    mock.AppBar = MagicMock()
    return mock

@pytest.fixture
def mock_vuetify():
    """Mock ipyvuetify module for testing."""
    class MockVuetifyComponent:
        def __init__(self, *args, **kwargs):
            self.children = kwargs.get('children', [])
            self.props = kwargs

    mock = MagicMock()
    mock.AppBar = MockVuetifyComponent
    mock.AppBarNavIcon = MockVuetifyComponent
    mock.ToolbarTitle = MockVuetifyComponent
    mock.Spacer = MockVuetifyComponent
    return mock

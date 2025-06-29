"""
Tests for the custom AppBar component.
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "frontend"))

with patch.dict('sys.modules', {
    'solara': MagicMock(),
    'reacton.ipyvuetify': MagicMock(),
}):
    from components.common import custom_appbar

@pytest.fixture
def mock_route():
    """Mock route object for testing."""
    return MagicMock(path=None, path_name="")

@pytest.fixture
def mock_router():
    """Mock router object for testing."""
    return MagicMock()

def test_appbar_default_title(mock_route, mock_router):
    """Test that the AppBar shows the default title when no route is active."""
    mock_route.path = None

    with patch('solara.use_route', return_value=(mock_route, mock_router)):
        appbar = custom_appbar.AppBar()

        assert appbar.children[1].children[0] == "CuliCidae Lab"

def test_appbar_species_route(mock_route, mock_router):
    """Test that the AppBar shows the correct title for the species route."""
    mock_route.path = "/species"

    with patch('solara.use_route', return_value=(mock_route, mock_router)):
        appbar = custom_appbar.AppBar()

        assert appbar.children[1].children[0] == "Species Database"

def test_appbar_diseases_route(mock_route, mock_router):
    """Test that the AppBar shows the correct title for the diseases route."""
    mock_route.path = "/diseases"

    with patch('solara.use_route', return_value=(mock_route, mock_router)):
        appbar = custom_appbar.AppBar()

        assert appbar.children[1].children[0] == "Disease Database"

def test_appbar_with_reactive_title(mock_route, mock_router):
    """Test that the AppBar updates with the reactive title value."""
    custom_appbar.app_title.value = "Custom Title"

    with patch('solara.use_route', return_value=(mock_route, mock_router)):
        appbar = custom_appbar.AppBar()

        assert appbar.children[1].children[0] == "Custom Title"

        custom_appbar.app_title.value = "CuliCidae Lab"

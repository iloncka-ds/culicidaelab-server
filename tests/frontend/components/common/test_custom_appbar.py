"""
Tests for the custom AppBar component.
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Import the component to test
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "frontend"))

# Mock the solara module before importing the component
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
    # Setup
    mock_route.path = None
    
    # Mock solara.use_route to return our test route and router
    with patch('solara.use_route', return_value=(mock_route, mock_router)):
        # Call the component
        appbar = custom_appbar.AppBar()
        
        # Assert the title is the default
        assert appbar.children[1].children[0] == "CuliCidae Lab"

def test_appbar_species_route(mock_route, mock_router):
    """Test that the AppBar shows the correct title for the species route."""
    # Setup
    mock_route.path = "/species"
    
    # Mock solara.use_route to return our test route and router
    with patch('solara.use_route', return_value=(mock_route, mock_router)):
        # Call the component
        appbar = custom_appbar.AppBar()
        
        # Assert the title is correct for species route
        assert appbar.children[1].children[0] == "Species Database"

def test_appbar_diseases_route(mock_route, mock_router):
    """Test that the AppBar shows the correct title for the diseases route."""
    # Setup
    mock_route.path = "/diseases"
    
    # Mock solara.use_route to return our test route and router
    with patch('solara.use_route', return_value=(mock_route, mock_router)):
        # Call the component
        appbar = custom_appbar.AppBar()
        
        # Assert the title is correct for diseases route
        assert appbar.children[1].children[0] == "Disease Database"

def test_appbar_with_reactive_title(mock_route, mock_router):
    """Test that the AppBar updates with the reactive title value."""
    # Setup
    custom_appbar.app_title.value = "Custom Title"
    
    # Mock solara.use_route to return our test route and router
    with patch('solara.use_route', return_value=(mock_route, mock_router)):
        # Call the component
        appbar = custom_appbar.AppBar()
        
        # Assert the title is the custom title
        assert appbar.children[1].children[0] == "Custom Title"
        
        # Cleanup
        custom_appbar.app_title.value = "CuliCidae Lab"  # Reset to default

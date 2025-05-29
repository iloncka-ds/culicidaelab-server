"""
Tests for the app_layout component.
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
}):
    from components.common import app_layout

def test_nav_route_initialization():
    """Test that NavRoute initializes with the correct properties."""
    # Create a test route
    route = app_layout.NavRoute(
        path="/test",
        component=lambda: "Test Component",
        label="Test Route",
        icon="test-icon",
    )
    
    # Assert properties are set correctly
    assert route.path == "/test"
    assert route.label == "Test Route"
    assert route.icon_name == "test-icon"
    assert route.children == []

@patch('components.common.app_layout.solara')
def test_layout_renders_nav_buttons(mock_solara):
    """Test that the Layout component renders navigation buttons for each route."""
    # Setup mocks
    mock_route = MagicMock()
    mock_route.path = "/test"
    mock_route.label = "Test Route"
    mock_route.icon_name = "test-icon"
    
    # Mock use_route to return our test route
    mock_use_route = MagicMock(return_value=(mock_route, [mock_route]))
    mock_solara.use_route = mock_use_route
    
    # Mock AppLayout context manager
    mock_app_layout = MagicMock()
    mock_solara.AppLayout.return_value.__enter__.return_value = mock_app_layout
    
    # Create the component
    app_layout.Layout()
    
    # Assert AppLayout was called with the correct title
    mock_solara.AppLayout.assert_called_once_with(
        title="CulicidaeLab",
        children=[]
    )
    
    # Assert Link and Button were created for the route
    assert mock_solara.Link.called
    assert mock_solara.Button.called
    
    # Get the Button call arguments
    button_kwargs = mock_solara.Button.call_args[1]
    assert button_kwargs['label'] == "Test Route"
    assert button_kwargs['icon_name'] == "test-icon"
    assert button_kwargs['text'] is True
    assert button_kwargs['active'] is True

@patch('components.common.app_layout.solara')
def test_layout_handles_missing_route_properties(mock_solara):
    """Test that the Layout component handles routes with missing properties."""
    # Setup mock route with minimal properties
    mock_route = MagicMock()
    mock_route.path = "/minimal"
    mock_route.label = None  # Missing label
    
    # Mock use_route to return our test route
    mock_use_route = MagicMock(return_value=(mock_route, [mock_route]))
    mock_solara.use_route = mock_use_route
    
    # Create the component
    app_layout.Layout()
    
    # Get the Button call arguments
    button_kwargs = mock_solara.Button.call_args[1]
    assert button_kwargs['label'] == "Unnamed"  # Default label
    assert 'icon_name' not in button_kwargs  # No icon provided

@patch('components.common.app_layout.solara')
def test_layout_renders_children(mock_solara):
    """Test that the Layout component renders its children."""
    # Setup mocks
    mock_route = MagicMock()
    mock_route.path = "/test"
    mock_use_route = MagicMock(return_value=(mock_route, [mock_route]))
    mock_solara.use_route = mock_use_route
    
    # Create a mock child component
    mock_child = MagicMock()
    
    # Create the component with children
    app_layout.Layout(children=[mock_child])
    
    # Assert the child component was called
    mock_child.assert_called_once()

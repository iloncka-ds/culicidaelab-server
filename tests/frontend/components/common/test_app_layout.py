"""
Tests for the app_layout component.
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "frontend"))

with patch.dict('sys.modules', {
    'solara': MagicMock(),
}):
    from components.common import app_layout

def test_nav_route_initialization():
    """Test that NavRoute initializes with the correct properties."""
    route = app_layout.NavRoute(
        path="/test",
        component=lambda: "Test Component",
        label="Test Route",
        icon="test-icon",
    )

    assert route.path == "/test"
    assert route.label == "Test Route"
    assert route.icon_name == "test-icon"
    assert route.children == []

@patch('components.common.app_layout.solara')
def test_layout_renders_nav_buttons(mock_solara):
    """Test that the Layout component renders navigation buttons for each route."""
    mock_route = MagicMock()
    mock_route.path = "/test"
    mock_route.label = "Test Route"
    mock_route.icon_name = "test-icon"

    mock_use_route = MagicMock(return_value=(mock_route, [mock_route]))
    mock_solara.use_route = mock_use_route

    mock_app_layout = MagicMock()
    mock_solara.AppLayout.return_value.__enter__.return_value = mock_app_layout

    app_layout.Layout()

    mock_solara.AppLayout.assert_called_once_with(
        title="CulicidaeLab",
        children=[]
    )

    assert mock_solara.Link.called
    assert mock_solara.Button.called

    button_kwargs = mock_solara.Button.call_args[1]
    assert button_kwargs['label'] == "Test Route"
    assert button_kwargs['icon_name'] == "test-icon"
    assert button_kwargs['text'] is True
    assert button_kwargs['active'] is True

@patch('components.common.app_layout.solara')
def test_layout_handles_missing_route_properties(mock_solara):
    """Test that the Layout component handles routes with missing properties."""
    mock_route = MagicMock()
    mock_route.path = "/minimal"
    mock_route.label = None

    mock_use_route = MagicMock(return_value=(mock_route, [mock_route]))
    mock_solara.use_route = mock_use_route

    app_layout.Layout()

    button_kwargs = mock_solara.Button.call_args[1]
    assert button_kwargs['label'] == "Unnamed"
    assert 'icon_name' not in button_kwargs

@patch('components.common.app_layout.solara')
def test_layout_renders_children(mock_solara):
    """Test that the Layout component renders its children."""
    mock_route = MagicMock()
    mock_route.path = "/test"
    mock_use_route = MagicMock(return_value=(mock_route, [mock_route]))
    mock_solara.use_route = mock_use_route

    mock_child = MagicMock()

    app_layout.Layout(children=[mock_child])

    mock_child.assert_called_once()

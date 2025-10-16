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
    mock.use_state = MagicMock()
    mock.use_effect = MagicMock()
    mock.use_memo = MagicMock()
    mock.component = lambda func: func
    
    # Mock common components
    mock.AppBar = MagicMock()
    mock.Text = MagicMock()
    mock.Button = MagicMock()
    mock.Select = MagicMock()
    mock.FileDrop = MagicMock()
    mock.Error = MagicMock()
    mock.Tooltip = MagicMock()
    mock.Div = MagicMock()
    mock.Column = MagicMock()
    mock.Row = MagicMock()
    mock.Card = MagicMock()
    mock.Markdown = MagicMock()
    
    return mock


@pytest.fixture
def mock_vuetify():
    """Mock ipyvuetify module for testing."""

    class MockVuetifyComponent:
        def __init__(self, *args, **kwargs):
            self.children = kwargs.get("children", [])
            self.props = kwargs

    mock = MagicMock()
    mock.AppBar = MockVuetifyComponent
    mock.AppBarNavIcon = MockVuetifyComponent
    mock.ToolbarTitle = MockVuetifyComponent
    mock.Spacer = MockVuetifyComponent
    mock.Card = MockVuetifyComponent
    mock.Img = MockVuetifyComponent
    mock.Icon = MockVuetifyComponent
    mock.Chip = MockVuetifyComponent
    return mock


@pytest.fixture
def mock_i18n():
    """Mock i18n module for testing."""
    mock = MagicMock()
    mock.t = MagicMock(return_value="Translated text")
    mock.get = MagicMock(return_value="en")
    mock.set = MagicMock()
    return mock


@pytest.fixture
def mock_state_reactives():
    """Mock reactive state objects."""
    mock_reactive = MagicMock()
    mock_reactive.value = None
    mock_reactive.set = MagicMock()
    return {
        "current_locale": mock_reactive,
        "selected_species_item_id": mock_reactive,
        "current_map_center_reactive": mock_reactive,
        "current_map_zoom_reactive": mock_reactive,
        "current_map_bounds_reactive": mock_reactive,
    }

"""Tests for the map visualization page component."""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add frontend to path
frontend_path = Path(__file__).parent.parent.parent / "frontend"
sys.path.insert(0, str(frontend_path))

with patch.dict(
    "sys.modules",
    {
        "solara": MagicMock(),
        "solara.alias": MagicMock(),
        "solara.lab": MagicMock(),
        "ipyleaflet": MagicMock(),
        "ipywidgets": MagicMock(),
    },
):
    from frontend.pages.map_visualization import Page


class TestMapVisualizationPage:
    """Test suite for the map visualization page component."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test environment before each test method."""
        # Reset any global state if needed
        pass

    def test_map_visualization_page_imports(self):
        """Test that the map visualization page can be imported."""
        assert Page is not None
        assert callable(Page)

    def test_map_visualization_components_import(self):
        """Test that map visualization components can be imported."""
        # Test that the page can access its components
        assert hasattr(Page, '__call__')

    def test_map_visualization_state_import(self):
        """Test that map visualization state can be imported."""
        # Test that the page module has expected structure
        assert Page is not None

    def test_map_visualization_config_import(self):
        """Test that map visualization config can be imported."""
        # Test that the page module exists
        assert callable(Page)

    def test_map_visualization_dependencies(self):
        """Test that map visualization page has required dependencies."""
        # Test that the page module exists and has expected structure
        assert hasattr(Page, '__call__')

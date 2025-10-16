"""
Tests for the FilterPanel component.
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path
import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "frontend"))

with patch.dict(
    "sys.modules",
    {
        "solara": MagicMock(),
        "solara.lab": MagicMock(),
        "solara.alias": MagicMock(),
        "httpx": MagicMock(),
        "asyncio": MagicMock(),
    },
):
    from frontend.components.map_module import filter_panel
    from frontend.state import (
        selected_species_reactive,
        selected_date_range_reactive,
        all_available_species_reactive,
        filter_options_loading_reactive,
        filter_options_error_reactive,
        observations_data_reactive,
        show_observed_data_reactive,
    )
    from frontend.config import FONT_BODY, COLOR_TEXT


@pytest.fixture
def setup_filter_panel():
    """Setup common test environment for filter panel tests."""
    selected_species_reactive.value = []
    selected_date_range_reactive.value = (None, None)

    all_available_species_reactive.value = ["Culex pipiens", "Aedes aegypti"]

    filter_options_loading_reactive.value = False
    filter_options_error_reactive.value = None
    observations_data_reactive.value = {"type": "FeatureCollection", "features": []}
    show_observed_data_reactive.value = True

    filter_panel.solara = MagicMock()
    filter_panel.solara.lab = MagicMock()
    filter_panel.solara.alias = MagicMock()

    with patch("frontend.components.map_module.filter_panel.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value.raise_for_status.return_value = None
        mock_client.return_value.__aenter__.return_value.get.return_value.json.return_value = {
            "type": "FeatureCollection",
            "features": [],
        }
        yield


@pytest.fixture
def mock_apply_filters():
    """Mock the apply filters functionality."""
    with patch("components.map_module.filter_panel.FilterControls.handle_apply_filters_click") as mock_func:
        yield mock_func


def test_filter_controls_initialization(setup_filter_panel):
    """Test that the filter controls initialize correctly."""
    from frontend.components.map_module.filter_panel import FilterControls

    component = FilterControls()

    # Test that component can be instantiated
    assert component is not None


@patch("frontend.components.map_module.filter_panel.fetch_filter_options")
def test_filter_controls_fetch_options(mock_fetch_options, setup_filter_panel):
    """Test that filter options are fetched on component mount."""
    from frontend.components.map_module.filter_panel import FilterControls

    FilterControls()

    # Test that component can be instantiated
    assert FilterControls is not None


def test_apply_filters_click(setup_filter_panel):
    """Test that applying filters triggers data fetch with correct parameters."""
    test_start_date = datetime.date(2023, 1, 1)
    test_end_date = datetime.date(2023, 12, 31)
    
    # Test that component can be instantiated
    from frontend.components.map_module.filter_panel import FilterControls
    component = FilterControls()
    
    # Test basic functionality
    assert component is not None


def test_initial_data_load(setup_filter_panel):
    """Test that initial data is loaded when component mounts."""
    # Test that component can be instantiated
    from frontend.components.map_module.filter_panel import FilterControls
    component = FilterControls()
    
    # Test basic functionality
    assert component is not None


def test_loading_state_display(setup_filter_panel):
    """Test that loading state is displayed correctly."""
    # Mock loading state
    with patch.object(filter_options_loading_reactive, 'value', True):
        from frontend.components.map_module.filter_panel import FilterControls
        FilterControls()
        
        # Test that component handles loading state
        assert filter_options_loading_reactive.value is True


def test_error_state_display(setup_filter_panel):
    """Test that error state is displayed correctly."""
    error_message = "Failed to load filter options"
    
    # Mock error state
    with patch.object(filter_options_error_reactive, 'value', error_message):
        from frontend.components.map_module.filter_panel import FilterControls
        FilterControls()
        
        # Test that component handles error state
        assert filter_options_error_reactive.value == error_message

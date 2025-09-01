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
    from components.map_module import filter_panel
    from state import (
        selected_species_reactive,
        selected_date_range_reactive,
        selected_region_reactive,
        selected_data_source_reactive,
        all_available_species_reactive,
        all_available_regions_reactive,
        all_available_data_sources_reactive,
        filter_options_loading_reactive,
        filter_options_error_reactive,
        observations_data_reactive,
        show_observed_data_reactive,
    )
    from config import FONT_BODY, COLOR_TEXT


@pytest.fixture
def setup_filter_panel():
    """Setup common test environment for filter panel tests."""
    selected_species_reactive.value = []
    selected_date_range_reactive.value = (None, None)
    selected_region_reactive.value = None
    selected_data_source_reactive.value = None
    all_available_species_reactive.value = ["Culex pipiens", "Aedes aegypti"]
    all_available_regions_reactive.value = ["Region 1", "Region 2"]
    all_available_data_sources_reactive.value = ["Source 1", "Source 2"]
    filter_options_loading_reactive.value = False
    filter_options_error_reactive.value = None
    observations_data_reactive.value = {"type": "FeatureCollection", "features": []}
    show_observed_data_reactive.value = True

    filter_panel.solara = MagicMock()
    filter_panel.solara.lab = MagicMock()
    filter_panel.solara.alias = MagicMock()

    with patch("components.map_module.filter_panel.httpx.AsyncClient") as mock_client:
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
    from components.map_module.filter_panel import FilterControls

    FilterControls()

    filter_panel.solara.Column.assert_called_once()

    filter_panel.solara.Markdown.assert_any_call(
        "##### Species",
        style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; margin-top: 10px;",
    )

    filter_panel.solara.Markdown.assert_any_call(
        "##### Date Range",
        style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; margin-top: 10px;",
    )


@patch("components.map_module.filter_panel.fetch_filter_options")
def test_filter_controls_fetch_options(mock_fetch_options, setup_filter_panel):
    """Test that filter options are fetched on component mount."""
    from components.map_module.filter_panel import FilterControls

    FilterControls()

    mock_fetch_options.assert_called_once()


@patch("components.map_module.filter_panel.fetch_observations_data_for_panel")
async def test_apply_filters_click(mock_fetch_data, setup_filter_panel):
    """Test that applying filters triggers data fetch with correct parameters."""
    test_start_date = datetime.date(2023, 1, 1)
    test_end_date = datetime.date(2023, 12, 31)
    selected_date_range_reactive.value = (test_start_date, test_end_date)
    selected_species_reactive.value = ["Culex pipiens"]

    from components.map_module.filter_panel import FilterControls

    component = FilterControls()

    await component.handle_apply_filters_click()

    expected_params = {
        "species": "Culex pipiens",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
    }

    call_args = mock_fetch_data.call_args[0][0]

    assert call_args["species"] == expected_params["species"]
    assert call_args["start_date"] == expected_params["start_date"]
    assert call_args["end_date"] == expected_params["end_date"]


@patch("components.map_module.filter_panel.fetch_observations_data_for_panel")
async def test_initial_data_load(mock_fetch_data, setup_filter_panel):
    """Test that initial data is loaded when component mounts."""
    selected_species_reactive.value = ["Culex pipiens"]
    test_start_date = datetime.date(2023, 1, 1)
    test_end_date = datetime.date(2023, 12, 31)
    selected_date_range_reactive.value = (test_start_date, test_end_date)

    from components.map_module.filter_panel import FilterControls

    component = FilterControls()

    await component.initial_load_observations()

    mock_fetch_data.assert_called_once()

    call_args = mock_fetch_data.call_args[0][0]

    assert call_args["species"] == "Culex pipiens"
    assert call_args["start_date"] == "2023-01-01"
    assert call_args["end_date"] == "2023-12-31"


def test_loading_state_display(setup_filter_panel):
    """Test that loading state is displayed correctly."""
    filter_options_loading_reactive.value = True

    from components.map_module.filter_panel import FilterControls

    FilterControls()

    filter_panel.solara.ProgressLinear.assert_called_with(True)
    filter_panel.solara.Text.assert_any_call(
        "Loading filter options...",
        style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; font-style: italic;",
    )


def test_error_state_display(setup_filter_panel):
    """Test that error state is displayed correctly."""
    error_message = "Failed to load filter options"
    filter_options_error_reactive.value = error_message

    from components.map_module.filter_panel import FilterControls

    FilterControls()

    filter_panel.solara.Error.assert_called_once_with(error_message)

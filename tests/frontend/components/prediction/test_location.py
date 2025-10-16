"""
Tests for the LocationComponent.
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "frontend"))

with patch.dict(
    "sys.modules",
    {
        "solara": MagicMock(),
        "ipyleaflet": MagicMock(),
    },
):
    from frontend.components.prediction import location


@pytest.fixture
def setup_location_component():
    """Setup common test environment for location component tests."""
    location.solara = MagicMock()
    location.L = MagicMock()

    mock_marker = MagicMock()
    location.L.Marker.return_value = mock_marker

    mock_map = MagicMock()
    location.L.Map.return_value = mock_map

    mock_use_state = MagicMock(return_value=(None, MagicMock()))

    mock_use_memo = MagicMock(return_value=mock_map)

    mock_use_effect = MagicMock()

    with patch.multiple(
        location,
        use_state=mock_use_state,
        use_memo=mock_use_memo,
        use_effect=mock_use_effect,
    ):
        yield {
            "mock_map": mock_map,
            "mock_marker": mock_marker,
            "mock_use_state": mock_use_state,
            "mock_use_memo": mock_use_memo,
            "mock_use_effect": mock_use_effect,
        }


def test_location_component_initialization(setup_location_component):
    """Test that the location component initializes correctly."""
    mock_set_latitude = MagicMock()
    mock_set_longitude = MagicMock()

    location.LocationComponent(
        latitude=None,
        set_latitude=mock_set_latitude,
        longitude=None,
        set_longitude=mock_set_longitude,
        initial_lat=40.0,
        initial_lon=-74.0,
        initial_zoom=10,
    )

    location.L.Map.assert_called_once()
    args, kwargs = location.L.Map.call_args
    assert kwargs["center"] == (40.0, -74.0)
    assert kwargs["zoom"] == 10
    assert kwargs["scroll_wheel_zoom"] is True


def test_location_component_marker_creation(setup_location_component):
    """Test that a marker is created when coordinates are provided."""
    mock_set_latitude = MagicMock()
    mock_set_longitude = MagicMock()

    location.LocationComponent(
        latitude=40.7128,
        set_latitude=mock_set_latitude,
        longitude=-74.0060,
        set_longitude=mock_set_longitude,
    )

    sync_effect = setup_location_component["mock_use_effect"].call_args_list[0][0][0]

    sync_effect()

    location.L.Marker.assert_called_once_with(
        location=(40.7128, -74.0060),
        draggable=True,
        title="Selected location",
    )

    setup_location_component["mock_map"].add_layer.assert_called_once_with(
        setup_location_component["mock_marker"],
    )

    assert setup_location_component["mock_map"].center == (40.7128, -74.0060)
    assert setup_location_component["mock_map"].zoom == 10


def test_location_component_map_click(setup_location_component):
    """Test that clicking the map updates the coordinates."""
    mock_set_latitude = MagicMock()
    mock_set_longitude = MagicMock()

    location.LocationComponent(
        latitude=None,
        set_latitude=mock_set_latitude,
        longitude=None,
        set_longitude=mock_set_longitude,
    )

    click_effect = setup_location_component["mock_use_effect"].call_args_list[1][0][0]

    click_handler = None
    for call_args in setup_location_component["mock_map"].on_interaction.call_args_list:
        if call_args[0][0] == click_effect:
            click_handler = call_args[0][1]
            break

    assert click_handler is not None, "Click handler not found"

    click_event = {
        "type": "click",
        "coordinates": (40.7128, -74.0060),
    }
    click_handler(**click_event)

    mock_set_latitude.assert_called_once_with(40.7128)
    mock_set_longitude.assert_called_once_with(-74.0060)


def test_location_component_marker_drag(setup_location_component):
    """Test that dragging the marker updates the coordinates."""
    mock_set_latitude = MagicMock()
    mock_set_longitude = MagicMock()

    location.LocationComponent(
        latitude=40.7128,
        set_latitude=mock_set_latitude,
        longitude=-74.0060,
        set_longitude=mock_set_longitude,
    )

    sync_effect = setup_location_component["mock_use_effect"].call_args_list[0][0][0]
    sync_effect()

    marker = setup_location_component["mock_marker"]
    marker.observe.assert_called_once()

    location_change_handler = marker.observe.call_args[0][0]

    location_change_handler({"name": "location", "new": (40.7138, -74.0070)})

    mock_set_latitude.assert_called_once_with(40.7138)
    mock_set_longitude.assert_called_once_with(-74.0070)

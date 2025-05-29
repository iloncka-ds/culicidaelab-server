"""
Tests for the LocationComponent.
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Import the component to test
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "frontend"))

# Mock the solara and other modules before importing the component
with patch.dict('sys.modules', {
    'solara': MagicMock(),
    'ipyleaflet': MagicMock(),
}):
    from components.prediction import location

@pytest.fixture
def setup_location_component():
    """Setup common test environment for location component tests."""
    # Mock solara and ipyleaflet
    location.solara = MagicMock()
    location.L = MagicMock()
    
    # Mock the Marker class
    mock_marker = MagicMock()
    location.L.Marker.return_value = mock_marker
    
    # Mock the Map widget
    mock_map = MagicMock()
    location.L.Map.return_value = mock_map
    
    # Mock use_state
    mock_use_state = MagicMock(return_value=(None, MagicMock()))
    
    # Mock use_memo
    mock_use_memo = MagicMock(return_value=mock_map)
    
    # Mock use_effect
    mock_use_effect = MagicMock()
    
    with patch.multiple(location,
        use_state=mock_use_state,
        use_memo=mock_use_memo,
        use_effect=mock_use_effect,
    ):
        yield {
            'mock_map': mock_map,
            'mock_marker': mock_marker,
            'mock_use_state': mock_use_state,
            'mock_use_memo': mock_use_memo,
            'mock_use_effect': mock_use_effect,
        }

def test_location_component_initialization(setup_location_component):
    """Test that the location component initializes correctly."""
    # Setup
    mock_set_latitude = MagicMock()
    mock_set_longitude = MagicMock()
    
    # Call the component
    location.LocationComponent(
        latitude=None,
        set_latitude=mock_set_latitude,
        longitude=None,
        set_longitude=mock_set_longitude,
        initial_lat=40.0,
        initial_lon=-74.0,
        initial_zoom=10
    )
    
    # Verify the map was created with correct initial parameters
    location.L.Map.assert_called_once()
    args, kwargs = location.L.Map.call_args
    assert kwargs['center'] == (40.0, -74.0)
    assert kwargs['zoom'] == 10
    assert kwargs['scroll_wheel_zoom'] is True

def test_location_component_marker_creation(setup_location_component):
    """Test that a marker is created when coordinates are provided."""
    # Setup
    mock_set_latitude = MagicMock()
    mock_set_longitude = MagicMock()
    
    # Call the component with coordinates
    location.LocationComponent(
        latitude=40.7128,
        set_latitude=mock_set_latitude,
        longitude=-74.0060,
        set_longitude=mock_set_longitude,
    )
    
    # Get the effect that syncs the marker with state
    sync_effect = setup_location_component['mock_use_effect'].call_args_list[0][0][0]
    
    # Execute the effect to trigger marker creation
    sync_effect()
    
    # Verify the marker was created with the correct location
    location.L.Marker.assert_called_once_with(
        location=(40.7128, -74.0060),
        draggable=True,
        title="Selected location"
    )
    
    # Verify the marker was added to the map
    setup_location_component['mock_map'].add_layer.assert_called_once_with(
        setup_location_component['mock_marker']
    )
    
    # Verify the map was centered on the marker
    assert setup_location_component['mock_map'].center == (40.7128, -74.0060)
    assert setup_location_component['mock_map'].zoom == 10

def test_location_component_map_click(setup_location_component):
    """Test that clicking the map updates the coordinates."""
    # Setup
    mock_set_latitude = MagicMock()
    mock_set_longitude = MagicMock()
    
    # Call the component
    location.LocationComponent(
        latitude=None,
        set_latitude=mock_set_latitude,
        longitude=None,
        set_longitude=mock_set_longitude,
    )
    
    # Get the click handler
    click_effect = setup_location_component['mock_use_effect'].call_args_list[1][0][0]
    
    # Simulate a map click
    click_handler = None
    for call_args in setup_location_component['mock_map'].on_interaction.call_args_list:
        if call_args[0][0] == click_effect:
            click_handler = call_args[0][1]
            break
    
    assert click_handler is not None, "Click handler not found"
    
    # Simulate a click event
    click_event = {
        'type': 'click',
        'coordinates': (40.7128, -74.0060)
    }
    click_handler(**click_event)
    
    # Verify the coordinates were updated
    mock_set_latitude.assert_called_once_with(40.7128)
    mock_set_longitude.assert_called_once_with(-74.0060)

def test_location_component_marker_drag(setup_location_component):
    """Test that dragging the marker updates the coordinates."""
    # Setup
    mock_set_latitude = MagicMock()
    mock_set_longitude = MagicMock()
    
    # Call the component with coordinates
    location.LocationComponent(
        latitude=40.7128,
        set_latitude=mock_set_latitude,
        longitude=-74.0060,
        set_longitude=mock_set_longitude,
    )
    
    # Get the marker creation effect
    sync_effect = setup_location_component['mock_use_effect'].call_args_list[0][0][0]
    sync_effect()  # Trigger marker creation
    
    # Get the marker's location change handler
    marker = setup_location_component['mock_marker']
    marker.observe.assert_called_once()
    
    # The first call to observe is for the location change handler
    location_change_handler = marker.observe.call_args[0][0]
    
    # Simulate a marker drag
    location_change_handler({'name': 'location', 'new': (40.7138, -74.0070)})
    
    # Verify the coordinates were updated with rounded values
    mock_set_latitude.assert_called_once_with(40.7138)
    mock_set_longitude.assert_called_once_with(-74.0070)

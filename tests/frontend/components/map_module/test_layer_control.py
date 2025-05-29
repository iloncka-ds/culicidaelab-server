"""
Tests for the LayerControl component.
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
}):
    from components.map_module import layer_control
    from state import show_observed_data_reactive

@pytest.fixture
def setup_layer_control():
    """Setup common test environment for layer control tests."""
    # Reset reactive variables
    show_observed_data_reactive.value = False
    
    # Mock solara components
    layer_control.solara = MagicMock()
    
    # Mock the Switch component
    mock_switch = MagicMock()
    layer_control.solara.Switch = mock_switch
    
    # Mock the Column component to return None
    mock_column = MagicMock()
    mock_column.return_value = None
    layer_control.solara.Column = mock_column
    
    return {
        'mock_switch': mock_switch,
        'mock_column': mock_column
    }

def test_layer_control_initial_state(setup_layer_control):
    """Test that the layer control initializes with the correct state."""
    # Import here to ensure mocks are in place
    from components.map_module.layer_control import LayerToggle
    
    # Call the component
    LayerToggle()
    
    # Verify the column was created
    setup_layer_control['mock_column'].assert_called_once()
    
    # Verify the Switch components were created with correct parameters
    # Only checking for the active layer (show_observed_data_reactive)
    switch_calls = setup_layer_control['mock_switch'].call_args_list
    
    # Verify the observed data switch is present
    found_observed_switch = False
    for call in switch_calls:
        args, kwargs = call
        if len(args) >= 2 and args[0] == "Observed Data":
            found_observed_switch = True
            # Verify it's bound to the correct reactive variable
            assert kwargs['value'] == show_observed_data_reactive
    
    assert found_observed_switch, "Observed Data switch not found in layer controls"

def test_layer_control_toggle_observed_data(setup_layer_control):
    """Test that toggling the observed data layer works."""
    # Import here to ensure mocks are in place
    from components.map_module.layer_control import LayerToggle
    
    # Call the component
    LayerToggle()
    
    # Get the Switch component for observed data
    switch_calls = setup_layer_control['mock_switch'].call_args_list
    observed_switch = None
    
    for call in switch_calls:
        args, kwargs = call
        if len(args) >= 2 and args[0] == "Observed Data":
            observed_switch = kwargs
            break
    
    assert observed_switch is not None, "Observed Data switch not found"
    
    # Initial state should be False
    assert show_observed_data_reactive.value is False
    
    # Simulate toggling the switch
    observed_switch['value'].value = True
    
    # Verify the reactive variable was updated
    assert show_observed_data_reactive.value is True

def test_layer_control_only_observed_data_layer(setup_layer_control):
    """Test that only the observed data layer is available (other layers removed)."""
    # Import here to ensure mocks are in place
    from components.map_module.layer_control import LayerToggle
    
    # Call the component
    LayerToggle()
    
    # Get all switch calls
    switch_calls = setup_layer_control['mock_switch'].call_args_list
    
    # Verify only one switch is created (for observed data)
    assert len(switch_calls) == 1, f"Expected 1 switch, got {len(switch_calls)}"
    
    # Verify it's the observed data switch
    args, _ = switch_calls[0]
    assert args[0] == "Observed Data"

def test_layer_control_no_other_layers(setup_layer_control):
    """Test that no other layer toggles are present."""
    # Import here to ensure mocks are in place
    from components.map_module.layer_control import LayerToggle
    
    # Call the component
    LayerToggle()
    
    # Get all switch calls
    switch_calls = setup_layer_control['mock_switch'].call_args_list
    
    # Verify no other layer toggles are present
    for call in switch_calls:
        args, _ = call
        layer_name = args[0] if len(args) > 0 else ""
        assert layer_name in ["Observed Data"], f"Unexpected layer toggle: {layer_name}"

"""
Tests for the LegendComponent.
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
    'solara.lab': MagicMock(),
    'solara.alias': MagicMock(),
}):
    from components.map_module import legend_component
    from state import (
        show_observed_data_reactive,
        selected_species_reactive,
        observations_data_reactive,
        all_available_species_reactive
    )
    from config import FONT_HEADINGS, COLOR_TEXT, FONT_BODY

@pytest.fixture
def mock_observations_data():
    """Provide sample observations data for testing."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "species": "Culex pipiens",
                    "date": "2023-01-15",
                    "count": 5
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [12.4923, 41.8902]
                }
            },
            {
                "type": "Feature",
                "properties": {
                    "species": "Aedes aegypti",
                    "date": "2023-01-16",
                    "count": 3
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [12.5, 41.9]
                }
            }
        ]
    }

def test_legend_display_no_data():
    """Test that the legend handles no data case correctly."""
    # Setup test data
    show_observed_data_reactive.value = False
    observations_data_reactive.value = None
    selected_species_reactive.value = []
    
    # Import here to ensure mocks are in place
    from components.map_module.legend_component import LegendDisplay
    
    # Call the component
    LegendDisplay()
    
    # Verify the component renders without errors
    legend_component.solara.Column.assert_called_once()
    legend_component.solara.Markdown.assert_called_with(
        "## Map Legend",
        style=f"font-family: {FONT_HEADINGS}; color: {COLOR_TEXT}; margin-bottom: 10px;"
    )

def test_legend_display_with_observed_data(mock_observations_data):
    """Test that the legend displays observed species correctly."""
    # Setup test data
    show_observed_data_reactive.value = True
    observations_data_reactive.value = mock_observations_data
    selected_species_reactive.value = []
    all_available_species_reactive.value = ["Culex pipiens", "Aedes aegypti"]
    
    # Mock generate_species_colors
    mock_colors = {
        "Culex pipiens": "#FF0000",
        "Aedes aegypti": "#00FF00"
    }
    with patch('components.map_module.legend_component.generate_species_colors', return_value=mock_colors):
        # Import here to ensure mocks are in place
        from components.map_module.legend_component import LegendDisplay
        
        # Call the component
        LegendDisplay()
        
        # Verify the component renders the observed species section
        legend_component.solara.Markdown.assert_any_call(
            "#### Observed Species",
            style=f"font-family: {FONT_HEADINGS}; color: {COLOR_TEXT}; margin-top: 10px; margin-bottom: 5px;"
        )
        
        # Verify species are displayed with their colors
        assert legend_component.solara.Row.call_count >= 2  # At least two species
        assert legend_component.solara.Div.call_count >= 2  # Color indicators
        assert legend_component.solara.Text.call_count >= 2  # Species names

def test_legend_display_with_selected_species(mock_observations_data):
    """Test that the legend respects selected species filter."""
    # Setup test data
    show_observed_data_reactive.value = True
    observations_data_reactive.value = mock_observations_data
    selected_species_reactive.value = ["Culex pipiens"]
    all_available_species_reactive.value = ["Culex pipiens", "Aedes aegypti"]
    
    # Mock generate_species_colors
    mock_colors = {
        "Culex pipiens": "#FF0000",
        "Aedes aegypti": "#00FF00"
    }
    with patch('components.map_module.legend_component.generate_species_colors', return_value=mock_colors):
        # Import here to ensure mocks are in place
        from components.map_module.legend_component import LegendDisplay
        
        # Call the component
        LegendDisplay()
        
        # Verify only the selected species is displayed
        legend_component.solara.Markdown.assert_any_call(
            "#### Observed Species",
            style=f"font-family: {FONT_HEADINGS}; color: {COLOR_TEXT}; margin-top: 10px; margin-bottom: 5px;"
        )
        
        # Verify only the selected species is displayed
        assert legend_component.solara.Row.call_count >= 1  # Only one species
        assert "Culex pipiens" in str(legend_component.solara.Text.call_args_list)
        assert "Aedes aegypti" not in str(legend_component.solara.Text.call_args_list)

def test_legend_display_no_species_in_view():
    """Test that the legend handles no species in current view."""
    # Setup test data
    show_observed_data_reactive.value = True
    observations_data_reactive.value = {"type": "FeatureCollection", "features": []}
    selected_species_reactive.value = []
    
    # Import here to ensure mocks are in place
    from components.map_module.legend_component import LegendDisplay
    
    # Call the component
    LegendDisplay()
    
    # Verify the no species message is displayed
    legend_component.solara.Text.assert_any_call(
        "No species in current data view",
        style=f"font-size: 0.9em; font-style: italic; font-family: {FONT_BODY}; color: {COLOR_TEXT};"
    )

"""
Tests for the InformationDisplay component.
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
    'solara.alias': MagicMock(),
    'pandas': MagicMock(),
    'plotly.express': MagicMock(),
    'plotly.graph_objects': MagicMock(),
}):
    # Create mock for plotly.graph_objects.Figure
    go = MagicMock()
    go.Figure = MagicMock()
    from components.map_module import info_panel
    from state import (
        selected_map_feature_info,
        selected_species_reactive,
        observations_data_reactive
    )
    from config import COLOR_BUTTON_PRIMARY_BG, COLOR_TEXT, FONT_HEADINGS

@pytest.fixture
def setup_info_panel():
    """Setup common test environment for info panel tests."""
    # Reset reactive variables
    selected_map_feature_info.value = None
    selected_species_reactive.value = []
    observations_data_reactive.value = {"type": "FeatureCollection", "features": []}
    
    # Mock plotly express
    info_panel.px = MagicMock()
    
    # Create a mock figure
    mock_fig = MagicMock(spec=go.Figure)
    info_panel.px.bar.return_value = mock_fig
    
    # Mock pandas
    mock_df = MagicMock()
    info_panel.pd.DataFrame.return_value = mock_df
    
    # Mock DataFrame operations
    mock_empty_df = MagicMock()
    mock_empty_df.empty = True
    mock_empty_df.__getitem__.return_value = MagicMock()
    mock_empty_df.__getitem__.return_value.isin.return_value = MagicMock()
    
    # Setup non-empty DataFrame
    mock_non_empty_df = MagicMock()
    mock_non_empty_df.empty = False
    mock_non_empty_df.__contains__.return_value = True  # For 'species' in df.columns check
    mock_non_empty_df.__getitem__.return_value = MagicMock()
    mock_non_empty_df.__getitem__.return_value.isin.return_value = MagicMock()
    
    # Mock value_counts
    value_counts_result = MagicMock()
    value_counts_result.reset_index.return_value = MagicMock(columns=["Species", "Count"])
    mock_non_empty_df.__getitem__.return_value.value_counts.return_value = value_counts_result
    
    # Return both mock dataframes
    return {
        'empty_df': mock_empty_df,
        'non_empty_df': mock_non_empty_df,
        'mock_fig': mock_fig
    }

def test_info_display_no_selection(setup_info_panel):
    """Test that the info panel shows a message when nothing is selected."""
    # Import here to ensure mocks are in place
    from components.map_module.info_panel import InformationDisplay
    
    # Setup empty selections
    selected_map_feature_info.value = None
    selected_species_reactive.value = []
    
    # Call the component
    InformationDisplay()
    
    # Verify the no selection message is shown
    info_panel.solara.Markdown.assert_called_with(
        "Click on a map feature or select species to see details.",
        style=f"color: {COLOR_TEXT};"
    )

def test_info_display_feature_selection(setup_info_panel):
    """Test that the info panel shows feature details when a feature is selected."""
    # Import here to ensure mocks are in place
    from components.map_module.info_panel import InformationDisplay
    
    # Setup feature selection
    feature_data = {
        "name": "Test Location",
        "species": "Culex pipiens",
        "count": 5,
        "date": "2023-01-15",
        "geometry": {"type": "Point"},  # Should be excluded
        "style": {"color": "red"},  # Should be excluded
    }
    selected_map_feature_info.value = feature_data
    
    # Call the component
    InformationDisplay()
    
    # Verify the feature title is shown
    info_panel.solara.Markdown.assert_any_call(
        "### Details for: `Test Location`",
        style=f"font-family: {FONT_HEADINGS}; color: {COLOR_TEXT};"
    )
    
    # Verify the clear selection button is shown
    info_panel.solara.Button.assert_called_with(
        "Clear Selection",
        on_click=info_panel.solara.get_reactive_value(info_panel.selected_map_feature_info).set,
        small=True,
        outlined=True,
        color=COLOR_BUTTON_PRIMARY_BG,
        style="margin-top: 10px; text-transform: none;"
    )

def test_info_display_species_selection_with_data(setup_info_panel):
    """Test that the info panel shows species summary when species are selected."""
    # Import here to ensure mocks are in place
    from components.map_module.info_panel import InformationDisplay
    
    # Setup species selection and observations data
    selected_species_reactive.value = ["Culex pipiens"]
    
    # Mock observations data
    obs_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "species": "Culex pipiens",
                    "count": 5,
                    "date": "2023-01-15"
                },
                "geometry": {"type": "Point"}
            }
        ]
    }
    observations_data_reactive.value = obs_data
    
    # Setup DataFrame mock to return non-empty DataFrame
    info_panel.pd.DataFrame.return_value = setup_info_panel['non_empty_df']
    
    # Call the component
    InformationDisplay()
    
    # Verify the species summary is shown
    info_panel.solara.Markdown.assert_any_call(
        "### Summary for: Culex pipiens",
        style=f"font-family: {FONT_HEADINGS}; color: {COLOR_TEXT};"
    )
    
    # Verify plotly express bar chart is created
    info_panel.px.bar.assert_called_once()
    
    # Verify the figure layout is updated
    setup_info_panel['mock_fig'].update_layout.assert_called_once()

def test_info_display_empty_observations(setup_info_panel):
    """Test that the info panel handles empty observations data."""
    # Import here to ensure mocks are in place
    from components.map_module.info_panel import InformationDisplay
    
    # Setup species selection but empty observations
    selected_species_reactive.value = ["Culex pipiens"]
    observations_data_reactive.value = {"type": "FeatureCollection", "features": []}
    
    # Setup DataFrame mock to return empty DataFrame
    info_panel.pd.DataFrame.return_value = setup_info_panel['empty_df']
    
    # Call the component
    InformationDisplay()
    
    # Verify the species summary is shown
    info_panel.solara.Markdown.assert_any_call(
        "### Summary for: Culex pipiens",
        style=f"font-family: {FONT_HEADINGS}; color: {COLOR_TEXT};"
    )
    
    # Verify no plot is created for empty data
    info_panel.px.bar.assert_not_called()

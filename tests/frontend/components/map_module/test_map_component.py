"""
Tests for the MapComponent and related functionality.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
from pathlib import Path
import json

# Import the component to test
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "frontend"))

# Mock the solara and other modules before importing the component
with patch.dict('sys.modules', {
    'solara': MagicMock(),
    'solara.lab': MagicMock(),
    'solara.alias': MagicMock(),
    'ipyleaflet': MagicMock(),
    'ipywidgets': MagicMock(),
    'httpx': MagicMock(),
    'asyncio': MagicMock(),
}):
    from components.map_module import map_component
    from state import (
        selected_species_reactive,
        show_observed_data_reactive,
        selected_map_feature_info,
        current_map_bounds_reactive,
        current_map_zoom_reactive,
        observations_data_reactive,
        observations_loading_reactive,
        selected_date_range_reactive,
        all_available_species_reactive
    )
    from config import DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM, SPECIES_COLORS

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
                    "coordinates": [12.4923, 41.8902]  # lon, lat
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
                    "coordinates": [12.5, 41.9]  # lon, lat
                }
            }
        ]
    }


@pytest.fixture
def mock_leaflet_map():
    """Mock the Leaflet map instance."""
    mock_map = MagicMock()
    mock_map.center = (0, 0)
    mock_map.zoom = 10
    mock_map.bounds = ((0, 0), (1, 1))
    return mock_map


@pytest.fixture
def map_manager(mock_leaflet_map):
    """Create a map manager with a mocked map instance."""
    with patch('components.map_module.map_component.L.Map', return_value=mock_leaflet_map):
        manager = map_component.LeafletMapManager()
        manager.map_instance = mock_leaflet_map
        return manager


def test_map_manager_initialization(map_manager, mock_leaflet_map):
    """Test that the map manager initializes correctly."""
    # Verify the map was created with the correct defaults
    map_component.L.Map.assert_called_once()
    
    # Check that the OSM layer was added
    assert mock_leaflet_map.add_layer.call_count >= 1  # At least OSM layer
    
    # Check that the observations layer group was created
    assert hasattr(map_manager, 'observations_layer_group')
    
    # Check that controls were added
    assert mock_leaflet_map.add_control.call_count >= 2  # Layers control and scale control


def test_handle_map_bounds_change(map_manager, mock_leaflet_map):
    """Test that map bounds changes are handled correctly."""
    # Setup test data
    test_bounds = ((40.0, -3.0), (60.0, 30.0))
    change_event = {'name': 'bounds', 'new': test_bounds}
    
    # Trigger the bounds change
    map_manager._handle_map_bounds_change(change_event)
    
    # Verify the reactive variable was updated
    assert current_map_bounds_reactive.value == test_bounds


def test_handle_map_zoom_change(map_manager):
    """Test that map zoom changes are handled correctly."""
    # Setup test data
    test_zoom = 8
    change_event = {'name': 'zoom', 'new': test_zoom}
    
    # Trigger the zoom change
    map_manager._handle_map_zoom_change(change_event)
    
    # Verify the reactive variable was updated
    assert current_map_zoom_reactive.value == test_zoom


def test_create_popup_html(map_manager):
    """Test that popup HTML is generated correctly."""
    # Test data
    props = {
        'name': 'Test Location',
        'count': 5,
        'date': '2023-01-15',
        'geometry': {'type': 'Point'},  # Should be excluded
        'style': {'color': 'red'},  # Should be excluded
    }
    
    # Generate the popup HTML
    html = map_manager._create_popup_html(props)
    
    # Verify the content
    assert '<h4>Test Location</h4>' in html
    assert 'Count: 5' in html
    assert 'Date: 2023-01-15' in html
    assert 'geometry' not in html  # Should be excluded
    assert 'style' not in html  # Should be excluded


@patch('components.map_module.map_component.generate_species_colors')
def test_get_species_color(mock_generate_colors, map_manager):
    """Test that species colors are retrieved correctly."""
    # Setup test data
    test_species = ['Culex pipiens', 'Aedes aegypti']
    test_colors = {
        'Culex pipiens': '#FF0000',
        'Aedes aegypti': '#00FF00'
    }
    
    # Configure the mock
    mock_generate_colors.return_value = test_colors
    all_available_species_reactive.value = test_species
    
    # Test getting a color for a known species
    color = map_manager._get_species_color('Culex pipiens')
    assert color == '#FF0000'
    
    # Test getting a color for an unknown species (should return default)
    default_color = map_manager._get_species_color('Unknown Species')
    assert default_color == 'rgba(128,128,128,0.7)'


def test_update_observations_layer(map_manager, mock_observations_data):
    """Test that the observations layer is updated correctly."""
    # Setup test data
    map_manager.observations_layer_group.clear_layers = MagicMock()
    map_manager.observations_layer_group.add_layer = MagicMock()
    
    # Test with observations data
    show_observed_data_reactive.value = True
    map_manager.update_observations_layer(mock_observations_data)
    
    # Verify the layer group was cleared and markers were added
    map_manager.observations_layer_group.clear_layers.assert_called_once()
    assert map_manager.observations_layer_group.add_layer.call_count == 1  # Should add marker cluster
    
    # Test with observations disabled
    show_observed_data_reactive.value = False
    map_manager.observations_layer_group.clear_layers.reset_mock()
    map_manager.update_observations_layer(mock_observations_data)
    
    # Verify the layer group was cleared but no markers were added
    map_manager.observations_layer_group.clear_layers.assert_called_once()
    map_manager.observations_layer_group.add_layer.assert_not_called()


@patch('components.map_module.map_component.fetch_geojson_data')
@patch('components.map_module.map_component.LeafletMapManager')
@patch('solara.use_memo')
@patch('solara.lab.use_task')
@patch('solara.use_effect')
async def test_map_display_component(
    mock_use_effect, mock_use_task, mock_use_memo, mock_map_manager_class, mock_fetch, mock_observations_data
):
    """Test the MapDisplay component integration."""
    # Setup mocks
    mock_map_manager = MagicMock()
    mock_map_manager_class.return_value = mock_map_manager
    mock_use_memo.return_value = mock_map_manager
    mock_fetch.return_value = mock_observations_data
    
    # Import here to avoid circular imports
    from components.map_module.map_component import MapDisplay
    
    # Call the component
    MapDisplay()
    
    # Verify the map manager was created
    mock_map_manager_class.assert_called_once()
    
    # Verify use_memo was called with the correct dependencies
    mock_use_memo.assert_called_once()
    
    # Verify use_task was set up
    mock_use_task.assert_called_once()
    
    # Verify use_effect was set up for layer updates
    assert mock_use_effect.call_count >= 1

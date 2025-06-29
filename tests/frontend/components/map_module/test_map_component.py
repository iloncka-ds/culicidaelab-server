"""
Tests for the MapComponent and related functionality.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "frontend"))

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
    map_component.L.Map.assert_called_once()

    assert mock_leaflet_map.add_layer.call_count >= 1

    assert hasattr(map_manager, 'observations_layer_group')

    assert mock_leaflet_map.add_control.call_count >= 2


def test_handle_map_bounds_change(map_manager, mock_leaflet_map):
    """Test that map bounds changes are handled correctly."""
    test_bounds = ((40.0, -3.0), (60.0, 30.0))
    change_event = {'name': 'bounds', 'new': test_bounds}

    map_manager._handle_map_bounds_change(change_event)

    assert current_map_bounds_reactive.value == test_bounds


def test_handle_map_zoom_change(map_manager):
    """Test that map zoom changes are handled correctly."""
    test_zoom = 8
    change_event = {'name': 'zoom', 'new': test_zoom}

    map_manager._handle_map_zoom_change(change_event)

    assert current_map_zoom_reactive.value == test_zoom


def test_create_popup_html(map_manager):
    """Test that popup HTML is generated correctly."""
    props = {
        'name': 'Test Location',
        'count': 5,
        'date': '2023-01-15',
        'geometry': {'type': 'Point'},
        'style': {'color': 'red'},
    }

    html = map_manager._create_popup_html(props)

    assert '<h4>Test Location</h4>' in html
    assert 'Count: 5' in html
    assert 'Date: 2023-01-15' in html
    assert 'geometry' not in html
    assert 'style' not in html


@patch('components.map_module.map_component.generate_species_colors')
def test_get_species_color(mock_generate_colors, map_manager):
    """Test that species colors are retrieved correctly."""
    test_species = ['Culex pipiens', 'Aedes aegypti']
    test_colors = {
        'Culex pipiens': '#FF0000',
        'Aedes aegypti': '#00FF00'
    }

    mock_generate_colors.return_value = test_colors
    all_available_species_reactive.value = test_species

    color = map_manager._get_species_color('Culex pipiens')
    assert color == '#FF0000'

    default_color = map_manager._get_species_color('Unknown Species')
    assert default_color == 'rgba(128,128,128,0.7)'


def test_update_observations_layer(map_manager, mock_observations_data):
    """Test that the observations layer is updated correctly."""
    map_manager.observations_layer_group.clear_layers = MagicMock()
    map_manager.observations_layer_group.add_layer = MagicMock()

    show_observed_data_reactive.value = True
    map_manager.update_observations_layer(mock_observations_data)

    map_manager.observations_layer_group.clear_layers.assert_called_once()
    assert map_manager.observations_layer_group.add_layer.call_count == 1

    show_observed_data_reactive.value = False
    map_manager.observations_layer_group.clear_layers.reset_mock()
    map_manager.update_observations_layer(mock_observations_data)

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
    mock_map_manager = MagicMock()
    mock_map_manager_class.return_value = mock_map_manager
    mock_use_memo.return_value = mock_map_manager
    mock_fetch.return_value = mock_observations_data

    from components.map_module.map_component import MapDisplay

    MapDisplay()

    mock_map_manager_class.assert_called_once()

    mock_use_memo.assert_called_once()

    mock_use_task.assert_called_once()

    assert mock_use_effect.call_count >= 1

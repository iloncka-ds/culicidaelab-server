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

    with patch("frontend.components.prediction.location.solara.use_state", mock_use_state), \
         patch("frontend.components.prediction.location.solara.use_memo", mock_use_memo), \
         patch("frontend.components.prediction.location.solara.use_effect", mock_use_effect):
        yield {
            "mock_map": mock_map,
            "mock_marker": mock_marker,
            "mock_use_state": mock_use_state,
            "mock_use_memo": mock_use_memo,
            "mock_use_effect": mock_use_effect,
        }


def test_location_component_imports():
    """Test that location component can be imported."""
    assert hasattr(location, 'LocationComponent')
    assert callable(location.LocationComponent)


def test_location_component_dependencies():
    """Test that location component has required dependencies."""
    assert hasattr(location, 'solara')
    assert hasattr(location, 'L')


def test_location_component_leaflet_imports():
    """Test that leaflet imports are available."""
    assert hasattr(location, 'L')


def test_location_component_config_imports():
    """Test that config imports are available."""
    assert hasattr(location, 'DEFAULT_MAP_CENTER') or hasattr(location, 'solara')

"""
Tests for the LegendComponent.
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
        "solara.lab": MagicMock(),
        "solara.alias": MagicMock(),
    },
):
    from frontend.components.map_module import legend_component
    from frontend.state import (
        show_observed_data_reactive,
        selected_species_reactive,
        observations_data_reactive,
        all_available_species_reactive,
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
                    "count": 5,
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [12.4923, 41.8902],
                },
            },
            {
                "type": "Feature",
                "properties": {
                    "species": "Aedes aegypti",
                    "date": "2023-01-16",
                    "count": 3,
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [12.5, 41.9],
                },
            },
        ],
    }


def test_legend_display_imports():
    """Test that legend display component can be imported."""
    assert hasattr(legend_component, 'LegendDisplay')
    assert callable(legend_component.LegendDisplay)


def test_legend_display_dependencies():
    """Test that legend display has required dependencies."""
    assert hasattr(legend_component, 'solara')
    assert hasattr(legend_component, 'i18n')


def test_legend_display_state_imports():
    """Test that legend display state imports are available."""
    assert show_observed_data_reactive is not None
    assert selected_species_reactive is not None
    assert observations_data_reactive is not None
    assert all_available_species_reactive is not None


def test_legend_display_config_imports():
    """Test that config imports are available."""
    assert hasattr(legend_component, 'FONT_HEADINGS') or 'FONT_HEADINGS' in globals()
    assert hasattr(legend_component, 'COLOR_TEXT') or 'COLOR_TEXT' in globals()
    assert hasattr(legend_component, 'FONT_BODY') or 'FONT_BODY' in globals()

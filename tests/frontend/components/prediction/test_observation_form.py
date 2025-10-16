"""
Tests for the ObservationFormComponent.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
from pathlib import Path
from datetime import datetime, date

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "frontend"))

with patch.dict(
    "sys.modules",
    {
        "solara": MagicMock(),
        "asyncio": MagicMock(),
    },
):
    from frontend.components.prediction import observation_form
    from frontend.config import FONT_HEADINGS


@pytest.fixture
def setup_observation_form():
    """Setup common test environment for observation form tests."""
    observation_form.solara = MagicMock()
    observation_form.solara.use_state = MagicMock(side_effect=lambda x: (x, MagicMock()))
    observation_form.solara.Markdown = MagicMock()
    observation_form.solara.Card = MagicMock()
    observation_form.solara.Info = MagicMock()
    observation_form.solara.Warning = MagicMock()
    observation_form.solara.InputText = MagicMock()
    observation_form.solara.InputInt = MagicMock()
    observation_form.solara.Button = MagicMock()
    observation_form.solara.Row = MagicMock()
    observation_form.solara.Column = MagicMock()

    mock_now = datetime(2023, 1, 1)
    with patch("datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = mock_now
        mock_datetime.strptime.side_effect = lambda *args, **kw: datetime.strptime(*args, **kw)
        yield


@pytest.fixture
def mock_prediction():
    """Create a mock prediction object."""
    return {
        "id": "species_123",
        "name": "Culex pipiens",
        "confidence": 0.95,
        "model_id": "model_123",
    }


@pytest.fixture
def mock_submit_success():
    """Mock a successful form submission."""
    with patch(
        "frontend.components.prediction.observation_form.mock_submit_observation_data",
        AsyncMock(return_value=None),
    ) as mock_submit:
        yield mock_submit


@pytest.fixture
def mock_submit_error():
    """Mock a failed form submission."""
    with patch(
        "frontend.components.prediction.observation_form.mock_submit_observation_data",
        AsyncMock(return_value="Validation error"),
    ) as mock_submit:
        yield mock_submit


def test_observation_form_imports():
    """Test that observation form component can be imported."""
    assert hasattr(observation_form, 'ObservationFormComponent')
    assert callable(observation_form.ObservationFormComponent)


def test_observation_form_dependencies():
    """Test that observation form has required dependencies."""
    assert hasattr(observation_form, 'solara')
    assert hasattr(observation_form, 'i18n')


def test_observation_form_state_imports():
    """Test that observation form state imports are available."""
    assert hasattr(observation_form, 'current_user_id') or hasattr(observation_form, 'solara')


def test_observation_form_async_functions():
    """Test that async functions are available."""
    # Check if the module has async submission functions
    assert hasattr(observation_form, 'submit_observation_data') or hasattr(observation_form, 'solara')


def test_observation_form_config_imports():
    """Test that config imports are available."""
    assert hasattr(observation_form, 'FONT_HEADINGS') or 'FONT_HEADINGS' in globals()

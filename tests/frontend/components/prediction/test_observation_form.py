"""
Tests for the ObservationFormComponent.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
from pathlib import Path
from datetime import datetime, date

# Import the component to test
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "frontend"))

# Mock the solara and other modules before importing the component
with patch.dict('sys.modules', {
    'solara': MagicMock(),
    'asyncio': MagicMock(),
}):
    from components.prediction import observation_form
    from config import FONT_HEADINGS

@pytest.fixture
def setup_observation_form():
    """Setup common test environment for observation form tests."""
    # Mock solara components
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
    
    # Mock datetime
    mock_now = datetime(2023, 1, 1)
    with patch('datetime.datetime') as mock_datetime:
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
        "model_id": "model_123"
    }

@pytest.fixture
def mock_submit_success():
    """Mock a successful form submission."""
    with patch('components.prediction.observation_form.mock_submit_observation_data', 
              AsyncMock(return_value=None)) as mock_submit:
        yield mock_submit

@pytest.fixture
def mock_submit_error():
    """Mock a failed form submission."""
    with patch('components.prediction.observation_form.mock_submit_observation_data', 
              AsyncMock(return_value="Validation error")) as mock_submit:
        yield mock_submit

def test_observation_form_initialization(setup_observation_form, mock_prediction):
    """Test that the observation form initializes correctly."""
    # Setup
    mock_on_success = MagicMock()
    mock_on_error = MagicMock()
    
    # Call the component
    observation_form.ObservationFormComponent(
        prediction=mock_prediction,
        file_name="test.jpg",
        current_latitude=40.7128,
        current_longitude=-74.0060,
        on_submit_success=mock_on_success,
        on_submit_error=mock_on_error
    )
    
    # Verify the form title is shown
    observation_form.solara.Markdown.assert_any_call(
        "### Submit Observation Details",
        style=f"margin-top:10px; margin-bottom:10px; font-family: {FONT_HEADINGS};"
    )
    
    # Verify the location info is shown
    observation_form.solara.Info.assert_called_once_with(
        "Selected Location: Lat: 40.7128, Lon: -74.0060",
        dense=True,
        style="margin-bottom:10px;"
    )

@pytest.mark.asyncio
async def test_observation_form_validation_errors(setup_observation_form, mock_prediction):
    """Test form validation with missing required fields."""
    # Setup
    mock_on_success = MagicMock()
    mock_on_error = MagicMock()
    
    # Call the component with missing required fields
    component = observation_form.ObservationFormComponent(
        prediction=None,  # Missing prediction
        file_name=None,  # Missing file name
        current_latitude=None,  # Missing latitude
        current_longitude=None,  # Missing longitude
        on_submit_success=mock_on_success,
        on_submit_error=mock_on_error
    )
    
    # Trigger form submission
    await component.handle_submit()
    
    # Verify the error callback was called with validation errors
    mock_on_error.assert_called_once()
    error_message = mock_on_error.call_args[0][0]
    assert "Prediction data is missing" in error_message
    assert "Image file name is missing" in error_message
    assert "Latitude and Longitude are required" in error_message
    
    # Verify success callback was not called
    mock_on_success.assert_not_called()

@pytest.mark.asyncio
async def test_observation_form_successful_submission(setup_observation_form, mock_prediction, mock_submit_success):
    """Test successful form submission."""
    # Setup
    mock_on_success = MagicMock()
    mock_on_error = MagicMock()
    
    # Setup mock date input
    test_date = date(2023, 1, 1)
    observation_form.solara.use_state.side_effect = [
        (test_date, MagicMock()),  # For obs_date_obj_state
        (1, MagicMock()),  # For obs_count
        ("", MagicMock()),  # For obs_notes
        ("user_01", MagicMock()),  # For obs_observer_id
        (50, MagicMock()),  # For obs_location_accuracy_m
        (False, MagicMock()),  # For is_submitting
    ]
    
    # Call the component
    component = observation_form.ObservationFormComponent(
        prediction=mock_prediction,
        file_name="test.jpg",
        current_latitude=40.7128,
        current_longitude=-74.0060,
        on_submit_success=mock_on_success,
        on_submit_error=mock_on_error
    )
    
    # Trigger form submission
    await component.handle_submit()
    
    # Verify the submission was successful
    mock_submit_success.assert_awaited_once()
    
    # Get the submitted payload
    submitted_payload = mock_submit_success.call_args[0][0]
    
    # Verify the payload structure
    assert submitted_payload["type"] == "Feature"
    assert submitted_payload["geometry"]["type"] == "Point"
    assert submitted_payload["geometry"]["coordinates"] == [-74.006, 40.7128]
    
    # Verify the properties
    props = submitted_payload["properties"]
    assert props["predicted_species_id"] == "species_123"
    assert props["observation_date"] == "2023-01-01"
    assert props["count"] == 1
    assert props["image_filename"] == "test.jpg"
    assert props["confidence"] == 0.95
    assert props["model_id"] == "model_123"
    
    # Verify success callback was called
    mock_on_success.assert_called_once()
    mock_on_error.assert_not_called()

@pytest.mark.asyncio
async def test_observation_form_submission_error(setup_observation_form, mock_prediction, mock_submit_error):
    """Test form submission with server error."""
    # Setup
    mock_on_success = MagicMock()
    mock_on_error = MagicMock()
    
    # Setup mock date input
    test_date = date(2023, 1, 1)
    observation_form.solara.use_state.side_effect = [
        (test_date, MagicMock()),  # For obs_date_obj_state
        (1, MagicMock()),  # For obs_count
        ("", MagicMock()),  # For obs_notes
        ("user_01", MagicMock()),  # For obs_observer_id
        (50, MagicMock()),  # For obs_location_accuracy_m
        (False, MagicMock()),  # For is_submitting
    ]
    
    # Call the component
    component = observation_form.ObservationFormComponent(
        prediction=mock_prediction,
        file_name="test.jpg",
        current_latitude=40.7128,
        current_longitude=-74.0060,
        on_submit_success=mock_on_success,
        on_submit_error=mock_on_error
    )
    
    # Trigger form submission
    await component.handle_submit()
    
    # Verify the submission was attempted but failed
    mock_submit_error.assert_awaited_once()
    
    # Verify error callback was called with the error message
    mock_on_error.assert_called_once_with("Validation error")
    mock_on_success.assert_not_called()

def test_observation_form_date_picker_fallback(setup_observation_form, mock_prediction):
    """Test that the form falls back to text input when DatePicker is not available."""
    # Setup to simulate DatePicker import failure
    with patch('components.prediction.observation_form.DatePicker', None):
        # Call the component
        observation_form.ObservationFormComponent(
            prediction=mock_prediction,
            file_name="test.jpg",
            current_latitude=40.7128,
            current_longitude=-74.0060,
            on_submit_success=MagicMock(),
            on_submit_error=MagicMock()
        )
        
        # Verify the fallback InputText is used for date
        observation_form.solara.InputText.assert_any_call(
            "Date (YYYY-MM-DD) *",
            value=datetime.now().date().strftime("%Y-%m-%d"),
            on_value=observation_form.solara.use_state.return_value[1],
        )

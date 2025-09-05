"""
Defines a form for submitting detailed species observation data.

This module contains the `ObservationFormComponent`, which is used in the
prediction workflow to collect additional details (like date, count, and notes)
after a species has been identified from an uploaded image.
"""

from typing import Any
from collections.abc import Callable
import asyncio
from datetime import datetime
import solara
from frontend.config import FONT_HEADINGS
from frontend.state import current_user_id, use_locale_effect
import i18n

from .observation_service import submit_observation_data


@solara.component
def ObservationFormComponent(
    prediction: dict[str, Any] | None,
    file_name: str | None,
    current_latitude: float | None,
    current_longitude: float | None,
    on_submit_success: Callable,
    on_submit_error: Callable,
):
    """
    A form for submitting detailed observation data following a successful prediction.

    This component renders a user interface for collecting additional information
    related to a species observation, such as the date, count, and notes. It is
    designed to be used in conjunction with a prediction result and location data.
    Upon submission, it validates the inputs, constructs a payload, and calls an
    asynchronous service to submit the data.

    The component manages its own internal state for form inputs and submission
    status (e.g., loading). It communicates the outcome of the submission
    process back to the parent component via the `on_submit_success` and
    `on_submit_error` callbacks.

    Args:
        prediction: A dictionary containing the results of the species
            prediction, including at least a "scientific_name".
        file_name: The name of the image file associated with the observation.
        current_latitude: The latitude of the observation location.
        current_longitude: The longitude of the observation location.
        on_submit_success: A callback function that is called when the
            observation is submitted successfully.
        on_submit_error: A callback function that is called with an error
            message string if the submission fails.

    Example:
        ```python
        import solara

        @solara.component
        def Page():
            # Mock data that would typically come from other components
            mock_prediction = {"scientific_name": "Aedes aegypti", "confidence": 0.95}
            mock_filename = "mosquito_image.jpg"
            lat, set_lat = solara.use_state(34.05)
            lon, set_lon = solara.use_state(-118.24)

            # State to track submission status
            status_message, set_status_message = solara.use_state("")

            def handle_success():
                set_status_message("Observation submitted successfully!")
                print("Success callback triggered.")

            def handle_error(error_msg):
                set_status_message(f"Submission failed: {error_msg}")
                print(f"Error callback triggered: {error_msg}")

            with solara.Column():
                solara.Text("Submit your observation:")
                ObservationFormComponent(
                    prediction=mock_prediction,
                    file_name=mock_filename,
                    current_latitude=lat,
                    current_longitude=lon,
                    on_submit_success=handle_success,
                    on_submit_error=handle_error,
                )
                if status_message:
                    solara.Info(status_message)
        ```
    """
    use_locale_effect()
    obs_date_str, set_obs_date_str = solara.use_state(datetime.now().date().strftime("%Y-%m-%d"))
    obs_count, set_obs_count = solara.use_state(1)
    obs_notes, set_obs_notes = solara.use_state("")
    obs_location_accuracy_m, set_obs_location_accuracy_m = solara.use_state(50)

    is_submitting, set_is_submitting = solara.use_state(False)

    DatePickerComponent = None
    use_date_picker = False
    obs_date_obj_state = solara.use_state(datetime.now().date())
    try:
        from solara.lab import DatePicker

        DatePickerComponent = DatePicker
        use_date_picker = True
    except ImportError:
        pass

    async def handle_submit():
        error_messages = []
        if not current_user_id.value:
            error_msg = "User ID could not be identified for this session."
            error_messages.append(error_msg)
        if not prediction or not prediction.get("scientific_name"):
            error_msg = "Prediction data with a species name is missing."
            error_messages.append(error_msg)
        if not file_name:
            error_msg = "Image file name is missing."
            error_messages.append(error_msg)
        if current_latitude is None or current_longitude is None:
            error_msg = "Latitude and Longitude are required."
            error_messages.append(error_msg)

        date_to_submit = obs_date_obj_state[0].strftime("%Y-%m-%d") if use_date_picker else obs_date_str
        if not date_to_submit:
            error_msg = "Observation date is required."
            error_messages.append(error_msg)
        else:
            try:
                datetime.strptime(date_to_submit, "%Y-%m-%d")
            except ValueError:
                error_msg = "Invalid date format (YYYY-MM-DD)."
                error_messages.append(error_msg)

        if error_messages:
            full_error = " ".join(error_messages)
            on_submit_error(full_error)
            set_is_submitting(False)
            return

        set_is_submitting(True)

        observation_payload = {
            "species_scientific_name": prediction.get("scientific_name"),
            "count": obs_count,
            "location": {"lat": float(current_latitude), "lng": float(current_longitude)},
            "observed_at": f"{date_to_submit}T12:00:00Z",  # Send as full ISO 8601 string
            "notes": obs_notes.strip() or None,
            "user_id": current_user_id.value,
            "location_accuracy_m": obs_location_accuracy_m,
            "data_source": "culicidaelab-web-app",
            "image_filename": file_name,
            "model_id": prediction.get("model_id"),
            "confidence": prediction.get("confidence"),
            "metadata": {"prediction_details": prediction},
        }

        # Clean the payload of any None values for optional fields
        observation_payload = {k: v for k, v in observation_payload.items() if v is not None}
        submission_error = await submit_observation_data(observation_payload)

        if submission_error is None:
            on_submit_success()
        else:
            on_submit_error(str(submission_error))
        set_is_submitting(False)

    solara.Markdown(
        f'### {i18n.t("prediction.observation_form.submit_details")} ',
        style=f"margin-top:10px; margin-bottom:10px; font-family: {FONT_HEADINGS};",
    )

    with solara.Card(style="padding: 15px; margin-top: 5px;"):
        if current_latitude is not None and current_longitude is not None:
            label = (
                f'{i18n.t("prediction.observation_form.info_location_lat")}'
                + f"{current_latitude:.4f}"
                + f'{i18n.t("prediction.observation_form.info_location_lon")}'
                + f"{current_longitude:.4f}"
            )
            solara.Info(
                label,
                dense=True,
                style="margin-bottom:10px;",
            )
        else:
            solara.Warning(
                i18n.t("prediction.observation_form.warning_location"),
                dense=True,
                icon=True,
                style="margin-bottom:10px;",
            )

        if use_date_picker and DatePickerComponent:
            DatePickerComponent(
                label=i18n.t("prediction.observation_form.observation_date"),
                value=obs_date_obj_state[0],
                on_value=obs_date_obj_state[1],
            )
        else:
            solara.InputText(
                i18n.t("prediction.observation_form.input_date"),
                value=obs_date_str,
                on_value=set_obs_date_str,
            )

        solara.InputInt(
            i18n.t("prediction.observation_form.input_count"),
            value=obs_count,
            on_value=set_obs_count,
            style="margin-top: 10px;",
        )

        solara.InputInt(
            i18n.t("prediction.observation_form.input_accuracy"),
            value=obs_location_accuracy_m,
            on_value=set_obs_location_accuracy_m,
            style="margin-top: 10px;",
        )
        solara.InputText(
            i18n.t("prediction.observation_form.input_notes"),
            value=obs_notes,
            on_value=set_obs_notes,
            style="margin-top: 10px;",
        )

        solara.Button(
            i18n.t("prediction.observation_form.submit_observation"),
            on_click=lambda: asyncio.create_task(handle_submit()),
            disabled=is_submitting or not prediction or current_latitude is None or current_longitude is None,
            loading=is_submitting,
            style="margin-top: 20px; width: 100%;",
        )

from typing import Optional, Dict, Any
import asyncio
from datetime import datetime
import solara
from ...config import FONT_HEADINGS
import i18n

from .observation_service import submit_observation_data


@solara.component
def ObservationFormComponent(
    prediction: Optional[Dict[str, Any]],
    file_name: Optional[str],
    current_latitude: Optional[float],
    current_longitude: Optional[float],
    on_submit_success: callable,
    on_submit_error: callable,
):
    """
    Form for submitting observation details along with a prediction.
    """
    obs_date_str, set_obs_date_str = solara.use_state(datetime.now().date().strftime("%Y-%m-%d"))
    obs_count, set_obs_count = solara.use_state(1)
    obs_notes, set_obs_notes = solara.use_state("")
    obs_observer_id, set_obs_observer_id = solara.use_state("user_01")
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
        if not prediction:
            error_messages.append("Prediction data is missing.")
        if not file_name:
            error_messages.append("Image file name is missing.")
        if current_latitude is None or current_longitude is None:
            error_messages.append("Latitude and Longitude are required.")
        else:
            try:
                lat = float(current_latitude)
                lon = float(current_longitude)
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    error_messages.append("Invalid latitude or longitude values.")
            except ValueError:
                error_messages.append("Latitude and Longitude must be valid numbers.")

        date_to_submit = obs_date_obj_state[0].strftime("%Y-%m-%d") if use_date_picker else obs_date_str
        if not date_to_submit:
            error_messages.append("Observation date is required.")
        else:
            try:
                datetime.strptime(date_to_submit, "%Y-%m-%d")
            except ValueError:
                error_messages.append("Invalid date format (YYYY-MM-DD).")

        predicted_species_id = prediction.get("id") if prediction else None
        if not predicted_species_id:
            error_messages.append("Predicted species ID is missing from prediction data.")

        if error_messages:
            on_submit_error(". ".join(error_messages))
            return

        set_is_submitting(True)

        payload_properties = {
            "predicted_species_id": predicted_species_id,
            "observation_date": date_to_submit,
            "count": obs_count,
            "observer_id": obs_observer_id or "anonymous_user",
            "data_source": "field_app_v1",
            "location_accuracy_m": obs_location_accuracy_m,
            "notes": obs_notes.strip() or None,
            "image_filename": file_name,
            "confidence": prediction.get("confidence") if prediction else None,
            "model_id": prediction.get("model_id") if prediction else None,
        }
        payload_properties = {k: v for k, v in payload_properties.items() if v is not None}

        observation_payload = {
            "type": "Feature",
            "properties": payload_properties,
            "geometry": {"type": "Point", "coordinates": [float(current_longitude), float(current_latitude)]},
        }

        submission_error = await submit_observation_data(observation_payload)

        if submission_error is None:
            on_submit_success()
        else:
            on_submit_error(str(submission_error))
        set_is_submitting(False)

    solara.Markdown(
        f"### {i18n.t("prediction.observation_form.submit_details")} ",
        style=f"margin-top:10px; margin-bottom:10px; font-family: {FONT_HEADINGS};",
    )

    with solara.Card(style="padding: 15px; margin-top: 5px;"):
        if current_latitude is not None and current_longitude is not None:
            solara.Info(
                f"{i18n.t("prediction.observation_form.info_location")}",
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
            solara.InputText(i18n.t("prediction.observation_form.input_date"),
                            value=obs_date_str,
                            on_value=set_obs_date_str)

        solara.InputInt(i18n.t("prediction.observation_form.input_count"),
        value=obs_count,
        on_value=set_obs_count,
        style="margin-top: 10px;")
        solara.InputText(i18n.t("prediction.observation_form.input_observer"),
                        value=obs_observer_id,
                        on_value=set_obs_observer_id,
                        style="margin-top: 10px;")
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
            color="green",
            disabled=is_submitting or not prediction or current_latitude is None or current_longitude is None,
            loading=is_submitting,
            style="margin-top: 20px; width: 100%;",
        )

from typing import Optional, Dict, Any
import asyncio
from datetime import datetime
import solara
from ...config import FONT_HEADINGS
from ...state import current_user_id, use_locale_effect
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
    use_locale_effect()
    obs_date_str, set_obs_date_str = solara.use_state(datetime.now().date().strftime("%Y-%m-%d"))
    obs_count, set_obs_count = solara.use_state(1)
    obs_notes, set_obs_notes = solara.use_state("")
    # obs_observer_id, set_obs_observer_id = solara.use_state("user_01")
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
            # "user_id": obs_observer_id or "anonymous_user",
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
        print(f"[DEBUG] Prepared observation payload: {observation_payload}")

        print("[DEBUG] Submitting observation data...")
        submission_error = await submit_observation_data(observation_payload)

        if submission_error is None:
            print("[DEBUG] Observation submitted successfully")
            on_submit_success()
        else:
            print(f"[ERROR] Observation submission failed: {submission_error}")
            on_submit_error(str(submission_error))
        set_is_submitting(False)
        print("[DEBUG] Form submission process completed")

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
                i18n.t("prediction.observation_form.input_date"), value=obs_date_str, on_value=set_obs_date_str
            )

        solara.InputInt(
            i18n.t("prediction.observation_form.input_count"),
            value=obs_count,
            on_value=set_obs_count,
            style="margin-top: 10px;",
        )
        # solara.InputText(
        #     i18n.t("prediction.observation_form.input_observer"),
        #     value=obs_observer_id,
        #     on_value=set_obs_observer_id,
        #     style="margin-top: 10px;",
        # )
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

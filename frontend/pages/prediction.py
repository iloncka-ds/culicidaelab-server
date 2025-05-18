import solara
import solara.lab
from solara.alias import rv
import httpx
import asyncio
from typing import Dict, Any, Optional, List, cast, Tuple
import io
import base64
from datetime import datetime

# Configuration constants
FONT_HEADINGS = "Arial, Helvetica, sans-serif"
FONT_BODY = "Roboto, sans-serif"
COLOR_PRIMARY = "primary"
COLOR_TEXT = "black"
API_BASE_URL = "http://localhost:8000"
PREDICTION_ENDPOINT = f"{API_BASE_URL}/predict_species/"
OBSERVATIONS_ENDPOINT = f"{API_BASE_URL}/observations/"


@solara.component
def SpeciesCard(species: Dict[str, Any]):
    """Displays information about a mosquito species in a card format."""
    species_id_for_link = species.get("id", species.get("species_id", "unknown"))
    with rv.Card(
        class_="ma-2 pa-3", hover=True, style_="cursor: pointer; max-width: 100%; width: 100%; text-decoration: none;"
    ):
        with solara.Link(path_or_route=f"/info/{species_id_for_link}", style="text-decoration: none;"):
            with solara.Row(style="align-items: center;"):
                if species.get("image_url"):
                    rv.Img(
                        src=species["image_url"],
                        height="100px",
                        width="100px",
                        aspect_ratio="1",
                        class_="mr-3 elevation-1",
                        style_="border-radius: 4px; object-fit: cover;",
                    )
                else:
                    rv.Icon(children=["mdi-bug"], size="100px", class_="mr-3", color=COLOR_PRIMARY)
                with solara.Column(align="start", style="overflow: hidden;"):
                    solara.Markdown(
                        f"#### {species.get('scientific_name', 'N/A')}",
                        style=f"font-family: {FONT_HEADINGS}; margin-bottom: 0px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: {COLOR_PRIMARY};",
                    )
                    solara.Text(
                        species.get("common_name", ""),
                        style=f"font-size: 0.9em; color: {COLOR_TEXT}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;",
                    )
                    if "confidence" in species and species["confidence"] is not None:
                        try:
                            confidence_value = float(species["confidence"])
                            solara.Text(
                                f"Confidence: {confidence_value:.2%}",
                                style=f"font-size: 0.85em; color: {COLOR_TEXT}; font-style: italic;",
                            )
                        except (ValueError, TypeError):
                            solara.Text(
                                f"Confidence: {species['confidence']}",
                                style=f"font-size: 0.85em; color: {COLOR_TEXT}; font-style: italic;",
                            )
            status_value = str(species.get("vector_status", "Unknown")).lower()
            status_color, text_c = "grey", "black"
            if status_value == "high":
                status_color, text_c = "red", "white"
            elif status_value == "medium":
                status_color, text_c = "orange", "white"
            elif status_value == "low":
                status_color, text_c = "green", "white"
            if species.get("vector_status"):
                rv.Chip(
                    small=True,
                    children=[f"Vector Status: {species.get('vector_status', 'Unknown')}"],
                    color=status_color,
                    class_="mt-1",
                    text_color=text_c,
                )


# async def upload_and_predict(file_obj: io.BytesIO, filename: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
#     """Upload image to prediction endpoint and get species prediction."""
#     files = {"file": (filename, file_obj, "image/jpeg")}
#     error_msg = None
#     prediction_result = None

#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.post(PREDICTION_ENDPOINT, files=files, timeout=60.0)
#             response.raise_for_status()
#             prediction_result = response.json()
#     except httpx.HTTPStatusError as e:
#         error_detail = e.response.text
#         try:
#             error_detail = e.response.json().get("detail", error_detail)
#         except Exception:
#             pass
#         error_msg = f"Prediction failed: {e.response.status_code} - {error_detail}"
#     except httpx.RequestError as e:
#         error_msg = f"Network error during prediction: {e}"
#     except Exception as e:
#         error_msg = f"An unexpected error occurred: {e}"

#     return prediction_result, error_msg
async def upload_and_predict(file_obj: io.BytesIO, filename: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    return {"scientific_name": "Aedes albopictus", "probabilities": {"Aedes albopictus": 1.0}}, None

async def submit_observation_data(observation_payload: Dict[str, Any]) -> Optional[str]:
    """Submit observation data to the backend API."""
    error_msg = None
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(OBSERVATIONS_ENDPOINT, json=observation_payload, timeout=30.0)
            response.raise_for_status()
            return None
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        try:
            error_detail = e.response.json().get("detail", error_detail)
        except Exception:
            pass
        error_msg = f"Submission failed: {e.response.status_code} - {error_detail}"
    except httpx.RequestError as e:
        error_msg = f"Network error during submission: {e}"
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"

    return error_msg


@solara.component
def ObservationForm(prediction: Dict[str, Any], file_name: str, on_submit_success: Any = None):
    """Form component for submitting observation details."""
    # State variables for form fields
    obs_latitude, set_obs_latitude = solara.use_state("")
    obs_longitude, set_obs_longitude = solara.use_state("")
    current_date = datetime.now().date()
    obs_date_str, set_obs_date_str = solara.use_state(current_date.strftime("%Y-%m-%d"))
    obs_count, set_obs_count = solara.use_state(1)
    obs_notes, set_obs_notes = solara.use_state("")
    obs_observer_id, set_obs_observer_id = solara.use_state("obs_trial")
    obs_location_accuracy_m, set_obs_location_accuracy_m = solara.use_state(100)

    # Submission state
    is_submitting, set_is_submitting = solara.use_state(False)
    submit_status, set_submit_status = solara.use_state(cast(Optional[str], None))

    # Try to use DatePicker if available
    DatePickerComponent = None
    use_date_picker = False
    try:
        from solara.lab import DatePicker

        DatePickerComponent = DatePicker
        obs_date_obj, set_obs_date_obj = solara.use_state(current_date)
        use_date_picker = True
    except ImportError:
        pass

    async def handle_submit():
        # Validate inputs
        if not (obs_latitude.strip() and obs_longitude.strip()):
            set_submit_status("Latitude and Longitude are required.")
            return

        try:
            lat = float(obs_latitude)
            lon = float(obs_longitude)
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                set_submit_status("Invalid latitude/longitude values.")
                return
        except ValueError:
            set_submit_status("Latitude and Longitude must be numbers.")
            return

        date_str = obs_date_obj.strftime("%Y-%m-%d") if use_date_picker else obs_date_str
        if not date_str:
            set_submit_status("Date is required.")
            return

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            set_submit_status("Invalid date format.")
            return

        predicted_species_id = prediction.get("id")
        if not predicted_species_id:
            set_submit_status("Predicted species ID is missing.")
            return

        # Prepare and submit observation
        set_is_submitting(True)
        set_submit_status(None)

        properties = {
            "predicted_species_id": predicted_species_id,
            "confirmed_species_id": None,
            "entomolog_id": None,
            "observation_date": date_str,
            "count": obs_count,
            "observer_id": obs_observer_id or "obs_trial",
            "data_source": "culicidaelab_server",
            "location_accuracy_m": obs_location_accuracy_m,
            "notes": obs_notes.strip() or None,
            "image_filename": file_name,
            "confidence": prediction.get("confidence"),
            "model_id": prediction.get("model_id"),
        }

        # Filter out None values
        properties = {k: v for k, v in properties.items() if v is not None}

        payload = {
            "type": "Feature",
            "properties": properties,
            "geometry": {"type": "Point", "coordinates": [float(obs_longitude), float(obs_latitude)]},
        }

        error = await submit_observation_data(payload)
        if error is None:
            set_submit_status("Observation submitted successfully!")
            if on_submit_success:
                on_submit_success()
        else:
            set_submit_status(error)

        set_is_submitting(False)

    # Render form
    solara.Markdown(
        "### Submit Observation Details", style=f"margin-top:20px; margin-bottom:10px; font-family: {FONT_HEADINGS};"
    )

    if submit_status:
        if "success" in submit_status.lower():
            solara.Success(submit_status, icon=True, dense=True, style="margin-bottom: 10px;")
        else:
            solara.Error(submit_status, icon=True, dense=True, style="margin-bottom: 10px;")

    with solara.Card(style="padding: 15px; margin-top: 5px;"):
        with solara.Columns([1, 1], gutters=True, style="margin-bottom: 10px;"):
            solara.InputText("Latitude *", value=obs_latitude, style="margin-right: 5px;")
            solara.InputText("Longitude *", value=obs_longitude, style="margin-left: 5px;")

        if use_date_picker and DatePickerComponent:
            DatePickerComponent(label="Observation Date *", value=obs_date_obj)
        else:
            solara.InputText("Observation Date (YYYY-MM-DD) *", value=obs_date_str)

        solara.InputInt("Count *", value=obs_count, style="max-width: 200px; margin-top: 10px;")
        solara.InputText("Observer ID", value=obs_observer_id, style="margin-top: 10px;")
        solara.InputInt(
            "Location Accuracy (m)", value=obs_location_accuracy_m, style="max-width: 200px; margin-top: 10px;"
        )
        solara.InputText("Notes", value=obs_notes, style="margin-top: 10px;")

        solara.Button(
            "Submit Observation",
            on_click=lambda: asyncio.create_task(handle_submit()),
            color="green",
            disabled=is_submitting,
            loading=is_submitting,
            style="margin-top: 15px;",
        )


@solara.component
def Page():
    """Main page component for mosquito species prediction."""
    # State for file upload
    file_data, set_file_data = solara.use_state(cast(Optional[bytes], None))
    file_name, set_file_name = solara.use_state(cast(Optional[str], None))

    # State for prediction
    prediction_result, set_prediction_result = solara.use_state(cast(Optional[Dict[str, Any]], None))
    is_predicting, set_is_predicting = solara.use_state(False)
    # Fix for error_message state - use empty string instead of None
    error_message, set_error_message = solara.use_state("")

    # State for workflow
    observation_submitted, set_observation_submitted = solara.use_state(False)

    def handle_file_upload(file_info: Dict[str, Any]):
        """Handle file upload and reset states."""
        set_error_message("")
        set_prediction_result(None)
        set_observation_submitted(False)

        try:
            if not file_info["file_obj"]:
                set_error_message("Error: Uploaded file appears to be empty")
                set_file_data(None)
                set_file_name(None)
                return

            set_file_name(file_info["name"])
            set_file_data(file_info["data"])
        except Exception as e:
            set_error_message(f"Error reading file: {e}")
            set_file_data(None)
            set_file_name(None)

    async def perform_prediction():
        """Send image to prediction API."""
        if not (file_data and file_name):
            set_error_message("Please upload an image first.")
            return

        set_is_predicting(True)
        set_error_message("")
        set_prediction_result(None)

        # Create BytesIO from our file data
        file_obj = io.BytesIO(file_data)

        # Call prediction API
        result, error = await upload_and_predict(file_obj, file_name)

        if result:
            set_prediction_result(result)
        else:
            set_error_message(error or "Prediction failed with unknown error.")

        set_is_predicting(False)

    def handle_observation_success():
        """Handle successful observation submission."""
        set_observation_submitted(True)

    # Main page layout
    with solara.Column(align="center", style="padding: 20px; width: 100%;"):
        # Page header
        solara.Markdown("# Mosquito Species Prediction", style=f"font-family: {FONT_HEADINGS}; color: {COLOR_PRIMARY};")
        solara.Markdown(
            "Upload an image of a mosquito, predict its species, and submit your observation.",
            style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; margin-bottom: 20px;",
        )

        # File upload area
        solara.FileDrop(
            label="Drag and drop an image here, or click to select.", on_file=handle_file_upload, lazy=False
        )

        # Error display
        if error_message:
            solara.Error(
                error_message, style="margin-top: 15px; margin-bottom: 10px; width: 100%; max-width: 700px;"
            )

        # Content area - shows after file upload
        if file_data:
            with solara.ColumnsResponsive(
                default=[12, 12],
                small=[6, 6],
                medium=[5, 7],
                large=[4, 8],
                gutters=True,
                style="width: 100%; max-width: 1000px; margin-top: 20px;",
            ):
                # Left column - image and predict button
                with solara.Column(align="center", style="padding: 10px;"):
                    if file_name:
                        solara.Text(
                            f"Uploaded: {file_name}", style=f"font-family: {FONT_BODY}; margin-bottom: 10px;"
                        )

                    try:
                        # Display the uploaded image
                        image_data_url = f"data:image/jpeg;base64,{base64.b64encode(file_data).decode()}"
                        rv.Img(
                            src=image_data_url,
                            max_height="350px",
                            contain=True,
                            class_="elevation-2",
                            style_="border-radius: 4px; width: 100%; object-fit: contain;",
                        )
                    except Exception as e:
                        set_error_message(f"Error displaying image: {e}")

                    # Predict button
                    solara.Button(
                        label="Predict Species",
                        on_click=lambda: asyncio.create_task(perform_prediction()),
                        color=COLOR_PRIMARY,
                        disabled=is_predicting,
                        loading=is_predicting,
                        style="margin-top: 15px;",
                    )

                # Right column - prediction results or observation form
                with solara.Column(style="padding: 10px;"):
                    if is_predicting:
                        # Show loading state
                        solara.ProgressLinear(True, color=COLOR_PRIMARY, style="margin-top: 20px;")
                        solara.Text(
                            "Predicting, please wait...",
                            style=f"font-style: italic; font-family: {FONT_BODY}; margin-top:10px; text-align: center;",
                        )
                    elif prediction_result:
                        # Show prediction results
                        solara.Markdown(
                            "### Prediction Result", style=f"margin-bottom:10px; font-family: {FONT_HEADINGS};"
                        )
                        SpeciesCard(species=prediction_result)

                        # Show observation form or success message
                        solara.Markdown("---")
                        if observation_submitted:
                            solara.Success("Observation submitted successfully!", icon=True, style="margin-top: 20px;")
                            solara.Button(
                                "Submit Another Observation",
                                on_click=lambda: set_observation_submitted(False),
                                color="green",
                                style="margin-top: 15px;",
                            )
                        else:
                            # Show observation form
                            ObservationForm(
                                prediction=prediction_result,
                                file_name=file_name,
                                on_submit_success=handle_observation_success,
                            )
                    else:
                        # Show instructions
                        solara.Info(
                            "Upload an image and click 'Predict Species' to see results.",
                            icon="mdi-arrow-up-bold-box-outline",
                            style="margin-top:20px;",
                        )

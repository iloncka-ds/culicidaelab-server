import solara
import solara.lab
import io
import base64
from typing import Dict, Any, Optional, cast
import asyncio
from functools import partial

# Assuming components are in the same directory or adjust path
from ..config import FONT_HEADINGS, FONT_BODY, COLOR_PRIMARY
from frontend.components.prediction.file_upload import FileUploadComponent, mock_upload_and_predict
from frontend.components.prediction.location import LocationComponent
from frontend.components.prediction.observation_form import ObservationFormComponent
from frontend.components.species.species_card import SpeciesCard


@solara.component
def Page():
    with solara.AppBar():
        solara.lab.ThemeToggle()
    with solara.AppBarTitle():
        solara.Text("CulicidaeLab", style="font-size: 2rem; font-weight: bold; color: white;")
    # --- Page View Mode ---
    # "form": shows the 3-column input form
    # "results": shows submitted image, prediction, and success message
    view_mode, set_view_mode = solara.use_state("form")

    # --- Cross-Component State ---
    # File & Prediction
    file_data_state, set_file_data_state = solara.use_state(cast(Optional[bytes], None))
    file_name_state, set_file_name_state = solara.use_state(cast(Optional[str], None))
    prediction_result_state, set_prediction_result_state = solara.use_state(cast(Optional[Dict[str, Any]], None))

    # Location
    latitude_state, set_latitude_state = solara.use_state(cast(Optional[float], None))  # Start with no location
    longitude_state, set_longitude_state = solara.use_state(cast(Optional[float], None))

    # Operation Status
    is_predicting_state, set_is_predicting_state = solara.use_state(False)
    page_error_message, set_page_error_message = solara.use_state("")
    page_success_message, set_page_success_message = solara.use_state("")
    file_upload_specific_error, set_file_upload_specific_error = solara.use_state("")

    def reset_to_new_submission():
        set_file_data_state(None)
        set_file_name_state(None)
        set_prediction_result_state(None)
        # Optionally reset location, or keep it for convenience
        # set_latitude_state(None)
        # set_longitude_state(None)
        set_is_predicting_state(False)
        set_page_error_message("")
        set_page_success_message("")
        set_file_upload_specific_error("")
        set_view_mode("form")



    # This callback handles the result or error from the prediction
    def _handle_prediction_result(result_tuple):
        print(f"Handling prediction result: {result_tuple}")
        result, error = result_tuple

        if error:
            set_page_error_message(f"Prediction Error: {error}")
            set_page_success_message("")
        elif result:
            set_prediction_result_state(result)
            set_page_success_message(f"Prediction complete: {result.get('scientific_name', 'Unknown species')}")
        else:
            set_page_error_message("Prediction returned no result and no error.")
            set_page_success_message("")

        set_is_predicting_state(False)

    def handle_file_selected_from_component(file_info: Dict[str, Any]) -> bool:
        # Clear previous states related to file/prediction
        set_page_error_message("")
        set_page_success_message("")
        set_file_upload_specific_error("")
        set_prediction_result_state(None)
        set_is_predicting_state(False)  # Reset predicting state

        try:
            if not file_info:
                set_file_upload_specific_error("File information is empty.")
                return False

            if "data" not in file_info or file_info["data"] is None:
                set_file_upload_specific_error("File data is missing from uploaded file.")
                return False

            if "name" not in file_info or not file_info["name"]:
                set_file_upload_specific_error("File name is missing from uploaded file.")
                return False

            # Debug info
            print(
                f"Received file: {file_info['name']}, size: {len(file_info['data']) if file_info['data'] else 'None'} bytes"
            )

            # Store file data and name in state
            set_file_data_state(file_info["data"])
            set_file_name_state(file_info["name"])


            img_bytes_io = io.BytesIO(file_info["data"])
            result = asyncio.run(mock_upload_and_predict(img_bytes_io, file_info["name"]))
            print(f"Prediction complete for {file_info['name']}: {'Success' if result[0] else 'Failed'}")
            _handle_prediction_result(result)
            # set_prediction_result_state(result)
            return True
        except Exception as e:
            set_file_upload_specific_error(f"Error processing uploaded file: {str(e)}")
            set_file_data_state(None)
            set_file_name_state(None)
            return False

    def handle_observation_success():
        set_page_success_message("Observation submitted successfully!")
        set_page_error_message("")  # Clear any previous errors
        set_view_mode("results")

    def handle_observation_error(error_msg: str):
        set_page_error_message(f"Failed to submit observation: {error_msg}")
        set_page_success_message("")  # Clear any previous success

    # Page Title
    solara.Markdown(
        "# Mosquito Species Prediction & Observation",
        style=f"font-family: {FONT_HEADINGS}; color: {COLOR_PRIMARY}; text-align: center; margin-bottom:20px;",
    )

    # Global status messages
    if page_error_message:
        solara.Error(
            page_error_message,
            icon=True,
            style="margin-bottom: 15px; width:100%; max-width:900px; margin-left:auto; margin-right:auto;",
        )
    if page_success_message and view_mode == "form":  # Show ongoing status in form view
        solara.Info(
            page_success_message,
            icon=True,
            style="margin-bottom: 15px; width:100%; max-width:900px; margin-left:auto; margin-right:auto;",
        )

    if view_mode == "form":
        with solara.ColumnsResponsive(
            6, large=[4, 4, 4], gutters_dense=True, style="max-width: 1200px; margin: 0 auto;"
        ):
            # Column 1: File Upload
            with solara.Card("1. Upload Mosquito Image", margin=0, style="height: 100%;"):
                FileUploadComponent(
                    on_file_selected=handle_file_selected_from_component,
                    upload_error_message=file_upload_specific_error,
                    is_processing=is_predicting_state,  # Let component know if parent is busy with its file
                )
                if file_data_state and not is_predicting_state and prediction_result_state:
                    solara.Success(
                        f"Image uploaded & predicted: {prediction_result_state}",  # .get('scientific_name', 'N/A')
                        dense=True,
                        icon=True,
                        style="margin-top:10px;",
                    )
                elif (
                    file_data_state
                    and not is_predicting_state
                    and not prediction_result_state
                    and not page_error_message
                ):
                    solara.Info(
                        "Awaiting prediction results or further action.",
                        dense=True,
                        icon=True,
                        style="margin-top:10px;",
                    )

            # Column 2: Location Picker
            with solara.Card("2. Pinpoint Observation Location", margin=0, style="height: 100%;"):
                LocationComponent(
                    latitude=latitude_state,
                    set_latitude=set_latitude_state,
                    longitude=longitude_state,
                    set_longitude=set_longitude_state,
                    initial_lat=20.0,  # Global default view
                    initial_lon=0.0,
                    initial_zoom=1,
                )

            # Column 3: Observation Form
            with solara.Card("3. Record Observation Details", margin=0, style="height: 100%;"):
                if not file_data_state:
                    solara.Info(
                        "Upload an image first to enable the observation form.",
                        icon="mdi-image-off-outline",
                        style="padding:10px;",
                    )
                elif is_predicting_state:
                    solara.Info(
                        "Waiting for prediction to complete before enabling form...",
                        icon="mdi-timer-sand",
                        style="padding:10px;",
                    )
                elif not prediction_result_state:
                    solara.Warning(
                        "Prediction failed or no result. Cannot submit observation without a prediction.",
                        icon="mdi-alert-circle-outline",
                        style="padding:10px;",
                    )
                else:
                    ObservationFormComponent(
                        prediction=prediction_result_state,
                        file_name=file_name_state,
                        current_latitude=latitude_state,
                        current_longitude=longitude_state,
                        on_submit_success=handle_observation_success,
                        on_submit_error=handle_observation_error,
                    )

    elif view_mode == "results":
        with solara.Column(align="center", style="padding: 20px; max-width: 800px; margin: 0 auto;"):
            solara.Success(
                page_success_message or "Observation recorded!",
                icon="mdi-check-circle-outline",
                style="font-size:1.2em; margin-bottom:20px;",
            )

            if file_data_state:
                solara.Markdown("### Uploaded Image", style=f"font-family:{FONT_HEADINGS}; margin-top:20px;")
                try:
                    img_bytes = file_data_state
                    b64_img = base64.b64encode(img_bytes).decode("utf-8")
                    # Determine content type roughly, default to jpeg
                    content_type = "image/jpeg"
                    if file_name_state and file_name_state.lower().endswith(".png"):
                        content_type = "image/png"
                    elif file_name_state and file_name_state.lower().endswith(".gif"):
                        content_type = "image/gif"

                    solara.HTML(
                        tag="img",
                        unsafe_innerHTML="",
                        attributes={
                            "src": f"data:{content_type};base64,{b64_img}",
                            "style": "max-width: 100%; max-height: 400px; border: 1px solid #ccc; margin-top:10px; border-radius: 4px;",
                        },
                    )
                except Exception as e:
                    solara.Error(f"Could not display uploaded image: {e}")

            if prediction_result_state:
                # print(prediction_result_state)
                solara.Markdown("### Prediction Details", style=f"font-family:{FONT_HEADINGS}; margin-top:30px;")
                SpeciesCard(species=prediction_result_state)
            else:  # Should ideally not happen if submission was successful
                solara.Warning("No prediction data available for this observation.", style="margin-top:20px;")

            solara.Button(
                "Submit Another Observation",
                on_click=reset_to_new_submission,
                color=COLOR_PRIMARY,
                icon_name="mdi-plus-circle-outline",
                style="margin-top: 30px; padding: 10px 20px; font-size:1.1em;",
            )

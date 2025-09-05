"""
Defines the main page for the species prediction workflow.

This module contains the top-level page component that orchestrates the entire
prediction process. It integrates the file upload, location selection, and
observation form components, managing the state and flow between these steps.
"""

import solara

import io
import base64
from typing import Any, Optional, cast
import asyncio

from frontend.config import (
    page_style,
    heading_style,
    sub_heading_style,
    card_style,
    theme,
)

from frontend.components.prediction.file_upload import FileUploadComponent, upload_and_predict
from frontend.components.prediction.location import LocationComponent
from frontend.components.prediction.observation_form import ObservationFormComponent
from frontend.components.prediction.prediction_card import PredictionCard
from frontend.state import use_persistent_user_id, use_locale_effect
import i18n


@solara.component
def Page():
    """
    Renders the interactive species prediction page, managing a multi-step workflow.

    This component serves as the main interface for the species prediction feature.
    It orchestrates a workflow where users first upload an image of a specimen,
    which triggers an asynchronous prediction. Simultaneously, the user can
    select the observation's location on an interactive map and fill out a form
    with additional details.

    The component is divided into two main views:
    1.  **'form' view**: The initial layout with three main sections for file
        upload, location selection, and the observation form.
    2.  **'results' view**: Displayed after a successful observation submission,
        showing a summary of the uploaded image and the prediction details.

    It manages all the necessary state for this process, including the uploaded
    file, prediction results, location coordinates, loading indicators, and
    success/error messages.

    Example:
        This component is intended to be a top-level page within a Solara
        application, typically linked from a main navigation or routing system.

        ```python
        # In your main app file (e.g., app.py)
        import solara
        from pages import prediction

        routes = [
            solara.Route(path="/", component=...),
            solara.Route(path="/predict", component=prediction.Page, label="Predict"),
            # ... other routes
        ]

        @solara.component
        def Layout():
            # ... your app layout ...
            # The RoutingProvider will render the prediction.Page component
            # when the user navigates to the '/predict' path.
            solara.RoutingProvider(routes=routes, children=[...])
        ```
    """
    use_persistent_user_id()
    use_locale_effect()

    view_mode, set_view_mode = solara.use_state("form")
    file_data_state, set_file_data_state = solara.use_state(cast(Optional[bytes], None))
    file_name_state, set_file_name_state = solara.use_state(cast(Optional[str], None))
    prediction_result_state, set_prediction_result_state = solara.use_state(cast(Optional[dict[str, Any]], None))
    latitude_state, set_latitude_state = solara.use_state(cast(Optional[float], None))
    longitude_state, set_longitude_state = solara.use_state(cast(Optional[float], None))
    is_predicting_state, set_is_predicting_state = solara.use_state(False)
    page_error_message, set_page_error_message = solara.use_state("")
    page_success_message, set_page_success_message = solara.use_state("")
    file_upload_specific_error, set_file_upload_specific_error = solara.use_state("")

    def reset_to_new_submission():
        set_file_data_state(None)
        set_file_name_state(None)
        set_prediction_result_state(None)
        set_is_predicting_state(False)
        set_page_error_message("")
        set_page_success_message("")
        set_file_upload_specific_error("")
        set_view_mode("form")

    def _handle_prediction_result(result_tuple):
        result, error = result_tuple
        if error:
            set_page_error_message(i18n.t("prediction.messages.error.generic", message=error))
            set_page_success_message("")
        elif result:
            set_prediction_result_state(result)
        else:
            set_page_error_message(i18n.t("prediction.messages.error.generic", message="No result and no error"))
            set_page_success_message("")
        set_is_predicting_state(False)

    def handle_file_selected_from_component(file_info: dict[str, Any]) -> bool:
        set_page_error_message("")
        set_page_success_message("")
        set_file_upload_specific_error("")
        set_prediction_result_state(None)
        set_is_predicting_state(False)

        try:
            if not file_info:
                set_file_upload_specific_error(i18n.t("prediction.messages.error.empty_file"))
                return False
            if "data" not in file_info or file_info["data"] is None:
                set_file_upload_specific_error(i18n.t("prediction.messages.error.missing_data"))
                return False
            if "name" not in file_info or not file_info["name"]:
                set_file_upload_specific_error(i18n.t("prediction.messages.error.missing_name"))
                return False

            set_file_data_state(file_info["data"])
            set_file_name_state(file_info["name"])
            img_bytes_io = io.BytesIO(file_info["data"])
            result = asyncio.run(upload_and_predict(img_bytes_io, file_info["name"]))
            _handle_prediction_result(result)
            return True
        except Exception as e:
            set_file_upload_specific_error(i18n.t("prediction.messages.error.processing", error=str(e)))
            set_file_data_state(None)
            set_file_name_state(None)
            return False

    def handle_observation_success():
        set_page_error_message("")
        set_view_mode("results")

    def handle_observation_error(error_msg: str):
        translated_msg = i18n.t("prediction.messages.error.submission", error=error_msg)
        set_page_error_message(translated_msg)
        set_page_success_message("")

    solara.Text(
        i18n.t("prediction.page_title"),
        style=heading_style,
    )

    if page_error_message:
        solara.Error(
            page_error_message,
            icon=True,
            style="margin-bottom: 15px; width:100%; max-width:900px; margin-left:auto; margin-right:auto;",
        )
    if page_success_message and view_mode == "form":
        solara.Info(
            page_success_message,
            icon=True,
            style="margin-bottom: 15px; width:100%; max-width:900px; margin-left:auto; margin-right:auto;",
        )

    if view_mode == "form":
        with solara.ColumnsResponsive(
            default=[12],
            large=[4, 4, 4],
            gutters_dense=True,
            style=page_style,
        ):
            with solara.Card(i18n.t("prediction.cards.upload.title"), margin=0, style=card_style):  # "height: 100%;"
                FileUploadComponent(
                    on_file_selected=handle_file_selected_from_component,
                    upload_error_message=file_upload_specific_error,
                )
                if file_data_state and not is_predicting_state and prediction_result_state:
                    solara.Success(
                        i18n.t("prediction.messages.success.upload_predicted", result=prediction_result_state),
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
                        i18n.t("prediction.messages.info.awaiting_prediction"),
                        dense=True,
                        icon=True,
                        style="margin-top:10px;",
                    )

            with solara.Card(i18n.t("prediction.cards.location.title"), margin=0, style=card_style):
                LocationComponent(
                    latitude=latitude_state,
                    set_latitude=set_latitude_state,
                    longitude=longitude_state,
                    set_longitude=set_longitude_state,
                    initial_lat=20.0,
                    initial_lon=0.0,
                    initial_zoom=1,
                )

            with solara.Card(i18n.t("prediction.cards.observation.title"), margin=0, style=card_style):
                if not file_data_state:
                    solara.Info(
                        i18n.t("prediction.messages.info.upload_first"),
                        icon="mdi-image-off-outline",
                        style="padding:10px;",
                    )
                elif is_predicting_state or not prediction_result_state:
                    solara.Info(
                        i18n.t("prediction.messages.info.awaiting_prediction"),
                        icon="mdi-timer-sand",
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
        with solara.Column(align="center", style=page_style):
            solara.Success(
                page_success_message or i18n.t("prediction.messages.success.observation_recorded"),
                icon="mdi-check-circle-outline",
                style="font-size:1.2em; margin-bottom:20px;",
            )

            if prediction_result_state:
                with solara.ColumnsResponsive(
                    default=[12],
                    small=[6, 6],
                    medium=[6, 6],
                    large=[6, 6],
                    gutters="20px",
                    style=page_style,
                ):
                    # Column 1: Uploaded Image
                    with solara.Column():
                        solara.Markdown(
                            i18n.t("prediction.labels.uploaded_image"),
                            style=sub_heading_style,
                        )
                        try:
                            img_bytes = file_data_state
                            b64_img = base64.b64encode(img_bytes).decode("utf-8")
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
                                    "style": "width: 100%; height: 100%; object-fit: cover; "
                                    "border: 1px solid #ccc; border-radius: 4px;",
                                },
                            )
                        except Exception as e:
                            solara.Error(i18n.t("prediction.messages.error.image_display", error=str(e)))

                    # Column 2: Prediction Details
                    with solara.Column():
                        solara.Markdown(
                            i18n.t("prediction.labels.prediction_details"),
                            style=sub_heading_style,
                        )
                        PredictionCard(species=prediction_result_state)
            else:
                solara.Warning(i18n.t("prediction.messages.warning.no_prediction_data"), style="margin-top:20px;")

            solara.Button(
                i18n.t("prediction.buttons.submit_another"),
                on_click=reset_to_new_submission,
                color=theme.themes.light.primary,
                icon_name="mdi-plus-circle-outline",
                style="margin-top: 30px; padding: 10px 20px; font-size:1.1em;",
            )

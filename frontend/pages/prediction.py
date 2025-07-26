import solara
import solara.lab
import io
import base64
from typing import Dict, Any, Optional, cast
import asyncio

from ..config import load_themes
from frontend.components.prediction.file_upload import FileUploadComponent, upload_and_predict
from frontend.components.prediction.location import LocationComponent
from frontend.components.prediction.observation_form import ObservationFormComponent
from frontend.components.species.species_card import SpeciesCard
from frontend.components.common.locale_selector import LocaleSelector
from frontend.state import use_persistent_user_id, current_user_id
import i18n
from pathlib import Path


def setup_i18n():
    i18n.load_path.append(str(Path(__file__).parent.parent / "translations"))
    i18n.set("fallback", "en")


@solara.component
def Page():
    theme = load_themes(solara.lab.theme)
    heading_style = f"font-size: 2.5rem; text-align: center; margin-bottom: 1rem; color: {theme.themes.light.primary};"
    sub_heading_style = "font-size: 1.2rem; text-align: center; margin-bottom: 3rem; color: #555;"
    # Ensure user ID is initialized

    use_persistent_user_id()
    print(f"[DEBUG] Current user ID: {current_user_id.value}")

    _, set_rerender_trigger = solara.use_state(0)

    def force_rerender():
        set_rerender_trigger(lambda x: x + 1)

    setup_i18n()
    with solara.AppBar():
        solara.v.Spacer()
        LocaleSelector(on_change=force_rerender)
    with solara.AppBarTitle():
        solara.Text(i18n.t("prediction.app_title"), style="font-size: 2rem; font-weight: bold; color: white;")

    view_mode, set_view_mode = solara.use_state("form")
    file_data_state, set_file_data_state = solara.use_state(cast(Optional[bytes], None))
    file_name_state, set_file_name_state = solara.use_state(cast(Optional[str], None))
    prediction_result_state, set_prediction_result_state = solara.use_state(cast(Optional[Dict[str, Any]], None))
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
        print(f"Handling prediction result: {result_tuple}")
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

    def handle_file_selected_from_component(file_info: Dict[str, Any]) -> bool:
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
        print("[DEBUG] handle_observation_success called")
        print(f"[DEBUG] Current view mode (before update): {view_mode}")
        print(f"[DEBUG] Current page success message (before update): {page_success_message}")

        # Don't set success message here, it's already set in prediction result handler
        set_page_error_message("")
        set_view_mode("results")

        print(f"[DEBUG] View mode after update: {view_mode}")
        print(f"[DEBUG] Page success message after update: {page_success_message}")
        print(f"[DEBUG] Page error message after update: {page_error_message}")

    def handle_observation_error(error_msg: str):
        print(f"[DEBUG] handle_observation_error called with error: {error_msg}")
        print(f"[DEBUG] Current view mode: {view_mode}")
        print(f"[DEBUG] Current page error message (before update): {page_error_message}")

        translated_msg = i18n.t("prediction.messages.error.submission", error=error_msg)
        print(f"[DEBUG] Translated error message: {translated_msg}")

        set_page_error_message(translated_msg)
        set_page_success_message("")

        print(f"[DEBUG] Page error message after update: {page_error_message}")
        print(f"[DEBUG] Page success message after update: {page_success_message}")

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
            default=[12], large=[4, 4, 4], gutters_dense=True, style="max-width: 1200px; margin: 0 auto;"
        ):
            with solara.Card(i18n.t("prediction.cards.upload.title"), margin=0, style="height: 100%;"):
                FileUploadComponent(
                    on_file_selected=handle_file_selected_from_component,
                    upload_error_message=file_upload_specific_error,
                    is_processing=is_predicting_state,
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

            with solara.Card(i18n.t("prediction.cards.location.title"), margin=0, style="height: 100%;"):
                LocationComponent(
                    latitude=latitude_state,
                    set_latitude=set_latitude_state,
                    longitude=longitude_state,
                    set_longitude=set_longitude_state,
                    initial_lat=20.0,
                    initial_lon=0.0,
                    initial_zoom=1,
                )

            with solara.Card(i18n.t("prediction.cards.observation.title"), margin=0, style="height: 100%;"):
                if not file_data_state:
                    solara.Info(
                        i18n.t("prediction.messages.info.upload_first"),
                        icon="mdi-image-off-outline",
                        style="padding:10px;",
                    )
                elif is_predicting_state:
                    solara.Info(
                        i18n.t("prediction.messages.info.waiting_prediction"),
                        icon="mdi-timer-sand",
                        style="padding:10px;",
                    )
                elif not prediction_result_state:
                    solara.Warning(
                        i18n.t("prediction.messages.warning.no_prediction"),
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
                page_success_message or i18n.t("prediction.messages.success.observation_recorded"),
                icon="mdi-check-circle-outline",
                style="font-size:1.2em; margin-bottom:20px;",
            )

            if prediction_result_state:

                with solara.ColumnsResponsive(default=[12], small=[6, 6], medium=[6, 6], large=[6, 6], gutters="20px"):
                    # Column 1: Uploaded Image
                    with solara.VBox():
                        solara.Markdown(i18n.t("prediction.labels.uploaded_image"),
                                        style=sub_heading_style)
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
                    with solara.VBox():
                        solara.Markdown(
                            i18n.t("prediction.labels.prediction_details"),
                            style=sub_heading_style,
                        )
                        SpeciesCard(species=prediction_result_state)
            else:
                solara.Warning(i18n.t("prediction.messages.warning.no_prediction_data"), style="margin-top:20px;")

            solara.Button(
                i18n.t("prediction.buttons.submit_another"),
                on_click=reset_to_new_submission,
                color=theme.themes.light.primary,
                icon_name="mdi-plus-circle-outline",
                style="margin-top: 30px; padding: 10px 20px; font-size:1.1em;",
            )

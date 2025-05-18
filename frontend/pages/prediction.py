import solara
import solara.lab
from solara.alias import rv
import httpx
import asyncio
from typing import Dict, Any, Optional, List, cast
import io  # For handling file bytes
import base64  # For image data URL

from ..config import FONT_HEADINGS, FONT_BODY, COLOR_PRIMARY, COLOR_TEXT, API_BASE_URL

PREDICTION_ENDPOINT = f"{API_BASE_URL}/predict_species"


# --- Re-usable Species Card (Ensure this is your actual component or imported correctly) ---
@solara.component
def SpeciesCard(species: Dict[str, Any]):
    species_id_for_link = species.get("id", species.get("species_id", "unknown"))

    with rv.Card(
        class_="ma-2 pa-3",
        hover=True,
        style_="cursor: pointer; max-width: 350px; width: 100%; text-decoration: none;",  # Ensure it takes available width
    ):
        with solara.Link(path_or_route=f"/info/{species_id_for_link}"):
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

                with solara.Column(align="start", style_="overflow: hidden;"):
                    solara.Markdown(
                        f"#### {species.get('scientific_name', 'N/A')}",
                        style=f"font-family: {FONT_HEADINGS}; margin-bottom: 0px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: {COLOR_PRIMARY};",
                    )
                    solara.Text(
                        species.get("common_name", ""),
                        style=f"font-size: 0.9em; color: {COLOR_TEXT}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;",
                    )
                    if "confidence" in species:
                        solara.Text(
                            f"Confidence: {species['confidence']:.2%}",
                            style=f"font-size: 0.85em; color: {COLOR_TEXT}; font-style: italic;",
                        )
            status = str(species.get("vector_status", "Unknown")).lower()
            status_color, text_c = "grey", "black"
            if status == "high":
                status_color, text_c = "red", "white"
            elif status == "medium":
                status_color, text_c = "orange", "white"
            elif status == "low":
                status_color, text_c = "green", "white"
            rv.Chip(
                small=True,
                children=[f"Vector Status: {species.get('vector_status', 'Unknown')}"],
                color=status_color,
                class_="mt-1",
                text_color=text_c,
            )


async def upload_and_predict(file_obj: io.BytesIO, filename: str) -> Optional[Dict[str, Any]]:
    print(f"[DEBUG] Uploading '{filename}' to {PREDICTION_ENDPOINT}")
    files = {"file": (filename, file_obj, "image/jpeg")}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(PREDICTION_ENDPOINT, files=files, timeout=60.0)
            response.raise_for_status()
            prediction_result = response.json()
            print(f"[DEBUG] Prediction received: {prediction_result}")
            return prediction_result
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        try:
            error_detail = e.response.json().get("detail", error_detail)
        except:
            pass
        solara.Error(f"Prediction failed: {e.response.status_code} - {error_detail}")
        print(f"[DEBUG] Prediction HTTPStatusError: {error_detail}")
        return None
    except Exception as e:
        solara.Error(f"An error occurred during prediction: {e}")
        print(f"[DEBUG] Prediction Exception: {e}")
        return None


@solara.component
def Page():
    file_data, set_file_data = solara.use_state(cast(Optional[bytes], None))
    file_name, set_file_name = solara.use_state(cast(Optional[str], None))
    prediction, set_prediction = solara.use_state(cast(Optional[Dict[str, Any]], None))
    is_predicting, set_is_predicting = solara.use_state(False)
    error_message, set_error_message = solara.use_state(cast(Optional[str], None))

    def handle_file_upload(file_info: Dict[str, Any]):
        set_error_message(None)
        set_prediction(None)
        set_file_name(file_info["name"])
        data = file_info["file_obj"].read()
        set_file_data(data)
        print(f"[DEBUG] File '{file_info['name']}' captured, size: {file_info['size']}")

    async def perform_prediction():
        if not file_data or not file_name:
            set_error_message("Please upload an image first.")
            return

        set_is_predicting(True)
        set_error_message(None)
        set_prediction(None)
        file_obj_for_upload = io.BytesIO(file_data)

        pred_result = await upload_and_predict(file_obj_for_upload, file_name)

        if pred_result:
            set_prediction(pred_result)
        else:
            # Error displayed by upload_and_predict via solara.Error
            # Or set a generic one if solara.Error wasn't triggered (e.g. network issues before HTTPStatusError)
            current_error = solara.get_widget_context().app_state.get(
                "solara_error_message"
            )  # Check if solara.Error set something
            if not current_error and not error_message:
                set_error_message("Prediction failed. Please try again or check console.")
        set_is_predicting(False)

    with solara.Column(align="center", style="padding: 20px; width: 100%;"):
        solara.Markdown("# Mosquito Species Prediction", style=f"font-family: {FONT_HEADINGS}; color: {COLOR_PRIMARY};")
        solara.Markdown(
            "Upload an image of a mosquito, and we'll try to predict its species.",
            style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; margin-bottom: 20px;",
        )

        solara.FileDrop(
            label="Drag and drop an image here, or click to select.",
            on_file=handle_file_upload,
            lazy=False,

        )

        if (
            error_message
        ):  # Display general errors above the two-column layout if they are not part of prediction process
            solara.Error(error_message, style_="margin-bottom: 20px; width: 100%; max-width: 600px;")
            # Clear error if user uploads a new file
            if file_data:
                set_error_message(None)

        if file_data:
            # Two-column layout for image and prediction/status
            # Use solara.ColumnsResponsive for better behavior on small screens (stacking)
            with solara.ColumnsResponsive(
                default=[12, 12],  # Stack on smallest screens
                small=[6, 6],  # Side-by-side from 'small' breakpoint upwards
                medium=[5,7], # Example: 5/12 for image, 7/12 for card on medium
                large=[4,8],  # Example: 4/12 for image, 8/12 for card on large
                gutters=True,
                style="width: 100%; max-width: 900px; margin-top: 20px;",  # Max width for the two-column section
            ):
                # --- Left Column: Uploaded Image ---
                with solara.Column(align="center", style="padding: 10px;"):
                    solara.Text(f"Uploaded: {file_name}", style=f"font-family: {FONT_BODY}; margin-bottom: 10px;")
                    image_data_url = f"data:image/jpeg;base64,{base64.b64encode(file_data).decode()}"
                    rv.Img(
                        src=image_data_url,
                        max_height="400px",  # Max height for the image
                        contain=True,
                        class_="elevation-2",
                        style_="border-radius: 4px; width: 100%; object-fit: contain;",  # Ensure image scales nicely
                    )
                    solara.Button(
                        label="Predict Species",
                        on_click=lambda: asyncio.create_task(perform_prediction()),
                        color=COLOR_PRIMARY,
                        disabled=is_predicting,
                        style="margin-top: 15px;",
                    )

                # --- Right Column: Prediction Result / Loading / Prompt ---
                with solara.Column(
                    align="center", justify="center", style_="padding: 10px; min-height: 250px;"
                ):  # min-height helps alignment
                    if is_predicting:
                        solara.ProgressLinear(True, color=COLOR_PRIMARY)
                        solara.Text(
                            "Predicting, please wait...",
                            style=f"font-style: italic; font-family: {FONT_BODY}; margin-top:10px;",
                        )
                    elif prediction:
                        solara.Markdown(
                            "### Prediction Result", style=f"margin-bottom:10px; font-family: {FONT_HEADINGS};"
                        )
                        SpeciesCard(species=prediction)
                    elif not error_message:  # If no active prediction, no result, and no overriding error
                        solara.Info("Click 'Predict Species' to see the result.", icon=True)

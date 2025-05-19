import solara
import io
from typing import Optional, Dict, Any, Tuple
import asyncio  # For mock delay

from ...config import FONT_BODY, COLOR_TEXT  # Assuming app_config.py is in the same directory


async def mock_upload_and_predict(
    file_obj: io.BytesIO, filename: str
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    MOCK FUNCTION: Simulates uploading an image to a prediction endpoint
    and getting a species prediction.
    """
    await asyncio.sleep(2)  # Simulate network delay
    # Ensure mock result contains fields expected by SpeciesCard and ObservationForm
    return {
        "scientific_name": "Aedes fictus",
        "probabilities": {"Aedes fictus": 0.95, "Culex pipiens": 0.05},
        "id": "species_mock_001",  # Example species ID
        "model_id": "model_v1_mock",  # Example model ID
        "confidence": 0.95,  # Overall confidence
        "image_url_species": "https://via.placeholder.com/300x200.png?text=Aedes+fictus",  # Placeholder species image
    }, None


@solara.component
def FileUploadComponent(
    on_file_selected: callable,  # Callback: (file_info: Dict[str, Any]) -> bool
    upload_error_message: Optional[str] = None,
    is_processing: bool = False,  # To show a general processing state if needed by parent
):
    """
    A component for handling file uploads.
    Calls `on_file_selected` with file_info upon successful file drop/selection.
    Displays an optional `upload_error_message`.
    """
    solara.Markdown(
        "Upload an image of a mosquito to predict its species.",
        style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; margin-bottom: 20px;",
    )

    solara.FileDrop(
        label="Drag and drop an image here, or click to select.",
        on_file=on_file_selected,
        lazy=False,  # Process immediately
    )

    if upload_error_message:
        solara.Error(upload_error_message, style="margin-top: 15px; margin-bottom: 10px; width: 100%;")
    elif is_processing:  # Parent can indicate if something is happening post-upload
        solara.ProgressLinear(True, color="primary", style="margin-top: 10px;")

import solara
import io
from typing import Optional, Dict, Any, Tuple
import aiohttp

from ...config import FONT_BODY, COLOR_TEXT, API_BASE_URL


async def upload_and_predict(file_obj: io.BytesIO, filename: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Upload an image to the prediction endpoint and get a species prediction.

    Args:
        file_obj: BytesIO object containing the image data
        filename: Name of the file being uploaded

    Returns:
        Tuple containing (prediction_result, error_message)
        If successful, error_message will be None
        If failed, prediction_result will be None and error_message will contain the error
    """
    try:
        # Prepare the file for upload
        file_data = file_obj.getvalue()

        # Determine content type based on file extension
        content_type = "image/jpeg"  # Default
        if filename.lower().endswith(".png"):
            content_type = "image/png"
        elif filename.lower().endswith(".gif"):
            content_type = "image/gif"

        # Create API endpoint URL
        prediction_url = f"{API_BASE_URL}/predict"

        # Create form data with file
        form_data = aiohttp.FormData()
        form_data.add_field("file", file_data, filename=filename, content_type=content_type)

        # Make API request
        async with aiohttp.ClientSession() as session:
            async with session.post(prediction_url, data=form_data) as response:
                if response.status == 200:
                    # Successfully got prediction
                    prediction_data = await response.json()
                    return prediction_data, None
                else:
                    # Error occurred
                    try:
                        error_data = await response.json()
                        error_message = error_data.get("detail", f"Error: HTTP {response.status}")
                    except (aiohttp.ContentTypeError, ValueError):
                        # Handle case where response is not valid JSON
                        error_message = f"Error: HTTP {response.status} - {await response.text()}"
                    return None, error_message

    except aiohttp.ClientError as e:
        # Network or connection error
        return None, f"Connection error: {str(e)}"
    except Exception as e:
        # Any other error
        return None, f"Error: {str(e)}"


@solara.component
def FileUploadComponent(
    on_file_selected: callable,  # Callback: (file_info: Dict[str, Any]) -> bool
    upload_error_message: Optional[str] = None,
    is_processing: bool = True,  # To show a general processing state if needed by parent
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
        label="Drag and drop an image here...",
        on_file=on_file_selected,
        lazy=False,  # Process immediately
    )

    if upload_error_message:
        solara.Error(upload_error_message, style="margin-top: 15px; margin-bottom: 10px; width: 100%;")
    elif is_processing:  # Parent can indicate if something is happening post-upload
        solara.ProgressLinear(True, color="primary", style="margin-top: 10px;")

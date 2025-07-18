import solara
import io
from typing import Optional, Dict, Any, Tuple
import aiohttp

from ...config import FONT_BODY, COLOR_TEXT, API_BASE_URL
import i18n

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
        file_data = file_obj.getvalue()

        content_type = "image/jpeg"
        if filename.lower().endswith(".png"):
            content_type = "image/png"
        elif filename.lower().endswith(".gif"):
            content_type = "image/gif"

        prediction_url = f"{API_BASE_URL}/predict"

        form_data = aiohttp.FormData()
        form_data.add_field("file", file_data, filename=filename, content_type=content_type)

        async with aiohttp.ClientSession() as session:
            async with session.post(prediction_url, data=form_data) as response:
                if response.status == 200:
                    prediction_data = await response.json()
                    return prediction_data, None
                else:
                    try:
                        error_data = await response.json()
                        error_message = error_data.get("detail", f"Error: HTTP {response.status}")
                    except (aiohttp.ContentTypeError, ValueError):
                        error_message = f"Error: HTTP {response.status} - {await response.text()}"
                    return None, error_message

    except aiohttp.ClientError as e:
        return None, f"Connection error: {str(e)}"
    except Exception as e:
        return None, f"Error: {str(e)}"


@solara.component
def FileUploadComponent(
    on_file_selected: callable,
    upload_error_message: Optional[str] = None,
    is_processing: bool = True,
):
    """
    A component for handling file uploads.
    Calls `on_file_selected` with file_info upon successful file drop/selection.
    Displays an optional `upload_error_message`.
    """
    solara.Markdown(
        i18n.t("prediction.file_upload.subtitle"),
        style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; margin-bottom: 20px;",
    )

    solara.FileDrop(
        label=i18n.t("prediction.file_upload.drag_image"),
        on_file=on_file_selected,
        lazy=False,
    )

    if upload_error_message:
        solara.Error(upload_error_message, style="margin-top: 15px; margin-bottom: 10px; width: 100%;")
    elif is_processing:
        solara.ProgressLinear(True, color="primary", style="margin-top: 10px;")

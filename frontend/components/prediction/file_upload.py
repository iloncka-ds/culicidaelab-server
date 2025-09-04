"""
Provides a file upload component and an associated API call for predictions.

This module contains the `FileUploadComponent` for the user interface and the
`upload_and_predict` asynchronous function, which handles sending the uploaded
image file to the backend prediction service.
"""

import solara
import io
from typing import Any

from collections.abc import Callable
import aiohttp

from frontend.config import FONT_BODY, COLOR_TEXT, API_BASE_URL
from frontend.state import use_locale_effect
import i18n


async def upload_and_predict(file_obj: io.BytesIO, filename: str) -> tuple[dict[str, Any] | None, str | None]:
    """
    Uploads an image to the prediction endpoint and gets a species prediction.

    This asynchronous function takes an in-memory image file, sends it to the
    prediction API endpoint using a multipart/form-data POST request, and
    processes the response. It handles different image content types based on
    the filename extension.

    Args:
        file_obj: A BytesIO object containing the raw image data.
        filename: The original name of the file being uploaded, used to infer
            the content type.

    Returns:
        A tuple containing two elements:
        - A dictionary with the prediction result if the upload and prediction
          are successful.
        - A string with an error message if any part of the process fails.
        If successful, the error message will be `None`. If it fails, the
        prediction result will be `None`.
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
    on_file_selected: Callable,
    upload_error_message: str | None = None,
):
    """
    A user interface component for handling file uploads.

    This component renders a drag-and-drop area for file selection. When a
    file is successfully selected by the user, it triggers the `on_file_selected`
    callback with the file information provided by `solara.FileDrop`. It can
    also display an error message if one is provided via the
    `upload_error_message` prop.

    Args:
        on_file_selected: A callback function that is executed when a file is
            selected. The function receives one argument: a dictionary
            containing file information (e.g., 'name', 'file_obj').
        upload_error_message: An optional string. If provided, it will be
            displayed as an error message to the user.

    Example:
        ```python
        import solara
        import io

        @solara.component
        def Page():
            # State to hold any error messages
            error, set_error = solara.use_state(None)

            def handle_file(file_info: dict):
                # This function is called when a file is dropped.
                # 'file_info' is a dict like {'name': '...', 'file_obj': ...}
                file_name = file_info["name"]
                file_obj = file_info["file_obj"]

                print(f"File selected: {file_name}")

                # Example of simple validation
                if not file_name.lower().endswith((".png", ".jpg", ".jpeg")):
                    set_error("Invalid file type. Please upload a PNG or JPG image.")
                    return

                # Clear previous errors
                set_error(None)
                # Here you would typically proceed with the file,
                # e.g., by calling an upload function.

            with solara.Column(align="center"):
                solara.Text("Upload an image for prediction:")
                FileUploadComponent(
                    on_file_selected=handle_file,
                    upload_error_message=error
                )
        ```
    """
    use_locale_effect()

    solara.Text(
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

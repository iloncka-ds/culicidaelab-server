"""
Service for submitting mosquito observation data to the backend API.
"""

from typing import Optional, Dict, Any
import httpx
import json

from ...config import API_BASE_URL


async def submit_observation_data(observation_data: Dict[str, Any]) -> Optional[str]:
    """
    Submit observation data to the backend API.

    This function sends data as 'multipart/form-data' as expected by the refactored
    backend endpoint. For the web source, no file is attached.

    Args:
        observation_data: Dictionary containing observation data that conforms to the
                          backend's Observation Pydantic schema.

    Returns:
        Optional[str]: Error message if submission failed, None if successful.
    """
    if not API_BASE_URL:
        return "API URL is not configured"

    url = f"{API_BASE_URL}/observations"

    # The web client sends the source and the observation data as a JSON string.
    # No file is sent from this form, as it was handled in the prediction step.
    form_data = {
        "source": "web",
        "observation_data": json.dumps(observation_data),
    }
    print(form_data)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                data=form_data,  # httpx automatically sets content-type to multipart/form-data
                timeout=30.0,
            )

            if response.status_code >= 400:
                try:
                    error_detail = response.json().get("detail", "Unknown server error")
                except json.JSONDecodeError:
                    error_detail = response.text
                return f"Failed to submit observation: {error_detail}"

            return None

    except httpx.HTTPStatusError as e:
        return f"HTTP error: {str(e)}"
    except httpx.RequestError as e:
        return f"Request failed: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

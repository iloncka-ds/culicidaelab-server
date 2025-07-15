"""
Service for submitting mosquito observation data to the backend API.
"""

from typing import Optional, Dict, Any
import httpx
import json
import logging

from ...config import API_BASE_URL

logger = logging.getLogger("observation")


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
    print("\n[DEBUG] Starting observation submission process")
    print(f"[DEBUG] Raw observation data: {observation_data}")
    print(f"[DEBUG] API_BASE_URL: {API_BASE_URL}")
    
    if not API_BASE_URL:
        print("[ERROR] API_BASE_URL is not configured.")
        return "API URL is not configured"

    url = f"{API_BASE_URL}/observations"
    print(f"[DEBUG] Submission URL: {url}")

    # The web client sends the source and the observation data as a JSON string.
    # No file is sent from this form, as it was handled in the prediction step.
    form_data = {
        "source": "web",
        "observation_data": json.dumps(observation_data),
    }
    print(f"[DEBUG] Prepared form_data for submission: {form_data}")
    
    try:
        async with httpx.AsyncClient() as client:
            print("[DEBUG] Sending POST request to backend API...")
            response = await client.post(
                url,
                data=form_data,  # httpx automatically sets content-type to multipart/form-data
                timeout=30.0,
            )
            print(f"[DEBUG] Received response: status_code={response.status_code}, content={response.text}")

            if response.status_code >= 400:
                try:
                    error_detail = response.json().get("detail", "Unknown server error")
                    print(f"[ERROR] Backend returned error: {error_detail}")
                    return f"Failed to submit observation: {error_detail}"
                except json.JSONDecodeError:
                    error_detail = response.text
                    print(f"[ERROR] Backend returned non-JSON error: {error_detail}")
                    return f"Failed to submit observation: {error_detail}"

            print("[DEBUG] Observation data submitted successfully.")
            return None

    except httpx.HTTPStatusError as e:
        print(f"[ERROR] HTTPStatusError during submission: {str(e)}")
        return f"HTTP error: {str(e)}"
    except httpx.RequestError as e:
        print(f"[ERROR] RequestError during submission: {str(e)}")
        return f"Request failed: {str(e)}"
    except Exception as e:
        print(f"[ERROR] Unexpected exception during submission: {str(e)}")
        return f"An unexpected error occurred: {str(e)}"

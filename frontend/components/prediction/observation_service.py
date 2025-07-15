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
    logger.debug("Called submit_observation_data with observation_data: %r", observation_data)
    if not API_BASE_URL:
        logger.error("API_BASE_URL is not configured.")
        return "API URL is not configured"

    url = f"{API_BASE_URL}/observations"
    logger.debug("Submission URL: %s", url)

    # The web client sends the source and the observation data as a JSON string.
    # No file is sent from this form, as it was handled in the prediction step.
    form_data = {
        "source": "web",
        "observation_data": json.dumps(observation_data),
    }
    logger.debug("Prepared form_data for submission: %r", form_data)
    try:
        async with httpx.AsyncClient() as client:
            logger.debug("Sending POST request to backend API.")
            response = await client.post(
                url,
                data=form_data,  # httpx automatically sets content-type to multipart/form-data
                timeout=30.0,
            )
            logger.debug("Received response: status_code=%d, content=%r", response.status_code, response.text)

            if response.status_code >= 400:
                try:
                    error_detail = response.json().get("detail", "Unknown server error")
                    logger.error("Backend returned error: %s", error_detail)
                except json.JSONDecodeError:
                    error_detail = response.text
                    logger.error("Backend returned non-JSON error: %s", error_detail)
                return f"Failed to submit observation: {error_detail}"

            logger.info("Observation data submitted successfully.")
            return None

    except httpx.HTTPStatusError as e:
        logger.error("HTTPStatusError during submission: %s", str(e))
        return f"HTTP error: {str(e)}"
    except httpx.RequestError as e:
        logger.error("RequestError during submission: %s", str(e))
        return f"Request failed: {str(e)}"
    except Exception as e:
        logger.exception("Unexpected exception during submission.")
        return f"An unexpected error occurred: {str(e)}"

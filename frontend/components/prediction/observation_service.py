"""
Service for submitting mosquito observation data to the backend API.
"""
from typing import Optional, Dict, Any
import httpx

from ...config import API_BASE_URL


async def submit_observation_data(observation_payload: Dict[str, Any]) -> Optional[str]:
    """
        Submit observation data to the backend API.

        Args:
            observation_payload: Dictionary containing observation data with the following structure:
                {
                    "species_id": str,
                    "count": int,
                    "location": {
                        "lat": float,
                        "lng": float
                    },
                    "observed_at": str,
                    "notes": Optional[str],
                    "image_url": Optional[str],
                    "metadata": Dict[str, Any]
                }

        Returns:
            Optional[str]: Error message if submission failed, None if successful
    """
    if not API_BASE_URL:
        return "API URL is not configured"

    url = f"{API_BASE_URL}/observations"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=observation_payload,
                headers={"Content-Type": "application/json"},
                timeout=30.0
            )

            if response.status_code >= 400:
                error_detail = response.json().get("detail", "Unknown error")
                return f"Failed to submit observation: {error_detail}"

            return None

    except httpx.HTTPStatusError as e:
        return f"HTTP error: {str(e)}"
    except httpx.RequestError as e:
        return f"Request failed: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

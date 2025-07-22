"""
Service for submitting mosquito observation data to the backend API.
"""

from typing import Optional, Dict, Any
import httpx
import logging

from ...config import API_BASE_URL

logger = logging.getLogger("observation")


async def submit_observation_data(observation_data: Dict[str, Any]) -> Optional[str]:
    """
    Submit observation data to the backend API as a JSON payload.
    """
    url = f"{API_BASE_URL}/observations"
    print(f"[WEB-CLIENT] Preparing to POST JSON to: {url}")
    print(f"[WEB-CLIENT] Payload: {observation_data}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=observation_data,
                timeout=30.0,
            )

            if response.status_code >= 400:
                error_detail = response.json().get("detail", "Unknown server error")
                return f"Failed to submit observation: {error_detail}"

            print("[WEB-CLIENT] Observation submitted successfully.")
            return None

    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

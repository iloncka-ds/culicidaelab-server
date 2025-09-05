"""
Provides a service for submitting observation data to the backend API.

This module contains the `submit_observation_data` function, which is responsible
for sending a structured JSON payload of observation details to the server
via an HTTP POST request.
"""

from typing import Any
import httpx
import logging

from frontend.config import API_BASE_URL


logger = logging.getLogger("observation")


async def submit_observation_data(observation_data: dict[str, Any]) -> str | None:
    """
    Submits observation data to the backend API as a JSON payload.

    This asynchronous function sends a POST request with a JSON payload
    containing observation details to the configured API endpoint. It handles
    HTTP errors and other exceptions, returning a descriptive error message
    if the submission fails.

    Args:
        observation_data: A dictionary containing the observation details. The
            structure of this dictionary should match the schema expected by
            the '/observations' API endpoint.

    Returns:
        None if the submission is successful, otherwise a string containing
        the error message.

    Example:
        ```python
        import asyncio

        # This is a hypothetical example of how this function would be called.
        async def run_submission():
            sample_data = {
                "species_scientific_name": "Aedes aegypti",
                "count": 1,
                "location": {"lat": 34.0522, "lng": -118.2437},
                "observed_at": "2023-09-15T10:00:00Z",
                "user_id": "test-user-01",
                "notes": "Found near a standing water source."
            }
            error_message = await submit_observation_data(sample_data)
            if error_message:
                print(f"Failed to submit observation: {error_message}")
            else:
                print("Observation submitted successfully.")

        # To run this, you would use:
        # asyncio.run(run_submission())
        ```
    """
    url = f"{API_BASE_URL}/observations"

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

            return None

    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

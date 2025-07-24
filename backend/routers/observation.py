
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from backend.services.observation_service import get_observation_service
from backend.schemas.observation_schemas import Observation, ObservationListResponse

router = APIRouter()


@router.post(
    "/observations",
    response_model=Observation,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new observation",
    description="Submit a complete observation record. Prediction must be done beforehand.",
)
async def create_observation(
    observation: Observation,
) -> Observation:
    """
    Create a new observation record from a complete data payload.
    The client is expected to have already performed prediction if necessary.
    """
    print("\n--- [ROUTER] Received request to CREATE observation ---")
    try:
        # FastAPI has already validated the incoming JSON against the Observation model.
        # All we need to do is add any final business logic.

        # Ensure user_id exists
        if not observation.user_id:
            observation.user_id = uuid4()
            print(f"[ROUTER] Generated new user_id: {observation.user_id}")

        print("[ROUTER] Observation data is valid. Calling observation service to save...")
        service = await get_observation_service()
        new_observation = await service.create_observation(observation)
        print(f"[ROUTER] Observation created successfully with ID: {new_observation.id}")
        return new_observation

    except HTTPException:
        # Re-raise exceptions from services or validation
        raise
    except Exception as e:
        # Catch any other unexpected errors
        print(f"[ROUTER] CRITICAL ERROR in /observations: {type(e).__name__} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create observation: {str(e)}"
        )

@router.get(
    "/observations",
    response_model=ObservationListResponse,
    summary="Get observations",
)
async def get_observations(
    species_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    user_id: str = "default_user_id",  # This should likely be replaced with auth
) -> ObservationListResponse:
    """
    Get a list of observations, optionally filtered by species.
    """
    print("\n--- [ROUTER] Received request for /observations (GET) ---")
    print(f"[ROUTER] Params: species_id='{species_id}', limit={limit}, offset={offset}, user_id='{user_id}'")
    try:
        service = await get_observation_service()
        print("[ROUTER] Calling service.get_observations...")
        result = await service.get_observations(
            user_id=user_id,
            species_id=species_id,
            limit=min(limit, 1000),  # Ensure limit is not excessive
            offset=max(offset, 0),  # Ensure offset is non-negative
        )
        print(f"[ROUTER] Retrieved {len(result.observations)} observations.")
        return result
    except HTTPException as http_exc:
        print(f"[ROUTER] Caught HTTPException: {http_exc.status_code} - {http_exc.detail}")
        raise
    except Exception as e:
        print(f"[ROUTER] CRITICAL ERROR in GET /observations: {type(e).__name__} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve observations: {str(e)}"
        )

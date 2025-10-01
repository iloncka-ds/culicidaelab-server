"""Observation Router Module for CulicidaeLab Server API.

This module provides FastAPI router endpoints for managing mosquito observation records.
It handles creation and retrieval of observation data, including species identification,
location information, and metadata.

The router integrates with the observation service layer to persist and retrieve
data from the database while providing proper validation and error handling.

Typical usage example:
    from backend.routers.observation import router
    app.include_router(router, prefix="/api/v1")

Endpoints:
    POST /observations - Create a new observation record
    GET /observations - Retrieve observations with optional filtering
"""

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
    """Create a new mosquito observation record.

    This endpoint accepts a complete observation record and stores it in the database.
    The observation should include species identification, location data, and metadata.
    If no user_id is provided, a UUID will be automatically generated.

    Args:
        observation: Complete observation data including species information,
            location coordinates, count, and optional metadata. Must conform
            to the Observation schema with all required fields validated.

    Returns:
        Observation: The created observation record with assigned ID and
            any server-generated fields.

    Raises:
        HTTPException: If observation creation fails due to validation errors
            or database issues. Returns 500 status code for server errors.

    Example:
        >>> from backend.schemas.observation_schemas import Observation, Location
        >>> observation_data = Observation(
        ...     species_scientific_name="Aedes aegypti",
        ...     count=5,
        ...     location=Location(lat=40.7128, lng=-74.0060),
        ...     observed_at="2024-01-15T10:30:00Z",
        ...     notes="Found near standing water"
        ... )
        >>> result = await create_observation(observation_data)
        >>> print(f"Created observation with ID: {result.id}")
    """
    print("\n--- [ROUTER] Received request to CREATE observation ---")
    try:
        # FastAPI has already validated the incoming JSON against the Observation model.
        # All we need to do is add any final business logic.

        # Ensure user_id exists
        if not observation.user_id:
            observation.user_id = str(uuid4())
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create observation: {str(e)}",
        )


@router.get(
    "/observations",
    response_model=ObservationListResponse,
    summary="Get observations",
)
async def get_observations(
    species_id: str | None = None,
    limit: int = 100,
    offset: int = 0,
    user_id: str = "default_user_id",  # This should likely be replaced with auth
) -> ObservationListResponse:
    """Retrieve mosquito observations with optional filtering.

    This endpoint returns a paginated list of observation records. Results can be
    filtered by species and user, with configurable pagination limits.

    Args:
        species_id: Optional species identifier to filter observations. If None,
            returns observations for all species. Should be a valid species UUID
            or identifier from the database.
        limit: Maximum number of observations to return in a single response.
            Must be between 1 and 1000. Defaults to 100. Larger values are
            automatically capped at 1000 for performance.
        offset: Number of observations to skip for pagination. Must be non-negative.
            Defaults to 0. Use with limit for paginated results.
        user_id: Identifier for the user whose observations to retrieve. Currently
            defaults to "default_user_id" but should be replaced with proper
            authentication in production.

    Returns:
        ObservationListResponse: Paginated response containing the total count
            of matching observations and the list of observation records.
            Each observation includes full species, location, and metadata.

    Raises:
        HTTPException: If observation retrieval fails due to database errors
            or invalid parameters. Returns 500 status code for server errors.

    Example:
        >>> # Get first 50 observations for all species
        >>> response = await get_observations(limit=50)
        >>> print(f"Total observations: {response.count}")
        >>>
        >>> # Get observations for a specific species with pagination
        >>> response = await get_observations(
        ...     species_id="aedes-aegypti-uuid",
        ...     limit=25,
        ...     offset=25
        ... )
        >>> for obs in response.observations:
        ...     print(f"Species: {obs.species_scientific_name}")
        >>>
        >>> # Get observations for a specific user (when auth is implemented)
        >>> response = await get_observations(
        ...     user_id="authenticated-user-id",
        ...     limit=10
        ... )
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve observations: {str(e)}",
        )

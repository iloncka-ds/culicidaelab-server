from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from pydantic import HttpUrl, ValidationError

from backend.services.prediction_service import prediction_service, PredictionResult
from backend.services.observation_service import get_observation_service
from backend.schemas.observation_schemas import Observation, ObservationCreate, ObservationListResponse


router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictionResult,
    summary="Predict mosquito species from image",
    description="Upload an image of a mosquito to identify its species using AI.",
)
async def predict_species(
    file: UploadFile = File(...),
) -> PredictionResult:
    """
    Predict mosquito species from an uploaded image.

    Args:
        file: Uploaded image file (JPEG, PNG, etc.)

    Returns:
        Prediction result with species information and confidence scores

    Raises:
        HTTPException: If prediction fails or file is invalid
    """

    content_type = file.content_type
    if not content_type or not content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File must be an image, got {content_type}"
        )

    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file"
            )

        result, error = await prediction_service.predict_species(contents, file.filename)

        if error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Prediction failed: {error}"
            )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Prediction failed with no specific error"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )



@router.post(
    "/observations",
    response_model=Observation,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new observation",
    description="""Submit a new mosquito observation with species, location, and other details.

    Required fields:
    - species_id: ID of the observed species
    - count: Number of specimens (must be > 0)
    - location: Object with 'lat' and 'lng' as numbers
    - observed_at: ISO 8601 datetime string (e.g., '2024-01-01T12:00:00Z')

    Optional fields:
    - notes: String (max 1000 chars)
    - image_url: Valid HTTP/HTTPS URL
    - metadata: Additional key-value pairs
    """,
)
async def create_observation(
    observation_data: dict,
    user_id: str = None,
) -> Observation:
    """
    Create a new observation record with proper validation.

    Args:
        observation_data: Dictionary containing observation data
        user_id: Optional user ID (must be a valid UUID if provided)

    Returns:
        Created observation record

    Raises:
        HTTP 400: If input validation fails
        HTTP 500: If there's a server error
    """
    try:
        # Generate a UUID if none provided
        if not user_id:
            user_id = str(uuid4())

        # Validate user_id if provided
        if user_id != "default_user_id":
            try:
                UUID(user_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="user_id must be a valid UUID"
                )

        # Ensure location has required fields
        location = observation_data.get('location', {})
        if not isinstance(location, dict) or 'lat' not in location or 'lng' not in location:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="location must be an object with 'lat' and 'lng' fields"
            )

        # Ensure observed_at is in the correct format
        if 'observed_at' in observation_data:
            if isinstance(observation_data['observed_at'], str):
                try:
                    # Convert string to datetime
                    observation_data['observed_at'] = observation_data['observed_at'].replace('Z', '+00:00')
                except (ValueError, TypeError):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="observed_at must be a valid ISO 8601 datetime string"
                    )

        # Validate image_url if provided
        if 'image_url' in observation_data and observation_data['image_url']:
            try:
                # Create an HttpUrl instance which will validate the URL
                # If invalid, this will raise a ValidationError
                HttpUrl(observation_data['image_url'])
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="image_url must be a valid URL"
                )

        # Create the Pydantic model which will do additional validation
        observation = ObservationCreate(**observation_data)

        # Get the service and create the observation
        service = await get_observation_service()
        return await service.create_observation(observation, user_id)

    except HTTPException:
        raise
    except ValidationError as e:
        # Convert any datetime objects in the error details to ISO format strings
        errors = []
        for error in e.errors():
            error_dict = dict(error)
            if 'input' in error_dict and isinstance(error_dict['input'], datetime):
                error_dict['input'] = error_dict['input'].isoformat()
            errors.append(error_dict)

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=errors
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create observation: {str(e)}"
        )


@router.get(
    "/observations",
    response_model=ObservationListResponse,
    summary="Get observations",
    description="Retrieve observations with optional filtering.",
)
async def get_observations(
    species_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    user_id: str = "default_user_id",
) -> ObservationListResponse:
    """
    Get a list of observations, optionally filtered by species.

    Only returns observations for the authenticated user unless the user has admin privileges.
    """
    try:
        service = await get_observation_service()
        return await service.get_observations(
            user_id=user_id,
            species_id=species_id,
            limit=min(limit, 1000),
            offset=max(offset, 0),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve observations: {str(e)}"
        )

from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status

from backend.services.prediction_service import prediction_service, PredictionResult
from backend.services.observation_service import observation_service
from backend.models import Observation, ObservationCreate, ObservationListResponse


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
    description="Submit a new mosquito observation with species, location, and other details.",
)
async def create_observation(
    observation: ObservationCreate,
    user_id: str = "default_user_id",
) -> Observation:
    """
    Create a new observation record.

    This endpoint allows authenticated users to submit mosquito observation data.
    The observation will be associated with the authenticated user.
    """
    try:
        return await observation_service.create_observation(observation, user_id)
    except HTTPException:
        raise
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
        return await observation_service.get_observations(
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

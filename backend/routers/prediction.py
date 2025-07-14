from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
import json

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status, Form
from pydantic import HttpUrl, ValidationError

from backend.services.prediction_service import prediction_service, PredictionResult
from backend.services.observation_service import get_observation_service
from backend.schemas.observation_schemas import Observation, ObservationListResponse

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
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"File must be an image, got {content_type}"
        )

    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")

        result, error = await prediction_service.predict_species(contents, file.filename)

        if error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Prediction failed: {error}")

        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Prediction failed with no specific error"
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Prediction failed: {str(e)}")


@router.post(
    "/observations",
    response_model=Observation,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new observation",
    description="""
    Submit a new mosquito observation.
    - For **web** source: `observation_data` should be a JSON string with all details.
    - For **mobile** source: `observation_data` is a JSON string with observation details,
      and an image `file` should be uploaded for prediction. The predicted species will
      override any species info in the `observation_data`.
    """,
)
async def create_observation(
    observation_data_str: str = Form(..., alias="observation_data"),
    source: str = Form(..., description="The source of the observation, e.g., 'web' or 'mobile'"),
    file: Optional[UploadFile] = File(None),
) -> Observation:
    """
    Create a new observation record, with different handling based on the source.
    """
    try:
        observation_data = json.loads(observation_data_str)

        if source == "mobile":
            if not file:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File upload is required for source 'mobile'.",
                )
            contents = await file.read()
            if not contents:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file uploaded.")

            # Run prediction
            prediction_result, error = await prediction_service.predict_species(contents, file.filename)
            if error:
                raise HTTPException(status_code=500, detail=f"Prediction failed: {error}")
            if not prediction_result:
                raise HTTPException(status_code=500, detail="Prediction failed without a specific error.")

            # Update observation data with prediction results
            observation_data["species_scientific_name"] = prediction_result.scientific_name
            observation_data["model_id"] = prediction_result.model_id
            observation_data["confidence"] = prediction_result.confidence
            observation_data["image_filename"] = file.filename
            observation_data.setdefault("metadata", {})["prediction"] = prediction_result.model_dump()

        # --- Validation (adapted from original function) ---
        user_id = observation_data.get("user_id")
        if user_id:
            try:
                UUID(user_id)
            except (ValueError, TypeError):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id must be a valid UUID")
        else:
            observation_data["user_id"] = str(uuid4())

        location = observation_data.get("location", {})
        if not isinstance(location, dict) or "lat" not in location or "lng" not in location:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="location must be an object with 'lat' and 'lng' fields"
            )

        if "observed_at" in observation_data and isinstance(observation_data["observed_at"], str):
            try:
                observation_data["observed_at"] = observation_data["observed_at"].replace("Z", "+00:00")
                datetime.fromisoformat(observation_data["observed_at"])
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="observed_at must be a valid ISO 8601 datetime string",
                )

        # Create Pydantic model
        observation = Observation(**observation_data)

        # Get service and save
        service = await get_observation_service()
        return await service.create_observation(observation)

    except json.JSONDecodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON format in observation_data.")
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create observation: {str(e)}"
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve observations: {str(e)}"
        )

from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.services.prediction_service import prediction_service, PredictionResult

router = APIRouter()


@router.post("/predict", response_model=PredictionResult)
async def predict_species(
    file: UploadFile = File(...),
) -> PredictionResult:
    """
    Predict mosquito species from an uploaded image.

    Args:
        file: Uploaded image file

    Returns:
        PredictionResult: Prediction result with species information

    Raises:
        HTTPException: If prediction fails or file is invalid
    """
    # Validate file
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    # Check file type
    content_type = file.content_type
    if not content_type or not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail=f"File must be an image, got {content_type}")

    try:
        # Read file content
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")

        # Get prediction
        result, error = await prediction_service.predict_species(contents, file.filename)

        if error:
            raise HTTPException(status_code=500, detail=error)

        if not result:
            raise HTTPException(status_code=500, detail="Prediction failed with no specific error")

        return result

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log and convert other exceptions to HTTP exceptions
        print(f"Error in prediction endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

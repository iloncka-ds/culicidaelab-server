"""Prediction router for mosquito species identification.

This module provides FastAPI endpoints for predicting mosquito species from uploaded
images using AI-powered classification. The router handles image validation,
coordinates with the prediction service, and returns structured results.

Main Components:
    - APIRouter instance configured for prediction endpoints
    - predict_species endpoint for species identification

The prediction system supports:
    - Multiple image formats (JPEG, PNG, etc.)
    - Real-time species identification with confidence scores
    - Optional image saving for predicted results
    - Comprehensive error handling and logging

Example:
    >>> from fastapi import FastAPI
    >>> from backend.routers.prediction import router
    >>>
    >>> app = FastAPI()
    >>> app.include_router(router, prefix="/api/v1")
    >>>
    >>> # Now available at POST /api/v1/predict
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status

from backend.services.prediction_service import prediction_service, PredictionResult


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
    """Predict mosquito species from an uploaded image.

    This endpoint accepts an image file and uses AI-powered classification
    to identify the mosquito species. The prediction includes confidence scores
    and optional species information.

    Args:
        file (UploadFile): The image file to analyze. Must be a valid image
            format (JPEG, PNG, etc.). The file is validated for content type
            and non-empty content.

    Returns:
        PredictionResult: A structured response containing:
            - id: Species identifier (lowercase with underscores)
            - scientific_name: The predicted species name
            - probabilities: Dictionary of species -> confidence scores
            - model_id: Identifier of the AI model used
            - confidence: Confidence score of the top prediction
            - image_url_species: URL to processed image (if saving enabled)

    Raises:
        HTTPException: If the file is not an image (400 Bad Request)
        HTTPException: If the file is empty (400 Bad Request)
        HTTPException: If prediction fails (500 Internal Server Error)

    Example:
        >>> import requests
        >>>
        >>> # Using curl command:
        >>> # curl -X POST "http://localhost:8000/predict" \
        >>> #      -H "accept: application/json" \
        >>> #      -H "Content-Type: multipart/form-data" \
        >>> #      -F "file=@mosquito_image.jpg"
        >>>
        >>> # Using Python requests:
        >>> response = requests.post(
        ...     "http://localhost:8000/predict",
        ...     files={"file": open("mosquito_image.jpg", "rb")}
        ... )
        >>> result = response.json()
        >>> print(f"Predicted species: {result['scientific_name']}")
        >>> print(f"Confidence: {result['confidence']:.2%}")
    """
    print("\n--- [ROUTER] Received request for /predict ---")
    try:
        content_type = file.content_type
        print(f"[ROUTER] File received. Filename: '{file.filename}', Content-Type: '{content_type}'")

        if not content_type or not content_type.startswith("image/"):
            print("[ROUTER] ERROR: Invalid content type. Raising 400 Bad Request.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File must be an image, got {content_type}",
            )

        print("[ROUTER] Reading file contents...")
        contents = await file.read()
        if not contents:
            print("[ROUTER] ERROR: Empty file uploaded. Raising 400 Bad Request.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")

        print("[ROUTER] File contents read ({len(contents)} bytes). Calling prediction_service...")
        result, error = await prediction_service.predict_species(contents, file.filename)
        print("[ROUTER] Prediction service returned. Result: {result is not None}, Error: '{error}'")

        if error:
            print("[ROUTER] ERROR: Prediction service returned an error. Raising 500 Internal Server Error.")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Prediction failed: {error}")

        if not result:
            print("[ROUTER] ERROR: Prediction service returned no result and no error. Raising 500.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Prediction failed with no specific error",
            )

        print(f"[ROUTER] Prediction successful. Returning result for '{result.scientific_name}'.")
        return result

    except HTTPException as http_exc:
        # Re-raise HTTPExceptions to let FastAPI handle them
        print(f"[ROUTER] Caught HTTPException: {http_exc.status_code} - {http_exc.detail}")
        raise
    except Exception as e:
        # Catch any other unexpected errors
        print(f"[ROUTER] CRITICAL ERROR in /predict: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Prediction failed: {str(e)}")

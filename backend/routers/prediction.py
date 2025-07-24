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
    """
    Predict mosquito species from an uploaded image.
    """
    print("\n--- [ROUTER] Received request for /predict ---")
    try:
        content_type = file.content_type
        print(f"[ROUTER] File received. Filename: '{file.filename}', Content-Type: '{content_type}'")

        if not content_type or not content_type.startswith("image/"):
            print("[ROUTER] ERROR: Invalid content type. Raising 400 Bad Request.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"File must be an image, got {content_type}"
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
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Prediction failed with no specific error"
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

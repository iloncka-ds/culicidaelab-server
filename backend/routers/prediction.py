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


# @router.post(
#     "/observations",
#     response_model=Observation,
#     status_code=status.HTTP_201_CREATED,
#     summary="Submit a new observation",
# )
# async def create_observation(
#     observation_data_str: str = Form(..., alias="observation_data"),
#     source: str = Form(..., description="The source of the observation, e.g., 'web' or 'mobile'"),
#     file: Optional[UploadFile] = File(None),
# ) -> Observation:
#     """
#     Create a new observation record, with different handling based on the source.
#     """
#     print(f"\n--- [ROUTER] Received request for /observations from source: '{source}' ---")
#     try:
#         print("[ROUTER] Parsing observation_data JSON string...")
#         print(f"[ROUTER] Raw observation_data_str: {observation_data_str}")
#         observation_data = json.loads(observation_data_str)
#         print("[ROUTER] JSON parsing successful.")

#         if source == "mobile":
#             print("[ROUTER] Handling 'mobile' source logic...")
#             if not file:
#                 print("[ROUTER] ERROR: 'mobile' source but no file provided. Raising 400.")
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail="File upload is required for source 'mobile'.",
#                 )

#             print(f"[ROUTER] Mobile file received: '{file.filename}'. Reading contents...")
#             contents = await file.read()
#             if not contents:
#                 print("[ROUTER] ERROR: Empty mobile file. Raising 400.")
#                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file uploaded.")

#             print(f"[ROUTER] Mobile file contents read ({len(contents)} bytes). Calling prediction service...")
#             prediction_result, error = await prediction_service.predict_species(contents, file.filename)
#             print(f"[ROUTER] Prediction service returned. Result: {prediction_result is not None}, Error: '{error}'")
#             if error:
#                 print("[ROUTER] ERROR: Prediction service failed for mobile observation. Raising 500.")
#                 raise HTTPException(status_code=500, detail=f"Prediction failed: {error}")
#             if not prediction_result:
#                 print("[ROUTER] ERROR: Prediction service returned no result for mobile observation. Raising 500.")
#                 raise HTTPException(status_code=500, detail="Prediction failed without a specific error.")

#             print("[ROUTER] Prediction successful. Updating observation_data with prediction results...")
#             observation_data["species_scientific_name"] = prediction_result.scientific_name
#             observation_data["model_id"] = prediction_result.model_id
#             observation_data["confidence"] = prediction_result.confidence
#             # Important: Use the original filename for the record
#             observation_data["image_filename"] = file.filename
#             print("[ROUTER] observation_data updated.")

#         print("[ROUTER] Starting validation of observation data...")
#         user_id = observation_data.get("user_id")
#         if user_id:
#             try:
#                 UUID(user_id)
#             except (ValueError, TypeError):
#                 print(f"[ROUTER] ERROR: Invalid user_id format: '{user_id}'. Raising 400.")
#                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id must be a valid UUID")
#         else:
#             observation_data["user_id"] = str(uuid4())
#             print(f"[ROUTER] No user_id provided, generated new one: {observation_data['user_id']}")

#         location = observation_data.get("location", {})
#         if not isinstance(location, dict) or "lat" not in location or "lng" not in location:
#             print(f"[ROUTER] ERROR: Invalid location format: {location}. Raising 400.")
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST, detail="location must be an object with 'lat' and 'lng' fields"
#             )

#         if "observed_at" in observation_data and isinstance(observation_data["observed_at"], str):
#             try:
#                 # Handle timezone 'Z' for ISO compatibility
#                 observation_data["observed_at"] = observation_data["observed_at"].replace("Z", "+00:00")
#                 datetime.fromisoformat(observation_data["observed_at"])
#             except (ValueError, TypeError):
#                 print(f"[ROUTER] ERROR: Invalid observed_at format: '{observation_data['observed_at']}'. Raising 400.")
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail="observed_at must be a valid ISO 8601 datetime string",
#                 )
#         print("[ROUTER] Validation successful. Creating Pydantic model...")

#         # This is a key step where a ValidationError can occur if data doesn't match the schema
#         observation = Observation(**observation_data)
#         print("[ROUTER] Pydantic model created successfully.")

#         print("[ROUTER] Getting observation service...")
#         service = await get_observation_service()
#         print("[ROUTER] Calling service.create_observation...")
#         new_observation = await service.create_observation(observation)
#         print(f"[ROUTER] Observation created successfully with ID: {new_observation.id}")
#         return new_observation

#     except json.JSONDecodeError:
#         print("[ROUTER] ERROR: Failed to decode JSON from observation_data_str. Raising 400.")
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON format in observation_data.")
#     except ValidationError as e:
#         print(f"[ROUTER] ERROR: Pydantic validation failed. Raising 422. Details: {e.errors()}")
#         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors())
#     except HTTPException as http_exc:
#         print(f"[ROUTER] Caught HTTPException: {http_exc.status_code} - {http_exc.detail}")
#         raise
#     except Exception as e:
#         print(f"[ROUTER] CRITICAL ERROR in /observations: {type(e).__name__} - {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create observation: {str(e)}"
#         )


# @router.get(
#     "/observations",
#     response_model=ObservationListResponse,
#     summary="Get observations",
# )
# async def get_observations(
#     species_id: Optional[str] = None,
#     limit: int = 100,
#     offset: int = 0,
#     user_id: str = "default_user_id",  # This should likely be replaced with auth
# ) -> ObservationListResponse:
#     """
#     Get a list of observations, optionally filtered by species.
#     """
#     print(f"\n--- [ROUTER] Received request for /observations (GET) ---")
#     print(f"[ROUTER] Params: species_id='{species_id}', limit={limit}, offset={offset}, user_id='{user_id}'")
#     try:
#         service = await get_observation_service()
#         print("[ROUTER] Calling service.get_observations...")
#         result = await service.get_observations(
#             user_id=user_id,
#             species_id=species_id,
#             limit=min(limit, 1000),  # Ensure limit is not excessive
#             offset=max(offset, 0),  # Ensure offset is non-negative
#         )
#         print(f"[ROUTER] Retrieved {len(result.observations)} observations.")
#         return result
#     except HTTPException as http_exc:
#         print(f"[ROUTER] Caught HTTPException: {http_exc.status_code} - {http_exc.detail}")
#         raise
#     except Exception as e:
#         print(f"[ROUTER] CRITICAL ERROR in GET /observations: {type(e).__name__} - {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve observations: {str(e)}"
#         )

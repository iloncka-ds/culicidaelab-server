from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status

from backend.schemas.observation_schemas import Observation, ObservationListResponse, Location
from backend.database_utils.lancedb_manager import get_lancedb_manager


class ObservationService:
    """Service for managing mosquito observation data."""

    def __init__(self):
        self.table_name = "observations"
        self.db = None

    async def initialize(self):
        """Initialize the database connection."""
        lancedb_manager = await get_lancedb_manager()
        self.db = lancedb_manager.db
        return self

    async def create_observation(self, observation_data: Observation) -> Observation:
        """
        Create a new observation record.
        Maps the Pydantic Observation model to the LanceDB schema before insertion.
        """
        try:
            # Map Pydantic model to a dictionary that matches the LanceDB schema
            record_to_save = {
                "type": "Feature",
                "species": observation_data.species_scientific_name,
                "observation_date": observation_data.observed_at.split("T")[0],
                "count": observation_data.count,
                "observer_id": observation_data.user_id,
                "location_accuracy_m": observation_data.location_accuracy_m,
                "notes": observation_data.notes,
                "data_source": observation_data.data_source,
                "image_filename": observation_data.image_filename,
                "model_id": observation_data.model_id,
                "confidence": observation_data.confidence,
                "geometry_type": "Point",
                "coordinates": [observation_data.location.lng, observation_data.location.lat],
            }
            # Remove None values to avoid potential issues with LanceDB
            record_to_save = {k: v for k, v in record_to_save.items() if v is not None}

            table = await self.db.open_table(self.table_name)
            await table.add([record_to_save])

            # Return the original Pydantic model as confirmation
            return observation_data

        except Exception as e:
            detail = f"Failed to save observation to database: {str(e)}"
            print(detail)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

    async def get_observations(
        self,
        user_id: str | None = None,
        species_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> ObservationListResponse:
        """
        Retrieve observations with optional filtering.
        """
        try:
            table = await self.db.open_table(self.table_name)

            conditions = []
            if user_id and user_id != "default_user_id":
                conditions.append(f"observer_id = '{user_id}'")
            if species_id:
                conditions.append(f"species = '{species_id}'")

            query_str = " AND ".join(conditions) if conditions else None
            query = table.search()
            if query_str:
                query = query.where(query_str)

            results = await query.limit(limit).offset(offset).to_list()
            total = len(results) if results else 0

            # Map database records back to Pydantic models
            observations = []
            if results:
                for item in results:
                    coords = item.get("coordinates")
                    location = None
                    if coords and len(coords) == 2:
                        location = Location(lat=coords[1], lng=coords[0])

                    if location:
                        observation_model_data = {
                            "species_scientific_name": item.get("species"),
                            "count": item.get("count"),
                            "location": location,
                            "observed_at": item.get("observation_date"),
                            "notes": item.get("notes"),
                            "user_id": item.get("observer_id"),
                            "location_accuracy_m": item.get("location_accuracy_m"),
                            "data_source": item.get("data_source"),
                            "image_filename": item.get("image_filename"),
                            "model_id": item.get("model_id"),
                            "confidence": item.get("confidence"),
                            "metadata": {},  # Metadata is not stored in the database per the current schema
                        }
                        observations.append(Observation(**observation_model_data))

            return ObservationListResponse(count=total, observations=observations)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve observations: {str(e)}"
            )


observation_service = None


async def get_observation_service():
    """Get or initialize the observation service."""
    global observation_service
    if observation_service is None:
        observation_service = ObservationService()
        await observation_service.initialize()
    return observation_service

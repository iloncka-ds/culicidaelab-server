from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status

from backend.models import Observation, ObservationCreate, ObservationListResponse
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

    async def create_observation(self, observation_data: ObservationCreate, user_id: str | None = None) -> Observation:
        """
        Create a new observation record.

        Args:
            observation_data: Observation data to be saved
            user_id: ID of the user creating the observation

        Returns:
            Created observation with generated fields
        """
        try:
            # Convert to dict and add metadata
            observation_dict = observation_data.dict()
            observation_dict["id"] = str(uuid4())
            observation_dict["user_id"] = user_id
            current_time = datetime.utcnow().isoformat()
            observation_dict["created_at"] = current_time
            observation_dict["updated_at"] = current_time

            # Get or create table
            try:
                table = self.db.open_table(self.table_name)
            except Exception:
                # Create table with schema if it doesn't exist
                table = self.db.create_table(self.table_name, data=[observation_dict], mode="overwrite")
            else:
                # Table exists, insert new record
                table.add([observation_dict])

            return Observation(**observation_dict)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save observation: {str(e)}"
            )

    async def get_observations(
        self,
        user_id: str | None = None,
        species_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> ObservationListResponse:
        """
        Retrieve observations with optional filtering.

        Args:
            user_id: Filter by user ID
            species_id: Filter by species ID
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of observations matching the criteria
        """
        try:
            table = self.db.open_table(self.table_name)
            query = {}

            if user_id:
                query["user_id"] = user_id
            if species_id:
                query["species_id"] = species_id

            # Convert query to LanceDB format
            where = " AND ".join([f"{k} = '{v}'" for k, v in query.items()])

            results = table.search().where(where).limit(limit).offset(offset).to_list()
            total = len(results)  # This is a simple count, for pagination you might want a count query

            observations = [Observation(**item) for item in results]
            return ObservationListResponse(count=total, observations=observations)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve observations: {str(e)}"
            )


# Singleton instance
observation_service = None


# Async function to initialize the service
async def get_observation_service():
    global observation_service
    if observation_service is None:
        observation_service = await ObservationService().initialize()
    return observation_service

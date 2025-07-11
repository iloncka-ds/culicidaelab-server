from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status

from backend.schemas.observation_schemas import Observation, ObservationCreate, ObservationListResponse
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
            observation_dict = observation_data.dict()
            observation_dict["id"] = str(uuid4())
            observation_dict["user_id"] = user_id
            current_time = datetime.utcnow().isoformat()
            observation_dict["created_at"] = current_time
            observation_dict["updated_at"] = current_time

            try:
                table = await self.db.open_table(self.table_name)
                await table.add([observation_dict])
            except Exception:
                # If table doesn't exist, create it
                table = await self.db.create_table(
                    self.table_name, 
                    data=[observation_dict], 
                    mode="overwrite"
                )

            # Convert back to Pydantic model for response
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
            # Open the table
            table = await self.db.open_table(self.table_name)
            
            # Build query conditions
            conditions = []
            if user_id:
                conditions.append(f"user_id = '{user_id}'")
            if species_id:
                conditions.append(f"species_id = '{species_id}'")
                
            # Execute query
            query = " AND ".join(conditions) if conditions else None
            results = await table.search().where(query).limit(limit).offset(offset).to_list()
            
            # Get total count for pagination
            total = len(results) if results else 0
            
            # Convert to Pydantic models
            observations = [Observation(**item) for item in results] if results else []
            return ObservationListResponse(count=total, observations=observations)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve observations: {str(e)}"
            )


observation_service = None


async def get_observation_service():
    """Get or initialize the observation service.
    
    This function ensures the service is properly initialized before use.
    
    Returns:
        ObservationService: An initialized instance of ObservationService
    """
    global observation_service
    if observation_service is None:
        observation_service = ObservationService()
        await observation_service.initialize()
    return observation_service

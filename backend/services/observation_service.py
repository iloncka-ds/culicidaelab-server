"""
Observation service for managing mosquito observation data.

This module provides functionality for creating, storing, and retrieving
mosquito observation records in the LanceDB database. It handles data
validation, transformation, and provides both synchronous and asynchronous
methods for observation management.

Example:
    >>> from backend.services.observation_service import get_observation_service
    >>> service = await get_observation_service()
    >>> observation = await service.create_observation(obs_data)
"""

import json
from fastapi import HTTPException, status

from backend.schemas.observation_schemas import Observation, ObservationListResponse, Location
from backend.database_utils.lancedb_manager import get_lancedb_manager


class ObservationService:
    """Service for managing mosquito observation data.

    This class provides methods for creating new observations, retrieving
    existing observations with filtering options, and managing the database
    connection lifecycle.

    Attributes:
        table_name (str): The name of the database table for observations.
        db: The LanceDB database connection object.

    Example:
        >>> service = ObservationService()
        >>> await service.initialize()
        >>> observations = await service.get_observations(limit=10)
    """

    def __init__(self):
        """Initialize the ObservationService with default configuration.

        Sets up the service with the observations table name and prepares
        for database connection initialization.

        Example:
            >>> service = ObservationService()
            >>> print(service.table_name)  # "observations"
        """
        self.table_name = "observations"
        self.db = None

    async def initialize(self):
        """Initialize the database connection and ensure required tables exist.

        This method establishes a connection to the LanceDB database through
        the LanceDB manager and prepares the service for observation operations.
        The observations table will be created if it doesn't exist.

        Returns:
            ObservationService: The initialized service instance for method chaining.

        Example:
            >>> service = ObservationService()
            >>> await service.initialize()
            >>> print(f"Connected to DB: {service.db is not None}")
        """
        lancedb_manager = await get_lancedb_manager()
        self.db = lancedb_manager.db
        # Ensure the observations table exists; create it with the proper schema if it doesn't
        # await lancedb_manager.get_table(self.table_name, OBSERVATIONS_SCHEMA)
        return self

    async def create_observation(self, observation_data: Observation) -> Observation:
        """Create a new observation record in the database.

        This method transforms the Pydantic Observation model into the appropriate
        LanceDB schema format and inserts it into the observations table. It handles
        JSON serialization for complex fields like metadata and data_source.

        Args:
            observation_data (Observation): The observation data to store in the database.

        Returns:
            Observation: The same observation data that was passed in, confirming
                successful storage.

        Raises:
            HTTPException: If there's an error saving the observation to the database,
                an HTTP 500 error is raised with details about the failure.

        Example:
            >>> from backend.schemas.observation_schemas import Observation, Location
            >>> obs = Observation(
            ...     id="obs_001",
            ...     species_scientific_name="Aedes aegypti",
            ...     location=Location(lat=40.7128, lng=-74.0060),
            ...     observed_at="2023-06-15T10:30:00Z"
            ... )
            >>> result = await service.create_observation(obs)
        """
        try:
            metadata_value_str: str = ""
            metadata_value = observation_data.metadata
            if metadata_value is not None and not isinstance(metadata_value, str):
                metadata_value_str = json.dumps(metadata_value, ensure_ascii=False)
            elif isinstance(metadata_value, str):
                metadata_value_str = metadata_value

            data_source_value_str: str = ""
            data_source_value = observation_data.data_source
            if data_source_value is not None and not isinstance(data_source_value, str):
                data_source_value_str = json.dumps(data_source_value, ensure_ascii=False)
            elif isinstance(data_source_value, str):
                data_source_value_str = data_source_value

            record_to_save = {
                "id": str(observation_data.id),
                "species_scientific_name": observation_data.species_scientific_name,
                "observed_at": observation_data.observed_at.split("T")[0],
                "count": observation_data.count,
                "observer_id": observation_data.user_id,
                "location_accuracy_m": observation_data.location_accuracy_m,
                "notes": observation_data.notes,
                "data_source": data_source_value_str,
                "image_filename": observation_data.image_filename,
                "model_id": observation_data.model_id,
                "confidence": observation_data.confidence,
                "geometry_type": "Point",
                "coordinates": [observation_data.location.lat, observation_data.location.lng],
                "metadata": metadata_value_str,
            }
            # Remove None values to avoid potential issues with LanceDB
            record_to_save = {k: v for k, v in record_to_save.items() if v is not None}

            table = await self.db.open_table(self.table_name)
            await table.add([record_to_save])

            return observation_data

        except Exception as e:
            detail = f"Failed to save observation to database: {str(e)}"
            # print(detail)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

    async def get_observations(
        self,
        user_id: str | None = None,
        species_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> ObservationListResponse:
        """Retrieve observations with optional filtering by user and species.

        This method queries the observations table and returns filtered results
        based on user ID and/or species. It supports pagination and returns
        properly formatted Observation objects.

        Args:
            user_id (str | None, optional): Filter observations by a specific user ID.
                If None or "default_user_id", no user filtering is applied.
            species_id (str | None, optional): Filter observations by species scientific name.
                If None, no species filtering is applied.
            limit (int, optional): Maximum number of observations to return.
                Defaults to 100.
            offset (int, optional): Number of observations to skip for pagination.
                Defaults to 0.

        Returns:
            ObservationListResponse: A response object containing the total count
                and list of matching observations.

        Raises:
            HTTPException: If there's an error retrieving observations from the database,
                an HTTP 500 error is raised with details about the failure.

        Example:
            >>> # Get recent observations for a specific user
            >>> user_obs = await service.get_observations(user_id="user123", limit=50)
            >>> print(f"Found {user_obs.count} observations")
            >>>
            >>> # Get Aedes aegypti observations with pagination
            >>> aedes_obs = await service.get_observations(
            ...     species_id="Aedes aegypti",
            ...     limit=20,
            ...     offset=40
            ... )
        """
        try:
            print(
                f"[DEBUG] get_observations called with user_id={user_id}, species_id={species_id}, "
                f"limit={limit}, offset={offset}",
            )
            table = await self.db.open_table(self.table_name)

            # 1. Prepare conditions
            conditions = []
            if user_id and user_id != "default_user_id":
                conditions.append(f"observer_id = '{user_id}'")
            if species_id:
                conditions.append(f"species_scientific_name = '{species_id}'")

            # 2. Execute the query differently based on whether filters exist
            if conditions:
                # If there are filters, build a .where() clause
                query_str = " AND ".join(conditions)

                results = await table.search().where(query_str).limit(limit).offset(offset).to_list()

                arrow_table = await table.to_arrow()

                # Manually apply limit and offset
                start = offset
                end = offset + limit
                paginated_table = arrow_table.slice(start, end - start)
                results = paginated_table.to_pylist()

            total = len(results)

            observations = []
            if results:
                for item in results:
                    try:
                        location_data = item.get("coordinates")
                        if isinstance(location_data, list) and len(location_data) == 2:
                            location_obj = Location(lat=location_data[0], lng=location_data[1])
                        else:
                            continue

                        metadata_str = item.get("metadata", "{}")
                        metadata_dict = {}
                        if isinstance(metadata_str, str) and metadata_str.strip():
                            try:
                                metadata_dict = json.loads(metadata_str)
                            except json.JSONDecodeError:
                                print(f"[WARNING] Could not decode metadata for observation: {item.get('id')}")

                        observation_model = Observation(
                            id=item.get("id"),
                            species_scientific_name=item.get("species_scientific_name"),
                            count=item.get("count"),
                            location=location_obj,
                            observed_at=item.get("observed_at"),
                            notes=item.get("notes"),
                            user_id=item.get("user_id") or item.get("observer_id"),
                            location_accuracy_m=item.get("location_accuracy_m"),
                            data_source=item.get("data_source"),
                            image_filename=item.get("image_filename"),
                            model_id=item.get("model_id"),
                            confidence=item.get("confidence"),
                            metadata=metadata_dict,
                        )
                        observations.append(observation_model)
                    except Exception as model_exc:
                        print(f"[ERROR] Could not map record to Pydantic model for ID {item.get('id')}: {model_exc}")

            return ObservationListResponse(count=total, observations=observations)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve observations: {str(e)}",
            )


observation_service = None


async def get_observation_service():
    """Get or initialize the global observation service instance.

    This function implements a singleton pattern for the ObservationService,
    ensuring that only one instance exists and is properly initialized.
    If the service hasn't been created yet, it creates a new instance
    and initializes it.

    Returns:
        ObservationService: The global observation service instance,
            initialized and ready for use.

    Example:
        >>> service = await get_observation_service()
        >>> observations = await service.get_observations(limit=10)
    """
    global observation_service
    if observation_service is None:
        observation_service = ObservationService()
        await observation_service.initialize()
    return observation_service

import json
from fastapi import HTTPException, status

from backend.schemas.observation_schemas import Observation, ObservationListResponse, Location
from backend.database_utils.lancedb_manager import get_lancedb_manager


class ObservationService:
    """Service for managing mosquito observation data."""

    def __init__(self):
        self.table_name = "observations"
        self.db = None

    async def initialize(self):
        """Initialize the database connection and ensure required tables exist."""
        lancedb_manager = await get_lancedb_manager()
        self.db = lancedb_manager.db
        # Ensure the observations table exists; create it with the proper schema if it doesn't
        # await lancedb_manager.get_table(self.table_name, OBSERVATIONS_SCHEMA)
        return self

    async def create_observation(self, observation_data: Observation) -> Observation:
        """
        Create a new observation record.
        Maps the Pydantic Observation model to the LanceDB schema before insertion.
        """
        try:
            metadata_value = observation_data.metadata
            if metadata_value is not None and not isinstance(metadata_value, str):
                metadata_value_str: str = json.dumps(metadata_value, ensure_ascii=False)
            data_source_value = observation_data.data_source
            if data_source_value is not None and not isinstance(data_source_value, str):
                data_source_value_str: str = json.dumps(data_source_value, ensure_ascii=False)

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
        """
        Retrieve observations with optional filtering.
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
    """Get or initialize the observation service."""
    global observation_service
    if observation_service is None:
        observation_service = ObservationService()
        await observation_service.initialize()
    return observation_service

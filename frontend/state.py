import solara
import httpx
import i18n
from typing import List, Tuple, Optional, Dict, Any, cast
import uuid
from datetime import date, timedelta

from .config import FILTER_OPTIONS_ENDPOINT

current_user_id: solara.Reactive[Optional[str]] = solara.reactive(None)


@solara.component
def use_persistent_user_id():
    """
    A hook to get or create a user ID.
    """
    user_id, set_user_id = solara.use_state(None)
    
    def initialize_user_id():
        if user_id is None:
            new_id = str(uuid.uuid4())
            set_user_id(new_id)
            current_user_id.value = new_id
        else:
            if current_user_id.value != user_id:
                current_user_id.value = user_id
    
    solara.use_effect(initialize_user_id, [])

async def fetch_api_data(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    loading_reactive: Optional[solara.Reactive[bool]] = None,
    error_reactive: Optional[solara.Reactive[Optional[str]]] = None,
) -> Optional[Any]:
    if loading_reactive:
        loading_reactive.value = True
    if error_reactive:
        error_reactive.value = None
    try:
        async with httpx.AsyncClient() as client:
            print(f"Fetching data from {url} with params {params if params else ''}")
            response = await client.get(url, params=params, timeout=20.0)
            response.raise_for_status()
            return response.json()
    except httpx.ReadTimeout:
        msg = f"Timeout fetching data from {url}."
        if error_reactive:
            error_reactive.value = msg
        print(msg)
        return None
    except httpx.HTTPStatusError as e:
        detail = e.response.text
        try:
            detail_json = e.response.json()
            detail = detail_json.get("detail", detail)
        except Exception:
            pass
        msg = f"HTTP error {e.response.status_code} from {url}. Detail: {detail}"
        if error_reactive:
            error_reactive.value = msg
        print(msg)
        return None
    except Exception as e:
        msg = f"Failed to fetch data from {url}: {e}"
        if error_reactive:
            error_reactive.value = msg
        print(msg)
        return None
    finally:
        if loading_reactive:
            loading_reactive.value = False


default_end_date = date.today()
default_start_date = default_end_date - timedelta(days=365)

DEFAULT_INITIAL_SPECIES_TO_LOAD = ["Aedes albopictus", "Anopheles gambiae"]
selected_species_reactive: solara.Reactive[Optional[List[str]]] = solara.reactive(DEFAULT_INITIAL_SPECIES_TO_LOAD)
selected_date_range_reactive: solara.Reactive[Tuple[Optional[date], Optional[date]]] = solara.reactive(
    (default_start_date, default_end_date)
)
# selected_region_reactive: solara.Reactive[Optional[str]] = solara.reactive(None)
# selected_data_source_reactive: solara.Reactive[Optional[str]] = solara.reactive(None)
# selected_region_reactive = solara.reactive(cast(Optional[str], None))
# selected_data_source_reactive = solara.reactive(cast(Optional[str], None))
selected_species_item_id = solara.reactive(None)

show_observed_data_reactive = solara.reactive(True)
# show_modeled_data_reactive = solara.reactive(False)
# show_distribution_status_reactive = solara.reactive(True)
# show_breeding_sites_reactive = solara.reactive(False)

DEFAULT_MAP_CENTER = (20, 0)
DEFAULT_MAP_ZOOM = 3
current_map_center_reactive: solara.Reactive[Tuple[float, float]] = solara.reactive(DEFAULT_MAP_CENTER)
current_map_zoom_reactive: solara.Reactive[int] = solara.reactive(DEFAULT_MAP_ZOOM)
current_map_bounds_reactive: solara.Reactive[Optional[Tuple[Tuple[float, float], Tuple[float, float]]]] = (
    solara.reactive(None)
)

selected_map_feature_info = solara.reactive(None)

# distribution_data_reactive = solara.reactive(None)
observations_data_reactive = solara.reactive(None)
# modeled_data_reactive = solara.reactive(None)
# breeding_sites_data_reactive = solara.reactive(None)

all_available_species_reactive = solara.reactive(cast(List[str], []))
# all_available_regions_reactive = solara.reactive(cast(List[Dict[str, str]], []))
# all_available_data_sources_reactive = solara.reactive(cast(List[Dict[str, str]], []))
species_list_data_reactive = solara.reactive(cast(List[Dict[str, Any]], []))
species_list_loading_reactive = solara.reactive(False)
species_list_error_reactive = solara.reactive(cast(Optional[str], None))

filter_options_loading_reactive = solara.reactive(False)
filter_options_error_reactive = solara.reactive(cast(Optional[str], None))

selected_disease_item_id = solara.reactive(None)
disease_list_data_reactive = solara.reactive(cast(List[Dict[str, Any]], []))
disease_list_loading_reactive = solara.reactive(False)
disease_list_error_reactive = solara.reactive(cast(Optional[str], None))


async def fetch_filter_options():
    """Fetches species, regions, and data sources for filter dropdowns."""
    if filter_options_loading_reactive.value:
        return
    lang = i18n.get("locale")
    filter_options_loading_reactive.value = True
    filter_options_error_reactive.value = None
    try:
        async with httpx.AsyncClient() as client:
            print(f"Fetching filter options from {FILTER_OPTIONS_ENDPOINT} for lang='{lang}'")
            response = await client.get(FILTER_OPTIONS_ENDPOINT, params={"lang": lang}, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            all_available_species_reactive.value = data.get("species", [])
            # all_available_regions_reactive.value = data.get("regions", [])
            # all_available_data_sources_reactive.value = data.get("data_sources", [])
            # print(
            #     f"Filter options loaded: {len(all_available_species_reactive.value)} species, "
            #     f"{len(all_available_regions_reactive.value)} regions, "
            #     f"{len(all_available_data_sources_reactive.value)} sources."
            # )

    except httpx.HTTPStatusError as e:
        err_msg = f"HTTP error fetching filter options: {e.response.status_code} - {e.response.text}"
        print(err_msg)
        filter_options_error_reactive.value = err_msg
        all_available_species_reactive.value = []
        # all_available_regions_reactive.value = []
        # all_available_data_sources_reactive.value = []
    except Exception as e:
        err_msg = f"Error fetching filter options: {e}"
        print(err_msg)
        filter_options_error_reactive.value = err_msg
        all_available_species_reactive.value = []
        # all_available_regions_reactive.value = []
        # all_available_data_sources_reactive.value = []
    finally:
        filter_options_loading_reactive.value = False


distribution_loading_reactive = solara.reactive(False)
observations_loading_reactive = solara.reactive(False)
modeled_loading_reactive = solara.reactive(False)
breeding_sites_loading_reactive = solara.reactive(False)

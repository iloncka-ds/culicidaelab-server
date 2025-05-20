
import solara
import httpx
import asyncio
from typing import List, Tuple, Optional, Dict, Any, cast  # Add Dict, Any, cast
import datetime as dt

# Import new endpoint from config
from .config import FILTER_OPTIONS_ENDPOINT  # Assuming relative import within the package

# --- API Helper ---
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

# --- Filter States ---
selected_species_reactive = solara.reactive(cast(List[str], []))  # Ensure type hint
selected_date_range_reactive = solara.reactive(
    cast(Tuple[Optional[Any], Optional[Any]], [dt.date.today(), dt.date.today() + dt.timedelta(days=1)])
)
# More specific Any for date
selected_region_reactive = solara.reactive(cast(Optional[str], None))
selected_data_source_reactive = solara.reactive(cast(Optional[str], None))
selected_species_item_id = solara.reactive(None)

# --- Layer Visibility ---
show_observed_data_reactive = solara.reactive(True)
show_modeled_data_reactive = solara.reactive(False)  # Default off as it can be heavy
show_distribution_status_reactive = solara.reactive(True)
show_breeding_sites_reactive = solara.reactive(False)  # From map DETAILED PLAN

# --- Map Interaction State ---
# For info panel when a feature (polygon, marker) is clicked
selected_map_feature_info = solara.reactive(None)
# To fetch data for current view, or trigger other actions on map move
current_map_bounds_reactive = solara.reactive(None)  # ((south, west), (north, east))
current_map_zoom_reactive = solara.reactive(None)

# --- Data States ---
# These would be populated by API calls. GeoJSON is a common format.
distribution_data_reactive = solara.reactive(None)  # GeoJSON dictionary
observations_data_reactive = solara.reactive(None)  # GeoJSON dictionary
modeled_data_reactive = solara.reactive(None)  # GeoJSON for heatmap/contours
breeding_sites_data_reactive = solara.reactive(None)  # GeoJSON for breeding sites


all_available_species_reactive = solara.reactive(cast(List[str], []))  # Start empty
all_available_regions_reactive = solara.reactive(cast(List[str], []))  # Start empty
all_available_data_sources_reactive = solara.reactive(cast(List[str], []))  # Start empty
# --- Reactive States for Species Database Page ---
species_list_data_reactive = solara.reactive(cast(List[Dict[str, Any]], []))
species_list_loading_reactive = solara.reactive(False)
species_list_error_reactive = solara.reactive(cast(Optional[str], None))

filter_options_loading_reactive = solara.reactive(False)
filter_options_error_reactive = solara.reactive(cast(Optional[str], None))

# --- Reactive States for Disease Database Page ---
selected_disease_item_id = solara.reactive(None)
disease_list_data_reactive = solara.reactive(cast(List[Dict[str, Any]], []))
disease_list_loading_reactive = solara.reactive(False)
disease_list_error_reactive = solara.reactive(cast(Optional[str], None))

async def fetch_filter_options():
    """Fetches species, regions, and data sources for filter dropdowns."""
    if filter_options_loading_reactive.value:
        return
    filter_options_loading_reactive.value = True
    filter_options_error_reactive.value = None
    try:
        async with httpx.AsyncClient() as client:
            print(f"Fetching filter options from {FILTER_OPTIONS_ENDPOINT}")  # Debug
            response = await client.get(FILTER_OPTIONS_ENDPOINT, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            # Ensure keys exist in the response before assigning
            all_available_species_reactive.value = data.get("species", [])
            all_available_regions_reactive.value = data.get("regions", [])
            all_available_data_sources_reactive.value = data.get("data_sources", [])
            print(
                f"Filter options loaded: {len(all_available_species_reactive.value)} species, "
                f"{len(all_available_regions_reactive.value)} regions, "
                f"{len(all_available_data_sources_reactive.value)} sources."
            )

    except httpx.HTTPStatusError as e:
        err_msg = f"HTTP error fetching filter options: {e.response.status_code} - {e.response.text}"
        print(err_msg)
        filter_options_error_reactive.value = err_msg
        # Keep existing (empty) lists or set them to empty on error
        all_available_species_reactive.value = []
        all_available_regions_reactive.value = []
        all_available_data_sources_reactive.value = []
    except Exception as e:
        err_msg = f"Error fetching filter options: {e}"
        print(err_msg)
        filter_options_error_reactive.value = err_msg
        all_available_species_reactive.value = []
        all_available_regions_reactive.value = []
        all_available_data_sources_reactive.value = []
    finally:
        filter_options_loading_reactive.value = False

distribution_loading_reactive = solara.reactive(False)
observations_loading_reactive = solara.reactive(False)
modeled_loading_reactive = solara.reactive(False)
breeding_sites_loading_reactive = solara.reactive(False)
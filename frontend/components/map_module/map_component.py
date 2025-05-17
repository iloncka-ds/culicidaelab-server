import solara
import solara.lab  # Import solara.lab
from solara.alias import rv
import ipyleaflet as L
from ipywidgets import HTML
import json
import httpx
import asyncio
from typing import Dict, Any, Optional, List, Tuple

# Relative imports for a package structure
from frontend.state import (
    selected_species_reactive,
    show_observed_data_reactive,
    selected_map_feature_info,
    current_map_bounds_reactive,
    current_map_zoom_reactive,
    observations_data_reactive,
    observations_loading_reactive,
)
from frontend.config import (
    DEFAULT_MAP_CENTER,
    DEFAULT_MAP_ZOOM,
    SPECIES_COLORS,
    OBSERVATIONS_ENDPOINT,
    API_BASE_URL,
)


# --- Helper function to fetch data (example) ---
async def fetch_geojson_data(
    url: str, params: dict, loading_reactive: solara.Reactive[bool]
) -> Optional[Dict[str, Any]]:
    loading_reactive.value = True
    print(f"[DEBUG] fetch_geojson_data called for {url}")
    try:
        async with httpx.AsyncClient() as client:
            print(f"[DEBUG] Fetching data from {url} with params {params}")
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            print(f"[DEBUG] Successfully fetched data from {url}")
            return response.json()
    except httpx.ReadTimeout:
        solara.Error(f"Timeout fetching data from {url}. Please try again or check network.")
        print(f"[DEBUG] Timeout fetching data from {url}")
        return None
    except httpx.HTTPStatusError as e:
        error_message = f"HTTP error {e.response.status_code} from {url}."
        try:
            error_detail = e.response.json().get("detail", "No additional details.")
            error_message += f" Detail: {error_detail}"
        except:  # response might not be json
            pass
        solara.Error(error_message)
        print(f"[DEBUG] {error_message}")
        return None
    except json.JSONDecodeError:
        solara.Error(f"Invalid JSON response from {url}.")
        print(f"[DEBUG] Invalid JSON response from {url}")
        import traceback

        print(f"[DEBUG] JSON decode error details: {traceback.format_exc()}")
        return None
    except Exception as e:
        solara.Error(f"Failed to fetch data from {url}: {e}")
        print(f"[DEBUG] Error fetching data from {url}: {e}")
        import traceback

        print(f"[DEBUG] Exception details: {traceback.format_exc()}")
        return None
    finally:
        loading_reactive.value = False
        print(f"[DEBUG] fetch_geojson_data completed for {url}")


class LeafletMapManager:
    def __init__(self):
        print("[DEBUG] LeafletMapManager initializing")
        self.map_instance = L.Map(
            center=DEFAULT_MAP_CENTER, zoom=DEFAULT_MAP_ZOOM, scroll_wheel_zoom=True, prefer_canvas=True
        )
        osm_layer = L.TileLayer(
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            name="OpenStreetMap",
            attribution="© OpenStreetMap contributors",
        )
        self.map_instance.add_layer(osm_layer)
        self.observations_layer_group = L.LayerGroup(name="Observation Layers", layers=[])
        self.observations_layer_group.name = "Observations"
        self.map_instance.add_layer(self.observations_layer_group)
        self.layers_control = L.LayersControl(position="topright")
        self.map_instance.add_control(self.layers_control)
        self.map_instance.add_control(L.ScaleControl(position="bottomleft"))
        self.map_instance.add_control(L.FullScreenControl())
        self.map_instance.observe(self._handle_map_bounds_change, names=["bounds"])
        self.map_instance.observe(self._handle_map_zoom_change, names=["zoom"])

    def _handle_map_bounds_change(self, change):
        print("[DEBUG] Map bounds changed")
        if change["name"] == "bounds" and change["new"]:
            current_map_bounds_reactive.value = change["new"]

    def _handle_map_zoom_change(self, change):
        print(f"[DEBUG] Map zoom changed to {self.map_instance.zoom}")
        if change["name"] == "zoom" and change["new"]:
            current_map_zoom_reactive.value = int(change["new"])

    def _create_popup_html(self, props: Dict[str, Any], title_key: str = "name") -> str:
        title = props.get(title_key, "Details")
        html_content = f"<h4>{title}</h4><hr style='margin: 2px 0;'>"
        for key, value in props.items():
            if key.lower() not in ["geometry", title_key.lower(), "style"] and value is not None:
                html_content += f"<p style='margin: 1px 0; font-size: 0.9em;'><strong>{key.replace('_', ' ').title()}:</strong> {value}</p>"
        return html_content

    def _get_species_color(self, species_name: Optional[str]) -> str:
        return SPECIES_COLORS.get(species_name, "rgba(128,128,128,0.7)")

    def update_observations_layer(self, observations_json: Optional[Dict[str, Any]]) -> None:
        print(f"[DEBUG] update_observations_layer called with data: {observations_json is not None}")
        self.observations_layer_group.clear_layers()

        if not observations_json or not observations_json.get("features") or not show_observed_data_reactive.value:
            return

        markers = []
        for obs in observations_json["features"]:
            props = obs["properties"]
            coords = obs["geometry"]["coordinates"]
            species = props.get("species")
            marker_color = self._get_species_color(species)
            marker = L.CircleMarker(
                location=(coords[1], coords[0]),
                radius=7,
                color=marker_color,
                fillColor=marker_color,
                fill_opacity=0.8,
                weight=1,
                name=str(species) if species else "Observation",
            )
            marker.popup = HTML(self._create_popup_html(props, title_key="species"))
            marker.on_click(lambda p_captured=props, **event_kwargs: selected_map_feature_info.set(p_captured))
            markers.append(marker)

        if markers:
            marker_cluster = L.MarkerCluster(markers=markers, name="Observations Cluster")
            self.observations_layer_group.add_layer(marker_cluster)

    def get_widget(self):
        return self.map_instance


@solara.component
def MapDisplay():
    print("[DEBUG] MapDisplay component initializing")
    map_manager = solara.use_memo(LeafletMapManager, [])

    async def load_observations_data_task():
        # This function is now the task body for solara.lab.use_task
        print("[DEBUG] load_observations_data_task called")

        # Guard: Only proceed if the layer is visible
        if not show_observed_data_reactive.value:
            print("[DEBUG] Observations layer not visible, clearing data and skipping fetch.")
            observations_data_reactive.value = None
            observations_loading_reactive.value = False  # Ensure loading is false
            return

        species_list = selected_species_reactive.value
        if not species_list:
            print("[DEBUG] No species selected, clearing observations data.")
            observations_data_reactive.value = None
            observations_loading_reactive.value = False  # Ensure loading is false
            return

        params = {"species": ",".join(species_list)}

        print("[DEBUG] Adding observations data fetch task")
        # The fetch_geojson_data function handles setting loading_reactive
        data = await fetch_geojson_data(OBSERVATIONS_ENDPOINT, params, observations_loading_reactive)

        if data is not None:
            print("[DEBUG] Setting observations data from fetch result")
            observations_data_reactive.value = data
        else:
            # If fetch failed, data is None. Ensure reactive data is also None or empty.
            print("[DEBUG] Fetch returned None, ensuring observations_data_reactive is None.")
            observations_data_reactive.value = None  # Or an empty GeoJSON structure as fallback

    # Use solara.lab.use_task to run load_observations_data_task when dependencies change.
    # It handles cancellation on unmount or if dependencies change again before completion.
    solara.lab.use_task(
        load_observations_data_task,
        dependencies=[
            selected_species_reactive.value,  # Trigger on species change
            show_observed_data_reactive.value,  # Trigger on visibility change
            # current_map_bounds_reactive.value, # If API supports bbox and auto-reload on pan/zoom
        ],
    )

    # Effect to update map layers when data or visibility changes (visibility primarily for clearing)
    def _update_map_layers_effect():
        print("[DEBUG] _update_map_layers_effect called")
        print(f"[DEBUG] Updating layers with data - Observations: {observations_data_reactive.value is not None}")
        map_manager.update_observations_layer(observations_data_reactive.value)

    solara.use_effect(
        _update_map_layers_effect,
        [
            observations_data_reactive.value,  # When data changes
            show_observed_data_reactive.value,  # When visibility changes (to clear layer if hidden)
        ],
    )

    with solara.Div(style={"height": "100%", "width": "100%"}):
        solara.display(map_manager.get_widget())

import solara
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
    show_modeled_data_reactive,
    show_distribution_status_reactive,
    show_breeding_sites_reactive,  # Added from map DETAILED PLAN
    selected_map_feature_info,
    current_map_bounds_reactive,
    current_map_zoom_reactive,  # Added
    distribution_data_reactive,
    observations_data_reactive,
    modeled_data_reactive,
    breeding_sites_data_reactive,  # Added
    # data_loading_reactive,
    distribution_loading_reactive,  # Granular loading
    observations_loading_reactive,
    modeled_loading_reactive,
    breeding_sites_loading_reactive,
)
from frontend.config import (
    DEFAULT_MAP_CENTER,
    DEFAULT_MAP_ZOOM,
    DISTRIBUTION_STATUS_COLORS,
    SPECIES_COLORS,
    SPECIES_DISTRIBUTION_ENDPOINT,
    OBSERVATIONS_ENDPOINT,
    MODELED_PROBABILITY_ENDPOINT,
    BREEDING_SITES_ENDPOINT,
    API_BASE_URL,  # Assuming breeding sites endpoint follows pattern
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
        # Base layer
        osm_layer = L.TileLayer(
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            name="OpenStreetMap",
            attribution="© OpenStreetMap contributors",
        )
        self.map_instance.add_layer(osm_layer)

        # Layer groups for toggling individual layers
        self.distribution_layer_group = L.LayerGroup(name="Distribution Status Layers", layers=[])
        self.observations_layer_group = L.LayerGroup(name="Observation Layers", layers=[])
        self.modeled_layer_group = L.LayerGroup(name="Modeled Probability Layers", layers=[])
        self.breeding_sites_layer_group = L.LayerGroup(name="Breeding Site Layers", layers=[])  # Added

        self.distribution_layer_group.name = "Distribution Status"
        self.observations_layer_group.name = "Observations"
        self.modeled_layer_group.name = "Modeled Probability"
        self.breeding_sites_layer_group.name = "Breeding Sites"
        # Add layer groups to the map - they start empty
        self.map_instance.add_layer(self.distribution_layer_group)
        self.map_instance.add_layer(self.observations_layer_group)
        self.map_instance.add_layer(self.modeled_layer_group)
        self.map_instance.add_layer(self.breeding_sites_layer_group)

        # Layers control to toggle visibility of named layers/groups
        self.layers_control = L.LayersControl(position="topright")
        self.map_instance.add_control(self.layers_control)
        self.map_instance.add_control(L.ScaleControl(position="bottomleft"))
        self.map_instance.add_control(L.FullScreenControl())

        # Observe map interactions
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
        print("[DEBUG] Creating popup HTML")
        title = props.get(title_key, "Details")
        html_content = f"<h4>{title}</h4><hr style='margin: 2px 0;'>"
        for key, value in props.items():
            if key.lower() not in ["geometry", title_key.lower(), "style"] and value is not None:  # Simple filter
                html_content += f"<p style='margin: 1px 0; font-size: 0.9em;'><strong>{key.replace('_', ' ').title()}:</strong> {value}</p>"
        return html_content

    def _get_species_color(self, species_name: Optional[str]) -> str:
        print(f"[DEBUG] Getting species color for {species_name}")
        return SPECIES_COLORS.get(species_name, "rgba(128,128,128,0.7)")  # Default grey for unknown

    def update_distribution_layer(self, geojson_data: Optional[Dict[str, Any]]) -> None:
        print(f"[DEBUG] update_distribution_layer called with data: {geojson_data is not None}")
        # Clear existing layer
        for layer in list(self.distribution_layer_group.layers):
            self.distribution_layer_group.remove_layer(layer)

        if not geojson_data or not geojson_data.get("features") or not show_distribution_status_reactive.value:
            return

        def stylefunction(feature):
            status = feature["properties"].get("distribution_status", "unknown")
            return {
                "fillColor": DISTRIBUTION_STATUS_COLORS.get(status, DISTRIBUTION_STATUS_COLORS["unknown"]),
                "color": "black",
                "weight": 1,
                "fillOpacity": 0.65,
            }

        def on_each_feature(feature, layer):
            props = feature["properties"]
            layer.on_click(lambda **kwargs: selected_map_feature_info.set(props))
            layer.popup = HTML(self._create_popup_html(props, title_key="name"))  # 'name' often refers to region

        dist_layer = L.GeoJSON(
            data=geojson_data,
            name="Distribution Status",
            stylecallback=stylefunction,
            hover_style={"fillOpacity": 0.8, "weight": 2},
            on_each_feature=on_each_feature,
        )
        self.distribution_layer_group.add_layer(dist_layer)
        # self.layers_control.add_layer(dist_layer) # Add to map's layer control

    def update_observations_layer(self, observations_json: Optional[Dict[str, Any]]) -> None:
        print(f"[DEBUG] update_observations_layer called with data: {observations_json is not None}")
        # Clear existing layers
        for layer in list(self.observations_layer_group.layers):
            self.observations_layer_group.remove_layer(layer)

        if not observations_json or not observations_json.get("features") or not show_observed_data_reactive.value:
            return

        markers = []
        for obs in observations_json["features"]:
            props = obs["properties"]
            coords = obs["geometry"]["coordinates"]  # [lon, lat]
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
            # Fix: Add event parameter to lambda and ignore it
            marker.on_click(lambda event, p=props: selected_map_feature_info.set(p))  # Handle event parameter
            markers.append(marker)

        if markers:
            marker_cluster = L.MarkerCluster(markers=markers, name="Observations Cluster")
            self.observations_layer_group.add_layer(marker_cluster)
            # self.layers_control.add_layer(marker_cluster)

    def update_modeled_layer(self, geojson_data: Optional[Dict[str, Any]]) -> None:
        print(f"[DEBUG] update_modeled_layer called with data: {geojson_data is not None}")
        # Clear existing layer
        for layer in list(self.modeled_layer_group.layers):
            self.modeled_layer_group.remove_layer(layer)

        if not geojson_data or not geojson_data.get("features") or not show_modeled_data_reactive.value:
            return

        # Assuming GeoJSON with 'probability' property for styling
        def stylefunction(feature):
            prob = feature["properties"].get("probability", 0)  # 0 to 1
            # Viridis colormap: (blue to yellow)
            # Simplified: dark blue (low prob) to yellow (high prob)
            # This should ideally use a proper colormap library or predefined scale
            r = int(255 * prob)  # More red/yellow for higher prob
            g = int(255 * prob)  # More green/yellow for higher prob
            b = int(255 * (1 - prob))  # More blue for lower prob
            return {"fillColor": f"rgb({r},{g},{b})", "color": "transparent", "weight": 0, "fillOpacity": 0.6}

        modeled_layer = L.GeoJSON(
            data=geojson_data,
            name="Modeled Probability",
            stylecallback=stylefunction,
            # Add on_each_feature for popups if needed
        )
        self.modeled_layer_group.add_layer(modeled_layer)
        # self.layers_control.add_layer(modeled_layer)

    def update_breeding_sites_layer(self, geojson_data: Optional[Dict[str, Any]]) -> None:
        print(f"[DEBUG] update_breeding_sites_layer called with data: {geojson_data is not None}")
        # Clear existing layers
        for layer in list(self.breeding_sites_layer_group.layers):
            self.breeding_sites_layer_group.remove_layer(layer)

        if not geojson_data or not geojson_data.get("features") or not show_breeding_sites_reactive.value:
            return

        markers = []
        for site in geojson_data["features"]:
            props = site["properties"]
            coords = site["geometry"]["coordinates"]
            site_type = props.get("site_type", "unknown").lower()

            # Example custom icons (requires serving static assets or using data URLs)
            # Or use different CircleMarker colors based on site_type
            marker_color = "purple"  # Default
            if "stormdrain" in site_type and "water" in site_type:
                marker_color = "blue"
            elif "stormdrain" in site_type:
                marker_color = "grey"
            elif "container" in site_type:
                marker_color = "orange"

            marker = L.CircleMarker(
                location=(coords[1], coords[0]),
                radius=5,
                color=marker_color,
                fillColor=marker_color,
                fill_opacity=0.7,
                weight=1,
                name=props.get("name", "Breeding Site"),
            )
            marker.popup = HTML(self._create_popup_html(props, title_key="site_type"))
            marker.on_click(lambda p=props: selected_map_feature_info.set(p))
            markers.append(marker)

        if markers:
            site_cluster = L.MarkerCluster(markers=markers, name="Breeding Sites")
            self.breeding_sites_layer_group.add_layer(site_cluster)
            # self.layers_control.add_layer(site_cluster)

    def get_widget(self):
        return self.map_instance


@solara.component
def MapDisplay():
    print("[DEBUG] MapDisplay component initializing")
    # Create a new map manager instance
    map_manager = solara.use_memo(LeafletMapManager, [])

    async def load_all_data():
        print("[DEBUG] load_all_data called")
        # Reset loading state
        # data_loading_reactive.value = True
        distribution_loading_reactive.value = show_distribution_status_reactive.value
        observations_loading_reactive.value = show_observed_data_reactive.value
        modeled_loading_reactive.value = show_modeled_data_reactive.value
        breeding_sites_loading_reactive.value = show_breeding_sites_reactive.value

        print(f"[DEBUG] Layer visibility - Distribution: {show_distribution_status_reactive.value}, Observations: {show_observed_data_reactive.value}, Modeled: {show_modeled_data_reactive.value}, Breeding Sites: {show_breeding_sites_reactive.value}")

        species_list = selected_species_reactive.value
        if not species_list:  # Only load if species are selected
            distribution_data_reactive.value = None
            observations_data_reactive.value = None
            modeled_data_reactive.value = None
            breeding_sites_data_reactive.value = None
            # data_loading_reactive.value = False
            return

        params = {"species": ",".join(species_list)}
        # Add other params like date_range, bbox if your API supports them
        # if current_map_bounds_reactive.value:
        #    bounds = current_map_bounds_reactive.value
        #    params["bbox"] = f"{bounds[0][1]},{bounds[0][0]},{bounds[1][1]},{bounds[1][0]}" # W,S,E,N

        tasks = []
        print("[DEBUG] Creating data fetch tasks for enabled layers")

        if show_distribution_status_reactive.value:
            print("[DEBUG] Adding distribution data fetch task")
            tasks.append(fetch_geojson_data(SPECIES_DISTRIBUTION_ENDPOINT, params, distribution_loading_reactive))
        else:
            print("[DEBUG] Distribution layer disabled, skipping fetch")
            distribution_data_reactive.value = None
            tasks.append(asyncio.sleep(0, result=None))

        if show_observed_data_reactive.value:
            print("[DEBUG] Adding observations data fetch task")
            tasks.append(fetch_geojson_data(OBSERVATIONS_ENDPOINT, params, observations_loading_reactive))
        else:
            print("[DEBUG] Observations layer disabled, skipping fetch")
            observations_data_reactive.value = None
            tasks.append(asyncio.sleep(0, result=None))

        if show_modeled_data_reactive.value:
            print("[DEBUG] Adding modeled data fetch task")
            tasks.append(fetch_geojson_data(MODELED_PROBABILITY_ENDPOINT, params, modeled_loading_reactive))
        else:
            print("[DEBUG] Modeled layer disabled, skipping fetch")
            modeled_data_reactive.value = None
            tasks.append(asyncio.sleep(0, result=None))

        if show_breeding_sites_reactive.value:  # Added
            print("[DEBUG] Adding breeding sites data fetch task")
            tasks.append(fetch_geojson_data(BREEDING_SITES_ENDPOINT, params, breeding_sites_loading_reactive))
        else:
            print("[DEBUG] Breeding sites layer disabled, skipping fetch")
            breeding_sites_data_reactive.value = None
            tasks.append(asyncio.sleep(0, result=None))

        print("[DEBUG] Awaiting all fetch tasks to complete")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        print("[DEBUG] All fetch tasks completed")

        # Assign results, checking for exceptions
        if show_distribution_status_reactive.value and not isinstance(results[0], Exception):
            print("[DEBUG] Setting distribution data from fetch result")
            distribution_data_reactive.value = results[0]
        if show_observed_data_reactive.value and not isinstance(results[1], Exception):
            print("[DEBUG] Setting observations data from fetch result")
            observations_data_reactive.value = results[1]
        if show_modeled_data_reactive.value and not isinstance(results[2], Exception):
            print("[DEBUG] Setting modeled data from fetch result")
            modeled_data_reactive.value = results[2]
        if show_breeding_sites_reactive.value and not isinstance(results[3], Exception):  # Added
            print("[DEBUG] Setting breeding sites data from fetch result")
            breeding_sites_data_reactive.value = results[3]

        for i, res in enumerate(results):  # Log any exceptions from gather
            if isinstance(res, Exception):
                print(f"[DEBUG] Error in fetch task {i}: {res}")
                import traceback
                print(f"[DEBUG] Task {i} error details: {traceback.format_exc()}")

        # data_loading_reactive.value = False

    # Effect to trigger data loading
    def _trigger_load_data_effect():
        print("[DEBUG] _trigger_load_data_effect called")
        asyncio.create_task(load_all_data())

    # Re-fetch data when filters or layer visibility relevant to fetching change
    solara.use_effect(
        _trigger_load_data_effect,
        [
            selected_species_reactive.value,
            # current_map_bounds_reactive.value, # If API supports bbox filtering & want to reload on pan/zoom
            show_distribution_status_reactive.value,
            show_observed_data_reactive.value,
            show_modeled_data_reactive.value,
            show_breeding_sites_reactive.value,
        ],
    )

    # Effect to update map layers when data or visibility changes
    def _update_map_layers_effect():
        print("[DEBUG] _update_map_layers_effect called")
        print(f"[DEBUG] Updating layers with data - Distribution: {distribution_data_reactive.value is not None}, Observations: {observations_data_reactive.value is not None}, Modeled: {modeled_data_reactive.value is not None}, Breeding Sites: {breeding_sites_data_reactive.value is not None}")
        map_manager.update_distribution_layer(distribution_data_reactive.value)
        map_manager.update_observations_layer(observations_data_reactive.value)
        map_manager.update_modeled_layer(modeled_data_reactive.value)
        map_manager.update_breeding_sites_layer(breeding_sites_data_reactive.value)  # Added

    solara.use_effect(
        _update_map_layers_effect,
        [
            distribution_data_reactive.value,
            observations_data_reactive.value,
            modeled_data_reactive.value,
            breeding_sites_data_reactive.value,  # Added
            # Visibility toggles are handled in load_all_data for fetching,
            # and by layer update functions checking visibility before adding.
            # Explicitly adding them here ensures re-render if data exists but visibility changed.
            show_distribution_status_reactive.value,
            show_observed_data_reactive.value,
            show_modeled_data_reactive.value,
            show_breeding_sites_reactive.value,
        ],
    )

    # This Div needs to ensure the map widget can take full height and width
    # The parent Column in map_visualization.py is set to height: 100%
    # This Div should also be height: 100%
    with solara.Div(style={"height": "100%", "width": "100%"}):
        solara.display(map_manager.get_widget())

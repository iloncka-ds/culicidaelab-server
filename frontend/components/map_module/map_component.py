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
    try:
        async with httpx.AsyncClient() as client:
            print(f"Fetching data from {url} with params {params}")  # Debug
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            print(f"Successfully fetched data from {url}")  # Debug
            return response.json()
    except httpx.ReadTimeout:
        solara.Error(f"Timeout fetching data from {url}. Please try again or check network.")
        print(f"Timeout fetching data from {url}")
        return None
    except httpx.HTTPStatusError as e:
        error_message = f"HTTP error {e.response.status_code} from {url}."
        try:
            error_detail = e.response.json().get("detail", "No additional details.")
            error_message += f" Detail: {error_detail}"
        except:  # response might not be json
            pass
        solara.Error(error_message)
        print(error_message)
        return None
    except json.JSONDecodeError:
        solara.Error(f"Invalid JSON response from {url}.")
        print(f"Invalid JSON response from {url}")
        return None
    except Exception as e:
        solara.Error(f"Failed to fetch data from {url}: {e}")
        print(f"Error fetching data from {url}: {e}")
        return None
    finally:
        loading_reactive.value = False


class LeafletMapManager:
    def __init__(self):
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
        if change["name"] == "bounds" and change["new"]:
            current_map_bounds_reactive.value = change["new"]

    def _handle_map_zoom_change(self, change):
        if change["name"] == "zoom" and change["new"]:
            current_map_zoom_reactive.value = int(change["new"])

    def _create_popup_html(self, props: Dict[str, Any], title_key: str = "name") -> str:
        title = props.get(title_key, "Details")
        html_content = f"<h4>{title}</h4><hr style='margin: 2px 0;'>"
        for key, value in props.items():
            if key.lower() not in ["geometry", title_key.lower(), "style"] and value is not None:  # Simple filter
                html_content += f"<p style='margin: 1px 0; font-size: 0.9em;'><strong>{key.replace('_', ' ').title()}:</strong> {value}</p>"
        return html_content

    def _get_species_color(self, species_name: Optional[str]) -> str:
        return SPECIES_COLORS.get(species_name, "rgba(128,128,128,0.7)")  # Default grey for unknown

    def update_distribution_layer(self, geojson_data: Optional[Dict[str, Any]]):
        self.distribution_layer_group.clear_layers()
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

    def update_observations_layer(self, observations_json: Optional[Dict[str, Any]]):
        self.observations_layer_group.clear_layers()
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
            marker.on_click(lambda p=props: selected_map_feature_info.set(p))  # Capture props correctly in lambda
            markers.append(marker)

        if markers:
            marker_cluster = L.MarkerCluster(markers=markers, name="Observations Cluster")
            self.observations_layer_group.add_layer(marker_cluster)
            # self.layers_control.add_layer(marker_cluster)

    def update_modeled_layer(self, geojson_data: Optional[Dict[str, Any]]):
        self.modeled_layer_group.clear_layers()
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

    def update_breeding_sites_layer(self, geojson_data: Optional[Dict[str, Any]]):  # Added
        self.breeding_sites_layer_group.clear_layers()
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
    map_manager = solara.use_memo(LeafletMapManager, [])

    async def load_all_data():
        # This function will be called by the effect
        # It will launch multiple async fetch operations
        # This uses the global data_loading_reactive. Could use specific ones.
        global_any_data_loading = (
            distribution_loading_reactive.value
            or observations_loading_reactive.value
            or modeled_loading_reactive.value
            or breeding_sites_loading_reactive.value
        )
        if global_any_data_loading:  # Prevent re-triggering if already loading
            return

        # data_loading_reactive.value = True # Set a general loading flag

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
        if show_distribution_status_reactive.value:
            tasks.append(fetch_geojson_data(SPECIES_DISTRIBUTION_ENDPOINT, params, distribution_loading_reactive))
        else:
            distribution_data_reactive.value = None  # Clear if not shown
            tasks.append(asyncio.sleep(0, result=None))  # Placeholder for gather

        if show_observed_data_reactive.value:
            tasks.append(fetch_geojson_data(OBSERVATIONS_ENDPOINT, params, observations_loading_reactive))
        else:
            observations_data_reactive.value = None
            tasks.append(asyncio.sleep(0, result=None))

        if show_modeled_data_reactive.value:
            tasks.append(fetch_geojson_data(MODELED_PROBABILITY_ENDPOINT, params, modeled_loading_reactive))
        else:
            modeled_data_reactive.value = None
            tasks.append(asyncio.sleep(0, result=None))

        if show_breeding_sites_reactive.value:  # Added
            tasks.append(fetch_geojson_data(BREEDING_SITES_ENDPOINT, params, breeding_sites_loading_reactive))
        else:
            breeding_sites_data_reactive.value = None
            tasks.append(asyncio.sleep(0, result=None))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Assign results, checking for exceptions
        if show_distribution_status_reactive.value and not isinstance(results[0], Exception):
            distribution_data_reactive.value = results[0]
        if show_observed_data_reactive.value and not isinstance(results[1], Exception):
            observations_data_reactive.value = results[1]
        if show_modeled_data_reactive.value and not isinstance(results[2], Exception):
            modeled_data_reactive.value = results[2]
        if show_breeding_sites_reactive.value and not isinstance(results[3], Exception):  # Added
            breeding_sites_data_reactive.value = results[3]

        for i, res in enumerate(results):  # Log any exceptions from gather
            if isinstance(res, Exception):
                print(f"Error in task {i}: {res}")

        # data_loading_reactive.value = False

    # Effect to trigger data loading
    def _trigger_load_data_effect():
        # solara.lab.use_task or asyncio.create_task for async operations from effects
        # This ensures the effect itself remains synchronous
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

import solara
import solara.lab
from solara.alias import rv
import ipyleaflet as L
from ipywidgets import HTML
import json
import httpx
import asyncio
from typing import Dict, Any, Optional, List, Tuple

from frontend.state import (
    selected_species_reactive,
    show_observed_data_reactive,
    selected_map_feature_info,
    current_map_bounds_reactive,
    current_map_zoom_reactive,
    observations_data_reactive,
    observations_loading_reactive,
    selected_date_range_reactive,
)
from frontend.config import (
    DEFAULT_MAP_CENTER,
    DEFAULT_MAP_ZOOM,
    SPECIES_COLORS,
    OBSERVATIONS_ENDPOINT,
    API_BASE_URL,
    generate_species_colors,

)
from frontend.state import all_available_species_reactive, observations_loading_reactive

async def fetch_geojson_data(
    url: str, params: dict, loading_reactive: solara.Reactive[bool]
) -> Optional[Dict[str, Any]]:
    loading_reactive.value = True
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except httpx.ReadTimeout:
        solara.Error(f"Timeout fetching data from {url}. Please try again or check network.")
        return None
    except httpx.HTTPStatusError as e:
        error_message = f"HTTP error {e.response.status_code} from {url}."
        try:
            error_detail = e.response.json().get("detail", "No additional details.")
            error_message += f" Detail: {error_detail}"
        except:
            pass
        solara.Error(error_message)
        return None
    except json.JSONDecodeError:
        solara.Error(f"Invalid JSON response from {url}.")
        return None
    except Exception as e:
        solara.Error(f"Failed to fetch data from {url}: {e}")
        return None
    finally:
        loading_reactive.value = False


class LeafletMapManager:
    def __init__(self):
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

        self.species_color_map = SPECIES_COLORS.copy()
        if all_available_species_reactive.value:
            self.species_color_map = generate_species_colors(all_available_species_reactive.value)

    def _handle_map_bounds_change(self, change):
        if change["name"] == "bounds" and change["new"]:
            new_bounds = change["new"]
            if (
                isinstance(new_bounds, tuple)
                and len(new_bounds) == 2
                and isinstance(new_bounds[0], tuple)
                and len(new_bounds[0]) == 2
                and isinstance(new_bounds[1], tuple)
                and len(new_bounds[1]) == 2
                and all(isinstance(coord, (float, int)) for point in new_bounds for coord in point)
            ):
                current_map_bounds_reactive.value = new_bounds
            else:
                print(f"[WARN] Invalid map bounds received: {new_bounds}. Not updating reactive state.")

    def _handle_map_zoom_change(self, change):
        if change["name"] == "zoom" and change["new"]:
            current_map_zoom_reactive.value = int(change["new"])

    def _create_popup_html(self, props: Dict[str, Any], title_key: str = "name") -> str:
        title = props.get(title_key, "Details")
        html_content = f"<h4>{title}</h4><hr style='margin: 2px 0;'>"
        for key, value in props.items():
            if key.lower() not in [
                "geometry",
                title_key.lower(),
                "style", "observer_id",
                "location_accuracy_m"
                ] and value is not None:
                display_key = key.replace("_", " ").title()
                html_content += (
                    f"<p style='margin: 1px 0; font-size: 0.9em;'><strong>{display_key}:</strong> {value}</p>"
                )
        return html_content

    def _get_species_color(self, species_name: Optional[str]) -> str:
        if all_available_species_reactive.value:
            self.species_color_map = generate_species_colors(all_available_species_reactive.value)

        return self.species_color_map.get(species_name, "rgba(128,128,128,0.7)")

    def update_observations_layer(self, observations_json: Optional[Dict[str, Any]]) -> None:
        self.observations_layer_group.clear_layers()

        if not observations_json or not observations_json.get("features") or not show_observed_data_reactive.value:
            return

        markers = []
        for obs in observations_json["features"]:
            props = obs.get("properties", {})
            geometry = obs.get("geometry", {})
            if not geometry or geometry.get("type") != "Point" or not geometry.get("coordinates"):
                continue

            coords = geometry["coordinates"]
            species = props.get("species")
            marker_color = self._get_species_color(species)

            marker = L.CircleMarker(
                location=(coords[1], coords[0]),
                radius=7,
                color=marker_color,
                fill_color=marker_color,
                fill_opacity=0.8,
                weight=1,
                name=str(species) if species else "Observation",
            )
            popup_html = self._create_popup_html(props, title_key="species")
            marker.popup = HTML(popup_html)

            def on_marker_click(p_captured=props, **event_kwargs):
                selected_map_feature_info.set(p_captured)

            marker.on_click(on_marker_click)
            markers.append(marker)

        if markers:
            marker_cluster = L.MarkerCluster(markers=markers, name="Observations")
            self.observations_layer_group.add_layer(marker_cluster)

    def get_widget(self):
        return self.map_instance


@solara.component
def MapDisplay():
    map_manager = solara.use_memo(
        LeafletMapManager, [all_available_species_reactive.value]
    )

    async def load_observations_data_task():
        if not show_observed_data_reactive.value:
            observations_data_reactive.value = None
            observations_loading_reactive.value = False
            return

        species_list = selected_species_reactive.value
        if not species_list:
            observations_data_reactive.value = None
            observations_loading_reactive.value = False
            return

        params = {"species": ",".join(species_list)}

        s_date_obj, e_date_obj = selected_date_range_reactive.value
        if s_date_obj:
            params["start_date"] = s_date_obj.strftime("%Y-%m-%d")
        if e_date_obj:
            params["end_date"] = e_date_obj.strftime("%Y-%m-%d")


        data = await fetch_geojson_data(OBSERVATIONS_ENDPOINT, params, observations_loading_reactive)
        if data is not None:
            observations_data_reactive.value = data
        else:
            observations_data_reactive.value = None

    solara.lab.use_task(
        load_observations_data_task,
        dependencies=[
            selected_species_reactive.value,
            show_observed_data_reactive.value,
            selected_date_range_reactive.value,
        ],
    )

    def _update_map_layers_effect():
        map_manager.update_observations_layer(observations_data_reactive.value)

    solara.use_effect(
        _update_map_layers_effect,
        [
            observations_data_reactive.value,
            show_observed_data_reactive.value,
            all_available_species_reactive.value,
        ],
    )

    with solara.Div(style={"height": "100%", "width": "100%"}):
        solara.display(map_manager.get_widget())

import solara
import ipyleaflet as L
from typing import Optional, cast

from collections.abc import Callable
from frontend.state import use_locale_effect
import i18n


@solara.component
def LocationComponent(
    latitude: float | None,
    set_latitude: Callable[[float | None], None],
    longitude: float | None,
    set_longitude: Callable[[float | None], None],
    initial_lat: float | None = 20.0,
    initial_lon: float | None = 0.0,
    initial_zoom: int = 2,
):
    """
    An interactive map component for selecting and displaying geographic coordinates.

    This component functions as a controlled input for latitude and longitude.
    Users can select a location by clicking on the map, dragging a marker, or
    manually entering coordinate values in the input fields. The component's
    state is synchronized with a parent component through the provided state
    and setter functions.

    Args:
        latitude: The current latitude to display on the map. Can be `None`.
        set_latitude: Callback function to update the latitude in the parent's state.
        longitude: The current longitude to display on the map. Can be `None`.
        set_longitude: Callback function to update the longitude in the parent's state.
        initial_lat: The initial latitude for the map's center. Defaults to 20.0.
        initial_lon: The initial longitude for the map's center. Defaults to 0.0.
        initial_zoom: The initial zoom level of the map. Defaults to 2.

    Example:
        ```python
        import solara

        @solara.component
        def Page():
            # Parent component manages the state for latitude and longitude.
            lat, set_lat = solara.use_state(None)
            lon, set_lon = solara.use_state(None)

            with solara.Column():
                solara.Text("Select a location for the observation:")
                LocationComponent(
                    latitude=lat,
                    set_latitude=set_lat,
                    longitude=lon,
                    set_longitude=set_lon
                )
                if lat is not None and lon is not None:
                    solara.Success(f"Selected: Lat={lat:.4f}, Lon={lon:.4f}")
                else:
                    solara.Info("No location selected.")
        ```
    """
    use_locale_effect()
    marker_object, set_marker_object = solara.use_state(cast(Optional[L.Marker], None))

    map_center_init = (initial_lat, initial_lon)
    map_zoom_init = initial_zoom

    map_widget = solara.use_memo(
        lambda: L.Map(
            center=map_center_init,
            zoom=map_zoom_init,
            scroll_wheel_zoom=True,
        ),
        [],
    )

    def _update_parent_coordinates(lat_val: float | None, lon_val: float | None):
        set_latitude(round(lat_val, 6) if lat_val is not None else None)
        set_longitude(round(lon_val, 6) if lon_val is not None else None)

    def _handle_marker_location_changed(change):
        if change.get("new") and marker_object:
            new_location = change["new"]
            _update_parent_coordinates(new_location[0], new_location[1])

    def _handle_map_click(**kwargs):
        if kwargs.get("type") == "click":
            coords = kwargs.get("coordinates")
            if coords:
                _update_parent_coordinates(coords[0], coords[1])

    def _create_or_update_marker(lat: float, lon: float):
        current_marker = marker_object
        if current_marker:
            if current_marker.location != (lat, lon):
                current_marker.location = (lat, lon)
        else:
            new_marker = L.Marker(
                location=(lat, lon),
                draggable=True,
                title=i18n.t("prediction.location.selected_location"),
            )
            new_marker.observe(_handle_marker_location_changed, names=["location"])
            map_widget.add_layer(new_marker)
            set_marker_object(new_marker)

        if map_widget.center != (lat, lon):
            map_widget.center = (lat, lon)
        if map_widget.zoom < 10:
            map_widget.zoom = 10

    def _remove_marker():
        current_marker = marker_object
        if current_marker:
            try:
                current_marker.unobserve(_handle_marker_location_changed, names=["location"])
                map_widget.remove_layer(current_marker)
            except Exception:
                print(i18n.t("prediction.location.error_remove_marking"))
            set_marker_object(None)

    def sync_marker_with_state_effect():
        if latitude is not None and longitude is not None:
            _create_or_update_marker(latitude, longitude)
        else:
            _remove_marker()

    solara.use_effect(sync_marker_with_state_effect, [latitude, longitude])

    solara.use_effect(
        lambda: map_widget.on_interaction(_handle_map_click)
        or (lambda: map_widget.on_interaction(_handle_map_click, remove=True)),
        [map_widget],
    )

    with solara.Column(style={"min-height": "300px"}):
        solara.Markdown(f'#### {i18n.t("prediction.location.select_location")}', style="margin-bottom: 10px;")
        with solara.Row(gap="10px", style={"align-items": "center", "margin-bottom": "10px;"}):
            solara.InputFloat(
                label=i18n.t("prediction.location.latitude"),
                value=latitude,
                on_value=lambda v: _update_parent_coordinates(v, longitude),
                continuous_update=False,
                clearable=True,
            )
            solara.InputFloat(
                label=i18n.t("prediction.location.longitude"),
                value=longitude,
                on_value=lambda v: _update_parent_coordinates(latitude, v),
                continuous_update=False,
                clearable=True,
            )

        solara.HTML(
            tag="div",
            unsafe_innerHTML="<style>.leaflet-container { height: 350px !important; width: 100%; }</style>",
        )
        solara.display(map_widget)

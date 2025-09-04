"""
Defines the main page for the map visualization feature.

This module contains a top-level page component that assembles the complete map
interface. It integrates the interactive map, filter controls, and legend into a
single, cohesive user experience.
"""

import solara

from solara.alias import rv
from typing import cast, Optional

from frontend.components.map_module import (
    map_component,
    filter_panel,
    legend_component,
)

from frontend.state import use_locale_effect

import i18n


@solara.component
def Page():
    """
    Renders the main map visualization page, including the interactive map and control panels.

    This component constructs the primary user interface for map-based data
    exploration. It features a main map display area (`MapDisplay`) and two
    collapsible expansion panels below it for user interaction:

    1.  **Filters Panel**: Contains the `FilterControls` component, allowing users
        to select species and date ranges to filter the data shown on the map.
    2.  **Legend Panel**: Contains the `LegendDisplay` component, which shows a
        visual key for the species and data layers currently active on the map.

    The state of the expansion panels (i.e., whether they are open or closed)
    is managed locally within this component. The overall layout is responsive,
    adjusting the panels for different screen sizes.

    Example:
        This component is designed to be used as a top-level page in a Solara
        application's routing setup.

        ```python
        # In your main application file (e.g., app.py)
        import solara
        from pages import map_visualization

        routes = [
            solara.Route(path="/", component=...),
            solara.Route(path="/map", component=map_visualization.Page, label="Map"),
            # ... other routes
        ]

        @solara.component
        def Layout():
            # ... your app layout ...
            # The RoutingProvider makes the '/map' path render this Page component.
            solara.RoutingProvider(routes=routes, children=[...])
        ```
    """
    use_locale_effect()

    filters_panel_value, set_filters_panel_value = solara.use_state(cast(Optional[list[int]], [0]))

    legend_panel_value, set_legend_panel_value = solara.use_state(cast(Optional[list[int]], []))

    filter_item = {
        "title": i18n.t("map.panels.filters.title"),
        "icon": "mdi-filter-variant",
        "component": filter_panel.FilterControls,
        "state_value": filters_panel_value,
        "state_setter": set_filters_panel_value,
    }
    legend_item = {
        "title": i18n.t("map.panels.legend.title"),
        "icon": "mdi-format-list-bulleted-type",
        "component": legend_component.LegendDisplay,
        "state_value": legend_panel_value,
        "state_setter": set_legend_panel_value,
    }

    map_interactive_items = [filter_item, legend_item]
    with solara.Div(style="width: 100%; flex-grow: 1; min-height: 300px; display: flex; flex-direction: column;"):
        map_component.MapDisplay()

    with solara.ColumnsResponsive(default=[12], small=[6]):
        for item_data in map_interactive_items:
            with rv.ExpansionPanels(
                value=item_data["state_value"],
                on_input=item_data["state_setter"],
            ):
                with rv.ExpansionPanel():
                    with rv.ExpansionPanelHeader():
                        if item_data["icon"]:
                            rv.Icon(children=[item_data["icon"]], left=True, class_="mr-2")
                        solara.Text(item_data["title"])
                    with rv.ExpansionPanelContent(class_="pt-2"):
                        item_data["component"]()

import solara

from solara.alias import rv
from typing import List, cast, Optional

from ..components.map_module import (
    map_component,
    filter_panel,
    legend_component,
)

from frontend.state import use_locale_effect

import i18n
from pathlib import Path


def setup_i18n():
    i18n.load_path.append(str(Path(__file__).parent.parent / "translations"))
    i18n.set("fallback", "ru")


@solara.component
def Page():

    use_locale_effect()

    filters_panel_value, set_filters_panel_value = solara.use_state(cast(Optional[List[int]], [0]))

    legend_panel_value, set_legend_panel_value = solara.use_state(cast(Optional[List[int]], []))

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
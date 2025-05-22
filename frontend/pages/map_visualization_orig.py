import solara
import solara.lab
from solara.alias import rv
from typing import List, cast, Optional

from ..components.map_module import (
    map_component,
    filter_panel,
    info_panel,
    legend_component,
    layer_control,
)
from ..state import (
    distribution_loading_reactive,
    observations_loading_reactive,
)
from ..config import COLOR_BACKGROUND
from ..config import load_themes
from frontend.components.common.locale_selector import LocaleSelector
import i18n


@solara.component
def Page():
    with solara.AppBar():
        solara.v.Spacer()
        LocaleSelector()
    with solara.AppBarTitle():
        solara.Text(i18n.t("map.app_title"), style="font-size: 2rem; font-weight: bold; color: white;")
    theme = load_themes(solara.lab.theme)

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

    with solara.Column(style="width: 100%; height: 100vh; display: flex; flex-direction: column; overflow: hidden;"):
        with solara.Div(style="width: 100%; flex-shrink: 0; padding: 5px 0;"):
            with solara.Row(
                justify="space-around",
                style="width: 100%;",
            ):
                for item_data in map_interactive_items:
                    with solara.Column(
                        align="stretch",
                        style="min-width: 300px; flex-grow: 1; margin: 0 5px;",
                    ):
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

        with solara.Div(style="width: 100%; flex-grow: 1; min-height: 300px; display: flex; flex-direction: column;"):
            map_component.MapDisplay()

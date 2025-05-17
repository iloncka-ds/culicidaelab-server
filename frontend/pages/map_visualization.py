import solara
import solara.lab
from solara.alias import rv
from typing import List, cast

# Use relative imports instead of absolute imports
from ..components.map_module import (
    map_component,
    filter_panel,
    info_panel,
    legend_component,
    layer_control,
)
# from ..state import data_loading_reactive
from ..state import (  # Assuming you'll add spinner back, import loading states
    distribution_loading_reactive,
    observations_loading_reactive,
    modeled_loading_reactive,
    breeding_sites_loading_reactive,
)
from ..config import COLOR_BACKGROUND
from ..config import load_themes


@solara.component
def Page():
    theme = load_themes(solara.lab.theme)
    with solara.AppBar():
        solara.lab.ThemeToggle()

    with solara.Row(style="height: calc(100vh - 64px); width: 100%;"): # 64px is typical AppBar height

        with solara.Sidebar():
            open_accordion_panels, set_open_accordion_panels = solara.use_state(
                cast(List[int], [0])
            )  # Open "Filters" by default

            map_accordion_items = [
                {"title": "Filters", "icon": "mdi-filter-variant", "component": filter_panel.FilterControls},
                {"title": "Map Layers", "icon": "mdi-layers-triple-outline",
                 "component": layer_control.LayerToggle},
                {"title": "Legend", "icon": "mdi-format-list-bulleted-type",
                 "component": legend_component.LegendDisplay},
                {"title": "Details", "icon": "mdi-information-outline", "component": info_panel.InformationDisplay},
                ]
            with rv.ExpansionPanels(
                accordion=True, # Only one panel open at a time
                multiple=True,  # Allow multiple panels to be open
                tabbable=False,
                flat=True,  # No box-shadow on panels
                value=open_accordion_panels,  # Controlled by state
                on_input=set_open_accordion_panels,  # Update state on change
                class_="pa-1",  # Some padding around the panels
                ):
                for i, item in enumerate(map_accordion_items):
                    # rv.ExpansionPanel does not take a 'title' or 'icon_name' prop directly.
                    # It uses slots for the header and content.
                    with rv.ExpansionPanel(key=item["title"]):  # Key for reactivity
                        with rv.Col():
                            with rv.ExpansionPanelHeader():
                                rv.Icon(children=[item["icon"]], left=True, class_="mr-2")
                                solara.Text(item["title"])
                            with rv.ExpansionPanelContent(
                                class_="pt-2",
                                # style_="display: block; width: 100%;"
                            ):  # Add padding to content
                                item["component"]()

        # --- Column 2: Map Display ---
        with solara.Column(style="flex-grow: 1; height: 100%; padding:0; margin:0;"):  # Map takes remaining space
            with solara.Div(
                style="width: 100%; height: 100%; display: flex; flex-direction: column; position: relative;"
            ):
                map_component.MapDisplay()





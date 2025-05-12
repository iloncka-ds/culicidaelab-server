import solara
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


@solara.component
def Page():
    # This Page component will be the main content for the "/map" route.
    # It will define its own internal layout with a control panel (tabs) and a map area.

    # Define the content for each tab
    # Using dictionaries makes it cleaner to loop if needed, or just for organization.
    tab_config = [
        {"label": "Filters", "icon": "mdi-filter-variant", "content_component": filter_panel.FilterControls},
        {"label": "Layers", "icon": "mdi-layers-triple-outline", "content_component": layer_control.LayerToggle},
        {
            "label": "Legend",
            "icon": "mdi-format-list-bulleted-type",
            "content_component": legend_component.LegendDisplay,
        },
        {"label": "Details", "icon": "mdi-information-outline", "content_component": info_panel.InformationDisplay},
    ]

    # with solara.Div(  # Outermost container for the map page, ensuring it fills height
    #     style=f"background-color: {COLOR_BACKGROUND}; padding: 0; margin: 0; height: 100%; display: flex; flex-direction: column;"
    # ):
    #     with solara.Row(  # This Row will contain the Tabs column and the Map column side-by-side
    #         style="flex-grow: 1; height: 100%; overflow: hidden;",  # Fill available vertical space, hide overflow
    #         gap="0px",  # No gap between columns
    #     ):
    # --- Column 1: Vertical Tabs (Control Panel / Page-Specific Sidebar) ---
    # with rv.Col(  # Using rv.Col for explicit width control is common
    #     cols=1,  # Full width on small screens (tabs might stack above map or you adjust flex-direction)
    #     sm=5,  # Takes 5/12 on small screens and up
    #     md=4,  # Takes 4/12 on medium screens and up
    #     lg=3,  # Takes 3/12 on large screens and up
    #     class_="pa-0 ma-0",
    #     style="""
    #         height: 100%;
    #         display: flex; /* Needed for solara.lab.Tabs to structure itself correctly */
    #         flex-direction: column; /* Tabs will arrange its bar and content area */
    #         border-right: 1px solid #e0e0e0;
    #         background-color: #f9f9f9; /* Light background for the tab panel */
    #         overflow: hidden; /* Prevent this column from causing page scroll */
    #     """,
    # ):
    with solara.Row():
        with solara.ColumnsResponsive([1, 4]):
            with solara.Column():
                open_accordion_panels, set_open_accordion_panels = solara.use_state(
                    cast(List[int], [0])
                )  # Open "Filters" by default

                map_accordion_items = [
                    {"title": "Filters", "icon": "mdi-filter-variant", "component": filter_panel.FilterControls},
                    {"title": "Map Layers", "icon": "mdi-layers-triple-outline", "component": layer_control.LayerToggle},
                    {"title": "Legend", "icon": "mdi-format-list-bulleted-type", "component": legend_component.LegendDisplay},
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
        with solara.Column(style="flex-grow: 1; min-height: 400px; height: 100%; width: 100%;"):
            map_component.MapDisplay()

            # Add back the loading spinner
            # is_loading = (
            #     distribution_loading_reactive.value
            #     or observations_loading_reactive.value
            #     or modeled_loading_reactive.value
            #     or breeding_sites_loading_reactive.value
            # )
            # if is_loading:
            #     solara.SpinnerSolara(
            #         size="60px",
            #         style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 1000;",
            #     )



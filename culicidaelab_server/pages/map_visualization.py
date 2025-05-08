import solara
from solara.alias import rv

# Use relative imports instead of absolute imports
from ..components.map_module import (
    map_component,
    filter_panel,
    info_panel,
    legend_component,
    layer_control,
)
from ..state import data_loading_reactive
from ..config import COLOR_BACKGROUND


@solara.component
def Page():
    with solara.Div(
        style=f"background-color: {COLOR_BACKGROUND}; padding: 0; margin: 0; height: calc(100vh - 64px); display: flex; flex-direction: column;"
    ):
        with solara.Row(
            gap="0px",  # Control spacing between children
            style="flex-grow: 1; display: flex; flex-direction: row; height: 100%;",  # Ensure children flex correctly
        ):
            with rv.Col(
                cols=8,
                sm=12,
                md=7,
                style="height: 100%; display: flex; flex-direction: column; position: relative; padding:0;",
            ):
                with solara.Div(style="flex-grow: 1; min-height: 400px; height: 100%; width: 100%;"):  # Map container
                    map_component.MapDisplay()

                if data_loading_reactive.value:
                    solara.SpinnerSolara(
                        size="60px",
                        style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 1000;",
                    )

            with rv.Col(
                cols=4,
                sm=12,
                md=5,
                style=f"""
                    height: 100%;
                    overflow-y: auto;
                    background-color: {COLOR_BACKGROUND};
                    padding: 12px;
                    border-left: 1px solid #e0e0e0;
                """,
            ):
                with rv.ExpansionPanels(
                    accordion=False, multiple=True, flat=True, mandatory=False, value=[]
                ):  # value=[] ensures all are closed initially
                    with rv.ExpansionPanel(title="Filters", icon_name="mdi-filter-variant"):
                        filter_panel.FilterControls()
                    with rv.ExpansionPanel(title="Map Layers", icon_name="mdi-layers-triple-outline"):
                        layer_control.LayerToggle()
                    with rv.ExpansionPanel(title="Legend", icon_name="mdi-format-list-bulleted-type"):
                        legend_component.LegendDisplay()
                    with rv.ExpansionPanel(title="Details", icon_name="mdi-information-outline"):
                        info_panel.InformationDisplay()

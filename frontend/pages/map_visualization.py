import solara
import solara.lab
from solara.alias import rv  # Keep if rv.ExpansionPanels is still desired for styling
from typing import List, cast, Optional

# Use relative imports instead of absolute imports
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
    # modeled_loading_reactive, # Removed in previous steps
    # breeding_sites_loading_reactive, # Removed in previous steps
)
from ..config import COLOR_BACKGROUND  # Keep if used
from ..config import load_themes
from frontend.components.common.locale_selector import LocaleSelector
import i18n

@solara.component
def Page():
    with solara.AppBar():
        solara.v.Spacer()
        LocaleSelector()
    with solara.AppBarTitle():
        solara.Text("CulicidaeLab", style="font-size: 2rem; font-weight: bold; color: white;")
    theme = load_themes(solara.lab.theme)  # If you're using custom themes

    filters_panel_value, set_filters_panel_value = solara.use_state(
        cast(Optional[List[int]], [0])
    )  # Filters open by default

    # --- State for "Legend" Expansion Panel ---
    legend_panel_value, set_legend_panel_value = solara.use_state(
        cast(Optional[List[int]], [])
    )  # Legend closed by default

    # Define items more directly for clarity
    filter_item = {
        "title": "Filters",
        "icon": "mdi-filter-variant",
        "component": filter_panel.FilterControls,
        "state_value": filters_panel_value,
        "state_setter": set_filters_panel_value,
    }
    legend_item = {
        "title": "Legend",
        "icon": "mdi-format-list-bulleted-type",
        "component": legend_component.LegendDisplay,
        "state_value": legend_panel_value,
        "state_setter": set_legend_panel_value,
    }

    # If you had more items you wanted side-by-side, add them here with their own state

    map_interactive_items = [filter_item, legend_item]

    with solara.Column(style="width: 100%; height: 100vh; display: flex; flex-direction: column; overflow: hidden;"):
        # --- Section 1: Control Panels (Side-by-Side) ---
        with solara.Div(
            style="width: 100%; flex-shrink: 0; padding: 5px 0;"  # Added some padding
        ):
            # Use solara.Row to place expansion panels side-by-side
            # You might want solara.ColumnsResponsive for better behavior on small screens
            with solara.Row(
                justify="space-around",  # Example: space them out
                style="width: 100%;",
            ):
                for item_data in map_interactive_items:
                    # Each item will be a column containing its own ExpansionPanels group (with one panel)
                    with solara.Column(
                        # Define how much space each panel group takes.
                        # E.g., if 2 items, style_="flex-basis: 50%; max-width: 50%;"
                        # Or let them size naturally based on content and Row's justify.
                        # For simplicity, let Row handle spacing.
                        # Add some margin between the columns if needed: class_="ma-1"
                        align="stretch",  # Ensure panel stretches if content is small
                        style="min-width: 300px; flex-grow: 1; margin: 0 5px;",  # Allow growing but have min width
                    ):
                        # Each rv.ExpansionPanel needs to be wrapped in rv.ExpansionPanels
                        # for the v-model / value prop to work correctly for controlling its open state.
                        with rv.ExpansionPanels(
                            # accordion=False, # Not strictly accordion as it's one panel
                            # multiple=False, # Only one panel here
                            value=item_data["state_value"],  # Pass the current state (e.g., [0] or [])
                            on_input=item_data["state_setter"],  # Pass the state setter
                            # flat=True, # Optional: for styling
                        ):
                            with rv.ExpansionPanel():  # The single panel
                                with rv.ExpansionPanelHeader():
                                    if item_data["icon"]:
                                        rv.Icon(children=[item_data["icon"]], left=True, class_="mr-2")
                                    solara.Text(item_data["title"])
                                with rv.ExpansionPanelContent(class_="pt-2"):
                                    item_data["component"]()

        # --- Section 2: Map Display ---
        with solara.Div(style="width: 100%; flex-grow: 1; min-height: 300px; display: flex; flex-direction: column;"):
            map_component.MapDisplay()
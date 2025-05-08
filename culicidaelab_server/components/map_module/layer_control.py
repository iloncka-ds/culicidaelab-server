import solara

# Relative imports
from culicidaelab_server.state import (
    show_distribution_status_reactive,
    show_observed_data_reactive,
    show_modeled_data_reactive,
    show_breeding_sites_reactive,  # Added
)
from culicidaelab_server.config import FONT_BODY, COLOR_TEXT


@solara.component
def LayerToggle():
    with solara.VBox():  # Reduced gap
        solara.Switch(label="Distribution Status", value=show_distribution_status_reactive)
        solara.Switch(label="Observed Data", value=show_observed_data_reactive)
        solara.Switch(label="Modeled Probability", value=show_modeled_data_reactive)
        solara.Switch(label="Breeding Sites", value=show_breeding_sites_reactive)

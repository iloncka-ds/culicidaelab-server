import solara

# Relative imports
from frontend.state import (
    # show_distribution_status_reactive, # Removed
    show_observed_data_reactive,
    # show_modeled_data_reactive, # Removed
    # show_breeding_sites_reactive,  # Removed
)
from frontend.config import FONT_BODY, COLOR_TEXT


@solara.component
def LayerToggle():
    with solara.Column():
        # solara.Switch(label="Distribution Status", value=show_distribution_status_reactive) # Removed
        solara.Switch(label="Observed Data", value=show_observed_data_reactive)
        # solara.Switch(label="Modeled Probability", value=show_modeled_data_reactive) # Removed
        # solara.Switch(label="Breeding Sites", value=show_breeding_sites_reactive) # Removed

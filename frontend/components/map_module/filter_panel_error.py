import solara
import datetime
from typing import cast, Optional
import datetime as dt
from solara.alias import rv
import solara.lab

# Relative imports
from frontend.state import (
    selected_species_reactive,
    all_available_species_reactive,
    selected_date_range_reactive,
    selected_region_reactive,
    all_available_regions_reactive,
    selected_data_source_reactive,
    all_available_data_sources_reactive,
)


@solara.component
def FilterControls():


    # The card styling is better handled by ExpansionPanel in map_visualization.py
    # This component will just render the controls themselves.
    with solara.Column():
        # Species Filter
        solara.SelectMultiple(
            label="Select Mosquito Species",
            values=selected_species_reactive,
            all_values=all_available_species_reactive.value,
            dense=True,  # More compact
        )

        # Region Filter
        solara.Select(
            label="Select Region (Optional)",
            value=selected_region_reactive,
            values=[None] + all_available_regions_reactive.value,  # Allow unselecting
            dense=True,
        )

        # Data Source Filter
        solara.Select(
            label="Select Data Source (Optional)",
            value=selected_data_source_reactive,
            values=[None] + all_available_data_sources_reactive.value,
            dense=True,
        )

        # Date Range Filter

        solara.Markdown("#### Date Range (Optional)")
        dates = selected_date_range_reactive

        solara.lab.InputDateRange(dates, on_value=selected_date_range_reactive.set)

        # "Apply Filters" button is not strictly necessary if using reactive variables watched by effects.
        # However, it can provide a more explicit user action, especially for expensive re-queries.

        # solara.Button("Apply Filters", on_click=lambda: asyncio.create_task(load_all_data()),
        #               color=COLOR_BUTTON_PRIMARY_BG, dark=True,
        #               style="margin-top: 15px;")

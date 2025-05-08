import solara
import datetime
from typing import cast, Optional

# Relative imports
from culicidaelab_server.state import (
    selected_species_reactive,
    all_available_species_reactive,
    selected_date_range_reactive,
    selected_region_reactive,
    all_available_regions_reactive,
    selected_data_source_reactive,
    all_available_data_sources_reactive,
)
from culicidaelab_server.config import COLOR_BUTTON_PRIMARY_BG, FONT_BODY


@solara.component
def FilterControls():
    # Helper to manage date updates for the reactive tuple
    def _set_start_date(value: Optional[datetime.date]):
        current_end = selected_date_range_reactive.value[1] if selected_date_range_reactive.value else None
        selected_date_range_reactive.value = (value, current_end)

    def _set_end_date(value: Optional[datetime.date]):
        current_start = selected_date_range_reactive.value[0] if selected_date_range_reactive.value else None
        selected_date_range_reactive.value = (current_start, value)

    current_start_date, current_end_date = selected_date_range_reactive.value

    # The card styling is better handled by ExpansionPanel in map_visualization.py
    # This component will just render the controls themselves.
    with solara.VBox():
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
        # Solara does not have a built-in DateRangePicker. Use two DatePickers.
        # If using ipyvuetify's v.DatePicker, more setup is needed.
        # solara.InputDate is simpler if available and suitable.
        # For now, let's assume solara.lab.DatePicker or similar future component
        # or create simple date inputs if needed.
        # Placeholder using solara.Input for now, you'd replace with actual date pickers.

        solara.Markdown("#### Date Range (Optional)")
        with solara.Row(gap="10px", justify="space-between"):
            # Casting is needed because solara.InputDate might not exist
            # Using text inputs as a fallback, real date pickers are better
            # solara.Input(label="Start Date", value=start_date_str, on_value=set_start_date_str, style="flex-grow: 1;")
            # solara.Input(label="End Date", value=end_date_str, on_value=set_end_date_str, style="flex-grow: 1;")

            # Using Solara's DatePicker if available (check Solara version/docs)
            # solara.DatePicker(label="Start Date", value=current_start_date, on_value=_set_start_date, optional=True, dense=True)
            # solara.DatePicker(label="End Date", value=current_end_date, on_value=_set_end_date, optional=True, dense=True)

            # Fallback if no DatePicker, or if you need custom input format
            # This is a simplified representation. A real date picker is complex.
            start_date_val = current_start_date.isoformat() if current_start_date else ""
            end_date_val = current_end_date.isoformat() if current_end_date else ""

            def _on_start_date_str(val_str):
                try:
                    _set_start_date(datetime.date.fromisoformat(val_str) if val_str else None)
                except ValueError:
                    _set_start_date(None)  # Or keep old value / show error

            def _on_end_date_str(val_str):
                try:
                    _set_end_date(datetime.date.fromisoformat(val_str) if val_str else None)
                except ValueError:
                    _set_end_date(None)

            solara.InputText(
                label="Start Date (YYYY-MM-DD)",
                value=start_date_val,
                on_value=_on_start_date_str,
                continuous_update=False,

            )
            solara.InputText(
                label="End Date (YYYY-MM-DD)",
                value=end_date_val,
                on_value=_on_end_date_str,
                continuous_update=False,

            )

        # "Apply Filters" button is not strictly necessary if using reactive variables watched by effects.
        # However, it can provide a more explicit user action, especially for expensive re-queries.
        # For now, let's omit it, assuming reactive updates.
        # If added:
        # solara.Button("Apply Filters", on_click=lambda: asyncio.create_task(load_all_data()),
        #               color=COLOR_BUTTON_PRIMARY_BG, dark=True,
        #               style="margin-top: 15px;")

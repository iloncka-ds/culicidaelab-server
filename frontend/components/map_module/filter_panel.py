import solara
import solara.lab
from solara.alias import rv
import datetime
from typing import List, Optional, Dict, Any, cast, Tuple  # Added Tuple
import asyncio

# Relative imports
from frontend.state import (
    selected_species_reactive,
    selected_date_range_reactive,
    selected_region_reactive,
    selected_data_source_reactive,
    all_available_species_reactive,
    all_available_regions_reactive,
    all_available_data_sources_reactive,
    filter_options_loading_reactive,
    filter_options_error_reactive,
    fetch_filter_options,  # This is the function to get dropdown options
    observations_data_reactive,
    show_observed_data_reactive,  # To check if layer is active
)
from frontend.config import FONT_BODY, COLOR_TEXT, COLOR_BUTTON_PRIMARY_BG, OBSERVATIONS_ENDPOINT

import httpx

# Global state for tracking data loading for this panel's actions
observations_loading = solara.reactive(False)  # Specific to this panel's fetch trigger


async def fetch_observations_data_for_panel(params: Dict[str, Any]) -> None:  # Renamed to avoid conflict
    """Fetch species observation data, specific to filter panel trigger."""
    # print(f"[DEBUG filter_panel fetch_observations_data_for_panel] with params: {params}")
    observations_loading.value = True
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(OBSERVATIONS_ENDPOINT, params=params, timeout=20.0)
            response.raise_for_status()
            observations_data_reactive.value = response.json()
            # print(
            #     f"Observation data fetched by panel: {len(observations_data_reactive.value.get('features', []))} features"
            # )
    except Exception as e:
        print(f"Error fetching observation data from panel: {e}")
        observations_data_reactive.value = {"type": "FeatureCollection", "features": []}
    finally:
        observations_loading.value = False


@solara.component
def FilterControls():
    initial_start_dt, initial_end_dt = selected_date_range_reactive.value
    start_date, set_start_date = solara.use_state(initial_start_dt)
    end_date, set_end_date = solara.use_state(initial_end_dt)

    # Fetch filter options (for dropdowns) when component mounts.
    # This task runs once.
    solara.lab.use_task(fetch_filter_options, dependencies=[])

    # Ref for the task triggered by "Apply Filters" button
    apply_filters_task_ref = solara.use_ref(None)

    async def handle_apply_filters_click():  # Renamed to clarify it's the button click handler
        # print("[DEBUG FilterControls handle_apply_filters_click] called")
        if apply_filters_task_ref.current and not apply_filters_task_ref.current.done():
            # print("[DEBUG] Cancelling previous apply_filters task.")
            apply_filters_task_ref.current.cancel()
            try:
                await apply_filters_task_ref.current
            except asyncio.CancelledError:
                # print("[DEBUG] Previous apply_filters task successfully cancelled.")
                pass
            except Exception:
                pass  # Ignore other errors from awaiting a cancelled task

        # Update global reactive date state from local pickers *before* fetching
        selected_date_range_reactive.value = (start_date, end_date)

        params: Dict[str, Any] = {}
        if selected_species_reactive.value:
            params["species"] = ",".join(selected_species_reactive.value)

        # Use the (now updated) global date state for formatting
        current_start_date_obj, current_end_date_obj = selected_date_range_reactive.value
        if current_start_date_obj:
            params["start_date"] = current_start_date_obj.strftime("%Y-%m-%d")
        if current_end_date_obj:
            params["end_date"] = current_end_date_obj.strftime("%Y-%m-%d")

        # print(f"[DEBUG] Creating new apply_filters task with params: {params}")

        # Fetch observations data if the layer is active
        if show_observed_data_reactive.value:
            # Create and store the new task
            apply_filters_task_ref.current = asyncio.create_task(fetch_observations_data_for_panel(params))
            try:
                await apply_filters_task_ref.current
            except asyncio.CancelledError:
                # print("[DEBUG] New apply_filters task was cancelled during execution.")
                pass
            except Exception as e:
                print(f"[DEBUG] Error during new apply_filters task: {e}")
        else:
            # print("[DEBUG] Observations layer not active, skipping fetch in apply_filters_click.")
            observations_data_reactive.value = {"type": "FeatureCollection", "features": []}
            observations_loading.value = False  # Ensure loading state is reset

    # Cleanup task on unmount
    def _cleanup_apply_filters_task():
        def cleanup():
            if apply_filters_task_ref.current and not apply_filters_task_ref.current.done():
                # print("[DEBUG FilterControls unmount] Cancelling apply_filters task.")
                apply_filters_task_ref.current.cancel()

        return cleanup

    solara.use_effect(_cleanup_apply_filters_task, [])

    # Effect to trigger initial data load if conditions are met on mount
    # This tries to load data based on default filters when the component first appears
    # and the observations layer is visible.
    # It only runs once due to empty dependency list.
    # Ensure selected_species_reactive has a sensible default (e.g. None or empty list)
    # if you want an initial fetch without user interaction on species.
    # If species must be selected first, this initial fetch might not be desired or
    # should depend on selected_species_reactive.value having a value.
    initial_load_done = solara.use_reactive(False)  # Prevent re-running initial load

    async def initial_load_observations():
        if not initial_load_done.value and show_observed_data_reactive.value and selected_species_reactive.value:
            # print("[DEBUG FilterControls initial_load_observations] Triggering initial load.")
            params: Dict[str, Any] = {}
            if selected_species_reactive.value:  # Check again, could be None
                params["species"] = ",".join(selected_species_reactive.value)

            s_date_obj, e_date_obj = selected_date_range_reactive.value  # Use default dates
            if s_date_obj:
                params["start_date"] = s_date_obj.strftime("%Y-%m-%d")
            if e_date_obj:
                params["end_date"] = e_date_obj.strftime("%Y-%m-%d")

            # if params.get("species"):  # Only fetch if species are actually selected
            await fetch_observations_data_for_panel(params)
            initial_load_done.value = True
        # elif not selected_species_reactive.value and show_observed_data_reactive.value:
        #     # print("[DEBUG FilterControls initial_load_observations] No species selected, clearing observations.")
        #     observations_data_reactive.value = {"type": "FeatureCollection", "features": []}
        #     observations_loading.value = False
    initial_load_observations()

    with solara.Column(style="padding: 10px;"):
        # solara.Markdown("#### Filter Data", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT};")

        if filter_options_loading_reactive.value:
            solara.ProgressLinear(True)
            solara.Text(
                "Loading filter options...", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; font-style: italic;"
            )

        if filter_options_error_reactive.value:
            solara.Error(filter_options_error_reactive.value)

        solara.Markdown("##### Species", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; margin-top: 10px;")
        if all_available_species_reactive.value:
            solara.SelectMultiple(
                label="Select Species",
                values=selected_species_reactive,
                all_values=all_available_species_reactive.value,
                style="max-width: 400px; margin-bottom: 10px;",
            )
        else:
            solara.Text(
                "No species available", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; font-style: italic;"
            )

        # solara.Markdown("##### Region", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; margin-top: 10px;")
        # region_options = ["All Regions"] + (all_available_regions_reactive.value or [])
        # solara.Select(
        #     label="Select Region",
        #     value=selected_region_reactive,
        #     values=region_options,
        #     style="max-width: 400px; margin-bottom: 10px;",
        #     on_value=lambda x: selected_region_reactive.set(None if x == "All Regions" else x),
        # )

        # solara.Markdown("##### Data Source", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; margin-top: 10px;")
        # data_source_options = ["All Sources"] + (all_available_data_sources_reactive.value or [])
        # solara.Select(
        #     label="Select Data Source",
        #     value=selected_data_source_reactive,
        #     values=data_source_options,
        #     style="max-width: 400px; margin-bottom: 10px;",
        #     on_value=lambda x: selected_data_source_reactive.set(None if x == "All Sources" else x),
        # )

        solara.Markdown("##### Date Range", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; margin-top: 10px;")

        def set_local_dates_from_picker(
            new_dates_value: Optional[Tuple[Optional[datetime.date], Optional[datetime.date]]],
        ):
            if isinstance(new_dates_value, tuple) and len(new_dates_value) == 2:
                set_start_date(new_dates_value[0])
                set_end_date(new_dates_value[1])
            elif new_dates_value is None:
                set_start_date(None)
                set_end_date(None)
            # else:
            #     # print(f"[WARN] Unexpected value from InputDateRange: {new_dates_value}. Resetting dates to None.")
            #     set_start_date(None)
            #     set_end_date(None)

        current_date_range_for_picker = (start_date, end_date)
        solara.lab.InputDateRange(value=current_date_range_for_picker, on_value=set_local_dates_from_picker)

        with solara.Row(style="margin-top: 15px;"):
            solara.Button(
                "Apply Date Filters",
                # CHANGE HERE: Use a lambda to create the task
                on_click=lambda: asyncio.create_task(handle_apply_filters_click()),
                color=COLOR_BUTTON_PRIMARY_BG,
                style=f"color: white; font-family: {FONT_BODY};",
            )

            # Use the panel-specific loading state
            if observations_loading.value:
                with solara.Row(style="align-items: center; margin-left: 10px;"):
                    solara.ProgressLinear()
                    solara.Text(
                        "Loading data...", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; font-style: italic;"
                    )
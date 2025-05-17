import solara
import solara.lab
from solara.alias import rv
import datetime
from typing import List, Optional, Dict, Any, cast
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
    fetch_filter_options,
    # distribution_data_reactive, # Removed
    observations_data_reactive,
    # modeled_data_reactive, # Removed
    # breeding_sites_data_reactive, # Removed
)
from frontend.config import FONT_BODY, COLOR_TEXT, COLOR_BUTTON_PRIMARY_BG

# API call functions for data based on filters
import httpx
from frontend.config import (
    # SPECIES_DISTRIBUTION_ENDPOINT, # Removed
    OBSERVATIONS_ENDPOINT,
    # MODELED_PROBABILITY_ENDPOINT, # Removed
    # BREEDING_SITES_ENDPOINT, # Removed
)

# Global state for tracking data loading
# distribution_loading = solara.reactive(False) # Removed
observations_loading = solara.reactive(False)
# modeled_loading = solara.reactive(False) # Removed
# breeding_sites_loading = solara.reactive(False) # Removed


async def fetch_data_with_filters() -> None:
    """Fetch all map data based on current filters."""
    # Build query parameters from reactive state
    params: Dict[str, Any] = {}

    if selected_species_reactive.value:
        params["species"] = ",".join(selected_species_reactive.value)

    if selected_region_reactive.value:
        params["region"] = selected_region_reactive.value

    if selected_data_source_reactive.value:
        params["data_source"] = selected_data_source_reactive.value

    if selected_date_range_reactive.value and selected_date_range_reactive.value[0]:
        # Format dates for API: YYYY-MM-DD
        start_date, end_date = selected_date_range_reactive.value
        if start_date:
            params["start_date"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["end_date"] = end_date.strftime("%Y-%m-%d")

    # Fetch observations data
    await fetch_observations_data(params)


async def fetch_observations_data(params: Dict[str, Any]) -> None:
    """Fetch species observation data."""
    observations_loading.value = True
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(OBSERVATIONS_ENDPOINT, params=params, timeout=15.0)
            response.raise_for_status()
            observations_data_reactive.value = response.json()
            print(
                f"Observation data fetched: {len(observations_data_reactive.value.get('features', []))} features"
            )  # Safe get
    except Exception as e:
        print(f"Error fetching observation data: {e}")
        observations_data_reactive.value = {"type": "FeatureCollection", "features": []}
    finally:
        observations_loading.value = False


@solara.component
def FilterControls():
    # Local state for date picker
    start_date, set_start_date = solara.use_state(None)
    end_date, set_end_date = solara.use_state(None)

    # Fetch filter options when component mounts.
    # fetch_filter_options is an async function. solara.lab.use_task handles
    # running it and cancelling it if the component unmounts or dependencies change.
    # Empty dependencies [] means it runs once on mount.
    # This assumes fetch_filter_options is idempotent or has its own guards if called multiple times.
    # (which it does with filter_options_loading_reactive.value)
    solara.lab.use_task(fetch_filter_options, dependencies=[])

    # Handle when date range changes from date pickers
    # This function is not used directly, selected_date_range_reactive.set is used by InputDateRange
    # def handle_date_range_change():
    #     selected_date_range_reactive.value = (start_date, end_date)

    # Apply filters button handler
    # This task is created on click. If the component unmounts while it's running,
    # it won't be automatically cancelled by this structure.
    # For short operations, this is often fine. For long ones, more complex state mgmt might be needed.
    apply_filters_task_ref = solara.use_ref(None)

    async def handle_apply_filters():
        # Cancel previous task if still running
        if apply_filters_task_ref.current and not apply_filters_task_ref.current.done():
            apply_filters_task_ref.current.cancel()
            try:
                await apply_filters_task_ref.current  # Allow cancellation to propagate
            except asyncio.CancelledError:
                print("[DEBUG] Previous apply_filters task cancelled.")
            except Exception:  # pragma: no cover
                pass  # Ignore other exceptions from awaiting a cancelled task

        # Apply date range from local state before fetching
        current_start_date, current_end_date = selected_date_range_reactive.value
        if start_date != current_start_date or end_date != current_end_date:  # Check if date is from local state
            selected_date_range_reactive.value = (start_date, end_date)

        print("[DEBUG] Creating new apply_filters task.")
        apply_filters_task_ref.current = asyncio.create_task(fetch_data_with_filters())
        try:
            await apply_filters_task_ref.current
        except asyncio.CancelledError:  # pragma: no cover
            print("[DEBUG] New apply_filters task was cancelled during execution.")
        except Exception as e:  # pragma: no cover
            print(f"[DEBUG] Error during new apply_filters task: {e}")

    # Ensure apply_filters_task is cancelled on unmount if running
    def _cleanup_apply_filters_task():
        def cleanup():
            if apply_filters_task_ref.current and not apply_filters_task_ref.current.done():
                print("[DEBUG] FilterControls unmounting, cancelling apply_filters task.")
                apply_filters_task_ref.current.cancel()

        return cleanup

    solara.use_effect(_cleanup_apply_filters_task, [])

    with solara.Column(style="padding: 10px;"):
        solara.Markdown("#### Filter Data", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT};")

        if filter_options_loading_reactive.value:
            solara.ProgressLinear(True)
            solara.Text(
                "Loading filter options...", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; font-style: italic;"
            )

        if filter_options_error_reactive.value:
            solara.Error(filter_options_error_reactive.value)

        solara.Markdown("##### Species", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; margin-top: 10px;")
        if all_available_species_reactive.value:
            # Using solara.SelectMultiple which is generally preferred over raw rv.Select for state handling
            solara.SelectMultiple(
                label="Select Species",
                values=selected_species_reactive,  # Direct binding to reactive variable
                all_values=all_available_species_reactive.value,
                style="max-width: 400px; margin-bottom: 10px;",
            )
        else:
            solara.Text(
                "No species available", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; font-style: italic;"
            )

        solara.Markdown("##### Region", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; margin-top: 10px;")
        region_options = ["All Regions"] + all_available_regions_reactive.value
        # Allow direct binding if solara.Select value can be None
        solara.Select(
            label="Select Region",
            value=selected_region_reactive,  # Direct binding
            values=region_options,  # Solara will handle mapping "All Regions" to None if configured or you handle in setter
            style="max-width: 400px; margin-bottom: 10px;",
            # If "All Regions" should map to None, you might need a small wrapper or ensure API handles "All Regions"
            on_value=lambda x: selected_region_reactive.set(None if x == "All Regions" else x),
        )

        solara.Markdown("##### Data Source", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; margin-top: 10px;")
        data_source_options = ["All Sources"] + all_available_data_sources_reactive.value
        solara.Select(
            label="Select Data Source",
            value=selected_data_source_reactive,  # Direct binding
            values=data_source_options,
            style="max-width: 400px; margin-bottom: 10px;",
            on_value=lambda x: selected_data_source_reactive.set(None if x == "All Sources" else x),
        )

        solara.Markdown("##### Date Range", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; margin-top: 10px;")
        # Bind InputDateRange to local state, and update reactive var in handle_apply_filters or an effect
        current_selection = solara.use_reactive(selected_date_range_reactive.value)

        def set_local_dates(new_dates_tuple):
            set_start_date(new_dates_tuple[0])
            set_end_date(new_dates_tuple[1])
            # current_selection.value = new_dates_tuple # Not strictly needed if only reading from start_date, end_date

        solara.lab.InputDateRange(value=(start_date, end_date), on_value=set_local_dates)

        with solara.Row(style="margin-top: 15px;"):
            solara.Button(
                "Apply Filters",
                on_click=lambda: asyncio.create_task(handle_apply_filters()),
                color=COLOR_BUTTON_PRIMARY_BG,
                style=f"color: white; font-family: {FONT_BODY};",
            )

            loading_any = observations_loading.value
            if loading_any:
                with solara.Row(style="align-items: center; margin-left: 10px;"):
                    solara.ProgressLinear(True, style="width: 24px; height: 24px;")
                    solara.Text(
                        "Loading data...", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; font-style: italic;"
                    )

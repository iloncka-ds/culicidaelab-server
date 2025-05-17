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
    distribution_data_reactive,
    observations_data_reactive,
    modeled_data_reactive,
    breeding_sites_data_reactive,
)
from frontend.config import FONT_BODY, COLOR_TEXT, COLOR_BUTTON_PRIMARY_BG

# API call functions for data based on filters
import httpx
from frontend.config import (
    SPECIES_DISTRIBUTION_ENDPOINT,
    OBSERVATIONS_ENDPOINT,
    MODELED_PROBABILITY_ENDPOINT,
    BREEDING_SITES_ENDPOINT,
)

# Global state for tracking data loading
distribution_loading = solara.reactive(False)
observations_loading = solara.reactive(False)
modeled_loading = solara.reactive(False)
breeding_sites_loading = solara.reactive(False)


async def fetch_data_with_filters() -> None:
    """Fetch all map data based on current filters."""
    print("[DEBUG] fetch_data_with_filters() called")
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

    print(f"[DEBUG] fetch_data_with_filters params: {params}")

    # Fetch distribution data
    await fetch_distribution_data(params)

    # Fetch observations data
    await fetch_observations_data(params)

    # Fetch modeled data
    await fetch_modeled_data(params)

    # Fetch breeding sites data
    await fetch_breeding_sites_data(params)

    print("[DEBUG] fetch_data_with_filters() completed")


async def fetch_distribution_data(params: Dict[str, Any]) -> None:
    """Fetch species distribution data."""
    print(f"[DEBUG] fetch_distribution_data() called with params: {params}")
    distribution_loading.value = True
    try:
        async with httpx.AsyncClient() as client:
            print(f"[DEBUG] Calling distribution API: {SPECIES_DISTRIBUTION_ENDPOINT}")
            response = await client.get(SPECIES_DISTRIBUTION_ENDPOINT, params=params, timeout=15.0)
            response.raise_for_status()
            distribution_data_reactive.value = response.json()
            print(f"[DEBUG] Distribution data fetched: {len(distribution_data_reactive.value)}")
    except Exception as e:
        print(f"[DEBUG] Error fetching distribution data: {e}")
        import traceback
        print(f"[DEBUG] Distribution fetch error details: {traceback.format_exc()}")
        distribution_data_reactive.value = {"type": "FeatureCollection", "features": []}
    finally:
        distribution_loading.value = False


async def fetch_observations_data(params: Dict[str, Any]) -> None:
    """Fetch species observation data."""
    print(f"[DEBUG] fetch_observations_data() called with params: {params}")
    observations_loading.value = True
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(OBSERVATIONS_ENDPOINT, params=params, timeout=15.0)
            response.raise_for_status()
            observations_data_reactive.value = response.json()
            print(f"Observation data fetched: {len(observations_data_reactive.value)}")
    except Exception as e:
        print(f"[DEBUG] Error fetching observation data: {e}")
        import traceback
        print(f"[DEBUG] Observation fetch error details: {traceback.format_exc()}")
        observations_data_reactive.value = {"type": "FeatureCollection", "features": []}
    finally:
        observations_loading.value = False


async def fetch_modeled_data(params: Dict[str, Any]) -> None:
    """Fetch modeled probability data."""
    print(f"[DEBUG] fetch_modeled_data() called with params: {params}")
    modeled_loading.value = True
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(MODELED_PROBABILITY_ENDPOINT, params=params, timeout=15.0)
            response.raise_for_status()
            modeled_data_reactive.value = response.json()
            print(f"Modeled data fetched: {len(modeled_data_reactive.value.get('features', []))} features")
    except Exception as e:
        print(f"[DEBUG] Error fetching modeled data: {e}")
        import traceback
        print(f"[DEBUG] Modeled data fetch error details: {traceback.format_exc()}")
        modeled_data_reactive.value = {"type": "FeatureCollection", "features": []}
    finally:
        modeled_loading.value = False


async def fetch_breeding_sites_data(params: Dict[str, Any]) -> None:
    """Fetch breeding sites data."""
    print(f"[DEBUG] fetch_breeding_sites_data() called with params: {params}")
    breeding_sites_loading.value = True
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(BREEDING_SITES_ENDPOINT, params=params, timeout=15.0)
            response.raise_for_status()
            breeding_sites_data_reactive.value = response.json()
            print(f"Breeding sites data fetched: {len(breeding_sites_data_reactive.value)}")
    except Exception as e:
        print(f"[DEBUG] Error fetching breeding sites data: {e}")
        import traceback
        print(f"[DEBUG] Breeding sites fetch error details: {traceback.format_exc()}")
        breeding_sites_data_reactive.value = {"type": "FeatureCollection", "features": []}
    finally:
        breeding_sites_loading.value = False


@solara.component
def FilterControls():
    # Local state for date picker
    start_date, set_start_date = solara.use_state(None)
    end_date, set_end_date = solara.use_state(None)

    # Reference to store async task
    task_ref = solara.use_ref(None)

    # Fetch filter options when component mounts with proper task cleanup
    solara.use_effect(
        lambda: (
            setattr(task_ref, "current", asyncio.create_task(fetch_filter_options())),
            lambda: task_ref.current.cancel() if task_ref.current else None,
        ),
        [],
    )

    # Handle when date range changes from date pickers
    def handle_date_range_change():
        selected_date_range_reactive.value = (start_date, end_date)

    # Reference for apply filters task
    apply_task_ref = solara.use_ref(None)

    # Apply filters button handler
    async def handle_apply_filters():
        print("[DEBUG] handle_apply_filters clicked")
        # Cancel any previously running task
        if apply_task_ref.current and not apply_task_ref.current.done():
            apply_task_ref.current.cancel()

        # Apply date range from local state
        selected_date_range_reactive.value = (start_date, end_date)
        # Fetch data with all current filters
        apply_task_ref.current = asyncio.create_task(fetch_data_with_filters())

    with solara.Column(style="padding: 10px;"):
        solara.Markdown("## Filter Data", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT};")

        # Display loading or error status
        if filter_options_loading_reactive.value:
            solara.ProgressLinear(True)
            solara.Text(
                "Loading filter options...", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; font-style: italic;"
            )

        if filter_options_error_reactive.value:
            solara.Error(filter_options_error_reactive.value)

        # Species Selection (Multi-select)
        solara.Markdown("### Species", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; margin-top: 10px;")

        if all_available_species_reactive.value:
            with rv.Select(
                label="Select Species",
                value=selected_species_reactive.value,
                items=all_available_species_reactive.value,
                multiple=True,
                on_value=lambda x: setattr(selected_species_reactive, "value", x),
                style_="max-width: 400px; margin-bottom: 10px;",
                chips=True,
            ):
                pass
        else:
            solara.Text(
                "No species available", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; font-style: italic;"
            )

        # Region Selection (Single-select)
        solara.Markdown("### Region", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; margin-top: 10px;")

        region_options = ["All Regions"] + all_available_regions_reactive.value
        selected_region_display = selected_region_reactive.value if selected_region_reactive.value else "All Regions"

        with rv.Select(
            label="Select Region",
            value=selected_region_display,
            items=region_options,
            on_value=lambda x: setattr(selected_region_reactive, "value", None if x == "All Regions" else x),
            style_="max-width: 400px; margin-bottom: 10px;",
        ):
            pass

        # Data Source Selection (Single-select)
        solara.Markdown("### Data Source", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; margin-top: 10px;")

        data_source_options = ["All Sources"] + all_available_data_sources_reactive.value
        selected_source_display = (
            selected_data_source_reactive.value if selected_data_source_reactive.value else "All Sources"
        )

        with rv.Select(
            label="Select Data Source",
            value=selected_source_display,
            items=data_source_options,
            on_value=lambda x: setattr(selected_data_source_reactive, "value", None if x == "All Sources" else x),
            style_="max-width: 400px; margin-bottom: 10px;",
        ):
            pass

        # Date Range Selection
        solara.Markdown("### Date Range", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; margin-top: 10px;")

        solara.lab.InputDateRange((start_date, end_date), on_value=selected_date_range_reactive.set)

        # Apply Filters Button
        with solara.Row(style="margin-top: 15px;"):
            solara.Button(
                "Apply Filters",
                on_click=lambda: (
                    # Create a new task but don't use create_task in the lambda directly
                    # Instead use a function that creates the task
                    handle_apply_filters()
                ),
                color=COLOR_BUTTON_PRIMARY_BG,
                style=f"color: white; font-family: {FONT_BODY};",
            )

            # Loading indicator
            loading_any = (
                distribution_loading.value
                or observations_loading.value
                or modeled_loading.value
                or breeding_sites_loading.value
            )

            if loading_any:
                with solara.Row(style="align-items: center; margin-left: 10px;"):
                    solara.ProgressLinear(True, style="width: 24px; height: 24px;")
                    solara.Text(
                        "Loading data...", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; font-style: italic;"
                    )

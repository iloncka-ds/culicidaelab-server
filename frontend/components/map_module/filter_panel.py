import solara
import solara.lab
from solara.alias import rv
import datetime
from typing import List, Optional, Dict, Any, cast, Tuple
import asyncio

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
    observations_data_reactive,
    show_observed_data_reactive,
)
from frontend.config import FONT_BODY, COLOR_TEXT, COLOR_BUTTON_PRIMARY_BG, OBSERVATIONS_ENDPOINT

import httpx

observations_loading = solara.reactive(False)


async def fetch_observations_data_for_panel(params: Dict[str, Any]) -> None:
    """Fetch species observation data, specific to filter panel trigger."""
    observations_loading.value = True
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(OBSERVATIONS_ENDPOINT, params=params, timeout=20.0)
            response.raise_for_status()
            observations_data_reactive.value = response.json()
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

    solara.lab.use_task(fetch_filter_options, dependencies=[])

    apply_filters_task_ref = solara.use_ref(None)

    async def handle_apply_filters_click():
        if apply_filters_task_ref.current and not apply_filters_task_ref.current.done():
            apply_filters_task_ref.current.cancel()
            try:
                await apply_filters_task_ref.current
            except asyncio.CancelledError:
                pass
            except Exception:
                pass

        selected_date_range_reactive.value = (start_date, end_date)

        params: Dict[str, Any] = {}
        if selected_species_reactive.value:
            params["species"] = ",".join(selected_species_reactive.value)

        current_start_date_obj, current_end_date_obj = selected_date_range_reactive.value
        if current_start_date_obj:
            params["start_date"] = current_start_date_obj.strftime("%Y-%m-%d")
        if current_end_date_obj:
            params["end_date"] = current_end_date_obj.strftime("%Y-%m-%d")


        if show_observed_data_reactive.value:
            apply_filters_task_ref.current = asyncio.create_task(fetch_observations_data_for_panel(params))
            try:
                await apply_filters_task_ref.current
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"[DEBUG] Error during new apply_filters task: {e}")
        else:
            observations_data_reactive.value = {"type": "FeatureCollection", "features": []}
            observations_loading.value = False

    def _cleanup_apply_filters_task():
        def cleanup():
            if apply_filters_task_ref.current and not apply_filters_task_ref.current.done():
                apply_filters_task_ref.current.cancel()

        return cleanup

    solara.use_effect(_cleanup_apply_filters_task, [])

    initial_load_done = solara.use_reactive(False)

    async def initial_load_observations():
        if not initial_load_done.value and show_observed_data_reactive.value and selected_species_reactive.value:
            params: Dict[str, Any] = {}
            if selected_species_reactive.value:
                params["species"] = ",".join(selected_species_reactive.value)

            s_date_obj, e_date_obj = selected_date_range_reactive.value
            if s_date_obj:
                params["start_date"] = s_date_obj.strftime("%Y-%m-%d")
            if e_date_obj:
                params["end_date"] = e_date_obj.strftime("%Y-%m-%d")

            await fetch_observations_data_for_panel(params)
            initial_load_done.value = True
    initial_load_observations()

    with solara.Column(style="padding: 10px;"):

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

        current_date_range_for_picker = (start_date, end_date)
        solara.lab.InputDateRange(value=current_date_range_for_picker, on_value=set_local_dates_from_picker)

        with solara.Row(style="margin-top: 15px;"):
            solara.Button(
                "Apply Date Filters",
                on_click=lambda: asyncio.create_task(handle_apply_filters_click()),
                color=COLOR_BUTTON_PRIMARY_BG,
                style=f"color: white; font-family: {FONT_BODY};",
            )

            if observations_loading.value:
                with solara.Row(style="align-items: center; margin-left: 10px;"):
                    solara.ProgressLinear()
                    solara.Text(
                        "Loading data...", style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; font-style: italic;"
                    )

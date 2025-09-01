import solara
import solara.lab
import datetime
from typing import Any
import asyncio
import i18n

from frontend.state import (
    selected_species_reactive,
    selected_date_range_reactive,
    all_available_species_reactive,
    filter_options_loading_reactive,
    filter_options_error_reactive,
    fetch_filter_options,
    observations_data_reactive,
    show_observed_data_reactive,
    use_locale_effect,
    current_locale,
)
from frontend.config import FONT_BODY, COLOR_TEXT, COLOR_BUTTON_PRIMARY_BG, OBSERVATIONS_ENDPOINT

import httpx

observations_loading = solara.reactive(False)


async def fetch_observations_data_for_panel(params: dict[str, Any]) -> None:
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
    solara.lab.use_task(fetch_filter_options, dependencies=[current_locale.value])
    apply_filters_task_ref = solara.use_ref(None)
    use_locale_effect()

    async def handle_apply_filters_click() -> None:
        if apply_filters_task_ref.current and not apply_filters_task_ref.current.done():
            apply_filters_task_ref.current.cancel()
            try:
                await apply_filters_task_ref.current
            except asyncio.CancelledError:
                print("Apply filters task cancelled.")
            except Exception as e:
                print(f"Apply filters task failed: {e}")

        selected_date_range_reactive.value = (start_date, end_date)

        params: dict[str, Any] = {}
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

    # THIS IS THE FIX:
    # The state variable is declared in the component's render scope.
    initial_load_done = solara.use_reactive(False)

    async def initial_load_observations_task():
        # The async task can now safely access the state variable
        # from its parent scope without violating hook rules.
        if not initial_load_done.value and show_observed_data_reactive.value and selected_species_reactive.value:
            await handle_apply_filters_click()
            initial_load_done.value = True

    solara.lab.use_task(initial_load_observations_task, dependencies=[])

    with solara.Column(style="padding: 10px;"):
        if filter_options_loading_reactive.value:
            solara.ProgressLinear(True)
            solara.Text(
                i18n.t("map.filter_controls.loading_options"),
                style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; font-style: italic;",
            )

        if filter_options_error_reactive.value:
            solara.Error(filter_options_error_reactive.value)

        solara.Markdown(
            f"##### {i18n.t('map.filter_controls.species_label')}",
            style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; margin-top: 10px;",
        )
        if all_available_species_reactive.value:
            solara.SelectMultiple(
                label=i18n.t("map.filter_controls.species_select"),
                values=selected_species_reactive,
                all_values=all_available_species_reactive.value,
                style="max-width: 400px; margin-bottom: 10px;",
            )
        else:
            solara.Text(
                i18n.t("map.filter_controls.species_none_available"),
                style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; font-style: italic;",
            )

        solara.Markdown(
            f"##### {i18n.t('map.filter_controls.date_range_label')}",
            style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; margin-top: 10px;",
        )

        def set_local_dates_from_picker(
            new_dates_value: tuple[datetime.date | None, datetime.date | None] | None,
        ):
            if isinstance(new_dates_value, tuple) and len(new_dates_value) == 2:
                set_start_date(new_dates_value[0])
                set_end_date(new_dates_value[1])
            elif new_dates_value is None:
                set_start_date(None)
                set_end_date(None)

        current_date_range_for_picker = (start_date, end_date)
        solara.lab.InputDateRange(
            value=current_date_range_for_picker,
            on_value=set_local_dates_from_picker,
        )

        with solara.Row(style="margin-top: 15px;"):
            solara.Button(
                i18n.t("map.filter_controls.apply_button"),
                on_click=lambda: asyncio.create_task(handle_apply_filters_click()),
                color=COLOR_BUTTON_PRIMARY_BG,
                style=f"color: white; font-family: {FONT_BODY};",
            )

            if observations_loading.value:
                with solara.Row(style="align-items: center; margin-left: 10px;"):
                    solara.ProgressLinear()
                    solara.Text(
                        i18n.t("map.filter_controls.loading_data"),
                        style=f"font-family: {FONT_BODY}; color: {COLOR_TEXT}; font-style: italic;",
                    )

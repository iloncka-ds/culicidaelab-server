import solara
import solara.lab
from solara.alias import rv

import httpx
import asyncio
from typing import Dict, Any, List, Optional, cast, Callable
from ..state import fetch_api_data
import frontend.pages.disease_detail as disease_detail
from frontend.components.diseases.disease_card import DiseaseCard

# Relative imports for config and state
from ..config import (
    COLOR_PRIMARY,
    FONT_HEADINGS,
    COLOR_TEXT,
    DISEASE_LIST_ENDPOINT,
    DISEASE_DETAIL_ENDPOINT_TEMPLATE,
    API_BASE_URL
)

# --- Reactive States for Disease Database Page ---
disease_list_data_reactive = solara.reactive(cast(List[Dict[str, Any]], []))
disease_list_loading_reactive = solara.reactive(False)
disease_list_error_reactive = solara.reactive(cast(Optional[str], None))

@solara.component
def Page():
    with solara.AppBar():
        solara.lab.ThemeToggle()

    search_query, set_search_query = solara.use_state("")

    def _load_disease_list_data_effect() -> Optional[Callable[[], None]]:
        task_ref = [cast(Optional[asyncio.Task], None)]

        async def _async_load_task():
            params = {}
            if search_query:
                params["search"] = search_query

            data = await fetch_api_data(
                DISEASE_LIST_ENDPOINT,
                params=params,
                loading_reactive=disease_list_loading_reactive,
                error_reactive=disease_list_error_reactive,
            )

            print("---- Received Disease List API Data ----")
            print(data)
            print("--------------------------------------")

            actual_disease_list = []
            if isinstance(data, dict) and "diseases" in data and isinstance(data["diseases"], list):
                actual_disease_list = data["diseases"]
                print(
                    f"Page Effect: Setting disease list from dict (count={data.get('count', len(actual_disease_list))})"
                )
            elif isinstance(data, list):
                actual_disease_list = data
                print(f"Page Effect: Setting disease list from direct list (count={len(actual_disease_list)})")
            else:
                print(f"Warning: Unexpected data format from disease list API: {type(data)}. List empty.")
                disease_list_error_reactive.value = (
                    disease_list_error_reactive.value or "Unexpected data format from API."
                )

            current_task = task_ref[0]
            if not (current_task and current_task.cancelled()):
                disease_list_data_reactive.value = actual_disease_list
            else:
                print(f"Disease list load task for search '{search_query}' was cancelled before setting data.")

        task_ref[0] = asyncio.create_task(_async_load_task())

        def cleanup():
            current_task = task_ref[0]
            if current_task and not current_task.done():
                print(f"Cleaning up: Cancelling disease list task for search '{search_query}'")
                current_task.cancel()

        return cleanup

    solara.use_effect(_load_disease_list_data_effect, [search_query])

    displayed_diseases = disease_list_data_reactive.value

    with solara.Column(
        style="padding-bottom: 20px; min-height: calc(100vh - 120px);"
    ):
        solara.Markdown(
            "# Vector-Borne Disease Gallery", style=f"font-family: {FONT_HEADINGS}; text-align:center; margin-bottom:20px;"
        )
        with solara.Row(
            classes=["pa-2 ma-2 elevation-1"],
            style="border-radius: 6px; background-color: var(--solara-card-background-color); align-items: center; gap: 10px; position: sticky; top: 0px; z-index:10; margin-bottom:10px;",
        ):
            solara.InputText(
                label="Search disease...",
                value=search_query,
                on_value=set_search_query,
                continuous_update=False,
                style="flex-grow: 1;",
            )
            solara.Button(
                "Filters",
                icon_name="mdi-filter-variant",
                outlined=True,
                color=COLOR_PRIMARY,
                on_click=lambda: solara.Warning("Filter panel not yet implemented."),
            )

        if disease_list_loading_reactive.value:
            solara.SpinnerSolara(size="60px")
        elif disease_list_error_reactive.value:
            solara.Error(
                f"Could not load diseases: {disease_list_error_reactive.value}",
                icon="mdi-alert-circle-outline",
            )
        elif displayed_diseases:  # Check if list is not None
            if not displayed_diseases:  # Empty list
                solara.Info(
                    "No diseases found matching your criteria.", icon="mdi-information-outline", style="margin: 16px;"
                )
            else:
                with solara.ColumnsResponsive(
                    default=[3, 3, 3, 3],
                    large=[4, 4, 4],
                    medium=[6, 6],
                    small=[12],
                    gutters="16px",
                    classes=["pa-2"],
                ):
                    for disease_item in displayed_diseases:
                        item_id = disease_item.get("id")
                        if item_id is None:
                            print(
                                f"Warning: Disease item {disease_item.get('name', 'Unknown')} is missing an 'id'. Card will not be clickable for details."
                            )
                        # Render the disease card
                        DiseaseCard(disease_item)
        else:  # displayed_diseases is None (should not happen if initialized to [])
            solara.Info(
                "Initializing disease data or an unexpected issue occurred.",
                icon="mdi-information-outline",
                style="margin: 16px;",
            )

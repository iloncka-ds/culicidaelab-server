import solara
import solara.lab
from solara.alias import rv

import httpx
import asyncio
from typing import Dict, Any, List, Optional, cast, Callable
from ...state import fetch_api_data, selected_species_item_id, species_list_data_reactive, species_list_loading_reactive, species_list_error_reactive

from frontend.components.species.species_card import SpeciesCard

# Assuming these are correctly defined in your project structure
# from ..config import load_themes # Not used in this snippet directly, but kept for context
# Relative imports for config and state
from ...config import (
    COLOR_PRIMARY,
    FONT_HEADINGS,
    COLOR_TEXT,
    SPECIES_LIST_ENDPOINT,
    SPECIES_DETAIL_ENDPOINT_TEMPLATE,
    API_BASE_URL
)


selected_species_item_id.set(None)

# @solara.component
# def SpeciesCard(species: Dict[str, Any]):


#     with rv.Card(
#         class_="ma-2 pa-3",
#         hover=True,
#         style="cursor: pointer; ...", # Add pointer cursor

#     ):
#         with solara.Row(style="align-items: center; flex-grow:1;"):
#             if species.get("image_url"):
#                 rv.Img(
#                     src=species["image_url"],
#                     height="100px",
#                     width="100px",
#                     aspect_ratio="1",
#                     class_="mr-3 elevation-1",
#                     style="border-radius: 4px; object-fit: cover;",
#                 )
#             else:
#                 rv.Icon(children=["mdi-bug"], size="100px", class_="mr-3", color=COLOR_PRIMARY)

#             with solara.Column(align="start", style="overflow: hidden;"):
#                 species_id = species.get("id")
#                 # Wrap the entire content in a Link for better UX
#                 with solara.Link(path_or_route=f"/info/{species_id}"):
#                     solara.Markdown(
#                         f"#### {species.get('scientific_name', 'N/A')}",
#                         style=f"font-family: {FONT_HEADINGS}; margin-bottom: 0px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: {COLOR_PRIMARY}; text-decoration: none;",
#                     )

#                     solara.Text(
#                         species.get("common_name", ""),
#                         style="font-size: 0.9em; color: #555; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;",
#                     )

#                 # Keep status chip outside the link for better UX
#                 status = str(species.get("vector_status", "Unknown")).lower()
#                 status_color, text_c = "grey", "black"
#                 if status == "high":
#                     status_color, text_c = "red", "white"
#                 elif status == "medium":
#                     status_color, text_c = "orange", "white"
#                 elif status == "low":
#                     status_color, text_c = "green", "white"
#                 rv.Chip(
#                     small=True,
#                     children=[f"Vector: {species.get('vector_status', 'Unknown')}"],
#                     color=status_color,
#                     class_="mt-1",
#                     text_color=text_c,
#                 )



@solara.component
def SpeciesGalleryPageComponent():
    # solara.Style("""
    # .card-link {
    #    text-decoration: none;
    #    color: inherit;
    # }
    # """)

    with solara.AppBar():  # Keep if you have an AppBar
        solara.lab.ThemeToggle()  # Keep if used

    search_query, set_search_query = solara.use_state("")

    def _load_species_list_data_effect() -> Optional[Callable[[], None]]:
        task_ref = [cast(Optional[asyncio.Task], None)]

        async def _async_load_task():
            params = {}
            if search_query:
                params["search"] = search_query

            data = await fetch_api_data(
                SPECIES_LIST_ENDPOINT,
                params=params,
                loading_reactive=species_list_loading_reactive,
                error_reactive=species_list_error_reactive,
            )

            print("---- Received Species List API Data ----")
            print(data)  # Crucial for checking 'id' field
            print("--------------------------------------")

            actual_species_list = []
            if isinstance(data, dict) and "species" in data and isinstance(data["species"], list):
                actual_species_list = data["species"]
                print(
                    f"Page Effect: Setting species list from dict (count={data.get('count', len(actual_species_list))})"
                )
            elif isinstance(data, list):
                actual_species_list = data
                print(f"Page Effect: Setting species list from direct list (count={len(actual_species_list)})")
            else:
                print(f"Warning: Unexpected data format from species list API: {type(data)}. List empty.")
                species_list_error_reactive.value = (
                    species_list_error_reactive.value or "Unexpected data format from API."
                )

            current_task = task_ref[0]
            if not (current_task and current_task.cancelled()):
                species_list_data_reactive.value = actual_species_list
            else:
                print(f"Species list load task for search '{search_query}' was cancelled before setting data.")

        task_ref[0] = asyncio.create_task(_async_load_task())

        def cleanup():
            current_task = task_ref[0]
            if current_task and not current_task.done():
                print(f"Cleaning up: Cancelling species list task for search '{search_query}'")
                current_task.cancel()

        return cleanup

    solara.use_effect(_load_species_list_data_effect, [search_query])

    displayed_species = species_list_data_reactive.value

    with solara.Column(
        style="padding-bottom: 20px; min-height: calc(100vh - 120px);"
    ):  # Adjust min-height based on AppBar/Footer
        solara.Markdown(
            "# Mosquito Species Gallery", style=f"font-family: {FONT_HEADINGS}; text-align:center; margin-bottom:20px;"
        )
        with solara.Row(
            classes=["pa-2 ma-2 elevation-1"],  # Removed sticky-search-bar, add style directly if needed
            style="border-radius: 6px; background-color: var(--solara-card-background-color); align-items: center; gap: 10px; position: sticky; top: 0px; z-index:10; margin-bottom:10px;",
        ):
            solara.InputText(
                label="Search by name...",
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
                # dense=True, # dense might make it too small
                on_click=lambda: solara.Warning("Filter panel not yet implemented."),
            )

        if species_list_loading_reactive.value:
            solara.SpinnerSolara(size="60px")
        elif species_list_error_reactive.value:
            solara.Error(
                f"Could not load species: {species_list_error_reactive.value}",
                icon="mdi-alert-circle-outline",
            )
        elif displayed_species:  # Check if list is not None
            if not displayed_species:  # Empty list
                solara.Info(
                    "No species found matching your criteria.", icon="mdi-information-outline", style="margin: 16px;"
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
                    for species_item in displayed_species:
                        # item_id = species_item.get(
                        #     "id"
                        # )  # Crucial: ensure 'id' is the correct key and gives a string or int
                        # if item_id is None:
                        #     print(
                        #         f"Warning: Species item {species_item.get('scientific_name', 'Unknown')} is missing an 'id'. Card will not be clickable for details."
                        #     )
                        # # Render the species card (now with proper linking)
                        SpeciesCard(species_item)
        else:  # displayed_species is None (should not happen if initialized to [])
            solara.Info(
                "Initializing species data or an unexpected issue occurred.",
                icon="mdi-information-outline",
                style="margin: 16px;",
            )

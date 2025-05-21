import solara
import solara.lab
from solara.alias import rv  # Make sure rv is imported
from typing import List, Optional, cast, Dict, Any, Callable  # typing.List is fine for type hints
import asyncio

# Updated config import to include DISEASE_DETAIL_ENDPOINT_TEMPLATE
from ...config import SPECIES_DETAIL_ENDPOINT_TEMPLATE, DISEASE_DETAIL_ENDPOINT_TEMPLATE
from ...state import fetch_api_data
from ...config import COLOR_PRIMARY, FONT_HEADINGS, COLOR_TEXT
from ...state import selected_species_item_id

# Import DiseaseCard to display related diseases
from frontend.components.diseases.disease_card import DiseaseCard

print("DEBUG: SPECIES_DETAIL.PY module loaded")


@solara.component
def SpeciesDetailPageComponent():
    # with solara.AppBar():
    #     solara.lab.ThemeToggle()

    species_id = selected_species_item_id.value
    router = solara.use_router()

    species_data, set_species_data = solara.use_state(cast(Optional[Dict[str, Any]], None))
    loading, set_loading = solara.use_state(False)
    error, set_error = solara.use_state(cast(Optional[str], None))

    related_diseases_data, set_related_diseases_data = solara.use_state(cast(List[Dict[str, Any]], []))
    diseases_loading, set_diseases_loading = solara.use_state(False)
    diseases_error, set_diseases_error = solara.use_state(cast(Optional[str], None))

    print(f"DEBUG: SPECIES_DETAIL.PY - Initializing for species_id: '{species_id}'")

    def _fetch_species_detail_effect() -> Optional[Callable[[], None]]:
        task_ref = [cast(Optional[asyncio.Task], None)]

        async def _async_task():
            print(f"DEBUG: SPECIES_DETAIL.PY _fetch_species_detail_effect for ID: '{species_id}' - Task started.")
            if not species_id:
                print("DEBUG: SPECIES_DETAIL.PY Effect: No species_id provided.")
                set_species_data(None)
                set_error("No species ID specified.")
                set_loading(False)
                set_related_diseases_data([])
                set_diseases_loading(False)
                set_diseases_error(None)
                return

            print(f"DEBUG: SPECIES_DETAIL.PY Effect: Attempting to fetch data for '{species_id}'")
            set_species_data(None)
            set_error(None)
            set_loading(True)
            set_related_diseases_data([])
            set_diseases_loading(False)
            set_diseases_error(None)

            disease_ids_to_fetch = []  # Initialize here

            try:
                url = SPECIES_DETAIL_ENDPOINT_TEMPLATE.format(species_id=species_id)
                print(f"DEBUG: SPECIES_DETAIL.PY Effect: Fetching URL: {url}")
                data = await fetch_api_data(url)

                current_task_check_one = task_ref[0]
                if current_task_check_one and current_task_check_one.cancelled():
                    print(f"DEBUG: SPECIES_DETAIL.PY Effect task for {species_id} was cancelled post-species-await.")
                    return

                if data is None:
                    print(f"DEBUG: SPECIES_DETAIL.PY Effect: No data returned for {species_id}")
                    set_error(f"Details for '{species_id}' not found or an API error occurred.")
                    set_species_data(None)
                else:
                    print(f"DEBUG: SPECIES_DETAIL.PY Effect: Data received for {species_id}: {data}")
                    set_species_data(data)
                    set_error(None)

                    disease_ids_to_fetch = data.get("related_diseases", [])

                    if disease_ids_to_fetch:
                        print(
                            f"DEBUG: SPECIES_DETAIL.PY: Found {len(disease_ids_to_fetch)} related disease IDs to fetch."
                        )
                        set_diseases_loading(True)
                        fetched_diseases_list = []
                        for disease_id_to_fetch in disease_ids_to_fetch:
                            current_task_check_loop = task_ref[0]
                            if current_task_check_loop and current_task_check_loop.cancelled():
                                print(
                                    f"DEBUG: SPECIES_DETAIL.PY: Task cancelled during related diseases fetch loop for species {species_id}."
                                )
                                raise asyncio.CancelledError

                            disease_url = DISEASE_DETAIL_ENDPOINT_TEMPLATE.format(disease_id=disease_id_to_fetch)
                            print(f"DEBUG: SPECIES_DETAIL.PY: Fetching related disease from URL: {disease_url}")
                            disease_item_data = await fetch_api_data(disease_url)
                            if disease_item_data:
                                fetched_diseases_list.append(disease_item_data)
                            else:
                                print(f"Warning: Could not fetch details for disease ID {disease_id_to_fetch}")

                        current_task_check_two = task_ref[0]
                        if not (current_task_check_two and current_task_check_two.cancelled()):
                            set_related_diseases_data(fetched_diseases_list)
                        else:
                            print(
                                f"DEBUG: SPECIES_DETAIL.PY: Task cancelled before setting related_diseases_data for species {species_id}."
                            )

                        set_diseases_loading(False)  # Moved inside 'if disease_ids_to_fetch'
                    else:
                        print(f"DEBUG: SPECIES_DETAIL.PY: No related disease IDs found for species {species_id}.")
                        set_related_diseases_data([])
                        set_diseases_loading(False)  # Ensure it's false if no IDs

            except asyncio.CancelledError:
                print(f"DEBUG: SPECIES_DETAIL.PY Effect _async_task for {species_id} was cancelled.")
            except Exception as e:
                print(f"DEBUG: SPECIES_DETAIL.PY Effect: Unexpected error in _async_task for {species_id}: {e}")
                set_error(f"An unexpected error occurred: {str(e)}")
                set_species_data(None)
                set_related_diseases_data([])
                set_diseases_error(f"Failed to load related diseases due to a main task error: {str(e)}")
            finally:
                if not (task_ref[0] and task_ref[0].cancelled()):
                    set_loading(False)
                    if disease_ids_to_fetch:  # Only if we attempted to load them
                        set_diseases_loading(False)  # Redundant if already set, but safe
                print(
                    f"DEBUG: SPECIES_DETAIL.PY Effect: Fetch process finished for {species_id}. Loading states: species_loading={loading}, diseases_loading={diseases_loading}"
                )

        task_ref[0] = asyncio.create_task(_async_task())
        print(f"DEBUG: SPECIES_DETAIL.PY _fetch_species_detail_effect for ID: '{species_id}' - Task created.")

        def cleanup():
            current_task = task_ref[0]
            if current_task and not current_task.done():
                print(f"DEBUG: SPECIES_DETAIL.PY Cleanup: Cancelling task for ID {species_id}")
                current_task.cancel()
            else:
                print(f"DEBUG: SPECIES_DETAIL.PY Cleanup: Task for ID {species_id} already done or no task found.")

        return cleanup

    solara.use_effect(_fetch_species_detail_effect, [species_id])

    with solara.Column(align="center", classes=["pa-4"], style="max-width: 900px; margin: auto;"):
        solara.Button(
            "Go to Species Gallery",
            icon_name="mdi-arrow-left",
            text=True,
            outlined=True,
            color=COLOR_PRIMARY,
            classes=["mb-4", "align-self-start"],
            on_click=lambda: selected_species_item_id.set(None),
        )

        if loading:  # Use .value for reactive variables in conditional rendering
            print(f"DEBUG: SPECIES_DETAIL.PY - Rendering loading spinner for {species_id}")
            solara.SpinnerSolara(size="60px")
        elif error:
            print(f"DEBUG: SPECIES_DETAIL.PY - Rendering error message: {error}")
            solara.Error(
                f"Could not load species details: {error}",
                icon="mdi-alert-circle-outline",
                style="margin-top: 20px;",
            )
        elif not species_id:
            print(
                f"DEBUG: SPECIES_DETAIL.PY - Rendering 'no species ID specified' because species_id is '{species_id}'"
            )
            solara.Info("No species ID specified.", icon="mdi-information-outline", style="margin-top: 20px;")
        elif not species_data:
            print(f"DEBUG: SPECIES_DETAIL.PY - Rendering 'details not found' for {species_id} (data is None/empty)")
            solara.Info(
                f"Species details for '{species_id}' not found or are unavailable.",
                icon="mdi-information-outline",
                style="margin-top: 20px;",
            )
        else:
            # Species details are loaded, render them
            _species_data = species_data  # Use a local variable for the current value
            print(f"DEBUG: SPECIES_DETAIL.PY - Rendering species data for: {_species_data.get('scientific_name')}")
            solara.Title(f"Species Details: {_species_data.get('scientific_name')}")
            solara.Markdown(
                f"# {_species_data.get('scientific_name', 'N/A')}",
                style=f"font-family: {FONT_HEADINGS}; text-align: center; margin-bottom: 5px;",
            )
            if common_name := _species_data.get("common_name"):
                solara.Text(
                    f"({common_name})", style="text-align: center; font-size: 1.2em; color: #555; margin-bottom: 20px;"
                )
            rv.Divider(style_="margin: 15px 0;")

            with solara.Row(style="margin-top:20px; gap: 20px;", justify="center"):
                with solara.Column(align="center"):
                    if _species_data.get("image_url"):
                        rv.Img(
                            src=_species_data["image_url"],
                            width="100%",
                            max_width="350px",
                            style_="border-radius: 8px; object-fit:cover; border: 1px solid #eee; box-shadow: 0 2px 8px rgba(0,0,0,0.1);",
                        )
                    else:
                        rv.Icon(
                            children=["mdi-image-off"],
                            size="200px",
                            color="grey",
                            style_="display:block; margin:auto; width:100%; max-height:300px; border: 1px dashed #ccc; border-radius: 8px; padding: 20px;",
                        )

                    status_detail = str(_species_data.get("vector_status", "Unknown")).lower()
                    status_color_detail, text_color_detail = "blue-grey", "white"
                    if status_detail == "high":
                        status_color_detail = "red"
                    elif status_detail == "medium":
                        status_color_detail = "orange"
                    elif status_detail == "low":
                        status_color_detail = "green"
                    elif status_detail == "unknown":
                        status_color_detail, text_color_detail = "grey", "black"
                    rv.Chip(
                        children=[f"Vector Status: {_species_data.get('vector_status', 'Unknown')}"],
                        color=status_color_detail,
                        text_color=text_color_detail,
                        class_="mt-3 pa-2 elevation-1",
                        style_="font-size: 1em;",
                    )

                with solara.Column():
                    if desc := _species_data.get("description"):
                        solara.Markdown(f"### Description\n{desc}")
                    else:
                        solara.Text("No description available.", style="font-style: italic; color: #777;")

                    if chars := _species_data.get("key_characteristics"):
                        solara.Markdown("### Key Identifying Characteristics")
                        # --- CORRECTED LIST RENDERING ---
                        with rv.List(  # Changed from solara.List
                            dense=True,
                            style_="padding-left:0; list-style-position: inside;",  # Changed style_ to style
                        ):
                            for char_item in chars:  # Renamed char to char_item to avoid conflict if char is imported
                                rv.ListItem(
                                    children=[f"• {char_item}"], style_="padding-left:0; margin-bottom:2px;"
                                )  # Changed from solara.ListItem, style_ to style
                        # --- END OF CORRECTION ---

                    if regions := _species_data.get("geographic_regions"):
                        # Ensure regions is a list of strings before joining
                        if isinstance(regions, list) and all(isinstance(r, str) for r in regions):
                            solara.Markdown(f"### Geographic Distribution\n{', '.join(regions)}")
                        elif isinstance(
                            regions, list
                        ):  # If it's a list but not all strings, display differently or log
                            solara.Markdown(f"### Geographic Distribution\n" + "; ".join(map(str, regions)))

            solara.Markdown(
                "## Related Diseases Transmitted",
                style=f"font-family: {FONT_HEADINGS}; text-align: center; margin-top: 30px; margin-bottom: 15px;",
            )

            if diseases_loading:
                solara.SpinnerSolara(size="40px")
            elif diseases_error:
                solara.Error(
                    f"Could not load related diseases: {diseases_error}", icon="mdi-alert-circle-outline"
                )
            elif not related_diseases_data and not _species_data.get("related_diseases"):
                solara.Info("No related diseases are listed for this species.")
            elif not related_diseases_data and _species_data.get("related_diseases"):
                solara.Warning(
                    "Related diseases are listed but could not be loaded. Please try again later.",
                    icon="mdi-alert-outline",
                )
            elif related_diseases_data:
                with solara.ColumnsResponsive(
                    default=[12, 6, 4],
                    small=[12],
                    medium=[6, 6],
                    large=[4, 4, 4],
                    xlarge=[3, 3, 3, 3],
                    gutters="16px",
                    classes=["pa-2", "mt-2"],
                ):
                    for disease_item in related_diseases_data:
                        DiseaseCard(disease_item)
            else:
                solara.Info("Information on related diseases is currently unavailable.")

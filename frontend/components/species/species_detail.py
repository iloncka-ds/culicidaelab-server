import solara
import solara.lab
from solara.alias import rv
from typing import List, Optional, cast, Dict, Any, Callable
import asyncio
from ...config import SPECIES_DETAIL_ENDPOINT_TEMPLATE
from ...state import fetch_api_data
from ...config import COLOR_PRIMARY, FONT_HEADINGS, COLOR_TEXT
from ...state import selected_species_item_id

print("DEBUG: SPECIES_DETAIL.PY module loaded")


@solara.component
def SpeciesDetailPageComponent():
    with solara.AppBar():
        solara.lab.ThemeToggle()


    species_id = selected_species_item_id.value
    router = solara.use_router()
    # Get the item ID from the URL path
    path_parts = router.parts
    # species_id = None
    print(f"DEBUG: SPECIES_DETAIL.PY - router parts {router.parts}")
    # Parse the item ID from the URL path (format: /item/{id})
    if len(path_parts) >= 2 and path_parts[0] == "species":
        try:
            # species_id = path_parts[1]
            print(f"DEBUG: SPECIES_DETAIL.PY - {path_parts[1]}")
        except ValueError:
            print(f"DEBUG: SPECIES_DETAIL.PY - router parts {router.parts}")


    # State for this page
    species_data, set_species_data = solara.use_state(cast(Optional[Dict[str, Any]], None))
    loading, set_loading = solara.use_state(False)
    error, set_error = solara.use_state(cast(Optional[str], None))

    print(f"DEBUG: SPECIES_DETAIL.PY - Initializing for species_id: '{species_id}'")

    def _fetch_species_detail_effect() -> Optional[Callable[[], None]]:
        task_ref = [cast(Optional[asyncio.Task], None)]

        async def _async_task():
            print(f"DEBUG: SPECIES_DETAIL.PY _fetch_species_detail_effect for ID: '{species_id}' - Task started.")
            if not species_id:
                print("DEBUG: SPECIES_DETAIL.PY Effect: No species_id provided.")
                set_species_data(None)
                set_error("No species ID specified in URL.")
                set_loading(False)
                return

            print(f"DEBUG: SPECIES_DETAIL.PY Effect: Attempting to fetch data for '{species_id}'")
            set_species_data(None)
            set_error(None)
            set_loading(True)
            try:
                url = SPECIES_DETAIL_ENDPOINT_TEMPLATE.format(species_id=species_id)
                print(f"DEBUG: SPECIES_DETAIL.PY Effect: Fetching URL: {url}")
                data = await fetch_api_data(url)

                current_task = task_ref[0]
                if current_task and current_task.cancelled():
                    print(f"DEBUG: SPECIES_DETAIL.PY Effect task for {species_id} was cancelled post-await.")
                    return

                if data is None:
                    print(f"DEBUG: SPECIES_DETAIL.PY Effect: No data returned for {species_id}")
                    set_error(f"Details for '{species_id}' not found or an API error occurred.")
                    set_species_data(None)
                else:
                    print(f"DEBUG: SPECIES_DETAIL.PY Effect: Data received for {species_id}: {data}")
                    set_species_data(data)
                    set_error(None)
            except asyncio.CancelledError:
                print(f"DEBUG: SPECIES_DETAIL.PY Effect _async_task for {species_id} was cancelled.")
                raise
            except Exception as e:
                print(f"DEBUG: SPECIES_DETAIL.PY Effect: Unexpected error in _async_task for {species_id}: {e}")
                set_error(f"An unexpected error occurred: {str(e)}")
                set_species_data(None)
            finally:
                set_loading(False)
                print(
                    f"DEBUG: SPECIES_DETAIL.PY Effect: Fetch process finished for {species_id}. Loading state: {loading}"
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

    # The dependency for the effect is 'species_id'. When route_current changes
    # such that 'species_id' changes, this effect will re-run.
    solara.use_effect(_fetch_species_detail_effect, [species_id])

    # --- Page Layout ---
    with solara.Column(align="center", classes=["pa-4"], style="max-width: 900px; margin: auto;"):
        # with solara.Link("/species"):
        solara.Button(
            "Go to Species Gallery",
            icon_name="mdi-arrow-left",
            text=True,
            outlined=True,
            color=COLOR_PRIMARY,
            classes=["mb-4", "align-self-start"],
            on_click=lambda: selected_species_item_id.set(None),
        )

        if loading:
            print(f"DEBUG: SPECIES_DETAIL.PY - Rendering loading spinner for {species_id}")
            solara.SpinnerSolara(size="60px")
        elif error:
            print(f"DEBUG: SPECIES_DETAIL.PY - Rendering error message: {error}")
            solara.Error(
                f"Could not load species details: {error}", icon="mdi-alert-circle-outline", style="margin-top: 20px;"
            )
        elif not species_id:
            print(
                f"DEBUG: SPECIES_DETAIL.PY - Rendering 'no species ID specified' because species_id is '{species_id}'"
            )
            solara.Info(
                "No species ID specified in the URL.", icon="mdi-information-outline", style="margin-top: 20px;"
            )
        elif not species_data:
            print(f"DEBUG: SPECIES_DETAIL.PY - Rendering 'details not found' for {species_id} (data is None/empty)")
            solara.Info(
                f"Species details for '{species_id}' not found or are unavailable.",
                icon="mdi-information-outline",
                style="margin-top: 20px;",
            )
        else:
            print(f"DEBUG: SPECIES_DETAIL.PY - Rendering species data for: {species_data.get('scientific_name')}")
            solara.Title(f"Item Details: {species_data.get('scientific_name')}")
            solara.Markdown(
                f"# {species_data.get('scientific_name', 'N/A')}",
                style=f"font-family: {FONT_HEADINGS}; text-align: center; margin-bottom: 5px;",
            )
            if common_name := species_data.get("common_name"):
                solara.Text(
                    f"({common_name})", style="text-align: center; font-size: 1.2em; color: #555; margin-bottom: 20px;"
                )
            rv.Divider(style="margin: 15px 0;")

            with solara.Row(style="margin-top:20px; gap: 20px;", justify="center"):
                with solara.Column( align="center"):  # Image and status chip column
                    if species_data.get("image_url"):
                        rv.Img(
                            src=species_data["image_url"],
                            width="100%",
                            max_width="350px",  # constrain image size
                            style="border-radius: 8px; object-fit:cover; border: 1px solid #eee; box-shadow: 0 2px 8px rgba(0,0,0,0.1);",
                        )
                    else:
                        rv.Icon(
                            children=["mdi-image-off"],
                            size="200px",
                            color="grey",
                            style="display:block; margin:auto; width:100%; max-height:300px; border: 1px dashed #ccc; border-radius: 8px; padding: 20px;",
                        )

                    status_detail = str(species_data.get("vector_status", "Unknown")).lower()
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
                        children=[f"Vector Status: {species_data.get('vector_status', 'Unknown')}"],
                        color=status_color_detail,
                        text_color=text_color_detail,
                        class_="mt-3 pa-2 elevation-1",  # Make chip a bit more prominent
                        style="font-size: 1em;",
                    )

                with solara.Column():  # Text details column
                    if desc := species_data.get("description"):
                        solara.Markdown(f"### Description\n{desc}")
                    else:
                        solara.Text("No description available.", style="font-style: italic; color: #777;")

                    if chars := species_data.get("key_characteristics"):
                        solara.Markdown("### Key Identifying Characteristics")
                        with solara.List(
                            dense=True, style_="padding-left:0; list-style-position: inside;"
                        ):  # Use ul/li for semantics
                            for char in chars:
                                solara.ListItem(children=[f"• {char}"], style_="padding-left:0; margin-bottom:2px;")

                    if regions := species_data.get("geographic_regions"):
                        solara.Markdown(f"### Geographic Distribution\n{', '.join(regions)}")

                    if diseases := species_data.get("related_diseases"):
                        solara.Markdown(f"### Related Diseases\n{', '.join(diseases)}")

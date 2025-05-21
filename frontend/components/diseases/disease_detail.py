import solara
import solara.lab
from solara.alias import rv
from typing import List, Optional, cast, Dict, Any, Callable
import asyncio
from ...config import DISEASE_DETAIL_ENDPOINT_TEMPLATE, SPECIES_LIST_ENDPOINT
from ...state import fetch_api_data, selected_disease_item_id
from ...config import COLOR_PRIMARY, FONT_HEADINGS, COLOR_TEXT
from frontend.components.species.species_card import SpeciesCard

print("DEBUG: DISEASE_DETAIL.PY module loaded")


@solara.component
def DiseaseDetailPageComponent():
    # with solara.AppBar():
    #     solara.lab.ThemeToggle()

    disease_id = selected_disease_item_id.value
    # router = solara.use_router()
    # # Get the disease ID from the URL path
    # path_parts = router.parts

    # print(f"DEBUG: DISEASE_DETAIL.PY - router parts {router.parts}")
    # # Parse the disease ID from the URL path (format: /diseases/{id})
    # if len(path_parts) >= 2 and path_parts[0] == "diseases":
    #     try:
    #         disease_id = path_parts[1]
    #         print(f"DEBUG: DISEASE_DETAIL.PY - {disease_id}")
    #     except ValueError:
    #         print(f"DEBUG: DISEASE_DETAIL.PY - router parts {router.parts}")


    # State for this page
    disease_data, set_disease_data = solara.use_state(cast(Optional[Dict[str, Any]], None))
    vectors_data, set_vectors_data = solara.use_state(cast(List[Dict[str, Any]], []))
    loading, set_loading = solara.use_state(False)
    vectors_loading, set_vectors_loading = solara.use_state(False)
    error, set_error = solara.use_state(cast(Optional[str], None))
    vectors_error, set_vectors_error = solara.use_state(cast(Optional[str], None))

    print(f"DEBUG: DISEASE_DETAIL.PY - Initializing for disease_id: '{disease_id}'")

    def _fetch_disease_detail_effect() -> Optional[Callable[[], None]]:
        task_ref = [cast(Optional[asyncio.Task], None)]

        async def _async_task():
            print(f"DEBUG: DISEASE_DETAIL.PY _fetch_disease_detail_effect for ID: '{disease_id}' - Task started.")
            if not disease_id:
                print("DEBUG: DISEASE_DETAIL.PY Effect: No disease_id provided.")
                set_disease_data(None)
                set_error("No disease ID specified in URL.")
                set_loading(False)
                return

            print(f"DEBUG: DISEASE_DETAIL.PY Effect: Attempting to fetch data for '{disease_id}'")
            set_disease_data(None)
            set_error(None)
            set_loading(True)
            try:
                url = DISEASE_DETAIL_ENDPOINT_TEMPLATE.format(disease_id=disease_id)
                print(f"DEBUG: DISEASE_DETAIL.PY Effect: Fetching URL: {url}")
                data = await fetch_api_data(url)

                current_task = task_ref[0]
                if current_task and current_task.cancelled():
                    print(f"DEBUG: DISEASE_DETAIL.PY Effect task for {disease_id} was cancelled post-await.")
                    return

                if data is None:
                    print(f"DEBUG: DISEASE_DETAIL.PY Effect: No data returned for {disease_id}")
                    set_error(f"Details for '{disease_id}' not found or an API error occurred.")
                    set_disease_data(None)
                else:
                    print(f"DEBUG: DISEASE_DETAIL.PY Effect: Data received for {disease_id}: {data}")
                    set_disease_data(data)
                    set_error(None)

                    # Fetch related vector species if the disease data contains vectors IDs
                    if vectors_ids := data.get("vectors", []):
                        set_vectors_loading(True)
                        try:
                            # We'll need to implement a fetch for each vector or create a batch API endpoint
                            vector_species = []
                            for vector_id in vectors_ids:
                                vector_data = await fetch_api_data(
                                    f"{SPECIES_LIST_ENDPOINT}/{vector_id}"
                                )
                                if vector_data:
                                    vector_species.append(vector_data)

                            set_vectors_data(vector_species)
                        except Exception as e:
                            print(f"DEBUG: DISEASE_DETAIL.PY Effect: Error fetching vector data: {e}")
                            set_vectors_error(f"Could not load vector species: {str(e)}")
                        finally:
                            set_vectors_loading(False)

            except asyncio.CancelledError:
                print(f"DEBUG: DISEASE_DETAIL.PY Effect _async_task for {disease_id} was cancelled.")
                raise
            except Exception as e:
                print(f"DEBUG: DISEASE_DETAIL.PY Effect: Unexpected error in _async_task for {disease_id}: {e}")
                set_error(f"An unexpected error occurred: {str(e)}")
                set_disease_data(None)
            finally:
                set_loading(False)
                print(
                    f"DEBUG: DISEASE_DETAIL.PY Effect: Fetch process finished for {disease_id}. Loading state: {loading}"
                )

        task_ref[0] = asyncio.create_task(_async_task())
        print(f"DEBUG: DISEASE_DETAIL.PY _fetch_disease_detail_effect for ID: '{disease_id}' - Task created.")

        def cleanup():
            current_task = task_ref[0]
            if current_task and not current_task.done():
                print(f"DEBUG: DISEASE_DETAIL.PY Cleanup: Cancelling task for ID {disease_id}")
                current_task.cancel()
            else:
                print(f"DEBUG: DISEASE_DETAIL.PY Cleanup: Task for ID {disease_id} already done or no task found.")

        return cleanup

    # The dependency for the effect is 'disease_id'. When route_current changes
    # such that 'disease_id' changes, this effect will re-run.
    solara.use_effect(_fetch_disease_detail_effect, [disease_id])

    # --- Page Layout ---
    with solara.Column(align="center", classes=["pa-4"], style="max-width: 900px; margin: auto;"):
        # with solara.Link("/diseases"):
        solara.Button(
            "Go to Disease Gallery",
            icon_name="mdi-arrow-left",
            text=True,
            outlined=True,
            color=COLOR_PRIMARY,
            classes=["mb-4 align-self-start"],
            on_click=lambda: selected_disease_item_id.set(None)
        )

        if loading:
            print(f"DEBUG: DISEASE_DETAIL.PY - Rendering loading spinner for {disease_id}")
            solara.SpinnerSolara(size="60px")
        elif error:
            print(f"DEBUG: DISEASE_DETAIL.PY - Rendering error message: {error}")
            solara.Error(
                f"Could not load disease details: {error}", icon="mdi-alert-circle-outline", style="margin-top: 20px;"
            )
        elif not disease_id:
            print(
                f"DEBUG: DISEASE_DETAIL.PY - Rendering 'no disease ID specified' because disease_id is '{disease_id}'"
            )
            solara.Info(
                "No disease ID specified in the URL.", icon="mdi-information-outline", style="margin-top: 20px;"
            )
        elif not disease_data:
            print(f"DEBUG: DISEASE_DETAIL.PY - Rendering 'details not found' for {disease_id} (data is None/empty)")
            solara.Info(
                f"Disease details for '{disease_id}' not found or are unavailable.",
                icon="mdi-information-outline",
                style="margin-top: 20px;",
            )
        else:
            print(f"DEBUG: DISEASE_DETAIL.PY - Rendering disease data for: {disease_data.get('name')}")
            solara.Title(f"Disease Details: {disease_data.get('name')}")
            solara.Markdown(
                f"# {disease_data.get('name', 'N/A')}",
                style=f"font-family: {FONT_HEADINGS}; text-align: center; margin-bottom: 20px;",
            )
            rv.Divider(style="margin: 15px 0;")

            with solara.Row(style="margin-top:20px; gap: 20px;", justify="center"):
                with solara.Column(align="center"):  # Image column
                    if disease_data.get("image_url"):
                        rv.Img(
                            src=disease_data["image_url"],
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

                    # Display prevalence as a chip
                    if prevalence := disease_data.get("prevalence"):
                        rv.Chip(
                            children=[f"Prevalence: {prevalence}"],
                            color="blue",
                            text_color="white",
                            class_="mt-3 pa-2 elevation-1",
                            style="font-size: 1em;",
                        )

                with solara.Column():  # Text details column
                    if desc := disease_data.get("description"):
                        solara.Markdown(f"### Description\n{desc}")
                    else:
                        solara.Text("No description available.", style="font-style: italic; color: #777;")

                    if symptoms := disease_data.get("symptoms"):
                        solara.Markdown(f"### Symptoms\n{symptoms}")

                    if treatment := disease_data.get("treatment"):
                        solara.Markdown(f"### Treatment\n{treatment}")

                    if prevention := disease_data.get("prevention"):
                        solara.Markdown(f"### Prevention\n{prevention}")

            # Vector Mosquito Species Section
            solara.Markdown(
                "## Vector Species",
                style=f"font-family: {FONT_HEADINGS}; text-align: center; margin-top: 30px; margin-bottom: 15px;",
            )

            if vectors_loading:
                solara.SpinnerSolara(size="40px")
            elif vectors_error:
                solara.Error(f"Could not load vector species: {vectors_error}")
            elif not vectors_data:
                solara.Info("No known vector species for this disease.")
            else:
                with solara.Row(justify="center", style="flex-wrap: wrap; gap: 16px;"):
                    for vector in vectors_data:
                        SpeciesCard(vector)
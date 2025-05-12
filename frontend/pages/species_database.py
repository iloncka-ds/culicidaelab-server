import solara
from solara.alias import rv
import httpx
import asyncio
from typing import Dict, Any, List, Optional, cast

# Relative imports for config and state
from ..config import (
    COLOR_PRIMARY,
    FONT_HEADINGS,
    COLOR_TEXT,
    SPECIES_LIST_ENDPOINT,  # For listing species
    SPECIES_DETAIL_ENDPOINT_TEMPLATE,  # For fetching single species detail
)

# --- Reactive States for Species Database Page ---
species_list_data_reactive = solara.reactive(cast(List[Dict[str, Any]], []))
species_list_loading_reactive = solara.reactive(False)
species_list_error_reactive = solara.reactive(cast(Optional[str], None))

# For SpeciesDetailView
detailed_species_data_reactive = solara.reactive(cast(Optional[Dict[str, Any]], None))
detailed_species_loading_reactive = solara.reactive(False)
detailed_species_error_reactive = solara.reactive(cast(Optional[str], None))


# --- API Helper ---
async def fetch_api_data(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    loading_reactive: Optional[solara.Reactive[bool]] = None,
    error_reactive: Optional[solara.Reactive[Optional[str]]] = None,
) -> Optional[Any]:
    if loading_reactive:
        loading_reactive.value = True
    if error_reactive:
        error_reactive.value = None  # Reset error on new attempt
    try:
        async with httpx.AsyncClient() as client:
            print(f"Fetching data from {url} with params {params if params else ''}")
            response = await client.get(url, params=params, timeout=20.0)
            response.raise_for_status()
            return response.json()
    except httpx.ReadTimeout:
        msg = f"Timeout fetching data from {url}."
        if error_reactive:
            error_reactive.value = msg
        print(msg)
        return None
    except httpx.HTTPStatusError as e:
        detail = e.response.text
        try:  # Try to parse detail if it's JSON
            detail_json = e.response.json()
            detail = detail_json.get("detail", detail)
        except Exception:
            pass
        msg = f"HTTP error {e.response.status_code} from {url}. Detail: {detail}"
        if error_reactive:
            error_reactive.value = msg
        print(msg)
        return None
    except Exception as e:
        msg = f"Failed to fetch data from {url}: {e}"
        if error_reactive:
            error_reactive.value = msg
        print(msg)
        return None
    finally:
        if loading_reactive:
            loading_reactive.value = False


# --- Components ---
@solara.component
def SpeciesCard(species: Dict[str, Any], on_click: callable):
    with rv.Card(
        class_="ma-2 pa-3",
        hover=True,
        onclick=on_click,
        style="border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); cursor: pointer; background-color: white; height: 100%; display: flex; flex-direction: column; justify-content: space-between;",  # Ensure card fills space
    ):
        with solara.Row(style="align-items: center; flex-grow:1;"):  # Allow content to grow
            if species.get("image_url"):
                rv.Img(
                    src=species["image_url"],
                    height="100px",
                    width="100px",
                    aspect_ratio="1",
                    class_="mr-3 elevation-1",
                    style="border-radius: 4px; object-fit: cover;",
                )
            else:
                rv.Icon(children=["mdi-bug"], size="100px", class_="mr-3", color=COLOR_PRIMARY)

            with solara.Column(align="start", style="overflow: hidden;"):  # Prevent text overflow issues
                solara.Markdown(
                    f"#### {species.get('scientific_name', 'N/A')}",
                    style=f"font-family: {FONT_HEADINGS}; margin-bottom: 0px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;",  # Handle long names
                )
                solara.Text(
                    species.get("common_name", ""),
                    style="font-size: 0.9em; color: #555; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;",
                )
                status = str(species.get("vector_status", "Unknown")).lower()
                status_color = "grey"
                text_c = "black"
                if status == "high":
                    status_color = "red"
                    text_c = "white"
                elif status == "medium":
                    status_color = "orange"
                    text_c = "white"
                elif status == "low":
                    status_color = "green"
                    text_c = "white"
                rv.Chip(
                    small=True,
                    children=[f"Vector: {species.get('vector_status', 'Unknown')}"],
                    color=status_color,
                    class_="mt-1",
                    text_color=text_c,
                )
        # Removed "Learn More" button as card is clickable


@solara.component
def SpeciesDetailView(species_id: str, on_close: callable):
    species = detailed_species_data_reactive.value
    loading = detailed_species_loading_reactive.value
    error = detailed_species_error_reactive.value

    def _fetch_species_detail_effect():
        # This task will be stored to be cancelled on cleanup
        task: Optional[asyncio.Task] = None

        async def _async_task():
            if not species_id:
                detailed_species_data_reactive.value = None
                detailed_species_error_reactive.value = None
                return

            detailed_species_data_reactive.value = None
            detailed_species_error_reactive.value = None

            url = SPECIES_DETAIL_ENDPOINT_TEMPLATE.format(species_id=species_id)
            # We are not assigning the result of fetch_api_data directly to detailed_species_data_reactive here
            # because the task might be cancelled. The reactive var is set inside the task.
            data = await fetch_api_data(
                url, loading_reactive=detailed_species_loading_reactive, error_reactive=detailed_species_error_reactive
            )
            # Only set if the task wasn't cancelled mid-way and we got data
            if not (task and task.cancelled()):  # Check if task is defined and not cancelled
                detailed_species_data_reactive.value = data

        # Create and store the task
        task = asyncio.create_task(_async_task())

        # Return a cleanup function
        def cleanup():
            if task and not task.done():
                print(f"Cleaning up: Cancelling SpeciesDetailView task for ID {species_id}")
                task.cancel()
                # Optionally, you could await task here with a try-except asyncio.CancelledError
                # but for fire-and-forget, just cancelling is often enough.

        return cleanup

    solara.use_effect(_fetch_species_detail_effect, [species_id])

    with rv.Dialog(
        v_model=True,
        on_v_model=lambda val: on_close() if not val else None,
        max_width="800px",
        scrollable=True,
    ) as dialog:
        with rv.Card(class_="pa-4"):
            if loading:
                solara.SpinnerSolara(size="50px", style="margin: 40px auto; display: block;")
                return dialog

            if error:
                solara.Error(f"Could not load species details: {error}", icon="mdi-alert-circle-outline")
                with rv.CardActions(class_="pt-3"):  # Add some padding top for the close button
                    solara.Button("Close", on_click=on_close, text=True, color=COLOR_PRIMARY)
                return dialog

            if not species:  # After loading and error checks, if species is still None
                solara.Info("Species details not found or not available.", icon="mdi-information-outline")
                with rv.CardActions(class_="pt-3"):
                    solara.Button("Close", on_click=on_close, text=True, color=COLOR_PRIMARY)
                return dialog

            # --- Display Species Details ---
            with solara.Row(justify="space-between", style="align-items: center;"):
                solara.Markdown(
                    f"## {species.get('scientific_name', 'N/A')} ({species.get('common_name', '')})",
                    style=f"font-family: {FONT_HEADINGS};",
                )
                solara.Button(icon_name="mdi-close", icon=True, on_click=on_close, color=COLOR_TEXT)
            rv.Divider(style="margin: 8px 0;")

            with solara.Row(gutters="16px", style="margin-top:10px;"):
                with solara.Column(md=5):
                    if species.get("image_url"):
                        rv.Img(
                            src=species["image_url"],
                            width="100%",
                            style="border-radius: 6px; object-fit:cover; max-height: 300px; border: 1px solid #eee;",
                        )
                    else:
                        rv.Icon(
                            children=["mdi-image-off"],
                            size="150px",
                            color="grey",
                            style="display:block; margin:auto; width:100%; height:auto; max-height:300px; border: 1px dashed #ccc; border-radius: 6px; padding: 20px;",
                        )

                    status_detail = str(species.get("vector_status", "Unknown")).lower()
                    status_color_detail = "blue-grey"
                    text_color_detail = "white"
                    # Match chip colors from SpeciesCard for consistency
                    if status_detail == "high":
                        status_color_detail = "red"
                    elif status_detail == "medium":
                        status_color_detail = "orange"
                    elif status_detail == "low":
                        status_color_detail = "green"
                    elif status_detail == "unknown":
                        status_color_detail = "grey"
                        text_color_detail = "black"

                    rv.Chip(
                        children=[f"Vector Status: {species.get('vector_status', 'Unknown')}"],
                        color=status_color_detail,
                        text_color=text_color_detail,
                        class_="mt-2 d-block text-center",
                    )

                with solara.Column(md=7):
                    if species.get("description"):
                        solara.Markdown(f"**Description:** {species.get('description')}")
                    else:
                        solara.Text("No description available.", style="font-style: italic; color: #777;")

                    if species.get("key_characteristics"):
                        solara.Markdown("**Key Identifying Characteristics:**")
                        with solara.List(dense=True, style="padding-left:0;"):
                            for char in species.get("key_characteristics", []):
                                solara.ListItem(children=[char], style="padding-left:0; margin-bottom:2px;")

                    if species.get("geographic_regions"):
                        solara.Markdown(
                            f"**Geographic Distribution:** {', '.join(species.get('geographic_regions', ['N/A']))}"
                        )

                    if species.get("related_diseases"):
                        solara.Markdown(f"**Related Diseases:** {', '.join(species.get('related_diseases',[]))}")
                    # Example placeholder if API doesn't provide it
                    # else:
                    #      solara.Markdown("**Related Diseases (Example):** Dengue, Zika")

            with rv.CardActions(class_="justify-end pt-4"):  # Align close button to the right
                solara.Button("Close", on_click=on_close, text=True, color=COLOR_PRIMARY)
    return dialog


@solara.component
def Page():
    search_query, set_search_query = solara.use_state("")
    selected_species_id_for_detail, set_selected_species_id_for_detail = solara.use_state(cast(Optional[str], None))

    def _load_species_list_data_effect():
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
            species_list_data_reactive.value = data if data is not None else []

        asyncio.create_task(_async_load_task())

    solara.use_effect(_load_species_list_data_effect, [search_query])

    displayed_species = species_list_data_reactive.value

    with solara.Column(style="padding-bottom: 20px; min-height: calc(100vh - 120px);"):  # Ensure it takes decent height
        solara.Markdown(
            "# Mosquito Species Gallery", style=f"font-family: {FONT_HEADINGS}; text-align:center; margin-bottom:20px;"
        )

        with solara.Row(
            classes=["pa-2 ma-2 elevation-1 sticky-search-bar"],  # Add a class for potential sticky CSS
            style="border-radius: 6px; background-color: white; align-items: center; gap: 10px; z-index:10; position: sticky; top: 0px; margin-bottom:10px;",  # Basic sticky
        ):
            solara.InputText(
                label="Search by name...",
                value=search_query,
                on_value=set_search_query,
                continuous_update=False,  # Trigger API on blur/enter
                style="flex-grow: 1;",

            )
            solara.Button(
                "Filters",
                icon_name="mdi-filter-variant",
                outlined=True,
                color=COLOR_PRIMARY,
                dense=True,
                on_click=lambda: solara.Warning("Filter panel for species database not yet implemented."),
            )

        if species_list_loading_reactive.value:
            solara.SpinnerSolara(size="60px")
        elif species_list_error_reactive.value:
            solara.Error(
                f"Could not load species: {species_list_error_reactive.value}",
                style="margin: 20px;",
                icon="mdi-alert-circle-outline",
            )
        elif displayed_species:  # Check if displayed_species is not None
            if not displayed_species:  # API returned empty list (e.g., for the search)
                solara.Info(
                    "No species found matching your criteria.", icon="mdi-information-outline", style="margin: 16px;"
                )
            else:  # Non-empty list
                with solara.ColumnsResponsive(
                    # Default to 4 columns on xl, 3 on lg, 2 on md, 1 on sm
                    default=[3, 3, 3, 3],
                    large=[4, 4, 4],
                    medium=[6, 6],
                    small=[12],
                    gutters="16px",
                    classes=["pa-2"],
                ):
                    for species_item in displayed_species:
                        # Wrap SpeciesCard in a Div to ensure ColumnsResponsive children are direct Solara elements if needed by layout engine
                        # Or ensure SpeciesCard itself is a direct solara.component at its root. It is.
                        SpeciesCard(
                            species_item,
                            on_click=lambda s_id=species_item.get("id"): set_selected_species_id_for_detail(s_id)
                            if s_id
                            else None,
                        )
        else:  # This case should ideally not be hit if species_list_data_reactive defaults to [] and is set to [] on error
            solara.Info(
                "Initializing species data or an unexpected issue occurred.",
                icon="mdi-information-outline",
                style="margin: 16px;",
            )

        if selected_species_id_for_detail:
            SpeciesDetailView(
                species_id=selected_species_id_for_detail,
                on_close=lambda: (
                    set_selected_species_id_for_detail(None),
                    # Optionally clear detail view states when dialog is closed by user action (ESC, close button)
                    # This ensures fresh data if reopened for the same ID later, though effect should handle it.
                    # detailed_species_data_reactive.value = None,
                    # detailed_species_error_reactive.value = None
                ),
            )

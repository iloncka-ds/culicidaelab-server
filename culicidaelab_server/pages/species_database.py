import solara
from solara.alias import rv  # For Vuetify components
from typing import Dict, Any

# Relative imports for config and state
from ..config import COLOR_PRIMARY, FONT_HEADINGS, COLOR_TEXT

# Mock data for species - replace with API call and reactive state later
MOCK_SPECIES_DATA = [
    {
        "id": "aedes_albopictus",
        "scientific_name": "Aedes albopictus",
        "common_name": "Asian Tiger Mosquito",
        "vector_status": "High",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Aedes_albopictus_PCSL_00000090_00.jpg/320px-Aedes_albopictus_PCSL_00000090_00.jpg",  # Placeholder
        "description": "Known for its black and white striped legs and body. A significant vector for dengue, chikungunya, and Zika.",
        "geographic_regions": ["Asia", "Europe", "Americas", "Africa"],
        "key_characteristics": ["Distinct white stripe on dorsal thorax", "Bites aggressively during the day"],
    },
    {
        "id": "aedes_aegypti",
        "scientific_name": "Aedes aegypti",
        "common_name": "Yellow Fever Mosquito",
        "vector_status": "High",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Aedes_Aegypti_Feeding.jpg/320px-Aedes_Aegypti_Feeding.jpg",  # Placeholder
        "description": "Primary vector for yellow fever, dengue, chikungunya, and Zika. Prefers urban habitats.",
        "geographic_regions": ["Tropics", "Subtropics Worldwide"],
        "key_characteristics": ["Lyre-shaped silver markings on thorax", "Prefers to feed on humans"],
    },
    {
        "id": "culex_pipiens",
        "scientific_name": "Culex pipiens",
        "common_name": "Common House Mosquito",
        "vector_status": "Medium",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/CulexPipiens.jpg/320px-CulexPipiens.jpg",  # Placeholder
        "description": "Vector for West Nile virus and St. Louis encephalitis. Often breeds in stagnant water.",
        "geographic_regions": ["Worldwide"],
        "key_characteristics": ["Brownish body with crossbands on abdomen", "Primarily bites at dusk and night"],
    },
]


@solara.component
def SpeciesCard(species: Dict[str, Any], on_click: callable):
    # Card styling from layout_INPUT.md: box-shadow, border-radius, padding
    with rv.Card(
        class_="ma-2 pa-3",  # Vuetify margin and padding
        hover=True,
        onclick=on_click,  # Use Vuetify's onclick for the card
        style="""
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            cursor: pointer; /* Indicate clickable */
            background-color: white; /* Card background */
        """,
    ):
        with solara.Row(style="align-items: center;"):
            if species.get("image_url"):
                # Using rv.Img for more control over aspect ratio, etc.
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

            with solara.Column(align="center"):
                solara.Markdown(
                    f"#### {species.get('scientific_name', 'N/A')}",
                    style=f"font-family: {FONT_HEADINGS}; margin-bottom: 0px;",
                )
                solara.Text(species.get("common_name", ""), style="font-size: 0.9em; color: #555;")
                # Vector status indicator (color-coded)
                status_color = "grey"
                if species.get("vector_status", "").lower() == "high":
                    status_color = "red"
                elif species.get("vector_status", "").lower() == "medium":
                    status_color = "orange"
                elif species.get("vector_status", "").lower() == "low":
                    status_color = "green"
                rv.Chip(
                    small=True,
                    children=[f"Vector: {species.get('vector_status', 'Unknown')}"],
                    color=status_color,
                    class_="mt-1",
                )

        # Hidden "Learn More" that is part of the card click action
        # solara.Button("Learn More", outlined=True, small=True, on_click=on_click, class_="mt-2", color=COLOR_PRIMARY)


@solara.component
def SpeciesDetailView(species_id: str, on_close: callable):
    species = next((s for s in MOCK_SPECIES_DATA if s["id"] == species_id), None)

    if not species:
        return solara.Error("Species not found.")

    with rv.Dialog(
        v_model=True,  # Control visibility via a reactive var if needed, or manage via parent
        on_v_model=lambda val: on_close() if not val else None,  # Call on_close when dialog is closed
        max_width="800px",
        scrollable=True,
    ) as dialog:
        with rv.Card(class_="pa-4"):
            with solara.Row(justify="space-between", style="align-items: center;"):
                solara.Markdown(
                    f"## {species['scientific_name']} ({species.get('common_name', '')})",
                    style=f"font-family: {FONT_HEADINGS};",
                )
                solara.Button(icon_name="mdi-close", icon=True, on_click=on_close, color=COLOR_TEXT)

            solara.Divider()

            with solara.Row(gutters=True):
                with solara.Column():  # Image column
                    if species.get("image_url"):
                        rv.Img(
                            src=species["image_url"],
                            width="100%",
                            aspect_ratio="1.2",
                            style="border-radius: 6px; object-fit:cover;",
                        )
                    else:
                        rv.Icon(children=["mdi-image-off"], size="150px", color="grey")
                    rv.Chip(
                        small=True,
                        children=[f"Vector Status: {species.get('vector_status', 'Unknown')}"],
                        color="blue-grey",
                        class_="mt-2",
                    )

                with solara.Column():  # Details column
                    solara.Markdown(f"**Description:** {species.get('description', 'N/A')}")
                    solara.Markdown("**Key Identifying Characteristics:**")
                    with solara.List():
                        for char in species.get("key_characteristics", []):
                            solara.ListItem(children=[char])
                    solara.Markdown(
                        f"**Geographic Distribution:** {', '.join(species.get('geographic_regions', ['N/A']))}"
                    )

                    # Placeholder for related diseases
                    solara.Markdown("**Related Diseases (Example):** Dengue, Zika")
                    solara.Button(
                        "View Disease Info", small=True, outlined=True, color=COLOR_PRIMARY, class_="mt-1"
                    )  # Link to disease page

            rv.CardActions(children=[solara.Button("Close", on_click=on_close, text=True)])
    return dialog


@solara.component
def Page():
    # State for search, filters, and selected species for detail view
    search_query, set_search_query = solara.use_state("")
    # TODO: Add filter states (region, vector status)

    selected_species_id_for_detail, set_selected_species_id_for_detail = solara.use_state(None)

    # Filtered species based on search
    # In a real app, this would come from a reactive variable populated by an API call
    # that also takes search_query and other filters as parameters.

    # For now, client-side filtering of MOCK_SPECIES_DATA
    def get_filtered_species():
        if not search_query:
            return MOCK_SPECIES_DATA
        sq_lower = search_query.lower()
        return [
            s
            for s in MOCK_SPECIES_DATA
            if sq_lower in s.get("scientific_name", "").lower() or sq_lower in s.get("common_name", "").lower()
        ]

    filtered_species = get_filtered_species()  # solara.use_memo(get_filtered_species, [search_query]) for performance

    with solara.VBox():
        solara.Markdown("# Mosquito Species Gallery", style=f"font-family: {FONT_HEADINGS}; text-align:center;")

        # Search and Filter Bar
        with solara.Row(
            classes=["pa-2 ma-2 elevation-1"],
            style=(
                "border-radius: 6px; " "background-color: white; " "align-items: center; " "gap: 10px;"
            ),  # Card-like appearance
        ):
            solara.InputText(
                label="Search by name...",
                value=search_query,
                on_value=set_search_query,
                continuous_update=True,
                # prepend_inner_icon="mdi-magnify",
                # clearable=True,

                style="flex-grow: 1;",
            )
            # Placeholder for more filter buttons (e.g., open a filter dialog)
            solara.Button(
                "Filters",
                icon_name="mdi-filter-variant",
                outlined=True,
                color=COLOR_PRIMARY,
                on_click=lambda: solara.Warning("Filter panel not yet implemented."),
            )

        # Grid layout for species cards
        # solara.ColumnsResponsive is good for this.
        if filtered_species:
            with solara.ColumnsResponsive(
                default=[6, 6],  # 2 cards per row on large screens (md=6 means 12/6=2 columns)
                medium=[6, 6],
                small=[12],  # 1 card per row on small screens
                gutters=True,
                classes=["pa-2"],
            ):
                for species_data in filtered_species:
                    SpeciesCard(
                        species_data, on_click=lambda s=species_data: set_selected_species_id_for_detail(s["id"])
                    )
        else:
            solara.Info("No species found matching your criteria.", icon="mdi-information-outline", class_="ma-4")

        # Detail View Dialog
        if selected_species_id_for_detail:
            SpeciesDetailView(
                species_id=selected_species_id_for_detail, on_close=lambda: set_selected_species_id_for_detail(None)
            )

import solara
from typing import Dict, List, Optional

# Relative imports
from frontend.state import (
    # show_distribution_status_reactive, # Removed
    show_observed_data_reactive,
    # show_modeled_data_reactive, # Removed
    # show_breeding_sites_reactive, # Removed
    selected_species_reactive,
    # distribution_data_reactive, # Removed
    observations_data_reactive,
    # modeled_data_reactive, # Removed
    # breeding_sites_data_reactive, # Removed
    all_available_species_reactive,
)
from frontend.config import (
    # DISTRIBUTION_STATUS_COLORS, # Removed
    SPECIES_COLORS,
    FONT_BODY,
    COLOR_TEXT,
    FONT_HEADINGS,
    generate_species_colors,
)


@solara.component
def LegendDisplay():
    # Track if any content will be displayed
    has_content = False

    # Actual species in data that match the filter
    active_species_in_data: List[str] = []
    # Generate dynamic colors for all available species
    all_species_colors: Dict[str, str] = {}

    # Get all species from observation data that match the current filter
    if observations_data_reactive.value and "features" in observations_data_reactive.value:
        features = observations_data_reactive.value["features"]
        observed_species = set()
        for feature in features:
            if feature.get("properties") and "species" in feature["properties"]:
                observed_species.add(feature["properties"]["species"])
        active_species_in_data = list(observed_species)

    # Generate colors for all available species to ensure consistency
    if all_available_species_reactive.value:
        all_species_colors = generate_species_colors(all_available_species_reactive.value)
    else:
        # Fallback to existing SPECIES_COLORS if all_available_species not loaded yet
        all_species_colors = SPECIES_COLORS

    with solara.Column(
        style="padding: 8px; background: rgba(255,255,255,0.9); border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
    ):
        solara.Markdown(
            "## Map Legend", style=f"font-family: {FONT_HEADINGS}; color: {COLOR_TEXT}; margin-bottom: 10px;"
        )

        # Distribution Status Layer Legend
        # Removed

        # Observed Species Layer Legend
        if show_observed_data_reactive.value and observations_data_reactive.value:
            has_content = True
            solara.Markdown(
                "#### Observed Species",
                style=f"font-family: {FONT_HEADINGS}; color: {COLOR_TEXT}; margin-top: 10px; margin-bottom: 5px;",
            )

            # If specific species are selected, show only those
            display_species = (
                selected_species_reactive.value if selected_species_reactive.value else active_species_in_data
            )

            if not display_species:
                solara.Text(
                    "No species in current data view",
                    style=f"font-size: 0.9em; font-style: italic; font-family: {FONT_BODY}; color: {COLOR_TEXT};",
                )
            else:
                for species_name in display_species:
                    # Get color from all_species_colors or fallback
                    color = all_species_colors.get(species_name, "rgba(128,128,128,0.7)")  # Default grey
                    with solara.Row(style="align-items: center; margin-bottom: 3px;"):
                        solara.Div(
                            style=f"""
                            width: 14px; height: 14px; background-color: {color};
                            margin-right: 8px; border-radius: 50%; border: 1px solid #555;
                            """
                        )
                        solara.Text(
                            species_name, style=f"font-size: 0.9em; font-family: {FONT_BODY}; color: {COLOR_TEXT};"
                        )

            solara.Markdown("", style="margin-top: 5px; margin-bottom: 5px;")  # Spacer

        # Modeled Probability Layer Legend
        # Removed

        # Breeding Sites Layer Legend
        # Removed

        if not has_content:
            solara.Info(
                "No active layers with legends to display. Toggle layers using the Layer Control panel.",
                style=f"font-family: {FONT_BODY};",
            )

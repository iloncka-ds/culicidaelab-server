# legend_component.py
import solara
from typing import Dict, List, Optional

# Relative imports
from frontend.state import (
    show_distribution_status_reactive,
    show_observed_data_reactive,
    show_modeled_data_reactive,
    show_breeding_sites_reactive,
    selected_species_reactive,
    distribution_data_reactive,
    observations_data_reactive,
    modeled_data_reactive,
    breeding_sites_data_reactive,
    all_available_species_reactive,
)
from frontend.config import (
    DISTRIBUTION_STATUS_COLORS,
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

    with solara.Column(style="padding: 8px; background: rgba(255,255,255,0.9); border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"):
        solara.Markdown("## Map Legend", style=f"font-family: {FONT_HEADINGS}; color: {COLOR_TEXT}; margin-bottom: 10px;")
        
        # Distribution Status Layer Legend
        if show_distribution_status_reactive.value and distribution_data_reactive.value:
            has_content = True
            solara.Markdown("#### Distribution Status", style=f"font-family: {FONT_HEADINGS}; color: {COLOR_TEXT}; margin-bottom: 5px;")
            
            # Find actually used statuses in the data
            statuses_in_data = set()
            if distribution_data_reactive.value and "features" in distribution_data_reactive.value:
                for feature in distribution_data_reactive.value["features"]:
                    if feature.get("properties") and feature["properties"].get("status"):
                        statuses_in_data.add(feature["properties"]["status"])
            
            # If no statuses found in data, show all possible statuses from config
            if not statuses_in_data:
                statuses_in_data = DISTRIBUTION_STATUS_COLORS.keys()
                
            # Display legend items for each status
            for status in statuses_in_data:
                color = DISTRIBUTION_STATUS_COLORS.get(status, "rgba(128,128,128,0.7)")  # Default gray if not found
                with solara.Row(style="align-items: center; margin-bottom: 3px;"):
                    solara.Div(
                        style=f"width: 18px; height: 18px; background-color: {color}; margin-right: 8px; border: 1px solid #bbb; border-radius: 3px;"
                    )
                    solara.Text(status.replace("_", " ").title(), style=f"font-size: 0.9em; font-family: {FONT_BODY}; color: {COLOR_TEXT};")
            
            solara.Markdown("", style="margin-top: 5px; margin-bottom: 5px;")  # Spacer

        # Observed Species Layer Legend
        if show_observed_data_reactive.value and observations_data_reactive.value:
            has_content = True
            solara.Markdown(
                "#### Observed Species", 
                style=f"font-family: {FONT_HEADINGS}; color: {COLOR_TEXT}; margin-top: 10px; margin-bottom: 5px;"
            )
            
            # If specific species are selected, show only those
            display_species = selected_species_reactive.value if selected_species_reactive.value else active_species_in_data
            
            if not display_species:
                solara.Text("No species in current data view", style=f"font-size: 0.9em; font-style: italic; font-family: {FONT_BODY}; color: {COLOR_TEXT};")
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
                            species_name, 
                            style=f"font-size: 0.9em; font-family: {FONT_BODY}; color: {COLOR_TEXT};"
                        )
            
            solara.Markdown("", style="margin-top: 5px; margin-bottom: 5px;")  # Spacer

        # Modeled Probability Layer Legend
        if show_modeled_data_reactive.value and modeled_data_reactive.value:
            has_content = True
            solara.Markdown(
                "#### Modeled Probability",
                style=f"font-family: {FONT_HEADINGS}; color: {COLOR_TEXT}; margin-top: 10px; margin-bottom: 5px;",
            )
            
            # Create a gradient legend
            with solara.Column(style="width: 100%;"):
                with solara.Row(style="align-items: center; justify-content: space-between; width: 100%;"):
                    solara.Text("Low", style=f"font-size: 0.9em; font-family: {FONT_BODY}; color: {COLOR_TEXT};")
                    solara.Text("High", style=f"font-size: 0.9em; font-family: {FONT_BODY}; color: {COLOR_TEXT};")
                
                # Gradient bar using CSS linear-gradient
                solara.Div(
                    style="""
                    width: 100%; 
                    height: 20px; 
                    background: linear-gradient(to right, 
                        rgba(0, 32, 255, 0.7), 
                        rgba(0, 192, 255, 0.7), 
                        rgba(0, 255, 128, 0.7), 
                        rgba(255, 255, 0, 0.7), 
                        rgba(255, 32, 0, 0.7)
                    );
                    border-radius: 3px;
                    border: 1px solid #aaa;
                    """
                )
            
            solara.Markdown("", style="margin-top: 5px; margin-bottom: 5px;")  # Spacer

        # Breeding Sites Layer Legend
        if show_breeding_sites_reactive.value and breeding_sites_data_reactive.value:
            has_content = True
            solara.Markdown(
                "#### Breeding Sites", 
                style=f"font-family: {FONT_HEADINGS}; color: {COLOR_TEXT}; margin-top: 10px; margin-bottom: 5px;"
            )
            
            # Extract site types from data if available
            site_types_in_data = set()
            if breeding_sites_data_reactive.value and "features" in breeding_sites_data_reactive.value:
                for feature in breeding_sites_data_reactive.value["features"]:
                    if feature.get("properties") and feature["properties"].get("site_type"):
                        site_types_in_data.add(feature["properties"]["site_type"])
            
            # Default site type colors
            site_type_colors = {
                "Stormdrain (Water)": "blue",
                "Stormdrain (Dry)": "grey",
                "Container": "orange",
                "Other/Unknown": "purple",
            }
            
            # If no site types found in data, use defaults
            display_site_types = site_types_in_data if site_types_in_data else site_type_colors.keys()
            
            for site_type in display_site_types:
                color = site_type_colors.get(site_type, "purple")  # Default to purple for unknown types
                with solara.Row(style="align-items: center; margin-bottom: 3px;"):
                    solara.Div(
                        style=f"width: 14px; height: 14px; background-color: {color}; margin-right: 8px; border-radius: 3px; border: 1px solid #555;"
                    )
                    solara.Text(
                        site_type, 
                        style=f"font-size: 0.9em; font-family: {FONT_BODY}; color: {COLOR_TEXT};"
                    )

        if not has_content:
            solara.Info(
                "No active layers with legends to display. Toggle layers using the Layer Control panel.",
                style=f"font-family: {FONT_BODY};"
            )

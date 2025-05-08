import solara

# Relative imports
from culicidaelab_server.state import (
    show_distribution_status_reactive,
    show_observed_data_reactive,
    show_modeled_data_reactive,
    show_breeding_sites_reactive,  # Added
    selected_species_reactive,  # To show legend for selected species observations
)
from culicidaelab_server.config import DISTRIBUTION_STATUS_COLORS, SPECIES_COLORS, FONT_BODY, COLOR_TEXT, FONT_HEADINGS


@solara.component
def LegendDisplay():
    # Check if any legend items are visible to avoid rendering an empty legend box
    has_content = False

    with solara.VBox():
        if show_distribution_status_reactive.value:
            has_content = True
            solara.Markdown("#### Distribution Status", style=f"font-family: {FONT_HEADINGS}; margin-bottom: 5px;")
            for status, color in DISTRIBUTION_STATUS_COLORS.items():
                with solara.Row(style="align-items: center; margin-bottom: 3px;"):
                    solara.Div(
                        style=f"width: 18px; height: 18px; background-color: {color}; margin-right: 8px; border: 1px solid #bbb; border-radius: 3px;"
                    )
                    solara.Text(status.replace("_", " ").title(), style="font-size: 0.9em;")

        if show_observed_data_reactive.value and selected_species_reactive.value:
            has_content = True
            solara.Markdown(
                "#### Observed Species", style=f"font-family: {FONT_HEADINGS}; margin-top: 10px; margin-bottom: 5px;"
            )
            # Use actual SPECIES_COLORS, not just for selected_species
            # It's better to show legend for all species present in the data, or all selectable species.
            # For now, using selected_species_reactive as per original logic.
            for species_name in selected_species_reactive.value:
                color = SPECIES_COLORS.get(species_name, "rgba(128,128,128,0.7)")  # Default grey
                with solara.Row(style="align-items: center; margin-bottom: 3px;"):
                    solara.Div(
                        style=f"""
                        width: 14px; height: 14px; background-color: {color};
                        margin-right: 8px; border-radius: 50%; border: 1px solid #555;
                    """
                    )
                    solara.Text(species_name, style="font-size: 0.9em;")

        if show_modeled_data_reactive.value:
            has_content = True
            solara.Markdown(
                "#### Modeled Probability",
                style=f"font-family: {FONT_HEADINGS}; margin-top: 10px; margin-bottom: 5px;",
            )
            # This needs a gradient legend. Solara doesn't have a native gradient bar.
            # You can create one with a sequence of Divs or use an SVG/image.
            # Simple representation:
            with solara.Row(style="align-items: center; margin-bottom: 3px;"):
                solara.Text("Low", style="font-size: 0.9em; margin-right: 5px;")
                # Example gradient (very basic, use CSS or SVG for better)
                gradient_colors = [
                    f"rgb({int(255 * (1-i/4))}, {int(255 * (i/4))}, {int(255 * (1-i/4))})" for i in range(5)
                ]  # Blue to Yellow/Red
                for color_step in gradient_colors:
                    solara.Div(style=f"width: 15px; height: 15px; background-color: {color_step};")
                solara.Text("High", style="font-size: 0.9em; margin-left: 5px;")

        if show_breeding_sites_reactive.value:  # Added
            has_content = True
            solara.Markdown(
                "#### Breeding Sites", style=f"font-family: {FONT_HEADINGS}; margin-top: 10px; margin-bottom: 5px;"
            )
            # Example site type colors (match map_component.py)
            site_type_colors = {
                "Stormdrain (Water)": "blue",
                "Stormdrain (Dry)": "grey",
                "Container": "orange",
                "Other/Unknown": "purple",
            }
            for site_type, color in site_type_colors.items():
                with solara.Row(style="align-items: center; margin-bottom: 3px;"):
                    solara.Div(
                        style=f"width: 14px; height: 14px; background-color: {color}; margin-right: 8px; border-radius: 3px; border: 1px solid #555;"
                    )
                    solara.Text(site_type, style="font-size: 0.9em;")

        if not has_content:
            solara.Info("No active layers with legends to display or no species selected for observation legend.")

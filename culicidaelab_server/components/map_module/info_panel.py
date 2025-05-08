import solara
import pandas as pd
import plotly.express as px
from typing import Dict, Any

# Relative imports
from culicidaelab_server.state import selected_map_feature_info, selected_species_reactive, observations_data_reactive
from culicidaelab_server.config import SPECIES_COLORS, COLOR_BUTTON_PRIMARY_BG, FONT_BODY, COLOR_TEXT, FONT_HEADINGS


@solara.component
def InformationDisplay():
    feature_info: Dict[str, Any] = selected_map_feature_info.value or {}  # Ensure it's a dict
    selected_species: list[str] = selected_species_reactive.value

    with solara.VBox():
        if not feature_info and not selected_species:
            solara.Markdown("Click on a map feature or select species to see details.", style=f"color: {COLOR_TEXT};")
            return

        if feature_info:
            title = feature_info.get("name", feature_info.get("species", feature_info.get("id", "Selected Feature")))
            solara.Markdown(f"### Details for: `{title}`", style=f"font-family: {FONT_HEADINGS}; color: {COLOR_TEXT};")

            # Display properties in a more structured way, e.g., definition list or table
            with solara.Div(style="max-height: 250px; overflow-y: auto; padding-right: 5px;"):  # Scrollable details
                for key, value in feature_info.items():
                    # Simple filter for cleaner display
                    if key.lower() not in ["geometry", "style", "_uuid"] and value is not None and value != "":
                        solara.Markdown(
                            f"**{key.replace('_', ' ').title()}:** {value}",
                            style=f"margin-bottom: 2px; font-size:0.9em; color: {COLOR_TEXT};",
                        )

            solara.Button(
                "Clear Selection",
                on_click=lambda: selected_map_feature_info.set(None),
                small=True,
                outlined=True,
                color=COLOR_BUTTON_PRIMARY_BG,
                style="margin-top: 10px; text-transform: none;",
            )
            solara.Divider(style="margin: 10px 0;")

        if selected_species:
            solara.Markdown(
                f"### Summary for: {', '.join(selected_species)}",
                style=f"font-family: {FONT_HEADINGS}; color: {COLOR_TEXT};",
            )

            obs_data = observations_data_reactive.value
            if obs_data and obs_data.get("features"):
                # Filter and process data for the chart
                all_obs_props = [f["properties"] for f in obs_data["features"] if f.get("properties")]

                if not all_obs_props:
                    solara.Info("No observation properties found in the data.")
                    return

                obs_df = pd.DataFrame(all_obs_props)

                if not obs_df.empty and "species" in obs_df.columns:
                    # Filter for selected species
                    filtered_df = obs_df[obs_df["species"].isin(selected_species)]

                    if not filtered_df.empty:
                        counts = filtered_df["species"].value_counts().reset_index()
                        counts.columns = ["Species", "Count"]

                        # Use SPECIES_COLORS from config for consistent coloring
                        # Ensure SPECIES_COLORS is populated for all species in counts['Species']
                        # If SPECIES_COLORS is a function, call it: color_map = SPECIES_COLORS(list(counts['Species']))
                        # If it's a dict:
                        color_discrete_map = {
                            species: SPECIES_COLORS.get(species, "#cccccc") for species in counts["Species"]
                        }

                        try:
                            fig = px.bar(
                                counts,
                                x="Species",
                                y="Count",
                                title="Observation Counts",
                                color="Species",
                                color_discrete_map=color_discrete_map,
                                labels={"Count": "Number of Observations"},
                            )
                            fig.update_layout(
                                showlegend=False,
                                paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(0,0,0,0)",
                                margin=dict(l=10, r=10, t=40, b=10),  # Adjust margins
                                height=300,  # Fixed height for the chart
                                font_family=FONT_BODY,
                                title_font_family=FONT_HEADINGS,
                                title_font_color=COLOR_TEXT,
                                xaxis_title_font_family=FONT_HEADINGS,
                                yaxis_title_font_family=FONT_HEADINGS,
                                font_color=COLOR_TEXT,
                            )
                            fig.update_xaxes(tickangle=-45)  # Angle ticks if species names are long
                            solara.FigurePlotly(
                                fig, dependencies=[counts.to_json()]
                            )  # Add dependencies for FigurePlotly
                        except Exception as e:
                            solara.Error(f"Could not render plot: {e}")
                            print(f"Plotly error: {e}")
                    else:
                        solara.Info("No observation data for the selected species in the current dataset/filters.")
                else:
                    solara.Info("No observation data loaded or 'species' field missing in properties.")
            else:
                solara.Info("Observation data not available or empty.")

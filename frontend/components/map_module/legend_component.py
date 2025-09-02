import solara
import i18n

from frontend.state import (
    show_observed_data_reactive,
    selected_species_reactive,
    observations_data_reactive,
    use_locale_effect,
)
from frontend.config import (
    SPECIES_COLORS,
    FONT_BODY,
    COLOR_TEXT,
    FONT_HEADINGS,
)


@solara.component
def LegendDisplay() -> None:
    has_content: bool = False
    use_locale_effect()
    active_species_in_data: list[str] = []
    all_species_colors: dict[str, str] = SPECIES_COLORS

    if observations_data_reactive.value and "features" in observations_data_reactive.value:
        features = observations_data_reactive.value["features"]
        observed_species = set()
        for feature in features:
            if feature.get("properties") and "species" in feature["properties"]:
                observed_species.add(feature["properties"]["species"])
        active_species_in_data = list(observed_species)

    with solara.Column(
        style="padding: 8px; background: rgba(255,255,255,0.9); border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);",
    ):
        if show_observed_data_reactive.value and observations_data_reactive.value:
            has_content = True
            solara.Markdown(
                f"#### {i18n.t('map.legend.observed_species_title')}",
                style=f"font-family: {FONT_HEADINGS}; color: {COLOR_TEXT}; margin-top: 10px; margin-bottom: 5px;",
            )

            display_species = (
                selected_species_reactive.value if selected_species_reactive.value else active_species_in_data
            )

            if not display_species:
                solara.Text(
                    i18n.t("map.legend.no_species_in_view"),
                    style=f"font-size: 0.9em; font-style: italic; font-family: {FONT_BODY}; color: {COLOR_TEXT};",
                )
            else:
                for species_name in display_species:
                    color = all_species_colors.get(species_name, "rgba(128,128,128,0.7)")
                    with solara.Row(style="align-items: center; margin-bottom: 3px;"):
                        solara.Div(
                            style=f"""
                            width: 14px; height: 14px; background-color: {color};
                            margin-right: 8px; border-radius: 50%; border: 1px solid
                            """,
                        )
                        solara.Text(
                            species_name,
                            style=f"font-size: 0.9em; font-family: {FONT_BODY}; color: {COLOR_TEXT};",
                        )

            solara.Markdown("", style="margin-top: 5px; margin-bottom: 5px;")

        if not has_content:
            solara.Info(
                i18n.t("map.legend.no_active_layers"),
                style=f"font-family: {FONT_BODY};",
            )

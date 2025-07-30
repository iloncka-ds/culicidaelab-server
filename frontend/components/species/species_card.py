import solara
from solara.alias import rv

import i18n

from typing import Dict, Any

from frontend.config import (
    COLOR_PRIMARY,
    FONT_HEADINGS,
)

from frontend.state import selected_species_item_id #, use_locale_effect
from frontend.components.species.species_status import get_status_color


i18n.add_translation("actions.view_details", "View Details", locale="en")
i18n.add_translation("species.status.high", "Vector Status: High", locale="en")
i18n.add_translation("species.status.medium", "Vector Status: Medium", locale="en")
i18n.add_translation("species.status.low", "Vector Status: Low", locale="en")
i18n.add_translation("species.status.unknown", "Vector Status: Unknown", locale="en")

i18n.add_translation("actions.view_details", "Читать далее", locale="ru")

i18n.add_translation("species.status.high", "Степень риска: Высокий", locale="ru")
i18n.add_translation("species.status.medium", "Степень риска: Средний", locale="ru")
i18n.add_translation("species.status.low", "Степень риска: Низкий", locale="ru")
i18n.add_translation("species.status.unknown", "Степень риска: Неизвестно", locale="ru")


@solara.component
def SpeciesCard(species: Dict[str, Any]):
    router = solara.use_router()
    # use_locale_effect()
    def redirect_to_species(species_id):
        selected_species_item_id.set(species_id)
        router.push("species")

    with rv.Card(
        class_="ma-2 pa-3",
        hover=True,
        style="cursor: pointer; ...",
    ):
        with solara.Row(style="align-items: center; flex-grow:1;"):
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

            with solara.Column(align="start", style="overflow: hidden;"):
                species_id = species.get("id")
                solara.Markdown(
                    f"#### {species.get('scientific_name', 'N/A')}",
                    style=f"font-family: {FONT_HEADINGS}; margin-bottom: 0px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: {COLOR_PRIMARY}; text-decoration: none;",
                )

                solara.Text(
                    species.get("common_name", ""),
                    style="font-size: 0.9em; color: #555; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;",
                )


                status_detail = str(species.get("vector_status", "Unknown")).lower()

                status_color_detail, text_color_detail = get_status_color(status_detail)

                rv.Chip(
                    small=True,
                    children=[i18n.t(f"species.status.{status_detail}")],
                    color=status_color_detail,
                    class_="mt-1",
                    text_color=text_color_detail,
                )
                solara.Button(i18n.t('actions.view_details'), on_click=lambda: redirect_to_species(species_id))

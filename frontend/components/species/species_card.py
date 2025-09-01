import solara
from solara.alias import rv

import i18n

from typing import Any

from frontend.config import COLOR_PRIMARY, FONT_HEADINGS, STATIC_FILES_URL

from frontend.state import selected_species_item_id, use_locale_effect
from frontend.components.species.species_status import get_status_color


i18n.add_translation("actions.view_details", "View Details", locale="en")
i18n.add_translation("species.status.high", "Vector Status: High", locale="en")
i18n.add_translation("species.status.moderate", "Vector Status: Moderate", locale="en")
i18n.add_translation("species.status.low", "Vector Status: Low", locale="en")
i18n.add_translation("species.status.unknown", "Vector Status: Unknown", locale="en")

i18n.add_translation("actions.view_details", "Читать далее", locale="ru")

i18n.add_translation("species.status.high", "Степень риска: Высокий", locale="ru")
i18n.add_translation("species.status.moderate", "Степень риска: Средний", locale="ru")
i18n.add_translation("species.status.low", "Степень риска: Низкий", locale="ru")
i18n.add_translation("species.status.unknown", "Степень риска: Неизвестно", locale="ru")


@solara.component
def SpeciesCard(species: dict[str, Any]):
    router = solara.use_router()
    use_locale_effect()

    def redirect_to_species(species_id):
        selected_species_item_id.set(species_id)
        router.push("species")

    with rv.Card(
        class_="ma-2 pa-3",
        hover=True,
        style="cursor: pointer; height: 100%;",
    ):
        with solara.Row(style="align-items: center; flex-grow:1;"):
            with solara.Column(style="flex: 0 0 auto;"):
                if species.get("image_url"):
                    # print(species.get("image_url"))
                    rv.Img(
                        src=f"{species['image_url']}",
                        height="100px",
                        width="100px",
                        aspect_ratio="1",
                        class_="mr-3 elevation-1",
                        contain=False,
                        style="border-radius: 4px; object-fit: cover; border-radius: 4px; object-fit: cover; flex-shrink: 0;",
                    )
                else:
                    rv.Img(
                        src=f"{STATIC_FILES_URL}/static/images/default_species.png",
                        height="100px",
                        width="100px",
                        aspect_ratio="1",
                        contain=False,
                        class_="mr-3 elevation-1",
                        style="border-radius: 4px; object-fit: cover; min-width: 100px; max-width: 100px; min-height: 100px; max-height: 100px;",
                    )

            with solara.Column(align="start", style="overflow: hidden;"):
                species_id = species.get("id")
                solara.Markdown(
                    f"#### {species.get('scientific_name', 'N/A')}",
                    style=f"font-family: {FONT_HEADINGS}; margin-bottom: 0px; white-space: normal; min-height: 3.5em; color: {COLOR_PRIMARY};",
                )

                solara.Text(
                    species.get("common_name", ""),
                    style="font-size: 0.9em; color: #555; white-space: normal; min-height: 3.5em;",
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
                if species_id != "species_not_defined":
                    solara.Button(i18n.t("actions.view_details"), on_click=lambda: redirect_to_species(species_id))

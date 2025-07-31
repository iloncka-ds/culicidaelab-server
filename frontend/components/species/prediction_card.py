import solara
from solara.alias import rv

import i18n

from typing import Dict, Any

from frontend.config import COLOR_PRIMARY, FONT_HEADINGS, STATIC_FILES_URL

from frontend.state import selected_species_item_id, use_locale_effect
from frontend.components.species.species_status import get_status_color


i18n.add_translation("actions.view_details", "View Details", locale="en")

i18n.add_translation("species.not_defined", "Unfortunately, the species could not be determined from the uploaded image.",
                    locale="en")

i18n.add_translation("actions.view_details", "Читать далее", locale="ru")

i18n.add_translation("species.not_defined", "К сожалению не удалось определить вид комара по загруженному изображению.",
                    locale="ru")


@solara.component
def PredictionCard(species: Dict[str, Any]):
    router = solara.use_router()
    use_locale_effect()

    def redirect_to_species(species_id):
        selected_species_item_id.set(species_id)
        router.push("species")

    with rv.Card(
        class_="ma-2 pa-3",
        hover=True,
        style="cursor: pointer; ...",
    ):
        with solara.Column(style="align-items: center; flex-grow:1;"):
            print(species)
            rv.Img(
                src=f"{STATIC_FILES_URL}/static/images/species/{species.get('id', 'species_not_defined')}/detail.jpg",
                height="224px",
                width="224px",
                aspect_ratio="1",
                class_="mr-3 elevation-1",
                style="border-radius: 4px; object-fit: cover;",
            )

            with solara.Column(align="start", style="overflow: hidden;"):
                species_id = species.get("id")
                if species_id != "species_not_defined":
                    solara.Markdown(
                    f"#### {species.get('scientific_name', 'N/A')}",
                    style=f"font-family: {FONT_HEADINGS}; margin-bottom: 0px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: {COLOR_PRIMARY}; text-decoration: none;",
                    )

                    solara.Text(
                    species.get("common_name", ""),
                    style="font-size: 0.9em; color: #555; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;",
                    )

                    solara.Button(i18n.t('actions.view_details'), on_click=lambda: redirect_to_species(species_id))

                else:
                    solara.Text(
                        i18n.t("species.not_defined"),
                        style="font-size: 0.9em; color: #555; white-space: normal;",
                    )



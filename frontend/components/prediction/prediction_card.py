import solara
from solara.alias import rv

import i18n

from typing import Any

from frontend.config import COLOR_PRIMARY, FONT_HEADINGS, STATIC_FILES_URL

from frontend.state import selected_species_item_id, use_locale_effect


i18n.add_translation("actions.view_details", "View Details", locale="en")

i18n.add_translation(
    "species.not_defined",
    "Unfortunately, the species could not be determined from the uploaded image.",
    locale="en",
)

i18n.add_translation("actions.view_details", "Читать далее", locale="ru")

i18n.add_translation(
    "species.not_defined",
    "К сожалению не удалось определить вид комара по загруженному изображению.",
    locale="ru",
)


@solara.component
def PredictionCard(species: dict[str, Any]):
    """
    Displays a card with the prediction result for a single species.

    This component visualizes the outcome of a species prediction. It shows the
    species' image, scientific name, and common name. It includes a button to
    navigate to a more detailed view of the species. A special state is handled
    for cases where the species could not be identified from an image,
    displaying an appropriate message instead of species details.

    Args:
        species: A dictionary containing the data for the predicted species.
            Expected keys include 'id', 'scientific_name', and 'common_name'.
            If the 'id' is 'species_not_defined', the card will display a
            fallback message.

    Example:
        ```python
        import solara

        # Example data for an identified species
        identified_species_data = {
            "id": "aedes_aegypti",
            "scientific_name": "Aedes aegypti",
            "common_name": "Yellow Fever Mosquito"
        }

        # Example data for an unidentified species
        unidentified_species_data = {
            "id": "species_not_defined"
        }

        @solara.component
        def Page():
            with solara.ColumnsResponsive(default=):
                # Card for a successful prediction
                PredictionCard(species=identified_species_data)

                # Card for a failed prediction
                PredictionCard(species=unidentified_species_data)

        # Note: The "View Details" button requires a router setup in the
        # main application to function correctly.
        ```
    """
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

                    solara.Button(i18n.t("actions.view_details"), on_click=lambda: redirect_to_species(species_id))

                else:
                    solara.Text(
                        i18n.t("species.not_defined"),
                        style="font-size: 0.9em; color: #555; white-space: normal;",
                    )

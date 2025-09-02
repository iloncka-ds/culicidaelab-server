from typing import Any

import solara
from solara.alias import rv
import i18n
from frontend.config import (
    COLOR_PRIMARY,
    FONT_HEADINGS,
)
from frontend.state import selected_disease_item_id


i18n.add_translation("actions.view_details", "View Details", locale="en")
i18n.add_translation("actions.view_details", "Читать далее", locale="ru")
i18n.set("fallback", "en")


@solara.component
def DiseaseCard(disease: dict[str, Any]):
    router = solara.use_router()

    def redirect_to_disease_item(disease_id):
        selected_disease_item_id.set(disease_id)
        router.push("diseases")

    with rv.Card(
        class_="ma-2 pa-3",
        hover=True,
        style="cursor: pointer; height: 100%;",
    ):
        with solara.Row(style="align-items: center; flex-grow:1;"):
            if disease.get("image_url"):
                rv.Img(
                    src=disease["image_url"],
                    height="100px",
                    width="100px",
                    aspect_ratio="1",
                    class_="mr-3 elevation-1",
                    style_="border-radius: 4px; object-fit: cover;",
                )
            else:
                rv.Icon(children=["mdi-virus"], size="100px", class_="mr-3", color=COLOR_PRIMARY)

            with solara.Column(align="start", style="overflow: hidden;"):
                solara.Markdown(
                    f"#### {disease.get('name', 'N/A')}",
                    style=f"font-family: {FONT_HEADINGS}; margin-bottom: 0px; white-space: normal; min-height: 5.5em; color: {COLOR_PRIMARY};",
                )

                description = disease.get("description", "")
                description_snippet = description[:55] + "..." if len(description) > 60 else description
                solara.Text(
                    description_snippet,
                    style="font-size: 0.9em; color: #555; white-space: normal; min-height: 3em; max-height: 4em;",
                )
                prevalence = disease.get("prevalence", "")
                prevalence_snippet = prevalence[:35] + "..." if len(prevalence) > 35 else prevalence
                if prevalence:
                    rv.Chip(
                        small=True,
                        children=[prevalence_snippet],
                        color="blue",
                        class_="mt-1",
                        text_color="white",
                    )
                solara.Button(
                    i18n.t("actions.view_details"),
                    on_click=lambda: redirect_to_disease_item(disease.get("id", "")),
                )

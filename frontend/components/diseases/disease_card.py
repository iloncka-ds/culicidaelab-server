import solara
import solara.lab
from solara.alias import rv

from typing import Dict, Any

# Imports for config
from ...config import (
    COLOR_PRIMARY,
    FONT_HEADINGS
)
from ...state import selected_disease_item_id
# In your initialization code (e.g., app.py or config/i18n.py)
import i18n

# English translations
i18n.add_translation("actions.view_details", "View Details", locale="en")

# Russian translations
i18n.add_translation("actions.view_details", "Читать далее", locale="ru")

# Configure i18n
i18n.set("locale", "ru")
i18n.set("fallback", "en")

@solara.component
def DiseaseCard(disease: Dict[str, Any]):
    router = solara.use_router()

    def redirect_to_disease_item(disease_id):
        selected_disease_item_id.set(disease_id)
        router.push("diseases")

    with rv.Card(
        class_="ma-2 pa-3",
        hover=True,
        style="cursor: pointer; height: 100%;",  # Add pointer cursor and ensure full height
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
                # disease_id = disease.get("id")
                # Wrap the entire content in a Link for better UX
                # with solara.Link(path_or_route=f"/diseases/{disease_id}"):
                solara.Markdown(
                    f"#### {disease.get('name', 'N/A')}",
                    style=f"font-family: {FONT_HEADINGS}; margin-bottom: 0px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: {COLOR_PRIMARY}; text-decoration: none;",
                )

                # Brief description snippet
                description = disease.get("description", "")
                # Truncate description if needed
                description_snippet = description[:60] + "..." if len(description) > 60 else description
                solara.Text(
                    description_snippet,
                    style="font-size: 0.9em; color: #555; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;",
                )

                # Prevalence information shown as a chip
                if prevalence := disease.get("prevalence"):
                    rv.Chip(
                        small=True,
                        children=[prevalence],
                        color="blue",
                        class_="mt-1",
                        text_color="white",
                    )
                solara.Button(i18n.t('actions.view_details'), on_click=lambda: redirect_to_disease_item(disease.get("id", "")) )

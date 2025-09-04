import asyncio
from typing import Any, Optional, cast

from collections.abc import Callable

import i18n
import solara
from solara.alias import rv

from frontend.components.species.species_card import SpeciesCard

from frontend.config import (
    COLOR_PRIMARY,
    FONT_HEADINGS,
    DISEASE_DETAIL_ENDPOINT_TEMPLATE,
    DISEASE_VECTORS_ENDPOINT_TEMPLATE,
    heading_style,
    page_style,
)
from frontend.state import (
    current_locale,
    fetch_api_data,
    selected_disease_item_id,
    use_locale_effect,
)

i18n.add_translation("disease.gallery_link", "Go to Disease Gallery", locale="en")
i18n.add_translation("disease.error.load", "Could not load disease details: %{error}", locale="en")
i18n.add_translation("disease.error.no_id", "No disease ID specified in the URL.", locale="en")
i18n.add_translation(
    "disease.error.not_found",
    'Disease details for "%{disease_id}" not found or are unavailable.',
    locale="en",
)
i18n.add_translation("disease.sections.description", "Description", locale="en")
i18n.add_translation("disease.sections.symptoms", "Symptoms", locale="en")
i18n.add_translation("disease.sections.treatment", "Treatment", locale="en")
i18n.add_translation("disease.sections.prevention", "Prevention", locale="en")
i18n.add_translation("disease.sections.vectors", "Vector Species", locale="en")
i18n.add_translation("disease.labels.prevalence", "Prevalence", locale="en")
i18n.add_translation("disease.messages.no_description", "No description available.", locale="en")
i18n.add_translation("disease.messages.no_vectors", "No known vector species for this disease.", locale="en")
i18n.add_translation("disease.errors.vector_load", "Could not load vector species: %{error}", locale="en")

i18n.add_translation("disease.gallery_link", "К списку заболеваний", locale="ru")
i18n.add_translation("disease.error.load", "Не удалось загрузить данные: %{error}", locale="ru")
i18n.add_translation("disease.error.no_id", "Идентификатор заболевания не указан.", locale="ru")
i18n.add_translation("disease.error.not_found", 'Данные для заболевания "%{disease_id}" не найдены.', locale="ru")
i18n.add_translation("disease.sections.description", "Описание", locale="ru")
i18n.add_translation("disease.sections.symptoms", "Симптомы", locale="ru")
i18n.add_translation("disease.sections.treatment", "Лечение", locale="ru")
i18n.add_translation("disease.sections.prevention", "Профилактика", locale="ru")
i18n.add_translation("disease.sections.vectors", "Переносчики заболевания", locale="ru")
i18n.add_translation("disease.labels.prevalence", "Распространенность", locale="ru")
i18n.add_translation("disease.messages.no_description", "Описание отсутствует.", locale="ru")
i18n.add_translation("disease.messages.no_vectors", "Известные переносчики отсутствуют.", locale="ru")
i18n.add_translation("disease.errors.vector_load", "Ошибка загрузки переносчиков: %{error}", locale="ru")


@solara.component
def DiseaseDetailPageComponent():
    """
    Renders a detailed page for a specific disease.

    This component fetches and displays comprehensive information about a disease
    based on an ID stored in the global `selected_disease_item_id` state.
    It handles loading states, potential errors, and also fetches and displays
    associated vector species for the disease.

    The component is language-aware and will refetch data if the application's
    locale changes. It relies on predefined API endpoint templates and the
    `fetch_api_data` utility for its data retrieval.

    Example:
        This component is typically used as a main content view, conditionally
        rendered when a disease ID is selected.

        ```python
        import solara
        from frontend.state import selected_disease_item_id

        # Assume DiseaseGallery is a component that lists diseases and sets
        # the selected_disease_item_id when one is clicked.
        # from .disease_gallery import DiseaseGallery

        @solara.component
        def Page():
            # This component will render when a disease ID is set,
            # and it will be replaced by the DiseaseGallery when the ID is None.
            if selected_disease_item_id.value:
                DiseaseDetailPageComponent()
            else:
                # DiseaseGallery() # Or any other component
                solara.Text("Select a disease to see details.")

        # To see this component, you would need to set the state, for example:
        # selected_disease_item_id.set("some-disease-id")
        ```
    """
    use_locale_effect()

    disease_id = selected_disease_item_id.value
    disease_data, set_disease_data = solara.use_state(cast(Optional[dict[str, Any]], None))
    vectors_data, set_vectors_data = solara.use_state(cast(list[dict[str, Any]], []))
    loading, set_loading = solara.use_state(False)
    vectors_loading, set_vectors_loading = solara.use_state(False)
    error, set_error = solara.use_state(cast(Optional[str], None))
    vectors_error, set_vectors_error = solara.use_state(cast(Optional[str], None))

    def _fetch_disease_detail_effect() -> Callable[[], None] | None:
        task_ref = [cast(Optional[asyncio.Task], None)]

        async def _async_task():
            if not disease_id:
                set_disease_data(None)
                set_error("No disease ID specified in URL.")
                set_loading(False)
                return

            set_disease_data(None)
            set_error(None)
            set_loading(True)
            set_vectors_data([])
            set_vectors_error(None)
            try:
                url = DISEASE_DETAIL_ENDPOINT_TEMPLATE.format(disease_id=disease_id)
                params = {"lang": current_locale.value}
                data = await fetch_api_data(url, params=params)

                current_task = task_ref[0]
                if current_task and current_task.cancelled():
                    return

                if data is None:
                    set_error(f"Details for '{disease_id}' not found or an API error occurred.")
                    set_disease_data(None)
                else:
                    set_disease_data(data)
                    set_error(None)

                    set_vectors_loading(True)
                    try:
                        vectors_url = DISEASE_VECTORS_ENDPOINT_TEMPLATE.format(disease_id=disease_id)
                        vectors_params = {"lang": current_locale.value}
                        vector_species = await fetch_api_data(vectors_url, params=vectors_params)
                        if vector_species is not None:
                            set_vectors_data(vector_species)
                        else:
                            set_vectors_data([])  # Ensure it's an empty list on failure
                            set_vectors_error("Failed to load vector data, or none exist.")

                    except Exception as e:
                        set_vectors_error(f"Could not load vector species: {str(e)}")
                    finally:
                        set_vectors_loading(False)

            except asyncio.CancelledError:
                raise
            except Exception as e:
                set_error(f"An unexpected error occurred: {str(e)}")
                set_disease_data(None)
            finally:
                set_loading(False)

        task_ref[0] = asyncio.create_task(_async_task())

        def cleanup():
            current_task = task_ref[0]
            if current_task and not current_task.done():
                current_task.cancel()

        return cleanup

    solara.use_effect(_fetch_disease_detail_effect, [disease_id, current_locale.value])

    with solara.Column(align="center", classes=["pa-4"], style=page_style):
        solara.Button(
            i18n.t("disease.gallery_link"),
            icon_name="mdi-arrow-left",
            text=True,
            outlined=True,
            color=COLOR_PRIMARY,
            classes=["mb-4 align-self-start"],
            on_click=lambda: selected_disease_item_id.set(None),
        )

        if loading:
            solara.SpinnerSolara(size="60px")
        elif error:
            solara.Error(
                i18n.t("disease.error.load", error=error),
                icon="mdi-alert-circle-outline",
                style="margin-top: 20px;",
            )
        elif not disease_id:
            solara.Info(i18n.t("disease.error.no_id"), icon="mdi-information-outline", style="margin-top: 20px;")
        elif not disease_data:
            solara.Info(
                i18n.t("disease.error.not_found", disease_id=disease_id),
                icon="mdi-information-outline",
                style="margin-top: 20px;",
            )
        else:
            solara.Title(i18n.t("disease.title", name=disease_data.get("name")))
            solara.Markdown(
                f"{disease_data.get('name', 'N/A')}",
                style=heading_style,
            )

            with solara.Column(style="align: center;margin-top:20px; text-align: left;"):
                if disease_data.get("image_url"):
                    rv.Img(
                        src=disease_data["image_url"],
                        style_=(
                            "float: left; "
                            "max-width: 250px; "
                            "margin: 0 20px 10px 0; "  # Margin for spacing (top, right, bottom, left)
                            "border-radius: 8px; "
                            "border: 1px solid #eee; "
                            "box-shadow: 0 2px 8px rgba(0,0,0,0.1);"
                        ),
                    )

                sections = [
                    ("prevalence", i18n.t("disease.labels.prevalence")),
                    ("description", i18n.t("disease.sections.description")),
                    ("symptoms", i18n.t("disease.sections.symptoms")),
                    ("treatment", i18n.t("disease.sections.treatment")),
                    ("prevention", i18n.t("disease.sections.prevention")),
                ]

                for key, title in sections:
                    if content := disease_data.get(key):
                        solara.Markdown(f"### {title}\n{content}")
                    else:
                        solara.Text(
                            i18n.t("disease.messages.no_description"),
                            style="font-style: italic; color: #777;",
                        )

            # Divider to clear the float and separate sections
            rv.Divider(style_="margin: 30px 0;")

            solara.Markdown(
                f"## {i18n.t('disease.sections.vectors')}",
                style=f"font-family: {FONT_HEADINGS}; text-align: center; margin-bottom: 15px;",
            )

            if vectors_loading:
                solara.SpinnerSolara(size="40px")
            elif vectors_error:
                solara.Error(i18n.t("disease.errors.vector_load", error=vectors_error))
            elif not vectors_data:
                solara.Info(i18n.t("disease.messages.no_vectors"))
            else:
                with solara.Row(justify="center", style="flex-wrap: wrap; gap: 16px;"):
                    for vector in vectors_data:
                        SpeciesCard(vector)

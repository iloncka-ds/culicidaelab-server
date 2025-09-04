import asyncio
from typing import Any, Optional, cast

from collections.abc import Callable

import i18n
import solara
from solara.alias import rv

from frontend.components.diseases.disease_card import DiseaseCard
from frontend.components.species.species_status import get_status_color

from frontend.config import (
    DISEASE_DETAIL_ENDPOINT_TEMPLATE,
    SPECIES_DETAIL_ENDPOINT_TEMPLATE,
    heading_style,
    page_style,
)
from frontend.config import COLOR_PRIMARY, FONT_HEADINGS

from frontend.state import current_locale, selected_species_item_id, use_locale_effect, fetch_api_data

i18n.add_translation("species.gallery_link", "Go to Species Gallery", locale="en")
i18n.add_translation("species.error.load", "Could not load species details: %{error}", locale="en")
i18n.add_translation("species.error.no_id", "No species ID specified.", locale="en")
i18n.add_translation(
    "species.error.not_found",
    'Species details for "%{species_id}" not found or are unavailable.',
    locale="en",
)
i18n.add_translation("species.labels.vector_status", "Vector Status: %{status}", locale="en")
i18n.add_translation("species.sections.description", "Description", locale="en")
i18n.add_translation("species.sections.characteristics", "Key Identifying Characteristics", locale="en")
i18n.add_translation("species.sections.distribution", "Geographic Distribution", locale="en")
i18n.add_translation("species.sections.diseases", "Related Diseases Transmitted", locale="en")
i18n.add_translation("species.messages.no_description", "No description available.", locale="en")
i18n.add_translation("species.messages.no_diseases", "No related diseases are listed for this species.", locale="en")
i18n.add_translation(
    "species.messages.disease_load_error",
    "Related diseases are listed but could not be loaded. Please try again later.",
    locale="en",
)
i18n.add_translation(
    "species.messages.disease_unavailable",
    "Information on related diseases is currently unavailable.",
    locale="en",
)

i18n.add_translation("species.status.high", "Vector Status: High", locale="en")
i18n.add_translation("species.status.moderate", "Vector Status: Moderate", locale="en")
i18n.add_translation("species.status.low", "Vector Status: Low", locale="en")
i18n.add_translation("species.status.unknown", "Vector Status: Unknown", locale="en")


i18n.add_translation("species.gallery_link", "К списку видов", locale="ru")
i18n.add_translation("species.error.load", "Ошибка загрузки данных: %{error}", locale="ru")
i18n.add_translation("species.error.no_id", "Идентификатор вида не указан.", locale="ru")
i18n.add_translation("species.error.not_found", 'Данные для вида "%{species_id}" не найдены.', locale="ru")
i18n.add_translation("species.labels.vector_status", "Статус переносчика", locale="ru")
i18n.add_translation("species.sections.description", "Описание", locale="ru")
i18n.add_translation("species.sections.characteristics", "Ключевые характеристики", locale="ru")
i18n.add_translation("species.sections.distribution", "Географическое распространение", locale="ru")
i18n.add_translation("species.sections.diseases", "Переносимые заболевания", locale="ru")
i18n.add_translation("species.messages.no_description", "Описание отсутствует.", locale="ru")
i18n.add_translation("species.messages.no_diseases", "Связанные заболевания отсутствуют.", locale="ru")
i18n.add_translation("species.messages.disease_load_error", "Ошибка загрузки связанных заболеваний.", locale="ru")
i18n.add_translation("species.messages.disease_unavailable", "Информация о заболеваниях недоступна.", locale="ru")

i18n.add_translation("species.status.high", "Степень риска: Высокий", locale="ru")
i18n.add_translation("species.status.moderate", "Степень риска: Средний", locale="ru")
i18n.add_translation("species.status.low", "Степень риска: Низкий", locale="ru")
i18n.add_translation("species.status.unknown", "Степень риска: Неизвестно", locale="ru")


@solara.component
def SpeciesDetailPageComponent():
    """
    Renders a detailed page for a specific biological species.

    This component fetches and displays comprehensive information about a species,
    identified by the global `selected_species_item_id` state. It presents
    details such as the species' scientific and common names, an image, vector
    status, description, and geographic distribution.

    A key feature is its ability to also fetch and display a list of diseases
    transmitted by the species, rendering them as a series of `DiseaseCard`
    components. The component manages its own loading and error states for both
    the species and the related disease data, providing feedback to the user
    during data retrieval. It is language-aware and will refetch data if the
    application's locale changes.

    Example:
        This component is typically used as a main content view, conditionally
        rendered when a species ID is selected.

        ```python
        import solara
        from frontend.state import selected_species_item_id

        # Assume SpeciesGallery is a component that lists species and sets
        # the selected_species_item_id when one is clicked.
        # from .species_gallery import SpeciesGallery

        @solara.component
        def Page():
            # The detail page is shown only when a species ID is present in the state.
            if selected_species_item_id.value:
                SpeciesDetailPageComponent()
            else:
                # Otherwise, show the gallery or another component.
                # SpeciesGallery()
                solara.Text("Select a species to see its details.")

        # To activate this component, the global state needs to be set, e.g.:
        # selected_species_item_id.set("aedes-aegypti")
        ```
    """
    use_locale_effect()
    species_id = selected_species_item_id.value
    species_data, set_species_data = solara.use_state(cast(Optional[dict[str, Any]], None))
    loading, set_loading = solara.use_state(False)
    error, set_error = solara.use_state(cast(Optional[str], None))
    related_diseases_data, set_related_diseases_data = solara.use_state(cast(list[dict[str, Any]], []))
    diseases_loading, set_diseases_loading = solara.use_state(False)
    diseases_error, set_diseases_error = solara.use_state(cast(Optional[str], None))

    def _fetch_species_detail_effect() -> Callable[[], None] | None:
        task_ref = [cast(Optional[asyncio.Task], None)]

        async def _async_task():
            if not species_id:
                set_species_data(None)
                set_error("No species ID specified.")
                set_loading(False)
                set_related_diseases_data([])
                set_diseases_loading(False)
                set_diseases_error(None)
                return

            set_species_data(None)
            set_error(None)
            set_loading(True)
            set_related_diseases_data([])
            set_diseases_loading(False)
            set_diseases_error(None)

            disease_ids_to_fetch = []

            try:
                url = SPECIES_DETAIL_ENDPOINT_TEMPLATE.format(species_id=species_id)
                params = {"lang": current_locale.value}
                data = await fetch_api_data(url, params=params)

                current_task_check_one = task_ref[0]
                if current_task_check_one and current_task_check_one.cancelled():
                    return

                if data is None:
                    set_error(f"Details for '{species_id}' not found or an API error occurred.")
                    set_species_data(None)
                else:
                    set_species_data(data)
                    set_error(None)

                    disease_ids_to_fetch = data.get("related_diseases", [])

                    if disease_ids_to_fetch:
                        set_diseases_loading(True)
                        fetched_diseases_list = []
                        for disease_id_to_fetch in disease_ids_to_fetch:
                            current_task_check_loop = task_ref[0]
                            if current_task_check_loop and current_task_check_loop.cancelled():
                                raise asyncio.CancelledError

                            disease_url = DISEASE_DETAIL_ENDPOINT_TEMPLATE.format(disease_id=disease_id_to_fetch)
                            disease_params = {"lang": current_locale.value}

                            disease_item_data = await fetch_api_data(disease_url, params=disease_params)
                            if disease_item_data:
                                fetched_diseases_list.append(disease_item_data)
                            else:
                                print(f"Warning: Could not fetch details for disease ID {disease_id_to_fetch}")

                        current_task_check_two = task_ref[0]
                        if not (current_task_check_two and current_task_check_two.cancelled()):
                            set_related_diseases_data(fetched_diseases_list)
                        else:
                            print(
                                f"Warning: Task cancelled before setting related_diseases_data for species {species_id}.",
                            )

                        set_diseases_loading(False)
                    else:
                        set_related_diseases_data([])
                        set_diseases_loading(False)

            except asyncio.CancelledError:
                print(f"Warning: Task cancelled before setting related_diseases_data for {species_id}.")
            except Exception as e:
                set_error(f"An unexpected error occurred: {str(e)}")
                set_species_data(None)
                set_related_diseases_data([])
                set_diseases_error(f"Failed to load related diseases due to a main task error: {str(e)}")
            finally:
                if not (task_ref[0] and task_ref[0].cancelled()):
                    set_loading(False)
                    if disease_ids_to_fetch:
                        set_diseases_loading(False)

        task_ref[0] = asyncio.create_task(_async_task())

        def cleanup():
            current_task = task_ref[0]
            if current_task and not current_task.done():
                current_task.cancel()
            else:
                print(f"Warning: Task for ID {species_id} already done or no task found.")

        return cleanup

    solara.use_effect(_fetch_species_detail_effect, [species_id, current_locale.value])

    with solara.Column(align="center", classes=["pa-4"], style=page_style):
        solara.Button(
            i18n.t("species.gallery_link"),
            icon_name="mdi-arrow-left",
            text=True,
            outlined=True,
            color=COLOR_PRIMARY,
            classes=["mb-4", "align-self-start"],
            on_click=lambda: selected_species_item_id.set(None),
        )

        if loading:
            solara.SpinnerSolara(size="60px")
        elif error:
            solara.Error(
                i18n.t("species.error.load", error=error),
                icon="mdi-alert-circle-outline",
                style="margin-top: 20px;",
            )
        elif not species_id:
            solara.Info(i18n.t("species.error.no_id"), icon="mdi-information-outline", style="margin-top: 20px;")
        elif not species_data:
            solara.Info(
                i18n.t("species.error.not_found", species_id=species_id),
                icon="mdi-information-outline",
                style="margin-top: 20px;",
            )
        else:
            _species_data = species_data
            solara.Text(_species_data.get("scientific_name"), style=heading_style)
            if common_name := _species_data.get("common_name"):
                solara.Text(
                    f"({common_name})",
                    style="text-align: center; font-size: 1.2em; color: #555; margin-bottom: 20px;",
                )
            rv.Divider(style_="margin: 15px 0;")

            with solara.Column(style="align: center; margin-top:20px; text-align: left;"):
                if _species_data.get("image_url"):
                    rv.Img(
                        src=_species_data["image_url"],
                        width="100%",
                        max_width="350px",
                        style_="border-radius: 8px; object-fit:cover; align-self: center; border: 1px solid #eee; box-shadow: 0 2px 8px rgba(0,0,0,0.1);",
                    )

                status_detail = str(_species_data.get("vector_status", "Unknown")).lower()

                status_color_detail, text_color_detail = get_status_color(status_detail)
                rv.Chip(
                    children=[i18n.t(f"species.status.{status_detail}")],
                    color=status_color_detail,
                    text_color=text_color_detail,
                    class_="mt-3 pa-2 elevation-1",
                    style_="font-size: 1em;",
                )

                if desc := _species_data.get("description"):
                    solara.Markdown(f"### {i18n.t('species.sections.description')}\n{desc}")
                else:
                    solara.Text(i18n.t("species.messages.no_description"), style="font-style: italic; color: #777;")

                if chars := _species_data.get("key_characteristics"):
                    solara.Markdown(f"### {i18n.t('species.sections.characteristics')}")
                    with rv.List(dense=True, style_="padding-left:0; list-style-position: inside;"):
                        for char_item in chars:
                            rv.ListItem(children=[f"• {char_item}"], style_="padding-left:0; margin-bottom:2px;")

                if regions := _species_data.get("geographic_regions"):
                    solara.Markdown(f"### {i18n.t('species.sections.distribution')}\n{', '.join(regions)}")

            solara.Markdown(
                f"## {i18n.t('species.sections.diseases')}",
                style=f"font-family: {FONT_HEADINGS}; text-align: center; margin-top: 30px; margin-bottom: 15px;",
            )

            if diseases_loading:
                solara.SpinnerSolara(size="40px")
            elif diseases_error:
                solara.Error(i18n.t("species.messages.disease_load_error"), icon="mdi-alert-circle-outline")
            elif not related_diseases_data and not _species_data.get("related_diseases"):
                solara.Info(i18n.t("species.messages.no_diseases"))
            elif not related_diseases_data and _species_data.get("related_diseases"):
                solara.Warning(
                    i18n.t("species.messages.disease_load_error"),
                    icon="mdi-alert-outline",
                )
            elif related_diseases_data:
                with solara.Row(justify="center", style="flex-wrap: wrap; gap: 16px;"):
                    for disease_item in related_diseases_data:
                        DiseaseCard(disease_item)
            else:
                solara.Info(i18n.t("species.messages.disease_unavailable"))

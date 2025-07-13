import solara
import solara.lab
from solara.alias import rv
from typing import List, Optional, cast, Dict, Any, Callable
import asyncio
from ...config import DISEASE_DETAIL_ENDPOINT_TEMPLATE, SPECIES_LIST_ENDPOINT, DISEASE_VECTORS_ENDPOINT_TEMPLATE
from ...state import fetch_api_data, selected_disease_item_id
from ...config import COLOR_PRIMARY, FONT_HEADINGS, COLOR_TEXT
from frontend.components.species.species_card import SpeciesCard
import i18n

i18n.add_translation("disease.gallery_link", "Go to Disease Gallery", locale="en")
i18n.add_translation("disease.error.load", "Could not load disease details: %{error}", locale="en")
i18n.add_translation("disease.error.no_id", "No disease ID specified in the URL.", locale="en")
i18n.add_translation("disease.error.not_found", 'Disease details for "%{disease_id}" not found or are unavailable.', locale="en")
i18n.add_translation("disease.sections.description", "Description", locale="en")
i18n.add_translation("disease.sections.symptoms", "Symptoms", locale="en")
i18n.add_translation("disease.sections.treatment", "Treatment", locale="en")
i18n.add_translation("disease.sections.prevention", "Prevention", locale="en")
i18n.add_translation("disease.sections.vectors", "Vector Species", locale="en")
i18n.add_translation("disease.labels.prevalence", "Prevalence: %{prevalence}", locale="en")
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
i18n.add_translation("disease.labels.prevalence", "Распространенность: %{prevalence}", locale="ru")
i18n.add_translation("disease.messages.no_description", "Описание отсутствует.", locale="ru")
i18n.add_translation("disease.messages.no_vectors", "Известные переносчики отсутствуют.", locale="ru")
i18n.add_translation("disease.errors.vector_load", "Ошибка загрузки переносчиков: %{error}", locale="ru")


@solara.component
def DiseaseDetailPageComponent():
    disease_id = selected_disease_item_id.value
    disease_data, set_disease_data = solara.use_state(cast(Optional[Dict[str, Any]], None))
    vectors_data, set_vectors_data = solara.use_state(cast(List[Dict[str, Any]], []))
    loading, set_loading = solara.use_state(False)
    vectors_loading, set_vectors_loading = solara.use_state(False)
    error, set_error = solara.use_state(cast(Optional[str], None))
    vectors_error, set_vectors_error = solara.use_state(cast(Optional[str], None))
    current_locale = i18n.get("locale")

    print(f"DEBUG: DISEASE_DETAIL.PY - Initializing for disease_id: '{disease_id}'")

    def _fetch_disease_detail_effect() -> Optional[Callable[[], None]]:
        task_ref = [cast(Optional[asyncio.Task], None)]

        async def _async_task():
            print(f"DEBUG: DISEASE_DETAIL.PY _fetch_disease_detail_effect for ID: '{disease_id}' - Task started.")
            if not disease_id:
                print("DEBUG: DISEASE_DETAIL.PY Effect: No disease_id provided.")
                set_disease_data(None)
                set_error("No disease ID specified in URL.")
                set_loading(False)
                return

            print(f"DEBUG: DISEASE_DETAIL.PY Effect: Attempting to fetch data for '{disease_id}'")
            set_disease_data(None)
            set_error(None)
            set_loading(True)
            set_vectors_data([])
            set_vectors_error(None)
            try:
                url = DISEASE_DETAIL_ENDPOINT_TEMPLATE.format(disease_id=disease_id)
                params = {"lang": current_locale}
                print(f"DEBUG: DISEASE_DETAIL.PY Effect: Fetching URL: {url} with params {params}")
                data = await fetch_api_data(url, params=params)

                current_task = task_ref[0]
                if current_task and current_task.cancelled():
                    print(f"DEBUG: DISEASE_DETAIL.PY Effect task for {disease_id} was cancelled post-await.")
                    return

                if data is None:
                    print(f"DEBUG: DISEASE_DETAIL.PY Effect: No data returned for {disease_id}")
                    set_error(f"Details for '{disease_id}' not found or an API error occurred.")
                    set_disease_data(None)
                else:
                    print(f"DEBUG: DISEASE_DETAIL.PY Effect: Data received for {disease_id}: {data}")
                    set_disease_data(data)
                    set_error(None)

                    # Now, fetch the associated vectors using the new endpoint.
                    set_vectors_loading(True)
                    try:
                        vectors_url = DISEASE_VECTORS_ENDPOINT_TEMPLATE.format(disease_id=disease_id)
                        vectors_params = {"lang": current_locale}
                        vector_species = await fetch_api_data(vectors_url, params=vectors_params)
                        if vector_species is not None:
                            set_vectors_data(vector_species)
                        else:
                            set_vectors_data([])  # Ensure it's an empty list on failure
                            set_vectors_error("Failed to load vector data, or none exist.")

                    except Exception as e:
                        print(f"DEBUG: DISEASE_DETAIL.PY Effect: Error fetching vector data: {e}")
                        set_vectors_error(f"Could not load vector species: {str(e)}")
                    finally:
                        set_vectors_loading(False)

            except asyncio.CancelledError:
                print(f"DEBUG: DISEASE_DETAIL.PY Effect _async_task for {disease_id} was cancelled.")
                raise
            except Exception as e:
                print(f"DEBUG: DISEASE_DETAIL.PY Effect: Unexpected error in _async_task for {disease_id}: {e}")
                set_error(f"An unexpected error occurred: {str(e)}")
                set_disease_data(None)
            finally:
                set_loading(False)
                print(
                    f"DEBUG: DISEASE_DETAIL.PY Effect: Fetch process finished for {disease_id}. Loading state: {loading}"
                )

        task_ref[0] = asyncio.create_task(_async_task())
        print(f"DEBUG: DISEASE_DETAIL.PY _fetch_disease_detail_effect for ID: '{disease_id}' - Task created.")

        def cleanup():
            current_task = task_ref[0]
            if current_task and not current_task.done():
                print(f"DEBUG: DISEASE_DETAIL.PY Cleanup: Cancelling task for ID {disease_id}")
                current_task.cancel()
            else:
                print(f"DEBUG: DISEASE_DETAIL.PY Cleanup: Task for ID {disease_id} already done or no task found.")

        return cleanup

    solara.use_effect(_fetch_disease_detail_effect, [disease_id, current_locale])

    with solara.Column(align="center", classes=["pa-4"], style="max-width: 900px; margin: auto;"):
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
                i18n.t("disease.error.load", error=error), icon="mdi-alert-circle-outline", style="margin-top: 20px;"
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
                f"# {disease_data.get('name', 'N/A')}",
                style=f"font-family: {FONT_HEADINGS}; text-align: center; margin-bottom: 20px;",
            )
            rv.Divider(style="margin: 15px 0;")

            with solara.Row(style="margin-top:20px; gap: 20px;", justify="center"):
                with solara.Column(align="center"):
                    if disease_data.get("image_url"):
                        rv.Img(
                            src=disease_data["image_url"],
                            width="100%",
                            max_width="350px",
                            style="border-radius: 8px; object-fit:cover; border: 1px solid #eee; box-shadow: 0 2px 8px rgba(0,0,0,0.1);",
                        )
                    else:
                        rv.Icon(
                            children=["mdi-image-off"],
                            size="200px",
                            color="grey",
                            style="display:block; margin:auto; width:100%; max-height:300px; border: 1px dashed #ccc; border-radius: 8px; padding: 20px;",
                        )

                    if prevalence := disease_data.get("prevalence"):
                        rv.Chip(
                            children=[i18n.t("disease.labels.prevalence", prevalence=prevalence)],
                            color="blue",
                            text_color="white",
                            class_="mt-3 pa-2 elevation-1",
                            style="font-size: 1em;",
                        )

                with solara.Column():
                    sections = [
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
                                i18n.t("disease.messages.no_description"), style="font-style: italic; color: #777;"
                            )

            solara.Markdown(
                f"## {i18n.t('disease.sections.vectors')}",
                style=f"font-family: {FONT_HEADINGS}; text-align: center; margin-top: 30px; margin-bottom: 15px;",
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
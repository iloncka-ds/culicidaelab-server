import solara
import solara.lab
from solara.alias import rv
import httpx
import asyncio
from typing import Dict, Any, List, Optional, cast, Callable
from ...state import (fetch_api_data, disease_list_data_reactive,
                      disease_list_loading_reactive, disease_list_error_reactive,
                      selected_disease_item_id,
    use_locale_effect,
    current_locale)
from frontend.components.diseases.disease_card import DiseaseCard

from ...config import (
    COLOR_PRIMARY,
    DISEASE_LIST_ENDPOINT,
    load_themes,
    page_style,
    heading_style,
    sub_heading_style,
    card_style,
    card_content_style,
    icon_style,
    footer_style,
)
import i18n

i18n.add_translation("disease_gallery.title", "Vector-Borne Disease Gallery", locale="en")
i18n.add_translation("disease_gallery.search.placeholder", "Search disease...", locale="en")
i18n.add_translation("disease_gallery.search.button", "Search", locale="en")
i18n.add_translation("disease_gallery.error.load", "Could not load diseases: %{error}", locale="en")
i18n.add_translation("disease_gallery.messages.no_results", "No diseases found matching your criteria.", locale="en")
i18n.add_translation("disease_gallery.messages.initializing", "Initializing disease data or an unexpected issue occurred.", locale="en")

i18n.add_translation("disease_gallery.title", "Трансмиссивные заболевания", locale="ru")
i18n.add_translation("disease_gallery.search.placeholder", "Поиск заболеваний...", locale="ru")
i18n.add_translation("disease_gallery.search.button", "Поиск", locale="ru")
i18n.add_translation("disease_gallery.error.load", "Ошибка загрузки списка заболеваний: %{error}", locale="ru")
i18n.add_translation("disease_gallery.messages.no_results", "Информация о заболевании не найдена.", locale="ru")
i18n.add_translation("disease_gallery.messages.initializing", "Инициализация данных или непредвиденная ошибка.", locale="ru")


@solara.component
def DiseaseGalleryPageComponent():
    theme = load_themes(solara.lab.theme)
    use_locale_effect()
    # heading_style = f"font-size: 2.5rem; text-align: center; margin-bottom: 1rem; color: {theme.themes.light.primary};"
    # page_style = "align: center; padding: 2rem; max-width: 1200px; margin: auto;"
    search_query, set_search_query = solara.use_state("")
    # current_locale = i18n.get("locale")

    def _load_disease_list_data_effect() -> Optional[Callable[[], None]]:
        task_ref = [cast(Optional[asyncio.Task], None)]

        async def _async_load_task():
            params = {"lang": current_locale.value}
            if search_query:
                params["search"] = search_query

            data = await fetch_api_data(
                DISEASE_LIST_ENDPOINT,
                params=params,
                loading_reactive=disease_list_loading_reactive,
                error_reactive=disease_list_error_reactive,
            )

            actual_disease_list = []
            if isinstance(data, dict) and "diseases" in data and isinstance(data["diseases"], list):
                actual_disease_list = data["diseases"]
            elif isinstance(data, list):
                actual_disease_list = data
            else:
                if data is not None:
                    disease_list_error_reactive.value = (
                        disease_list_error_reactive.value or "Unexpected data format from API."
                    )

            current_task = task_ref[0]
            if not (current_task and current_task.cancelled()):
                disease_list_data_reactive.value = actual_disease_list

        task_ref[0] = asyncio.create_task(_async_load_task())

        def cleanup():
            current_task = task_ref[0]
            if current_task and not current_task.done():
                current_task.cancel()

        return cleanup

    solara.use_effect(_load_disease_list_data_effect, [search_query, current_locale.value])

    displayed_diseases = disease_list_data_reactive.value

    # with solara.Column(style="padding-bottom: 20px; min-height: calc(100vh - 120px);"):
    solara.Text(
        i18n.t('disease_gallery.title'),
        style=heading_style,
    )

    with solara.Div(
        classes=["pa-2 ma-2 elevation-1"],
        style=f"border-radius: 6px; background-color: white; position: sticky; top: 0px; z-index:10; margin-bottom:10px;",
    ):
        with solara.ColumnsResponsive(default=[12, "auto"], small=[8, 4], gutters="10px"):
            solara.InputText(
                label=i18n.t("disease_gallery.search.placeholder"),
                value=search_query,
                on_value=set_search_query,
                continuous_update=False,
            )
            solara.Button(
                i18n.t("disease_gallery.search.button"),
                icon_name="mdi-magnify",
                outlined=True,
                color=COLOR_PRIMARY,
                on_click=lambda: solara.Warning("Filter panel not yet implemented."),
                style="width: 100%;",
            )


    if disease_list_loading_reactive.value:
        solara.SpinnerSolara(size="60px")
    elif disease_list_error_reactive.value:
        solara.Error(
            i18n.t("disease_gallery.error.load"),
            icon="mdi-alert-circle-outline",
        )
    elif not displayed_diseases and not disease_list_loading_reactive.value:
        solara.Info(
            i18n.t("disease_gallery.messages.no_results"),
            icon="mdi-information-outline",
            style="margin: 16px;",
        )
    elif displayed_diseases:
        with solara.ColumnsResponsive(
            default=[12],
            small=[6, 6],
            medium=[4, 4, 4],
            large=[4, 4, 4],
            gutters="16px",
            classes=["pa-2"],
        ):
            for disease_item in displayed_diseases:
                DiseaseCard(disease_item)
    else:
        solara.Info(
            i18n.t("disease_gallery.messages.initializing"),
            icon="mdi-information-outline",
            style="margin: 16px;",
        )

    # rv.Spacer(height="2rem")

    # with solara.Div(style=footer_style):
    #     solara.Markdown(i18n.t("home.disclaimer"))
    #     solara.Markdown(i18n.t("home.footer"))
"""
Defines a Solara component for displaying a searchable gallery of diseases.

This module contains the `DiseaseGalleryPageComponent`, which fetches a list of
diseases from an API and displays them in a responsive grid of `DiseaseCard`
components. It includes a search bar for filtering the results.
"""

import asyncio
from typing import Optional, cast

from collections.abc import Callable

import i18n
import solara

from frontend.components.diseases.disease_card import DiseaseCard

from frontend.config import (
    COLOR_PRIMARY,
    DISEASE_LIST_ENDPOINT,
    gallery_search_div_style,
    heading_style,
)
from frontend.state import (
    current_locale,
    disease_list_data_reactive,
    disease_list_error_reactive,
    disease_list_loading_reactive,
    fetch_api_data,
    use_locale_effect,
)

i18n.add_translation("disease_gallery.title", "Vector-Borne Disease Gallery", locale="en")
i18n.add_translation("disease_gallery.search.placeholder", "Search disease...", locale="en")
i18n.add_translation("disease_gallery.search.button", "Search", locale="en")
i18n.add_translation("disease_gallery.error.load", "Could not load diseases: %{error}", locale="en")
i18n.add_translation("disease_gallery.messages.no_results", "No diseases found matching your criteria.", locale="en")
i18n.add_translation(
    "disease_gallery.messages.initializing",
    "Initializing disease data or an unexpected issue occurred.",
    locale="en",
)

i18n.add_translation("disease_gallery.title", "Трансмиссивные заболевания", locale="ru")
i18n.add_translation("disease_gallery.search.placeholder", "Поиск заболеваний...", locale="ru")
i18n.add_translation("disease_gallery.search.button", "Поиск", locale="ru")
i18n.add_translation("disease_gallery.error.load", "Ошибка загрузки списка заболеваний: %{error}", locale="ru")
i18n.add_translation("disease_gallery.messages.no_results", "Информация о заболевании не найдена.", locale="ru")
i18n.add_translation(
    "disease_gallery.messages.initializing",
    "Инициализация данных или непредвиденная ошибка.",
    locale="ru",
)


@solara.component
def DiseaseGalleryPageComponent():
    """
    Displays a searchable gallery of vector-borne diseases.

    This component provides a user interface for browsing a collection of diseases.
    It fetches disease data from a remote API and presents it as a grid of
    `DiseaseCard` components. Key features include a search bar to filter
    diseases by name and dynamic data fetching that responds to both search
    queries and changes in the application's locale.

    The component manages its own state for loading, data, and errors using
    global reactive variables, ensuring the UI is always in sync with the
    data fetching process. It handles loading spinners, error messages, and
    'no results' notifications.

    Example:
        This component is designed to be a main page view. To use it,
        you would typically include it in your app's layout or routing setup.

        ```python
        import solara

        @solara.component
        def Page():
            # The gallery component manages its own data fetching and state.
            with solara.Column(align="center"):
                DiseaseGalleryPageComponent()

        # You would then render this Page component in your main application.
        ```
    """
    use_locale_effect()

    search_query, set_search_query = solara.use_state("")

    def perform_search(input_text):
        set_search_query(input_text)

    def _load_disease_list_data_effect() -> Callable[[], None] | None:
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

    solara.Text(
        i18n.t("disease_gallery.title"),
        style=heading_style,
    )

    with solara.Div(
        classes=["pa-2 ma-2 elevation-1"],
        style=gallery_search_div_style,
    ):
        with solara.ColumnsResponsive(default=[12, "auto"], small=[8, 4], gutters="10px"):
            solara.InputText(
                label=i18n.t("disease_gallery.search.placeholder"),
                value=search_query,
                on_value=lambda search_query: perform_search(search_query),
                continuous_update=False,
            )
            solara.Button(
                i18n.t("disease_gallery.search.button"),
                icon_name="mdi-magnify",
                outlined=True,
                color=COLOR_PRIMARY,
                on_click=lambda: perform_search(search_query),
                style="width: 100%;",
            )

    if disease_list_loading_reactive.value:
        solara.SpinnerSolara(size="60px")
    elif disease_list_error_reactive.value:
        solara.Error(
            i18n.t("disease_gallery.error.load", error=disease_list_error_reactive.value or "Unknown error"),
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

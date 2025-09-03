import solara
import solara.lab
import asyncio
from typing import Optional, cast

from collections.abc import Callable
from ...state import (
    fetch_api_data,
    species_list_data_reactive,
    species_list_loading_reactive,
    species_list_error_reactive,
    use_locale_effect,
    current_locale,
)
from frontend.components.species.species_card import SpeciesCard
from ...config import (
    COLOR_PRIMARY,
    SPECIES_LIST_ENDPOINT,
    heading_style,
    gallery_search_div_style,
)
import i18n

i18n.add_translation("species_gallery.title", "Mosquito Species Gallery", locale="en")
i18n.add_translation("species_gallery.search.placeholder", "Search by name...", locale="en")
i18n.add_translation("species_gallery.search.button", "Search", locale="en")
i18n.add_translation("species_gallery.error.load", "Could not load species: %{error}", locale="en")
i18n.add_translation("species_gallery.messages.no_results", "No species found matching your criteria.", locale="en")
i18n.add_translation(
    "species_gallery.messages.initializing",
    "Initializing species data or an unexpected issue occurred.",
    locale="en",
)
i18n.add_translation("species.status.high", "Vector Status: High", locale="en")
i18n.add_translation("species.status.medium", "Vector Status: Medium", locale="en")
i18n.add_translation("species.status.low", "Vector Status: Low", locale="en")
i18n.add_translation("species.status.unknown", "Vector Status: Unknown", locale="en")

i18n.add_translation("species_gallery.title", "База данных эпидемиологически опасных видов комаров", locale="ru")
i18n.add_translation("species_gallery.search.placeholder", "Поиск по названию...", locale="ru")
i18n.add_translation("species_gallery.search.button", "Поиск", locale="ru")
i18n.add_translation("species_gallery.error.load", "Ошибка загрузки видов: %{error}", locale="ru")
i18n.add_translation("species_gallery.messages.no_results", "Виды по вашему запросу не найдены.", locale="ru")
i18n.add_translation(
    "species_gallery.messages.initializing",
    "Инициализация данных или непредвиденная ошибка.",
    locale="ru",
)
i18n.add_translation("species.status.high", "Степень риска: Высокий", locale="ru")
i18n.add_translation("species.status.medium", "Степень риска: Средний", locale="ru")
i18n.add_translation("species.status.low", "Степень риска: Низкий", locale="ru")
i18n.add_translation("species.status.unknown", "Степень риска: Неизвестно", locale="ru")


@solara.component
def SpeciesGalleryPageComponent():
    # theme = load_themes(solara.lab.theme)
    # heading_style = f"font-size: 2.5rem; text-align: center; margin-bottom: 1rem; color: {theme.themes.light.primary};"
    # page_style = "align: center; padding: 2rem; max-width: 1200px; margin: auto;"
    search_query, set_search_query = solara.use_state("")
    # current_locale = i18n.get("locale")
    use_locale_effect()

    def _load_species_list_data_effect() -> Callable[[], None] | None:
        task_ref = [cast(Optional[asyncio.Task], None)]

        async def _async_load_task():
            params = {"lang": current_locale.value}
            if search_query:
                params["search"] = search_query

            data = await fetch_api_data(
                SPECIES_LIST_ENDPOINT,
                params=params,
                loading_reactive=species_list_loading_reactive,
                error_reactive=species_list_error_reactive,
            )

            actual_species_list = []
            if isinstance(data, dict) and "species" in data and isinstance(data["species"], list):
                actual_species_list = data["species"]
            elif isinstance(data, list):
                actual_species_list = data
            else:
                if data is not None:
                    species_list_error_reactive.value = (
                        species_list_error_reactive.value or "Unexpected data format from API."
                    )

            current_task = task_ref[0]
            if not (current_task and current_task.cancelled()):
                species_list_data_reactive.value = actual_species_list

        task_ref[0] = asyncio.create_task(_async_load_task())

        def cleanup():
            current_task = task_ref[0]
            if current_task and not current_task.done():
                current_task.cancel()

        return cleanup

    solara.use_effect(_load_species_list_data_effect, [search_query, current_locale.value])

    displayed_species = species_list_data_reactive.value

    with solara.Column(style="padding-bottom: 20px; min-height: calc(100vh - 120px);"):
        solara.Text(
            i18n.t("species_gallery.title"),
            style=heading_style,
        )
        # Mobile-friendly search bar section
        with solara.Div(
            classes=["pa-2 ma-2 elevation-1"],
            style=gallery_search_div_style,
        ):
            with solara.ColumnsResponsive(default=[12, "auto"], small=[8, 4], gutters="10px"):
                solara.InputText(
                    label=i18n.t("species_gallery.search.placeholder"),
                    value=search_query,
                    on_value=set_search_query,
                    continuous_update=True,
                )
                solara.Button(
                    i18n.t("species_gallery.search.button"),
                    icon_name="mdi-magnify",
                    outlined=True,
                    color=COLOR_PRIMARY,
                    # on_click=lambda: solara.Warning("Filter panel not yet implemented."),
                    style="width: 100%;",  # Ensure button takes full width of its column
                )

        if species_list_loading_reactive.value:
            solara.SpinnerSolara(size="60px")
        elif species_list_error_reactive.value:
            solara.Error(
                i18n.t("species_gallery.error.load"),
                icon="mdi-alert-circle-outline",
            )
        elif displayed_species:
            with solara.ColumnsResponsive(
                # Adjusted grid for better alignment across screen sizes
                default=[12],
                small=[6],
                medium=[4],
                large=[4],
                gutters="16px",
                classes=["pa-2"],
            ):
                for species_item in displayed_species:
                    SpeciesCard(species_item)
        elif not displayed_species and not species_list_loading_reactive.value:
            solara.Info(
                i18n.t("species_gallery.messages.no_results"),
                icon="mdi-information-outline",
                style="margin: 16px;",
            )
        else:
            solara.Info(
                i18n.t("species_gallery.messages.initializing"),
                icon="mdi-information-outline",
                style="margin: 16px;",
            )

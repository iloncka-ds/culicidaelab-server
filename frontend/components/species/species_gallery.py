import solara
import solara.lab
from solara.alias import rv
import httpx
import asyncio
from typing import Dict, Any, List, Optional, cast, Callable
from ...state import (
    fetch_api_data,
    selected_species_item_id,
    species_list_data_reactive,
    species_list_loading_reactive,
    species_list_error_reactive,
)
from frontend.components.species.species_card import SpeciesCard
from ...config import (
    COLOR_PRIMARY,
    FONT_HEADINGS,
    COLOR_TEXT,
    SPECIES_LIST_ENDPOINT,
    SPECIES_DETAIL_ENDPOINT_TEMPLATE,
    API_BASE_URL,
    load_themes
)
import i18n

i18n.add_translation("species_gallery.title", "Mosquito Species Gallery", locale="en")
i18n.add_translation("species_gallery.search.placeholder", "Search by name...", locale="en")
i18n.add_translation("species_gallery.search.button", "Search", locale="en")
i18n.add_translation("species_gallery.error.load", "Could not load species: %{error}", locale="en")
i18n.add_translation("species_gallery.messages.no_results", "No species found matching your criteria.", locale="en")
i18n.add_translation(
    "species_gallery.messages.initializing", "Initializing species data or an unexpected issue occurred.", locale="en"
)

i18n.add_translation("species_gallery.title", "База данных эпидемиологически опасных видов комаров", locale="ru")
i18n.add_translation("species_gallery.search.placeholder", "Поиск по названию...", locale="ru")
i18n.add_translation("species_gallery.search.button", "Поиск", locale="ru")
i18n.add_translation("species_gallery.error.load", "Ошибка загрузки видов: %{error}", locale="ru")
i18n.add_translation("species_gallery.messages.no_results", "Виды по вашему запросу не найдены.", locale="ru")
i18n.add_translation("species_gallery.messages.initializing", "Инициализация данных или непредвиденная ошибка.", locale="ru")


@solara.component
def SpeciesGalleryPageComponent():
    theme = load_themes(solara.lab.theme)
    heading_style = f"font-size: 1.5rem; ftext-align: center; margin-bottom: 1rem; color: {theme.themes.light.primary};"

    search_query, set_search_query = solara.use_state("")
    current_locale = i18n.get("locale")

    def _load_species_list_data_effect() -> Optional[Callable[[], None]]:
        task_ref = [cast(Optional[asyncio.Task], None)]

        async def _async_load_task():
            params = {"lang": current_locale}
            if search_query:
                params["search"] = search_query

            data = await fetch_api_data(
                SPECIES_LIST_ENDPOINT,
                params=params,
                loading_reactive=species_list_loading_reactive,
                error_reactive=species_list_error_reactive,
            )

            print("---- Received Species List API Data ----")
            print(data)
            print("--------------------------------------")

            actual_species_list = []
            if isinstance(data, dict) and "species" in data and isinstance(data["species"], list):
                actual_species_list = data["species"]
                print(
                    f"Page Effect: Setting species list from dict (count={data.get('count', len(actual_species_list))})"
                )
            elif isinstance(data, list):
                actual_species_list = data
                print(f"Page Effect: Setting species list from direct list (count={len(actual_species_list)})")
            else:
                print(f"Warning: Unexpected data format from species list API: {type(data)}. List empty.")
                species_list_error_reactive.value = (
                    species_list_error_reactive.value or "Unexpected data format from API."
                )

            current_task = task_ref[0]
            if not (current_task and current_task.cancelled()):
                species_list_data_reactive.value = actual_species_list
            else:
                print(f"Species list load task for search '{search_query}' was cancelled before setting data.")

        task_ref[0] = asyncio.create_task(_async_load_task())

        def cleanup():
            current_task = task_ref[0]
            if current_task and not current_task.done():
                print(f"Cleaning up: Cancelling species list task for search '{search_query}'")
                current_task.cancel()

        return cleanup

    solara.use_effect(_load_species_list_data_effect, [search_query, current_locale])

    displayed_species = species_list_data_reactive.value

    with solara.Column(style="padding-bottom: 20px; min-height: calc(100vh - 120px);"):
        solara.Markdown(
            f"{i18n.t('species_gallery.title')}",
            style=heading_style,
        )
        with solara.Row(
            classes=["pa-2 ma-2 elevation-1"],
            style="border-radius: 6px; background-color: var(--solara-card-background-color); align-items: center; gap: 10px; position: sticky; top: 0px; z-index:10; margin-bottom:10px;",
        ):
            solara.InputText(
                label=i18n.t("species_gallery.search.placeholder"),
                value=search_query,
                on_value=set_search_query,
                continuous_update=False,
                style="flex-grow: 1;",
            )
            solara.Button(
                i18n.t("species_gallery.search.button"),
                icon_name="mdi-magnify",
                outlined=True,
                color=COLOR_PRIMARY,
                on_click=lambda: solara.Warning("Filter panel not yet implemented."),
            )

        if species_list_loading_reactive.value:
            solara.SpinnerSolara(size="60px")
        elif species_list_error_reactive.value:
            solara.Error(
                i18n.t("species_gallery.error.load", error=species_list_error_reactive.value),
                icon="mdi-alert-circle-outline",
            )
        elif displayed_species:
            if not displayed_species:
                solara.Info(
                    i18n.t("species_gallery.messages.no_results"), icon="mdi-information-outline", style="margin: 16px;"
                )
            else:
                with solara.ColumnsResponsive(
                    default=[3, 3, 3, 3],
                    large=[4, 4, 4],
                    medium=[6, 6],
                    small=[12],
                    gutters="16px",
                    classes=["pa-2"],
                ):
                    for species_item in displayed_species:
                        SpeciesCard(species_item)
        else:
            solara.Info(
                i18n.t("species_gallery.messages.initializing"),
                icon="mdi-information-outline",
                style="margin: 16px;",
            )
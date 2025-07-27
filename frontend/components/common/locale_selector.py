import solara
import i18n
from typing import Optional, Callable
from ...state import current_locale, use_locale_effect
LOCALES = {

    "ru": "Русский",
    "en": "English",
}

i18n.add_translation("common.locale_selector.tooltip", "Change language", locale="en")
i18n.add_translation("common.locale_selector.tooltip", "Изменить язык", locale="ru")


def set_locale(locale: str):
    i18n.set("locale", locale)


@solara.component
def LocaleSelector(on_change: Optional[Callable[[], None]] = None):
    """A language selector component.

    Args:
        on_change: A callback function that is called when the locale changes.
    """

    use_locale_effect()
    def handle_locale_change(new_locale: str):
        # First, update the i18n library

        # Second, update the component's own state
        current_locale.set(new_locale)
        set_locale(new_locale)

        # Finally, trigger the parent's callback to force a re-render
        if on_change:
            on_change()

    with solara.Tooltip(i18n.t("common.locale_selector.tooltip")):
        with solara.Div(style="display: flex; align-items: center;"):
            solara.Text("🌐", style="font-size: 1.2rem; margin-right: 8px;")
            solara.Select(
                label="",
                value=current_locale.value,
                values=list(LOCALES.keys()),
                on_value=lambda new_locale: handle_locale_change(new_locale),
                dense=True,
                style="max-width: 50px;",
            )

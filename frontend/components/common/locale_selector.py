import solara
import i18n

from collections.abc import Callable
from frontend.state import current_locale, use_locale_effect

LOCALES = {
    "ru": "Русский",
    "en": "English",
}

i18n.add_translation("common.locale_selector.tooltip", "Change language", locale="en")
i18n.add_translation("common.locale_selector.tooltip", "Изменить язык", locale="ru")


def set_locale(locale: str):
    i18n.set("locale", locale)


@solara.component
def LocaleSelector(on_change: Callable[[], None] | None = None):
    """
    A language selector component that allows users to change the application's language.

    This component displays a dropdown menu with a list of available languages.
    When a user selects a new language, the application's locale is updated,
    and an optional callback function is triggered.

    Args:
        on_change: An optional callback function that is called when the locale changes.

    Example:
        ```python
        import solara

        @solara.component
        def Page():
            def on_locale_change():
                print("Locale has been changed.")

            with solara.Column():
                solara.Text("Select your preferred language:")
                LocaleSelector(on_change=on_locale_change)
        ```
    """

    use_locale_effect()

    def handle_locale_change(new_locale: str):
        current_locale.set(new_locale)
        set_locale(new_locale)

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

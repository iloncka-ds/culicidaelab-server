import solara
import i18n
from typing import List, Optional

# Supported locales with their display names
LOCALES = {
    "en": "English",
    "ru": "Русский",
    # Add more locales as needed
}


def get_current_locale() -> str:
    return i18n.get("locale")


def set_locale(locale: str):
    i18n.set("locale", locale)
    # You might want to store this in browser localStorage or a cookie for persistence
    # solara.reload()  # Uncomment if you need to force a full reload


@solara.component
def LocaleSelector():
    current_locale = solara.use_reactive(get_current_locale())

    with solara.Tooltip("Change language"):
        with solara.Div(style="display: flex; align-items: center;"):
            solara.Text("🌐", style="font-size: 1.2rem; margin-right: 8px;")
            solara.Select(
                label="",
                value=current_locale.value,
                values=list(LOCALES.keys()),
                # value_names=[LOCALES[code] for code in LOCALES],
                on_value=lambda new_locale: (set_locale(new_locale), current_locale.set(new_locale)),
                dense=True,
                style="max-width: 50px;",
            )

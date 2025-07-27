import solara
import solara.routing
from solara.alias import rv
from pathlib import Path
from ..config import load_themes
from frontend.components.common.locale_selector import LocaleSelector
from ..state import current_locale, use_locale_effect

import i18n


def setup_i18n():
    i18n.load_path.append(str(Path(__file__).parent.parent / "translations"))
    # i18n.set("fallback", "ru")


# route_icons = {
#     "/": "mdi-home",
#     "predict": "mdi-chart-bar",
#     "map": "mdi-map",
#     "species": "mdi-leaf",
#     "diseases": "mdi-virus-outline",
# }

@solara.component
def Home():
    # _, set_rerender_trigger = solara.use_state(0)
    # def force_rerender():
    #     set_rerender_trigger(lambda x: x + 1)
    theme = load_themes(solara.lab.theme)
    setup_i18n()
    use_locale_effect()

    # with solara.AppBar():
    #     solara.v.Spacer()
    #     LocaleSelector()
    # with solara.AppBarTitle():
    #     solara.Text(i18n.t("home.app_title"), style="font-size: 2rem; font-weight: bold; color: white;")


    page_style = "align: center; padding: 2rem; max-width: 1200px; margin: auto;"
    heading_style = f"font-size: 2.5rem; font-weight: bold; text-align: center; margin-bottom: 1rem; color: {theme.themes.light.primary};"
    sub_heading_style = "font-size: 1.2rem; text-align: center; margin-bottom: 3rem; color: #555;"
    card_style = "display: flex; flex-direction: column; height: 100%;"
    card_content_style = (
        "padding: 16px; flex-grow: 1; display: flex; flex-direction: column; align-items: center; text-align: center;"
    )
    icon_style = "margin-bottom: 1rem;"
    footer_style = "margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid #eee; text-align: center; font-size: 0.9em; color: #666;"

    card_data = [
        {
            "title": i18n.t("home.cards.predict.title"),
            "icon": "mdi-camera-plus-outline",
            "description": i18n.t("home.cards.predict.description"),
            "link": "predict",
            "button_label": i18n.t("home.cards.predict.button"),
        },
        {
            "title": i18n.t("home.cards.visualize.title"),
            "icon": "mdi-map-marker-radius-outline",
            "description": i18n.t("home.cards.visualize.description"),
            "link": "map",
            "button_label": i18n.t("home.cards.visualize.button"),
        },
        {
            "title": i18n.t("home.cards.species.title"),
            "icon": "mdi-database-search-outline",
            "description": i18n.t("home.cards.species.description"),
            "link": "species",
            "button_label": i18n.t("home.cards.species.button"),
        },
        {
            "title": i18n.t("home.cards.diseases.title"),
            "icon": "mdi-virus-outline",
            "description": i18n.t("home.cards.diseases.description"),
            "link": "diseases",
            "button_label": i18n.t("home.cards.diseases.button"),
        },
    ]

    # with solara.Column(style=page_style):
    solara.Text(i18n.t("home.welcome"), style=heading_style)
    solara.Markdown(
        i18n.t("home.intro"),
        style=sub_heading_style,
    )

    with solara.ColumnsResponsive(
        small=12,
        medium=6,
        large=6,
        gutters=True,
        style="margin-bottom: 2rem;",
    ):
        for item in card_data:
            with solara.Column():
                with solara.Card(
                    title=item["title"],
                    elevation=4,
                    style=card_style,
                    margin=2,
                ):
                    with solara.Column(style=card_content_style):
                        rv.Icon(name=item["icon"], size="4rem", color="primary", style_=icon_style)
                        solara.Markdown(item["description"], style="flex-grow: 1; margin-bottom: 1rem;")

                    with rv.CardActions(style_="justify-content: center; padding-bottom: 16px;"):
                        solara.Button(
                            label=item["button_label"],
                            on_click=lambda link=item["link"]: router.push(link),
                            color="primary",
                            outlined=True,
                            class_="px-4",
                        )

    rv.Spacer(height="2rem")

    with solara.Div(style=footer_style):
        solara.Markdown(i18n.t("home.disclaimer"))
        solara.Markdown(i18n.t("home.footer"))

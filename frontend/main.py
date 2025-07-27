import solara
import solara.lab

from typing import List

import i18n
from pathlib import Path
import frontend.pages.home as home
import frontend.pages.map_visualization as map_visualization
import frontend.pages.species as species
import frontend.pages.prediction as prediction
import frontend.pages.diseases as diseases
from frontend.config import load_themes
from frontend.components.common.locale_selector import LocaleSelector

import logging

from frontend.state import (
    fetch_filter_options,
    use_persistent_user_id,
    use_locale_effect,
    current_locale
)

logging.basicConfig(level=logging.INFO)

i18n.add_translation("layout.home", "Home", locale="en")
i18n.add_translation("layout.predict", "Predict", locale="en")
i18n.add_translation("layout.map", "Map", locale="en")
i18n.add_translation("layout.species", "Species", locale="en")
i18n.add_translation("layout.diseases", "Diseases", locale="en")
i18n.add_translation("layout.home", "Главная", locale="ru")
i18n.add_translation("layout.predict", "Наблюдения", locale="ru")
i18n.add_translation("layout.map", "Карта", locale="ru")
i18n.add_translation("layout.species", "Виды комаров", locale="ru")
i18n.add_translation("layout.diseases", "Заболевания", locale="ru")

def setup_i18n():
    # i18n.load_path.append(str(Path(__file__).parent / "translations"))
    # i18n.load_path.append(str(Path(__file__).parent.parent / "translations"))
    # i18n.set("locale", "ru")
    # i18n.set("fallback", "en")
    i18n.set("skip_locale_root_data", True)
    i18n.set("filename_format", "{namespace}.{locale}.{format}")

theme = load_themes(solara.lab.theme)
active_btn_style = {
    "box-shadow": "none",
    "border-radius": "0px",
    "background-color": f"{theme.themes.light.accent}",
    "color": "white",
}
inactive_btn_style = {
    "box-shadow": "none",
    "border-radius": "0px",
    "background-color": f"{theme.themes.light.primary}",
    "color": "white",
}
row_style = {
    "background-color": f"{theme.themes.light.primary}",
    "color": f"{theme.themes.light.primary}",
    "foreground-color": f"{theme.themes.light.primary}",
    "margin-left": "16px",
    "margin-right": "16px",
    "gap": "0px",
}

page_style = "align: center; padding: 2rem; max-width: 1200px; margin: auto;"

# @solara.component
# def AppInitializer():
#     """A component to handle one-time app initialization tasks."""
#     # This component is now only responsible for setting up i18n.
#     # Data fetching that depends on locale is moved to the Layout.
#     setup_i18n()
#     return None


@solara.component
def Layout(children: List[solara.Element]):
    route_current, routes_all = solara.use_route()
    # setup_i18n()
    use_persistent_user_id()
    use_locale_effect()

    solara.lab.use_task(fetch_filter_options, dependencies=[current_locale.value])
    route_current, routes_all = solara.use_route()
    # with solara.Column():
    # put all buttons in a single row
    with solara.AppLayout(toolbar_dark=True):  # , navigation=False
        with solara.AppBar():
            with solara.AppBarTitle():
                solara.Text("CulicidaeLab")  # , style="font-size: 2rem; font-weight: bold; color: white;"
            with solara.Row(style=row_style):
                for route in routes_all:
                    with solara.Link(route):
                        solara.Button(
                            route.label, style=active_btn_style if route_current == route else inactive_btn_style
                        )
            solara.v.Spacer()
            LocaleSelector()
        solara.Column(style=page_style, children=children)

routes = [
    solara.Route("/", component=home.Home, label=i18n.t("layout.home"), layout=Layout),
    solara.Route("predict", component=prediction.Page, label=i18n.t("layout.predict")),
    solara.Route("map", component=map_visualization.Page, label=i18n.t("layout.map")),
    solara.Route(
        "species",
        component=species.Page,
        label=i18n.t("layout.species"),
        children=[
            solara.Route(
                path=":species_id",
                component=species.Page,
            )
        ],
    ),
    solara.Route(
        "diseases",
        component=diseases.Page,
        label=i18n.t("layout.diseases"),
        children=[
            solara.Route(
                path=":disease_id",
                component=diseases.Page,
            )
        ],
    ),
]

@solara.component
def Page():
    return Layout()

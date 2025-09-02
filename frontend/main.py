import solara
import solara.lab
from solara.alias import rv


import i18n

import frontend.pages.home as home
import frontend.pages.map_visualization as map_visualization
import frontend.pages.species as species
import frontend.pages.prediction as prediction
import frontend.pages.diseases as diseases
from frontend.config import (
    page_style,
    footer_style,
    active_btn_style,
    inactive_btn_style,
    row_style,
)

from frontend.components.common.locale_selector import LocaleSelector

import logging

from frontend.state import (
    fetch_filter_options,
    use_persistent_user_id,
    use_locale_effect,
    current_locale,
)
from frontend.config import load_themes

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


@solara.component
def Layout(children: list[solara.Element]):
    route_current, routes_all = solara.use_route()

    use_persistent_user_id()
    use_locale_effect()
    load_themes(solara.lab.theme)
    solara.lab.use_task(fetch_filter_options, dependencies=[current_locale.value])
    route_current, routes_all = solara.use_route()

    with solara.AppLayout(toolbar_dark=True):
        with solara.AppBar():
            with solara.AppBarTitle():
                solara.Text("CulicidaeLab")
            with solara.Row(style=row_style):
                for route in routes_all:
                    with solara.Link(route):
                        solara.Button(
                            i18n.t(route.label),
                            style=active_btn_style if route_current == route else inactive_btn_style,
                        )
            solara.v.Spacer()
            LocaleSelector()
        with solara.Column(style=page_style, children=children):
            rv.Spacer(height="2rem")

            with solara.Div(style=footer_style):
                solara.Markdown(i18n.t("home.disclaimer"))
                solara.Markdown(i18n.t("home.footer"))


routes = [
    solara.Route("/", component=home.Home, label="layout.home", layout=Layout),
    solara.Route("predict", component=prediction.Page, label="layout.predict"),
    solara.Route("map", component=map_visualization.Page, label="layout.map"),
    solara.Route(
        "species",
        component=species.Page,
        label="layout.species",
        children=[
            solara.Route(
                path=":species_id",
                component=species.Page,
            ),
        ],
    ),
    solara.Route(
        "diseases",
        component=diseases.Page,
        label="layout.diseases",
        children=[
            solara.Route(
                path=":disease_id",
                component=diseases.Page,
            ),
        ],
    ),
]

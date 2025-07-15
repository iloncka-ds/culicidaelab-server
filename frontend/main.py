import solara
import solara.lab

from typing import List, Optional

import i18n
from pathlib import Path
import frontend.pages.home as home
import frontend.pages.map_visualization as map_visualization
import frontend.pages.species as species
import frontend.pages.prediction as prediction
import frontend.pages.diseases as diseases
import logging

from frontend.state import (
    fetch_filter_options,
    use_persistent_user_id,
)

logging.basicConfig(level=logging.INFO)

def setup_i18n():
    i18n.load_path.append(str(Path(__file__).parent / "translations"))
    i18n.set("locale", "ru")
    i18n.set("fallback", "en")
    i18n.set("skip_locale_root_data", True)
    i18n.set("filename_format", "{namespace}.{locale}.{format}")


routes = [
    solara.Route("/", component=home.Page, label=i18n.t("layout.home")),
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
def AppInitializer():
    """A component to handle one-time app initialization tasks."""
    # This component is now only responsible for setting up i18n.
    # Data fetching that depends on locale is moved to the Layout.
    setup_i18n()
    return None


@solara.component
def Layout(children: List[solara.Element]):
    AppInitializer()
    use_persistent_user_id()
    # Fetch filter options whenever the language changes.
    solara.lab.use_task(fetch_filter_options, dependencies=[i18n.get("locale")])

    return solara.AppLayout(
        title="CulicidaeLab",
        children=children,
    )


@solara.component
def Page():
    return Layout()

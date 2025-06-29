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


from frontend.state import (
    fetch_filter_options,
)




def setup_i18n():
    i18n.load_path.append(str(Path(__file__).parent / "translations"))
    i18n.set("locale", "en")
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
    initialized, set_initialized = solara.use_state(False)

    if not initialized:
        solara.lab.use_task(fetch_filter_options)
        set_initialized(True)
    setup_i18n()
    return None


@solara.component
def Layout(children: List[solara.Element]):

    AppInitializer()


    return solara.AppLayout(
        title="CulicidaeLab",
        children=children,

    )







@solara.component
def Page():

    return Layout()

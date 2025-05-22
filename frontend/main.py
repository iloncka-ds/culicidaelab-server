import solara
import solara.lab

from typing import List, Optional

import i18n
from pathlib import Path
# Application imports
import frontend.pages.home as home
import frontend.pages.map_visualization as map_visualization
import frontend.pages.species as species
import frontend.pages.prediction as prediction
import frontend.pages.diseases as diseases


# from frontend.config import load_themes  # Not used in this file
from frontend.state import (
    fetch_filter_options,
    # filter_options_loading_reactive, # Not directly used by AppInitializer for rendering
    # filter_options_error_reactive   # Not directly used by AppInitializer for rendering
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
    # Use a state to track if we've already initialized
    initialized, set_initialized = solara.use_state(False)

    # Use solara.lab.use_task at the component level, not inside an effect
    # This follows the rules of hooks properly
    if not initialized:
        # Run the fetch operation using solara.lab.use_task
        # This properly handles async operations without creating cleanup issues
        solara.lab.use_task(fetch_filter_options)
        # Mark as initialized after the task is started
        set_initialized(True)
    setup_i18n()
    return None


@solara.component
def Layout(children: List[solara.Element]):  # children is the current page content from the router

    AppInitializer()  # Initialize app data

    # `children` here is a list containing the component for the current route.
    # e.g., [<frontend.pages.map_visualization.Page object at ...>]
    # sidebar_is_open, set_sidebar_is_open = solara.use_state(True)
    # dark_effective = solara.lab.use_dark_effective()  # For ThemeToggle

    # toolbar_actions = [
    #     solara.Button(icon_name="mdi-menu", icon=True, on_click=lambda: set_sidebar_is_open(not sidebar_is_open)),
    #     solara.lab.ThemeToggle() # If you want it in the toolbar
    # ]
    # with solara.AppBar():
    #     solara.lab.ThemeToggle()
    # with solara.Sidebar():
    #     with solara.Card("Controls", margin=0, elevation=0):
    #         AppSidebarContent()
    return solara.AppLayout(
        title="CulicidaeLab",
        # navigation=False,  # Let AppLayout handle toolbar navigation tabs from `routes`
        # This will show tabs in the AppBar. If you want only sidebar nav, set this to False.
        children=children,
        # toolbar_dark can be set based on theme if desired
        # color=theme.themes.light.primary  # for the app bar

    )


# The top-level Page component that the router will render into the Layout.
# This is what Solara will typically look for if your file is run directly or as the main app.
# If your `main.py` only defines routes and a Layout, Solara's routing
# mechanism will pass the resolved route's component as `children` to `Layout`.
# So, you might not need a separate top-level Page() component here if `Layout` is the root UI for routes.

# If your routes are defined globally and Solara uses them to pick a page component,
# and that page component then calls `Layout()`, that's a common pattern.
# However, the `solara.AppLayout` is best used as the *outermost* visual component.

# Let's assume Solara's default behavior: routes are defined, and `Layout` is intended
# to wrap the content of the page selected by the router.

# So, `Page()` in your original code should return `Layout()`.
# The `children` argument of `Layout` will be automatically populated by Solara
# with the component of the currently active route.


@solara.component
def Page():  # This is the root component Solara will render.
    # Layout will receive the specific page component (home, map, species) as its children
    # based on the current route.

    # with solara.Sidebar():
    #     with solara.Card("Controls", margin=0, elevation=0):
    #         AppSidebarContent()
    return Layout()
import os
import sys
import asyncio
import solara
import solara.lab

from solara.alias import rv
from typing import List, Optional, cast

# Application imports
import frontend.pages.home as home
import frontend.pages.map_visualization as map_visualization
import frontend.pages.species_database as species_database
from frontend.config import load_themes
from frontend.state import (
    fetch_filter_options,
    # filter_options_loading_reactive, # Not directly used by AppInitializer for rendering
    # filter_options_error_reactive   # Not directly used by AppInitializer for rendering
)

# --- Routes with Icons ---
# To have icons, we can store them in a dictionary or extend solara.Route if needed.
# For simplicity, let's use a dictionary to map paths to icons and labels for the sidebar.
ROUTE_CONFIG = {
    "/": {"component": home.Page, "label": "Home", "icon": "mdi-home"},
    "map": {"component": map_visualization.Page, "label": "Map Visualization", "icon": "mdi-map-marker-radius"},
    "species": {"component": species_database.Page, "label": "Species Database", "icon": "mdi-format-list-bulleted-square"},
}

routes = [
    solara.Route(path=path, component=config["component"], label=config["label"]) # Use label from config for AppLayout nav
    for path, config in ROUTE_CONFIG.items()
]


@solara.component
def AppInitializer():
    """A component to handle one-time app initialization tasks."""
    def _init_app_data_effect():
        async def _async_task():
            await fetch_filter_options()
        asyncio.create_task(_async_task())
    solara.use_effect(_init_app_data_effect, [])
    return None

# @solara.component
# def AppSidebarContent():
#     """Defines the content of the AppLayout's sidebar.
#     This content is conditional based on the current route.
#     """
#     route_current, all_routes_from_hook = solara.use_route()  # Use all_routes_from_hook for navigation if needed

#     # Determine if the current page is the map visualization page
#     is_map_page = False
#     if route_current and route_current.component == map_visualization.Page:  # More robust check
#         is_map_page = True

#     with solara.Div(style="height: 100%; overflow-y: auto;"):  # Make sidebar content scrollable
#         if is_map_page:
#             # Accordion for Map Page Controls
#             # The value prop on ExpansionPanels controls which panels are open by default.
#             # `mandatory=False` allows all to be closed. `multiple=True` allows multiple open.
#             # `value=[]` (list of indices) would mean all closed by default if mandatory=False.
#             # For accordion, typically mandatory=True and value=0 means first is open.
#             # Or, `accordion=True` makes only one openable at a time.
#             # Let's go with multiple openable, none mandatory, all closed initially.

#             # State to manage open/closed panels for the accordion
#             # Each element in the list is the index of an open panel.
#             open_accordion_panels, set_open_accordion_panels = solara.use_state(
#                 cast(List[int], [0])
#             )  # Open "Filters" by default

#             map_accordion_items = [
#                 {"title": "Filters", "icon": "mdi-filter-variant", "component": filter_panel.FilterControls},
#                 {"title": "Map Layers", "icon": "mdi-layers-triple-outline", "component": layer_control.LayerToggle},
#                 {
#                     "title": "Legend",
#                     "icon": "mdi-format-list-bulleted-type",
#                     "component": legend_component.LegendDisplay,
#                 },
#                 {"title": "Details", "icon": "mdi-information-outline", "component": info_panel.InformationDisplay},
#             ]

#             # Using Vuetify's ExpansionPanels directly for accordion behavior
#             with rv.ExpansionPanels(
#                 # accordion=True, # Only one panel open at a time
#                 multiple=True,  # Allow multiple panels to be open
#                 flat=True,  # No box-shadow on panels
#                 value=open_accordion_panels,  # Controlled by state
#                 on_input=set_open_accordion_panels,  # Update state on change
#                 class_="pa-1",  # Some padding around the panels
#             ):
#                 for i, item in enumerate(map_accordion_items):
#                     # rv.ExpansionPanel does not take a 'title' or 'icon_name' prop directly.
#                     # It uses slots for the header and content.
#                     with rv.ExpansionPanel(key=item["title"]):  # Key for reactivity
#                         with rv.ExpansionPanelHeader():
#                             rv.Icon(children=[item["icon"]], left=True, class_="mr-2")
#                             solara.Text(item["title"])
#                         with rv.ExpansionPanelContent(
#                             class_="pt-2",
#                             style="""
#             display: flex;
#             flex-direction: column; /* Stack children of the content vertically (if multiple) */
#             justify-content: center; /* Vertical centering for flex-direction: column */
#             align-items: center;     /* Horizontal centering for flex-direction: column */
#             height: 100%;           /* Make it take full available height for vertical centering to work well */
#             text-align: center;       /* For inline or text elements within the centered content */
#         """,
#                         ):  # Add padding to content
#                             item["component"]()
#         else:
#             # Default Sidebar: General Navigation for other pages
#             with solara.Column(gap="5px", classes=["pa-2"]):
#                 for path_key, config in ROUTE_CONFIG.items():  # Use path_key for dictionary key
#                     # Find the route object to link to for proper active state
#                     target_route = next((r for r in all_routes_from_hook if r.path == path_key), None)
#                     if target_route:
#                         with solara.Link(target_route):
#                             solara.Button(
#                                 label=config["label"],
#                                 icon_name=config["icon"],
#                                 text=True,
#                                 classes=["nav-button-sidebar"],
#                                 style="width: 100%; justify-content: flex-start; margin-bottom: 4px; text-transform: none;",
#                                 color="primary" if route_current == target_route else None,
#                             )


@solara.component
def Layout(children: List[solara.Element]):  # children is the current page content from the router
    from solara.lab import theme
    theme = load_themes(theme)  # Load themes once when Layout is first rendered
    AppInitializer()  # Initialize app data

    # `children` here is a list containing the component for the current route.
    # e.g., [<frontend.pages.map_visualization.Page object at ...>]
    # sidebar_is_open, set_sidebar_is_open = solara.use_state(True)
    # dark_effective = solara.lab.use_dark_effective()  # For ThemeToggle

    # toolbar_actions = [
    #     solara.Button(icon_name="mdi-menu", icon=True, on_click=lambda: set_sidebar_is_open(not sidebar_is_open)),
    #     solara.lab.ThemeToggle() # If you want it in the toolbar
    # ]
    with solara.AppBar():
        solara.lab.ThemeToggle()
    # with solara.Sidebar():
    #     with solara.Card("Controls", margin=0, elevation=0):
    #         AppSidebarContent()
    return solara.AppLayout(
        title="CulicidaeLab",
        # navigation=False,  # Let AppLayout handle toolbar navigation tabs from `routes`
        # This will show tabs in the AppBar. If you want only sidebar nav, set this to False.
        children=children,
        # toolbar_dark can be set based on theme if desired
        color=theme.themes.light.primary  # for the app bar

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
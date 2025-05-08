import solara

# Import pages and components using relative imports
from .pages import home, map_visualization, species_database
from .components.common.app_layout import Layout, NavRoute
from .config import COLOR_PRIMARY, COLOR_BACKGROUND

# Define the routes for the application
routes = [
    NavRoute(path="/", component=home.Page, label="Home", icon="mdi-home"),
    NavRoute(path="map", component=map_visualization.Page, label="Map Visualization", icon="mdi-map-marker-radius"),
    NavRoute(
        path="species",
        component=species_database.Page,
        label="Species Database",
        icon="mdi-format-list-bulleted-square",
    ),
]

# This is the main entry point for Solara applications
@solara.component
def Page():
    # Apply theming
    from solara.lab import theme
    theme.themes.light.primary = COLOR_PRIMARY
    theme.themes.light.background = COLOR_BACKGROUND
    theme.themes.dark.primary = COLOR_PRIMARY
    theme.themes.dark.background = "#121212"

    # Return the Layout component
    # The Layout component will handle the routing internally
    return Layout()


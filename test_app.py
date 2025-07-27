import solara
from solara.components import AppLayout
import reacton.ipyvuetify as v


# Mock i18n for demonstration purposes. In a real application, you would
# use a proper i18n library.
class I18n:
    def t(self, key):
        translations = {
            "layout.home": "Home",
            "layout.predict": "Predict",
            "layout.map": "Map",
            "layout.species": "Species",
            "layout.diseases": "Diseases",
        }
        return translations.get(key, key)


i18n = I18n()

# --- Mock Pages for Demonstration ---
# In your actual application, these would be in their respective files
# (home.py, prediction.py, etc.).


@solara.component
def Home():
    solara.Title("Home")
    solara.Markdown("# Home Page")


@solara.component
def Prediction():
    solara.Title("Prediction")
    solara.Markdown("# Prediction Page")


@solara.component
def MapVisualization():
    solara.Title("Map")
    solara.Markdown("# Map Visualization Page")


@solara.component
def Species(species_id: str = None):
    if species_id:
        solara.Title(f"Species: {species_id}")
        solara.Markdown(f"# Species: {species_id}")
    else:
        solara.Title("Species")
        solara.Markdown("# All Species")


@solara.component
def Diseases(disease_id: str = None):
    if disease_id:
        solara.Title(f"Disease: {disease_id}")
        solara.Markdown(f"# Disease: {disease_id}")
    else:
        solara.Title("Diseases")
        solara.Markdown("# All Diseases")


# --- Route Definitions ---
routes = [
    solara.Route("/", component=Home, label=i18n.t("layout.home")),
    solara.Route("predict", component=Prediction, label=i18n.t("layout.predict")),
    solara.Route("map", component=MapVisualization, label=i18n.t("layout.map")),
    solara.Route(
        "species",
        component=Species,
        label=i18n.t("layout.species"),
        children=[
            solara.Route(
                path=":species_id",
                component=Species,
            )
        ],
    ),
    solara.Route(
        "diseases",
        component=Diseases,
        label=i18n.t("layout.diseases"),
        children=[
            solara.Route(
                path=":disease_id",
                component=Diseases,
            )
        ],
    ),
]

# --- Icon Mapping ---
route_icons = {
    "/": "mdi-home",
    "predict": "mdi-chart-bar",
    "map": "mdi-map",
    "species": "mdi-leaf",
    "diseases": "mdi-virus-outline",
}


# --- Mock Pages for a runnable demonstration ---
# In a real app, these would be in separate files.
@solara.component
def Home():
    solara.Title("Home")
    solara.Markdown("## Welcome to the Home Page")


@solara.component
def Predict():
    solara.Title("Prediction")
    solara.Markdown("## Prediction Model Page")


@solara.component
def Map():
    solara.Title("Map")
    solara.Markdown("## Map Visualization Page")


# --- 1. Define your routes and their icons ---
routes = [
    solara.Route(path="/", component=Home, label=i18n.t("layout.home")),
    solara.Route(path="predict", component=Predict, label=i18n.t("layout.predict")),
    solara.Route(path="map", component=Map, label=i18n.t("layout.map")),
]


# --- 2. Create a Layout component to hold the AppBar ---
@solara.component
def Layout(children):
    """This component defines the main layout, including the AppBar."""
    # The use_route hook gives us the currently active route.
    route_current, _ = solara.use_route()

    with AppLayout(title="Working Navigation App") as main:
        with solara.AppBar():
            # Iterate over your routes to create the navigation buttons
            for route in routes:
                # *** THE KEY FIX IS HERE ***
                # Wrap the Button in a Link to make it navigate.
                with solara.Link(route):
                    solara.Button(
                        label=route.label,
                        icon_name=route_icons.get(route.path),
                        text=True,  # Makes the button look cleaner in an AppBar
                        # Highlight the button if its route is the currently active one
                        color="primary" if route_current == route else None,
                    )

        # --- 3. This is where the content of your pages will be rendered ---
        with solara.Column(style={"width": "100%"}):
            # The 'children' passed to the Layout is the solara.router.Render() output
            children[0]

    return main


# --- 4. The main Page component that ties everything together ---
@solara.component
def Page():
    """
    This is the main entry point of the app.
    It renders the Layout and tells the router where to display the page content.
    """
    # The Layout wraps the router's renderer.
    # solara.router.Render() is the component that actually displays
    # the Home, Predict, or Map component based on the URL.
    return Layout(children=[solara.router.Render()])

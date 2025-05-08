import solara
from typing import List, Optional

# Assuming config.py is in the parent directory of 'components'
# Adjust the import path if your structure is different.
# If CulicidaeLab_server is the root package:
from ...config import COLOR_PRIMARY, COLOR_BACKGROUND, COLOR_TEXT, FONT_HEADINGS, FONT_BODY


class NavRoute(solara.Route):
    icon_name: Optional[str] = None

    def __init__(
        self,
        path: str,
        component,
        label: str,
        icon: Optional[str] = None,
        children: Optional[List["NavRoute"]] = None,
        **kwargs,
    ):
        actual_children = children if children is not None else []
        super().__init__(path=path, component=component, label=label, children=actual_children, **kwargs)
        self.icon_name = icon


@solara.component
def Layout(children: List[solara.Element] = []):
    route_current, routes_all = solara.use_route()

    with solara.VBox(
        style=f"background-color: {COLOR_BACKGROUND}; color: {COLOR_TEXT}; font-family: {FONT_BODY}; height: 100vh; margin:0; padding:0;"
    ) as main_container:
        solara.Style(f"""
            .v-application {{
                font-family: {FONT_BODY} !important;
                background-color: {COLOR_BACKGROUND} !important;
            }}
            .v-application h1, .v-application h2, .v-application h3, .v-application h4, .v-application h5, .v-application h6,
            .v-application .text-h1, .v-application .text-h2, .v-application .text-h3, .v-application .text-h4, .v-application .text-h5, .v-application .text-h6,
            .v-application .display-1, .v-application .headline, .v-application .title,
            .v-application .v-toolbar__title {{
                font-family: {FONT_HEADINGS} !important;
                color: {COLOR_TEXT};
            }}
            .nav-button .v-btn__content {{
                justify-content: flex-start !important;
            }}
            .nav-button.v-btn--active {{
                background-color: rgba(0, 0, 0, 0.08) !important;
                font-weight: bold;
            }}
            .solara-app-layout__content {{
                 padding: 16px;
                 background-color: {COLOR_BACKGROUND} !important;
                 height: calc(100vh - 64px);
                 overflow-y: auto;
            }}
            .v-navigation-drawer__content {{
                background-color: {COLOR_BACKGROUND} !important;
            }}
            .v-app-bar.v-toolbar.v-sheet {{
                 background-color: {COLOR_PRIMARY} !important;
            }}
             .v-toolbar__title, .v-app-bar .v-icon {{
                color: white !important; /* Assuming white text/icons on primary color appbar */
            }}
            .nav-button .v-btn__content .v-icon__svg {{ /* For SVG icons */
                color: {COLOR_TEXT}; /* Default nav icon color */
            }}
            .nav-button.v-btn--active .v-btn__content .v-icon__svg {{
                 color: {COLOR_PRIMARY}; /* Active nav icon color */
            }}
            .nav-button.v-btn--active .v-btn__content {{
                 color: {COLOR_PRIMARY} !important; /* Active nav text color */
            }}
        """)

        # Attempt to load assets/style.css.
        # The path for solara.Style(path=...) is relative to where `solara run` is executed,
        # or relative to the file if it's a single file app.
        # For packages, it's trickier. It might be better to serve assets explicitly.
        # For now, assuming it might work or can be adjusted.
        try:
            solara.Style(path="assets/style.css")
        except Exception as e:
            print(
                f"Could not load assets/style.css: {e}. Ensure the path is correct relative to server execution directory or use Solara's asset system."
            )

        with solara.AppLayout(
            title="CulicidaeLab",
            # color=COLOR_PRIMARY, # This sets the Vuetify theme color name, not hex directly
            # The CSS override for .v-app-bar handles background.
        ) as main_app_layout:
            for route_obj in routes_all:
                if route_obj.path is None:
                    continue

                icon = getattr(route_obj, "icon_name", None)

                with solara.Link(route_obj):
                    solara.Button(
                        label=str(route_obj.label) if route_obj.label else "Unnamed",
                        icon_name=icon,
                        text=True,
                        active=route_obj == route_current,
                        classes=["nav-button"],
                        style="width: 100%; text-transform: none; font-weight: normal; margin-bottom: 4px;",
                    )

            # The children (current page from router) are rendered here by AppLayout
            for child_component in children:
                child_component()

    return main_container

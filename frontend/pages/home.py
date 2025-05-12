import solara
import solara.lab
from frontend.config import load_themes
themes = load_themes()
# from frontend.components.map_module.app_layout import AppSidebarContent, AppMainContent


@solara.component
def Page():
    with solara.AppBar():
        solara.lab.ThemeToggle()
    solara.Markdown("# Home")

@solara.component
def Layout(children):
    route, routes = solara.use_route()
    dark_effective = solara.lab.use_dark_effective()
    return solara.AppLayout(children=children, toolbar_dark=dark_effective, color=themes.light.primary)


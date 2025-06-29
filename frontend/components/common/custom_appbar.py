import solara
import reacton.ipyvuetify as v

app_title = solara.reactive("CuliCidae Lab")


@solara.component
def AppBar():
    route, router = solara.use_route()
    current_title = app_title.value

    if route:
        if route.path == "/species":
            current_title = "Species Database"
        elif route.path == "/diseases":
            current_title = "Disease Database"
        elif route.path_name == ":species_id" and route.parent and route.parent.path == "/info":
            pass
        elif route.path_name == ":disease_id" and route.parent and route.parent.path == "/diseases":
            pass

    return v.AppBar(
        children=[
            v.AppBarNavIcon(on_click=lambda: solara.LayoutApp.drawer.set(True)),
            v.ToolbarTitle(children=[current_title]),
            v.Spacer(),
        ],
    )

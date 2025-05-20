import solara
import reacton.ipyvuetify as v

# This is a reactive value that detail pages can update
# It's better to manage this through a more structured state management approach
# for larger apps, but this demonstrates the concept.
app_title = solara.reactive("CuliCidae Lab")  # Default title


@solara.component
def AppBar():
    route, router = solara.use_route()
    current_title = app_title.value  # Use the reactive title

    # Logic to determine title based on route
    # This can get complex, so the detail page setting the title is often cleaner
    if route:
        if route.path == "/species":
            current_title = "Species Database"
        elif route.path == "/diseases":
            current_title = "Disease Database"
        elif route.path_name == ":species_id" and route.parent and route.parent.path == "/info":
            # Here you'd ideally fetch the species name based on route.session.params.get("species_id")
            # For simplicity, let's just say "Species Detail"
            # In a real app, the species_detail.Page would set app_title.value
            pass  # Rely on app_title.value being set by the detail page
        elif route.path_name == ":disease_id" and route.parent and route.parent.path == "/diseases":
            pass  # Rely on app_title.value being set by the detail page

    # Use solara.AppBar or build your own with ipyvuetify components
    return v.AppBar(
        children=[
            v.AppBarNavIcon(on_click=lambda: solara.LayoutApp.drawer.set(True)),
            v.ToolbarTitle(children=[current_title]),
            v.Spacer(),
            # ... other app bar items ...
        ],
        # ... other AppBar props ...
    )

import solara
from typing import List, Optional


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

    # navbar_color = "#22c55e"  # The green color we want

    with solara.AppLayout(
        title="CulicidaeLab",
        # color="primary",  # This may not work as expected with theme conflicts
        # style=f"background-color: {navbar_color}; color: white;"  # Force green background
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
                    color="primary" if route_obj == route_current else None,
                    style="width: 100%; text-transform: none; font-weight: normal; margin-bottom: 4px; ",
                )

        # The children (current page from router) are rendered here by AppLayout
        for child_component in children:
            child_component()

    return main_app_layout

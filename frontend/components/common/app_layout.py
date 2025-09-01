import solara


class NavRoute(solara.Route):
    icon_name: str | None = None

    def __init__(
        self,
        path: str,
        component,
        label: str,
        icon: str | None = None,
        children: list["NavRoute"] | None = None,
        **kwargs,
    ):
        actual_children = children if children is not None else []
        super().__init__(path=path, component=component, label=label, children=actual_children, **kwargs)
        self.icon_name = icon


@solara.component
def Layout(children: list[solara.Element] = []):
    route_current, routes_all = solara.use_route()

    with solara.AppLayout(
        title="CulicidaeLab",
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

        for child_component in children:
            child_component()

    return main_app_layout

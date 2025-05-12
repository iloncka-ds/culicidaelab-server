import solara
# from frontend.components.map_module.app_layout import AppSidebarContent, AppMainContent


@solara.component
def Page():
    return solara.AppLayout(
        # sidebar=AppSidebarContent(),
        # main=AppMainContent(),
    )


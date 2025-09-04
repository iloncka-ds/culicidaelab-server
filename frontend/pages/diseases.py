import solara

from frontend.components.diseases.disease_gallery import DiseaseGalleryPageComponent
from frontend.components.diseases.disease_detail import DiseaseDetailPageComponent

from frontend.state import selected_disease_item_id, use_locale_effect


@solara.component
def Page():
    """
    Renders the main page for the diseases section, switching between a gallery and a detail view.

    This component acts as a conditional router based on the global state of
    `selected_disease_item_id`.

    - If `selected_disease_item_id.value` is `None`, it displays the
        `DiseaseGalleryPageComponent`, showing a list of diseases.
    - If a disease ID is present in the state, it renders the
        `DiseaseDetailPageComponent` to show the details for that specific disease.

    The view automatically updates when the state changes, for example, when a
    user clicks on a disease in the gallery.

    Example:
        This component is typically used as a main route in a Solara application.
        The application's routing configuration would point a path (e.g., '/diseases')
        to this component.

        ```python
        # In your main application file (e.g., app.py)
        import solara
        from pages import diseases

        routes = [
            solara.Route(path="/", component=... # some other page),
            solara.Route(path="/diseases", component=diseases.Page),
        ]

        @solara.component
        def Layout():
            # ... your app layout ...
            solara.RoutingProvider(routes=routes, children=[...])

        # When a user navigates to '/diseases', this Page component will render.
        # User interactions within the DiseaseGalleryPageComponent will update
        # the `selected_disease_item_id` state, causing this component to
        # re-render and display the DiseaseDetailPageComponent.
        ```
    """
    use_locale_effect()

    if selected_disease_item_id.value is None:
        DiseaseGalleryPageComponent()

    else:
        DiseaseDetailPageComponent()

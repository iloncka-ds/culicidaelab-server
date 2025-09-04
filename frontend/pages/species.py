import solara
from frontend.components.species.species_detail import SpeciesDetailPageComponent
from frontend.components.species.species_gallery import SpeciesGalleryPageComponent

from frontend.state import selected_species_item_id, use_locale_effect


@solara.component
def Page():
    """
    Renders the interactive species prediction page, managing a multi-step workflow.

    This component serves as the main interface for the species prediction feature.
    It orchestrates a workflow where users first upload an image of a specimen,
    which triggers an asynchronous prediction. Simultaneously, the user can
    select the observation's location on an interactive map and fill out a form
    with additional details.

    The component is divided into two main views:
    1.  **'form' view**: The initial layout with three main sections for file
        upload, location selection, and the observation form.
    2.  **'results' view**: Displayed after a successful observation submission,
        showing a summary of the uploaded image and the prediction details.

    It manages all the necessary state for this process, including the uploaded
    file, prediction results, location coordinates, loading indicators, and
    success/error messages.

    Example:
        This component is intended to be a top-level page within a Solara
        application, typically linked from a main navigation or routing system.

        ```python
        # In your main app file (e.g., app.py)
        import solara
        from pages import prediction

        routes = [
            solara.Route(path="/", component=...),
            solara.Route(path="/predict", component=prediction.Page, label="Predict"),
            # ... other routes
        ]

        @solara.component
        def Layout():
            # ... your app layout ...
            # The RoutingProvider will render the prediction.Page component
            # when the user navigates to the '/predict' path.
            solara.RoutingProvider(routes=routes, children=[...])
        ```
    """
    use_locale_effect()

    if selected_species_item_id.value is None:
        SpeciesGalleryPageComponent()
    else:
        SpeciesDetailPageComponent()

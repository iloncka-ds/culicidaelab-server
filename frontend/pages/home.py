"""Defines the main home page for the application.

This module contains the `Home` component, which serves as the landing page.
It provides an introduction to the application's features and includes
navigational cards that link to the main sections of the site.
"""

from __future__ import annotations

import i18n
import solara
from solara.alias import rv

from frontend.config import card_content_style, card_style, heading_style, icon_style, sub_heading_style
from frontend.state import use_locale_effect


@solara.component
def Home():
    """
    Renders the home page of the application.

    This component serves as the main landing page, presenting an introduction
    to the application's features. It displays a welcome heading and a set of
    interactive cards. Each card represents a key section of the app:
    species prediction, data visualization on a map, a species database, and a
    disease information gallery.

    The cards are designed to be responsive and will adjust their layout based
    on the screen size. Clicking a button on any card navigates the user to the
    corresponding page using Solara's router. The text content is localized
    using the `i18n` library.

    Example:
        This component is typically used as the default route in a Solara
        application's routing setup.

        ```python
        # In your main app file or layout component
        import solara
        from pages import home

        routes = [
            solara.Route(path="/", component=home.Home, label="Home"),
            # ... other routes
        ]

        @solara.component
        def Layout():
            # ... your layout structure ...
            solara.RoutingProvider(routes=routes, children=[...])

        # When a user navigates to the root URL ('/'), the Home component
        # will be displayed.
        ```
    """
    use_locale_effect()
    router = solara.use_router()

    card_data = [
        {
            "title": i18n.t("home.cards.predict.title"),
            "icon": "mdi-camera-plus-outline",
            "description": i18n.t("home.cards.predict.description"),
            "link": "predict",
            "button_label": i18n.t("home.cards.predict.button"),
        },
        {
            "title": i18n.t("home.cards.visualize.title"),
            "icon": "mdi-map-marker-radius-outline",
            "description": i18n.t("home.cards.visualize.description"),
            "link": "map",
            "button_label": i18n.t("home.cards.visualize.button"),
        },
        {
            "title": i18n.t("home.cards.species.title"),
            "icon": "mdi-database-search-outline",
            "description": i18n.t("home.cards.species.description"),
            "link": "species",
            "button_label": i18n.t("home.cards.species.button"),
        },
        {
            "title": i18n.t("home.cards.diseases.title"),
            "icon": "mdi-virus-outline",
            "description": i18n.t("home.cards.diseases.description"),
            "link": "diseases",
            "button_label": i18n.t("home.cards.diseases.button"),
        },
    ]

    solara.Text(i18n.t("home.welcome"), style=heading_style)

    solara.Markdown(
        i18n.t("home.intro"),
        style=sub_heading_style,
    )

    with solara.ColumnsResponsive(
        small=12,
        medium=6,
        large=6,
        gutters=True,
        style="margin-bottom: 2rem;",
    ):
        for item in card_data:
            with solara.Column():
                with solara.Card(
                    title=item["title"],
                    elevation=4,
                    # hover=True,
                    style=card_style,
                    margin=2,
                ):
                    with solara.Column(style=card_content_style):
                        rv.Icon(name=item["icon"], size="4rem", color="primary", style_=icon_style)
                        solara.Markdown(item["description"], style="flex-grow: 1; margin-bottom: 1rem;")

                    with rv.CardActions(style_="justify-content: center; padding-bottom: 16px;"):
                        solara.Button(
                            label=item["button_label"],
                            on_click=lambda link=item["link"]: router.push(link),
                            color="primary",
                            outlined=True,
                            class_="px-4",
                        )

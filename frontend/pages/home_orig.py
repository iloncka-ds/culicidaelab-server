import solara
import solara.routing
from solara.alias import rv  # For potential direct Vuetify component use, though not strictly needed here

# Attempt to import config for styling, ensure paths are correct if used
from ..config import load_themes
from frontend.components.common.locale_selector import LocaleSelector
import i18n






@solara.component
def Page():
    theme = load_themes(solara.lab.theme)
    with solara.AppBar():
        solara.v.Spacer()
        LocaleSelector()

    with solara.AppBarTitle():
        solara.Text("CulicidaeLab", style="font-size: 2rem; font-weight: bold; color: white;")


    router = solara.use_router()
    # Page styles
    page_style = "padding: 2rem; max-width: 1200px; margin: auto;"
    heading_style = f"font-size: 2.5rem; font-weight: bold; text-align: center; margin-bottom: 1rem; color: {theme.themes.light.primary};"  # Using theme primary if COLOR_PRIMARY from config was "primary"
    sub_heading_style = "font-size: 1.2rem; text-align: center; margin-bottom: 3rem; color: #555;"
    card_style = "display: flex; flex-direction: column; height: 100%;"  # Ensure cards in a row have same height
    card_content_style = (
        "padding: 16px; flex-grow: 1; display: flex; flex-direction: column; align-items: center; text-align: center;"
    )
    icon_style = "margin-bottom: 1rem;"
    footer_style = "margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid #eee; text-align: center; font-size: 0.9em; color: #666;"

    card_data = [
        {
            "title": "Predict Mosquito Species",
            "icon": "mdi-camera-plus-outline",
            "description": "Upload an image of a mosquito and get an AI-powered species prediction. Contribute your findings by submitting observation data.",
            "link": "predict",
            "button_label": "Start Prediction",
        },
        {
            "title": "Visualize Mosquito Data",
            "icon": "mdi-map-marker-radius-outline",
            "description": "Explore interactive maps showing mosquito distribution, observation points, modeled probabilities, and breeding sites.",
            "link": "map",
            "button_label": "Explore Maps",
        },
        {
            "title": "Browse Species Database",
            "icon": "mdi-database-search-outline",
            "description": "Access detailed information about various mosquito species, including characteristics, vector status, and related diseases.",
            "link": "species",
            "button_label": "View Species",
        },
        {
            "title": "Explore Disease Information",
            "icon": "mdi-virus-outline",
            "description": "Learn about mosquito-borne diseases, their symptoms, prevention, and the mosquito species that transmit them.",
            "link": "diseases",
            "button_label": "Learn About Diseases",
        },
    ]

    with solara.Column(style=page_style):
        # Introduction Section
        solara.Text("Welcome to CulicidaeLab", style=heading_style)
        solara.Markdown(
            """
            CulicidaeLab is your comprehensive platform for mosquito research, surveillance, and data analysis.
            Our tools and resources are designed to empower researchers, public health officials, and enthusiasts
            in understanding and combating mosquito-borne diseases.
            """,
            style=sub_heading_style,
        )

        # Cards Section for Main Application Blocks
        with solara.ColumnsResponsive(
            small=12,  # 1 column on small screens (phones)
            medium=6,  # 2 columns on medium screens (tablets)
            large=6,  # 2 columns on large screens (desktops)

            gutters=True,  # Use default gutters
            style="margin-bottom: 2rem;",
        ):
            for item in card_data:
                with solara.Column():  # Each card is wrapped in a Column for ColumnsResponsive
                    with solara.Card(
                        title=item["title"],
                        # outlined=True,
                        elevation=4,
                        style=card_style,
                        margin=2,  # Add some margin around cards
                    ):
                        with solara.Column(style=card_content_style):
                            rv.Icon(name=item["icon"], size="4rem", color="primary", style_=icon_style)
                            solara.Markdown(item["description"], style="flex-grow: 1; margin-bottom: 1rem;")

                        with rv.CardActions(style_="justify-content: center; padding-bottom: 16px;"):
                            solara.Button(
                                label=item["button_label"],
                                on_click=lambda link=item["link"]: router.push(link),
                                color="primary",
                                outlined=True,  # A slightly different style for buttons
                                class_="px-4",  # Add some padding to button
                            )

        rv.Spacer(height="2rem")

        # Footer Section
        with solara.Div(style=footer_style):
            solara.Markdown(
                """
                **Disclaimer:** This platform is intended for educational and research purposes only.
                It is not a substitute for professional medical advice or public health directives.
                """
            )
            solara.Markdown(
                """
                ---
                CulicidaeLab development is supported by a grant from the
                [Innovation Assistance Foundation (Фонд содействия инновациям)](https://fasie.ru/).
                """
            )


# @solara.component
# def Layout(children):

#     route, routes = solara.use_route()
#     dark_effective = solara.lab.use_dark_effective()
#     return solara.AppLayout(children=children, toolbar_dark=dark_effective)


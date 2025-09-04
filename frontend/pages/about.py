"""Defines the informational 'About' page for the CulicidaeLab project.

This module contains the main page component that displays detailed information
about the CulicidaeLab ecosystem, including its architecture, data sources,
AI models, and software components. The content is presented using static
Markdown.
"""

import solara
import i18n

from frontend.config import page_style
from frontend.state import use_locale_effect, current_locale

from frontend.translations.about_en import MARKDOWN_CONTENT_EN
from frontend.translations.about_ru import MARKDOWN_CONTENT_RU


DIAGRAM_URL_RU = "https://i.ibb.co/jkbN0hKZ/Untitled-diagram-Mermaid-Chart-2025-09-04-191535.png"
DIAGRAM_URL_EN = "https://i.ibb.co/BH6T8yDG/Untitled-diagram-Mermaid-Chart-2025-09-04-185719.png"
# Note: The Mermaid diagram requires an internet connection to be rendered by the browser.
i18n.add_translation("info.content", MARKDOWN_CONTENT_EN, locale="en")
i18n.add_translation("info.content", MARKDOWN_CONTENT_RU, locale="ru")
i18n.add_translation("info.content.split", "## CulicidaeLab Ecosystem Architecture", locale="en")
i18n.add_translation("info.content.split", "## Архитектура экосистемы CulicidaeLab", locale="ru")


@solara.component
def Page():
    """
    Renders the main content for the 'About' page.

    This component displays a detailed overview of the CulicidaeLab project,
    including a Mermaid diagram illustrating the ecosystem architecture and
    lists of all related components like datasets, models, and applications.
    The content is static and rendered from a Markdown string.

    Example:
        This component is designed to be used as a page in a Solara application
        and is typically linked from a main route.

        ```python
        # In a routing setup file:
        import solara
        from . import about

        routes = [
            solara.Route(path="/about", component=about.Page),
        ]
        ```
    """
    use_locale_effect()

    # Determine which diagram to show based on the current locale
    diagram_src = DIAGRAM_URL_RU if current_locale.value == "ru" else DIAGRAM_URL_EN

    with solara.Column(style=page_style):
        # The Markdown content is split to insert the image correctly.
        # Split the translated text to get content before and after the diagram.
        content_parts = i18n.t("info.content").split(i18n.t("info.content.split"))

        # Render the first part of the markdown
        solara.Markdown(content_parts[0])

        # Render the heading, the diagram image, and the rest of the text
        if len(content_parts) > 1:
            solara.Markdown("## CulicidaeLab Ecosystem Architecture")
            solara.Image(diagram_src, width="100%")
            solara.Markdown(content_parts[1])

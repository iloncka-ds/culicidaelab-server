import solara as sl
from solara import lab as sl_lab


@sl.component
def Page():
    sl.Style(
        """
        body {
            max-width: 800px;
            margin: 30px auto 2em auto !important;
            padding-left: 2em;
            padding-right: 2em;
            /* not a very good solution, but at least not white)
            background-color: var(--jp-widgets-input-background-color)
        }
        /* for children of v-application, this works great */

        .theme--light .my-own-background {
            background-color: #fcc;
        }
        .theme--dark .my-own-background {
            background-color: #400;
        }
        """
    )

    sl_lab.ThemeToggle()
    sl.Markdown("# Hello, Solara!")
    with sl.Div(classes=[".my-own-background"]):
        sl.Markdown("# Hello, Solara, custom themed background!")

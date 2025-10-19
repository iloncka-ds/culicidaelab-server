import colorcet as cc
import solara
import os

COLOR_PRIMARY = "#009688"
COLOR_SECONDARY = "#B2DFDB"
COLOR_ACCENT = "#00796B"
COLOR_BACKGROUND = "#F8F9FA"
COLOR_TEXT = "#0D1B2A"
COLOR_BUTTON_PRIMARY_BG = "#005F73"
COLOR_BUTTON_WARNING = "#FF9500"

DISTRIBUTION_STATUS_COLORS = {
    "established": "rgba(227, 26, 28, 0.7)",
    "detected": "rgba(255, 127, 0, 0.7)",
    "absent": "rgba(173, 216, 230, 0.5)",
    "unknown": "rgba(200, 200, 200, 0.5)",
    "native_established": "rgba(51, 160, 44, 0.7)",
}


def load_themes(theme):
    """
    Directly apply theme definitions to solara.lab.theme.

    This function should be called at application startup to ensure consistent theming.
    """
    try:
        theme.themes.light.primary = "#009688"
        theme.themes.light.secondary = "#B2DFDB"
        theme.themes.light.accent = "#00796B"
        theme.themes.light.error = "#E74C3C"
        theme.themes.light.info = "#3498DB"
        theme.themes.light.success = "#1ABC9C"
        theme.themes.light.warning = "#F1C40F"

        theme.themes.dark.primary = "#009688"
        theme.themes.dark.secondary = "#B2DFDB"
        theme.themes.dark.accent = "#00796B"
        theme.themes.dark.error = "#E74C3C"
        theme.themes.dark.info = "#3498DB"
        theme.themes.dark.success = "#1ABC9C"

        theme.themes.dark.warning = "#F1C40F"

    except Exception as e:
        print(f"Error applying theme: {e}")
    return theme


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def generate_species_colors(species_list: list[str], alpha: float = 0.9) -> dict[str, str]:
    palette_name = "glasbey_bw"
    try:
        colors_hex = cc.palette[palette_name]

    except KeyError:
        colors_hex = [
            "#E6194B",
            "#3CB44B",
            "#FFE119",
            "#4363D8",
            "#F58231",
            "#911EB4",
            "#46F0F0",
            "#F032E6",
            "#BCF60C",
            "#FABEBE",
            "#008080",
            "#E6BEFF",
            "#9A6324",
            "#FFFAC8",
            "#800000",
            "#AAFFC3",
            "#808000",
            "#FFD8B1",
            "#000075",
            "#808080",
        ]

    num_colors = len(colors_hex)
    species_color_map = {}
    for i, species_name in enumerate(species_list):
        hex_color = colors_hex[i % num_colors]
        species_color_map[species_name] = _hex_to_rgba(hex_color, alpha)
    return species_color_map


DEFAULT_SPECIES_LIST_FOR_COLORS = [
    "Aedes aegypti",
    "Aedes albopictus",
    "Aedes canadensis",
    "Aedes dorsalis",
    "Aedes geniculatus",
    "Aedes koreicus",
    "Aedes triseriatus",
    "Aedes vexans",
    "Anopheles arabiensis",
    "Anopheles freeborni",
    "Anopheles sinensis",
    "Culex inatomii",
    "Culex pipiens",
    "Culex quinquefasciatus",
    "Culex tritaeniorhynchus",
    "Culiseta annulata",
    "Culiseta longiareolata",
]
theme = load_themes(solara.lab.theme)
SPECIES_COLORS = generate_species_colors(DEFAULT_SPECIES_LIST_FOR_COLORS)

DEFAULT_MAP_CENTER = (40.416775, -3.703790)
DEFAULT_MAP_ZOOM = 5

# Backend URL configuration - uses environment variable with fallback
CLIENT_BACKEND_URL = os.getenv("CLIENT_BACKEND_URL", "http://127.0.0.1:8000")  # For client-side (browser) requests
SERVER_BACKEND_URL = os.getenv("SERVER_BACKEND_URL", CLIENT_BACKEND_URL)  # For server-side requests
API_BASE_URL = f"{CLIENT_BACKEND_URL}/api"  # Client-side API base
SERVER_API_BASE_URL = f"{SERVER_BACKEND_URL}/api"  # Server-side API base

# Static files URL - for Docker setup, use nginx proxy; for local dev, use backend directly
STATIC_FILES_URL = os.getenv("STATIC_FILES_URL", CLIENT_BACKEND_URL)

# Backward compatibility
BACKEND_URL = CLIENT_BACKEND_URL
OBSERVATIONS_ENDPOINT = f"{API_BASE_URL}/geo/observations"
SPECIES_INFO_ENDPOINT = f"{API_BASE_URL}/species_info"
DISEASE_LIST_ENDPOINT = f"{SERVER_API_BASE_URL}/diseases"  # Server-side endpoint
DISEASE_DETAIL_ENDPOINT_TEMPLATE = f"{SERVER_API_BASE_URL}/diseases/{{disease_id}}"  # Server-side endpoint
DISEASE_VECTORS_ENDPOINT_TEMPLATE = f"{SERVER_API_BASE_URL}/diseases/{{disease_id}}/vectors"  # Server-side endpoint
BREEDING_SITES_ENDPOINT = f"{API_BASE_URL}/geo/breeding_sites"
FILTER_OPTIONS_ENDPOINT = f"{SERVER_API_BASE_URL}/filter_options"  # Server-side endpoint
SPECIES_LIST_ENDPOINT = f"{SERVER_API_BASE_URL}/species"  # Server-side endpoint
SPECIES_DETAIL_ENDPOINT_TEMPLATE = f"{SERVER_API_BASE_URL}/species/{{species_id}}"  # Server-side endpoint

FONT_HEADINGS = "Montserrat, sans-serif"
FONT_BODY = "Open Sans, sans-serif"
COLOR_PRIMARY = "primary"
COLOR_TEXT = "black"
COLOR_SECONDARY = "#1976D2"
COLOR_SUCCESS = "#4CAF50"
COLOR_WARNING = "#FF9800"
COLOR_ERROR = "#F44336"

PREDICTION_ENDPOINT = f"{API_BASE_URL}/predict_species/"
STORE_OBSERVATIONS_ENDPOINT = f"{API_BASE_URL}/observations/"

page_style = {
    "align": "center",
    "padding": "2rem",
    "max-width": "1200px",
    "margin": "auto",
}
heading_style = {
    "font-size": "2.5rem",
    "font-weight": "bold",
    "text-align": "center",
    "margin-bottom": "1rem",
    "color": "#009688",
}
sub_heading_style = {
    "font-size": "1.2rem",
    "text-align": "center",
    "margin-bottom": "3rem",
    "color": "#555",
    "min-height": "3.4em",
    "max-height": "3.4em",
}
card_style = {"display": "flex", "flex-direction": "column", "height": "100%"}
card_content_style = {
    "padding": "16px",
    "flex-grow": "1",
    "display": "flex",
    "flex-direction": "column",
    "align-items": "center",
    "text-align": "center",
}
icon_style = "margin-bottom:1rem"
footer_style = {
    "margin-top": "3rem",
    "padding-top": "1.5rem",
    "border-top": "1px solid #eee",
    "text-align": "center",
    "font-size": "0.9em",
    "color": "#0D1B2A",
}
active_btn_style = {
    "box-shadow": "none",
    "border-radius": "0px",
    "background-color": f"{theme.themes.light.accent}",
    "color": "white",
}
inactive_btn_style = {
    "box-shadow": "none",
    "border-radius": "0px",
    "background-color": f"{theme.themes.light.primary}",
    "color": "white",
}
row_style = {
    "background-color": f"{theme.themes.light.primary}",
    "color": f"{theme.themes.light.primary}",
    "foreground-color": f"{theme.themes.light.primary}",
    "margin-left": "16px",
    "margin-right": "16px",
    "gap": "0px",
}
gallery_search_div_style = {
    "border-radius": "6px",
    "background-color": "white",
    "position": "sticky",
    "top": "0px",
    "z-index": "10",
    "margin-bottom": "10px",
}

import colorcet as cc
from typing import List, Dict

COLOR_PRIMARY = "#21908C"
COLOR_SECONDARY = "#ADDC30"
COLOR_ACCENT = "#DBF3AD"
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


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def generate_species_colors(species_list: List[str], alpha: float = 0.9) -> Dict[str, str]:
    palette_name = "glasbey_bw"  # A good categorical palette from colorcet
    try:
        # colorcet.palette contains lists of hex color strings
        colors_hex = cc.palette[palette_name]

    except KeyError:
        # Absolute fallback (simple distinct colors)
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
        hex_color = colors_hex[i % num_colors]  # Cycle through colors if more species than palette colors
        species_color_map[species_name] = _hex_to_rgba(hex_color, alpha)
    return species_color_map


DEFAULT_SPECIES_LIST_FOR_COLORS = [
    "Aedes albopictus",
    "Aedes aegypti",
    "Culex pipiens",
    "Anopheles gambiae",
    "Culiseta annulata",
]
SPECIES_COLORS = generate_species_colors(DEFAULT_SPECIES_LIST_FOR_COLORS)

DEFAULT_MAP_CENTER = (40.416775, -3.703790)
DEFAULT_MAP_ZOOM = 5

API_BASE_URL = "http://localhost:8000/api"
SPECIES_DISTRIBUTION_ENDPOINT = f"{API_BASE_URL}/geo/distribution"
OBSERVATIONS_ENDPOINT = f"{API_BASE_URL}/geo/observations"
MODELED_PROBABILITY_ENDPOINT = f"{API_BASE_URL}/geo/modeled_probability"
SPECIES_INFO_ENDPOINT = f"{API_BASE_URL}/species_info"

FONT_HEADINGS = "Montserrat, sans-serif"
FONT_BODY = "Open Sans, sans-serif"

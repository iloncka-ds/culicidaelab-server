"""Provides a utility function for determining species status colors.

This module contains the `get_status_color` function, which maps a species'
vector status string (e.g., 'high', 'low') to a corresponding color pair for
consistent styling in the UI.
"""


def get_status_color(status_detail: str) -> tuple[str, str]:
    """Maps a species' vector status string to a corresponding color pair.

    This utility function provides a consistent color scheme for displaying
    the vector status of a species in the user interface. It returns a tuple
    containing a background color and a text color suitable for UI elements
    like chips or badges.

    Args:
        status_detail: A string representing the vector status. Expected
            values are 'high', 'moderate', 'low', or 'unknown'. The function
            is case-sensitive.

    Returns:
        A tuple containing two strings: the first is the background color name,
        and the second is the text color name. A default color pair is
        returned for unrecognized or empty status strings.

    Example:
        ```python
        high_status_bg, high_status_text = get_status_color("high")
        print(f"High status: Background='{high_status_bg}', Text='{high_status_text}'")
        # Expected output: High status: Background='red', Text='white'

        unknown_status_bg, unknown_status_text = get_status_color("unknown")
        print(f"Unknown status: Background='{unknown_status_bg}', Text='{unknown_status_text}'")
        # Expected output: Unknown status: Background='grey', Text='black'

        default_bg, default_text = get_status_color("some_other_value")
        print(f"Default status: Background='{default_bg}', Text='{default_text}'")
        # Expected output: Default status: Background='blue-grey', Text='white'
        ```
    """

    if not status_detail:
        return ("blue-grey", "white")

    status_color_detail, text_color_detail = "blue-grey", "white"
    if status_detail == "high":
        status_color_detail = "red"
    elif status_detail == "moderate":
        status_color_detail = "orange"
    elif status_detail == "low":
        status_color_detail = "green"
    elif status_detail == "unknown":
        status_color_detail, text_color_detail = "grey", "black"

    return (status_color_detail, text_color_detail)

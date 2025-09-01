def get_status_color(status_detail: str) -> tuple[str, str]:
    """Get the color for a species status detail.
    Args:
        status_detail (str): The status detail to get the color for.
    Returns:
        Tuple[str, str]: A tuple of the color and text color.
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

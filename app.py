# import solara
# import solara.lab
# from solara.lab import theme as theme


# def change_color(colors):
#     if "purple" in colors:
#         theme.themes.light.info = theme.themes.dark.info = "#8617c2"
#     else:
#         theme.themes.light.info = theme.themes.dark.info = "#2196f3"

#     if "green" in colors:
#         theme.themes.light.error = theme.themes.dark.error = "#33bd65"
#     else:
#         theme.themes.light.error = theme.themes.dark.error = "#ff5252"

import solara
from solara.lab import theme as theme
def load_themes():
    """
    Directly apply theme definitions to solara.lab.theme.

    This function should be called at application startup to ensure consistent theming.
    """
    try:
        # Apply themes directly using attribute access - LIGHT THEME
        theme.themes.light.primary = "#22c55e"  # Primary green color
        theme.themes.light.secondary = "#2ECC71"  # Secondary green shade
        theme.themes.light.accent = "#F39C12"  # Accent color (amber/orange)
        theme.themes.light.error = "#E74C3C"  # Error color (red)
        theme.themes.light.info = "#3498DB"  # Info color (blue)
        theme.themes.light.success = "#1ABC9C"  # Success color (teal)
        theme.themes.light.warning = "#F1C40F"  # Warning color (yellow)

        # Apply themes directly using attribute access - DARK THEME
        theme.themes.dark.primary = "#4ade80"  # Primary color for dark theme (lighter green)
        theme.themes.dark.secondary = "#03DAC6"  # Secondary color for dark theme (teal)
        theme.themes.dark.accent = "#F39C12"  # Accent color for dark theme (amber/orange)
        theme.themes.dark.error = "#FF5252"  # Error color for dark theme (red)
        theme.themes.dark.info = "#2196F3"  # Info color for dark theme (blue)
        theme.themes.dark.success = "#4CAF50"  # Success color for dark theme (green)
        theme.themes.dark.warning = "#FFC107"  # Warning color for dark theme (amber)

        print("Theme applied successfully")
        return True
    except Exception as e:
        print(f"Error applying theme: {e}")
        return False
load_themes()
clicks = solara.reactive(0)


@solara.component
def Page():
    color = "#22c55e"
    if clicks.value >= 5:
        color = "accent"
    if clicks.value==3:
        theme.themes.light.info = "#2ECC71"
        # solara.Info("clicks", clicks)
    def increment():
        clicks.value += 1
        print("clicks", clicks)

    solara.Button(label=f"Clicked: {clicks}", on_click=increment, color=color)
    solara.Info("app colors")

# @solara.component
# def Page():
#     solara.Info("Info message")
#     solara.Error("Error message")

#     with solara.ToggleButtonsMultiple(on_value=change_color):
#         solara.Button("Change Info", value="purple")
#         solara.Button("Change Error", value="green")

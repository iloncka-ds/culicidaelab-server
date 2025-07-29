import solara

from frontend.components.diseases.disease_gallery import DiseaseGalleryPageComponent
from frontend.components.diseases.disease_detail import DiseaseDetailPageComponent
from frontend.config import theme
from ..state import selected_disease_item_id, use_locale_effect
from ..config import (
    load_themes,
    page_style,
    heading_style,
    sub_heading_style,
    card_style,
    card_content_style,
    icon_style,
    footer_style,
)
from frontend.components.common.locale_selector import LocaleSelector
import i18n
from pathlib import Path

# def setup_i18n():
#     i18n.load_path.append(str(Path(__file__).parent.parent / "translations"))
#     i18n.set("fallback", "ru")



@solara.component
def Page():
    # theme = load_themes(solara.lab.theme)

    use_locale_effect()
    # heading_style = f"font-size: 2.5rem; font-weight: bold; text-align: center; margin-bottom: 1rem; color: {theme.themes.light.primary};"

    # rerender_trigger, set_rerender_trigger = solara.use_state(0)

    # def force_rerender():
    #     set_rerender_trigger(lambda x: x + 1)


    # setup_i18n()

    # with solara.AppBar():
    #     solara.v.Spacer()
    #     LocaleSelector() # on_change=force_rerender

    # with solara.AppBarTitle():
    #     solara.Text("CulicidaeLab", style="font-size: 2rem; font-weight: bold; color: white;")
    if selected_disease_item_id.value is None:
        DiseaseGalleryPageComponent()

    else:
        DiseaseDetailPageComponent()

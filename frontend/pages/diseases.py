import solara

from frontend.components.diseases.disease_gallery import DiseaseGalleryPageComponent
from frontend.components.diseases.disease_detail import DiseaseDetailPageComponent

from ..state import selected_disease_item_id
from frontend.components.common.locale_selector import LocaleSelector
import i18n
from pathlib import Path

# def setup_i18n():
#     i18n.load_path.append(str(Path(__file__).parent.parent / "translations"))
#     i18n.set("fallback", "en")

@solara.component
def I18nSetup():
    def setup():
        # Avoid adding the path multiple times
        translation_path = str(Path(__file__).parent.parent / "translations")
        if translation_path not in i18n.load_path:
            i18n.load_path.append(translation_path)
        i18n.set("fallback", "en")

    solara.use_memo(setup, [])


@solara.component
def Page():
    rerender_trigger, set_rerender_trigger = solara.use_state(0)

    def force_rerender():
        set_rerender_trigger(lambda x: x + 1)

    # setup_i18n()
    I18nSetup()
    with solara.AppBar():
        solara.v.Spacer()
        LocaleSelector(on_change=force_rerender)

    with solara.AppBarTitle():
        solara.Text("CulicidaeLab", style="font-size: 2rem; font-weight: bold; color: white;")
    if selected_disease_item_id.value is None:
        DiseaseGalleryPageComponent(rerender_trigger)
    else:
        DiseaseDetailPageComponent(rerender_trigger)

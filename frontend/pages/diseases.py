import solara

from frontend.components.diseases.disease_gallery import DiseaseGalleryPageComponent
from frontend.components.diseases.disease_detail import DiseaseDetailPageComponent

from ..state import selected_disease_item_id
from frontend.components.common.locale_selector import LocaleSelector
import i18n


@solara.component
def Page():
    with solara.AppBar():
        solara.v.Spacer()
        LocaleSelector()

    with solara.AppBarTitle():
        solara.Text("CulicidaeLab", style="font-size: 2rem; font-weight: bold; color: white;")
    if selected_disease_item_id.value is None:
        DiseaseGalleryPageComponent()
    else:
        DiseaseDetailPageComponent()

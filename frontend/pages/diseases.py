import solara

from frontend.components.diseases.disease_gallery import DiseaseGalleryPageComponent
from frontend.components.diseases.disease_detail import DiseaseDetailPageComponent

from frontend.state import selected_disease_item_id, use_locale_effect


@solara.component
def Page():
    use_locale_effect()

    if selected_disease_item_id.value is None:
        DiseaseGalleryPageComponent()

    else:
        DiseaseDetailPageComponent()

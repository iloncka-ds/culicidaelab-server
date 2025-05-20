import solara

from frontend.components.diseases.disease_gallery import DiseaseGalleryPageComponent
from frontend.components.diseases.disease_detail import DiseaseDetailPageComponent

from ..state import selected_disease_item_id



@solara.component
def Page():
    if selected_disease_item_id.value is None:
        DiseaseGalleryPageComponent()
    else:
        DiseaseDetailPageComponent()

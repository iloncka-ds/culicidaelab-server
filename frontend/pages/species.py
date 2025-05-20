import solara

from frontend.components.species.species_gallery import SpeciesGalleryPageComponent
from frontend.components.species.species_detail import SpeciesDetailPageComponent

from ..state import selected_species_item_id


@solara.component
def Page():
    if selected_species_item_id.value is None:
        SpeciesGalleryPageComponent()
    else:
        SpeciesDetailPageComponent()

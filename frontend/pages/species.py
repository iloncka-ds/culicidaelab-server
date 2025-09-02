import solara
from frontend.components.species.species_detail import SpeciesDetailPageComponent
from frontend.components.species.species_gallery import SpeciesGalleryPageComponent

from frontend.state import selected_species_item_id, use_locale_effect


@solara.component
def Page():
    use_locale_effect()

    if selected_species_item_id.value is None:
        SpeciesGalleryPageComponent()
    else:
        SpeciesDetailPageComponent()

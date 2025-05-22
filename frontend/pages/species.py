import solara

from frontend.components.species.species_gallery import SpeciesGalleryPageComponent
from frontend.components.species.species_detail import SpeciesDetailPageComponent

from ..state import selected_species_item_id
from frontend.components.common.locale_selector import LocaleSelector
import i18n

@solara.component
def Page():
    with solara.AppBar():
        solara.v.Spacer()
        LocaleSelector()
    with solara.AppBarTitle():
        solara.Text("CulicidaeLab", style="font-size: 2rem; font-weight: bold; color: white;")
    if selected_species_item_id.value is None:
        SpeciesGalleryPageComponent()
    else:
        SpeciesDetailPageComponent()

import solara
from frontend.components.species.species_detail import SpeciesDetailPageComponent
from frontend.components.species.species_gallery import SpeciesGalleryPageComponent

from ..state import selected_species_item_id, use_locale_effect


# def setup_i18n():
#     i18n.load_path.append(str(Path(__file__).parent.parent / "translations"))
#     i18n.set("fallback", "ru")


@solara.component
def Page():
    # _, set_rerender_trigger = solara.use_state(0)

    # def force_rerender():
    #     set_rerender_trigger(lambda x: x + 1)

    # setup_i18n()
    use_locale_effect()
    # with solara.AppBar():
    #     solara.v.Spacer()
    #     LocaleSelector() # on_change=force_rerender
    # with solara.AppBarTitle():
    #     solara.Text("CulicidaeLab", style="font-size: 2rem; font-weight: bold; color: white;")
    if selected_species_item_id.value is None:
        SpeciesGalleryPageComponent()
    else:
        SpeciesDetailPageComponent()

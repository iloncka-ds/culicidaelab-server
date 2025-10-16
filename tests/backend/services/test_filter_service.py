"""
Tests for the filter service.
"""

import pytest

from backend.schemas.filter_schemas import FilterOptions, RegionFilter, DataSourceFilter
from backend.services.filter_service import get_filter_options
from tests.factories.mock_factory import MockFactory


class TestFilterService:
    """Test cases for the filter service."""

    @pytest.fixture
    def sample_species_names(self):
        """Create sample species names list."""
        return [
            "Aedes aegypti",
            "Culex pipiens", 
            "Anopheles gambiae",
            "Aedes albopictus",
            "Culex quinquefasciatus"
        ]

    @pytest.fixture
    def sample_region_translations(self):
        """Create sample region translations dictionary."""
        return {
            "en": {
                "north_america": "North America",
                "south_america": "South America", 
                "europe": "Europe",
                "africa": "Africa",
                "asia": "Asia",
                "oceania": "Oceania"
            },
            "ru": {
                "north_america": "Северная Америка",
                "south_america": "Южная Америка",
                "europe": "Европа", 
                "africa": "Африка",
                "asia": "Азия",
                "oceania": "Океания"
            },
            "es": {
                "north_america": "América del Norte",
                "south_america": "América del Sur",
                "europe": "Europa",
                "africa": "África", 
                "asia": "Asia",
                "oceania": "Oceanía"
            }
        }

    @pytest.fixture
    def sample_data_source_translations(self):
        """Create sample data source translations dictionary."""
        return {
            "en": {
                "gbif": "Global Biodiversity Information Facility",
                "citizen_science": "Citizen Science",
                "who": "World Health Organization",
                "cdc": "Centers for Disease Control",
                "ecdc": "European Centre for Disease Prevention"
            },
            "ru": {
                "gbif": "Глобальный информационный фонд по биоразнообразию",
                "citizen_science": "Гражданская наука",
                "who": "Всемирная организация здравоохранения",
                "cdc": "Центры по контролю заболеваний",
                "ecdc": "Европейский центр профилактики заболеваний"
            },
            "es": {
                "gbif": "Facilidad Global de Información sobre Biodiversidad",
                "citizen_science": "Ciencia Ciudadana",
                "who": "Organización Mundial de la Salud",
                "cdc": "Centros para el Control de Enfermedades",
                "ecdc": "Centro Europeo para la Prevención de Enfermedades"
            }
        }

    def test_get_filter_options_english(self, sample_species_names, sample_region_translations, sample_data_source_translations):
        """Test filter options generation for English language."""
        result = get_filter_options(
            lang="en",
            species_names=sample_species_names,
            region_translations=sample_region_translations,
            data_source_translations=sample_data_source_translations
        )

        assert isinstance(result, FilterOptions)
        
        # Test species (should be passed through as-is)
        assert result.species == sample_species_names
        assert len(result.species) == 5
        assert "Aedes aegypti" in result.species
        assert "Culex pipiens" in result.species

        # Test regions (should be sorted alphabetically by name)
        assert len(result.regions) == 6
        assert all(isinstance(region, RegionFilter) for region in result.regions)
        
        # Check that regions are sorted alphabetically by name
        region_names = [region.name for region in result.regions]
        assert region_names == sorted(region_names)
        
        # Check specific region mappings
        africa_region = next(r for r in result.regions if r.id == "africa")
        assert africa_region.name == "Africa"
        
        north_america_region = next(r for r in result.regions if r.id == "north_america")
        assert north_america_region.name == "North America"

        # Test data sources (should be sorted alphabetically by name)
        assert len(result.data_sources) == 5
        assert all(isinstance(source, DataSourceFilter) for source in result.data_sources)
        
        # Check that data sources are sorted alphabetically by name
        source_names = [source.name for source in result.data_sources]
        assert source_names == sorted(source_names)
        
        # Check specific data source mappings
        gbif_source = next(s for s in result.data_sources if s.id == "gbif")
        assert gbif_source.name == "Global Biodiversity Information Facility"
        
        who_source = next(s for s in result.data_sources if s.id == "who")
        assert who_source.name == "World Health Organization"

    def test_get_filter_options_russian(self, sample_species_names, sample_region_translations, sample_data_source_translations):
        """Test filter options generation for Russian language."""
        result = get_filter_options(
            lang="ru",
            species_names=sample_species_names,
            region_translations=sample_region_translations,
            data_source_translations=sample_data_source_translations
        )

        assert isinstance(result, FilterOptions)
        
        # Species should be the same regardless of language
        assert result.species == sample_species_names

        # Check Russian region translations
        assert len(result.regions) == 6
        europe_region = next(r for r in result.regions if r.id == "europe")
        assert europe_region.name == "Европа"
        
        asia_region = next(r for r in result.regions if r.id == "asia")
        assert asia_region.name == "Азия"

        # Check Russian data source translations
        assert len(result.data_sources) == 5
        who_source = next(s for s in result.data_sources if s.id == "who")
        assert who_source.name == "Всемирная организация здравоохранения"
        
        citizen_science_source = next(s for s in result.data_sources if s.id == "citizen_science")
        assert citizen_science_source.name == "Гражданская наука"

    def test_get_filter_options_spanish(self, sample_species_names, sample_region_translations, sample_data_source_translations):
        """Test filter options generation for Spanish language."""
        result = get_filter_options(
            lang="es",
            species_names=sample_species_names,
            region_translations=sample_region_translations,
            data_source_translations=sample_data_source_translations
        )

        assert isinstance(result, FilterOptions)
        
        # Check Spanish region translations
        south_america_region = next(r for r in result.regions if r.id == "south_america")
        assert south_america_region.name == "América del Sur"
        
        oceania_region = next(r for r in result.regions if r.id == "oceania")
        assert oceania_region.name == "Oceanía"

        # Check Spanish data source translations
        gbif_source = next(s for s in result.data_sources if s.id == "gbif")
        assert gbif_source.name == "Facilidad Global de Información sobre Biodiversidad"

    def test_get_filter_options_unsupported_language(self, sample_species_names, sample_region_translations, sample_data_source_translations):
        """Test filter options generation for unsupported language."""
        result = get_filter_options(
            lang="fr",  # French not in sample translations
            species_names=sample_species_names,
            region_translations=sample_region_translations,
            data_source_translations=sample_data_source_translations
        )

        assert isinstance(result, FilterOptions)
        
        # Species should still be returned
        assert result.species == sample_species_names
        
        # Regions and data sources should be empty for unsupported language
        assert result.regions == []
        assert result.data_sources == []

    def test_get_filter_options_empty_species_list(self, sample_region_translations, sample_data_source_translations):
        """Test filter options generation with empty species list."""
        result = get_filter_options(
            lang="en",
            species_names=[],
            region_translations=sample_region_translations,
            data_source_translations=sample_data_source_translations
        )

        assert isinstance(result, FilterOptions)
        assert result.species == []
        assert len(result.regions) == 6  # Regions should still be populated
        assert len(result.data_sources) == 5  # Data sources should still be populated

    def test_get_filter_options_empty_translations(self, sample_species_names):
        """Test filter options generation with empty translation dictionaries."""
        result = get_filter_options(
            lang="en",
            species_names=sample_species_names,
            region_translations={},
            data_source_translations={}
        )

        assert isinstance(result, FilterOptions)
        assert result.species == sample_species_names
        assert result.regions == []
        assert result.data_sources == []

    def test_get_filter_options_partial_translations(self, sample_species_names):
        """Test filter options generation with partial translation data."""
        partial_region_translations = {
            "en": {
                "north_america": "North America",
                "europe": "Europe"
            }
        }
        
        partial_data_source_translations = {
            "en": {
                "gbif": "GBIF",
                "who": "WHO"
            }
        }

        result = get_filter_options(
            lang="en",
            species_names=sample_species_names,
            region_translations=partial_region_translations,
            data_source_translations=partial_data_source_translations
        )

        assert isinstance(result, FilterOptions)
        assert result.species == sample_species_names
        assert len(result.regions) == 2
        assert len(result.data_sources) == 2

    def test_get_filter_options_sorting_behavior(self):
        """Test that regions and data sources are sorted alphabetically by name."""
        # Create data that would not be alphabetically sorted by ID
        region_translations = {
            "en": {
                "z_region": "Alpha Region",
                "a_region": "Zulu Region", 
                "m_region": "Beta Region"
            }
        }
        
        data_source_translations = {
            "en": {
                "z_source": "Alpha Source",
                "a_source": "Zulu Source",
                "m_source": "Beta Source"
            }
        }

        result = get_filter_options(
            lang="en",
            species_names=["Species A", "Species B"],
            region_translations=region_translations,
            data_source_translations=data_source_translations
        )

        # Check that regions are sorted by name, not ID
        region_names = [region.name for region in result.regions]
        assert region_names == ["Alpha Region", "Beta Region", "Zulu Region"]
        
        # Check that data sources are sorted by name, not ID
        source_names = [source.name for source in result.data_sources]
        assert source_names == ["Alpha Source", "Beta Source", "Zulu Source"]

    def test_get_filter_options_with_mock_factory_data(self):
        """Test filter options generation using MockFactory data."""
        # Use MockFactory to create realistic test data
        mock_filter_options = MockFactory.create_filter_options_data()
        
        # Extract data from mock for testing the service function
        species_names = mock_filter_options.species
        
        # Create translations based on mock data
        region_translations = {
            "en": {region.id: region.name for region in mock_filter_options.regions}
        }
        
        data_source_translations = {
            "en": {source.id: source.name for source in mock_filter_options.data_sources}
        }

        result = get_filter_options(
            lang="en",
            species_names=species_names,
            region_translations=region_translations,
            data_source_translations=data_source_translations
        )

        assert isinstance(result, FilterOptions)
        assert len(result.species) == len(species_names)
        assert len(result.regions) == len(mock_filter_options.regions)
        assert len(result.data_sources) == len(mock_filter_options.data_sources)

    def test_get_filter_options_region_filter_structure(self, sample_region_translations):
        """Test that RegionFilter objects have correct structure."""
        result = get_filter_options(
            lang="en",
            species_names=[],
            region_translations=sample_region_translations,
            data_source_translations={}
        )

        for region in result.regions:
            assert isinstance(region, RegionFilter)
            assert hasattr(region, 'id')
            assert hasattr(region, 'name')
            assert isinstance(region.id, str)
            assert isinstance(region.name, str)
            assert len(region.id) > 0
            assert len(region.name) > 0

    def test_get_filter_options_data_source_filter_structure(self, sample_data_source_translations):
        """Test that DataSourceFilter objects have correct structure."""
        result = get_filter_options(
            lang="en",
            species_names=[],
            region_translations={},
            data_source_translations=sample_data_source_translations
        )

        for source in result.data_sources:
            assert isinstance(source, DataSourceFilter)
            assert hasattr(source, 'id')
            assert hasattr(source, 'name')
            assert isinstance(source.id, str)
            assert isinstance(source.name, str)
            assert len(source.id) > 0
            assert len(source.name) > 0

    def test_get_filter_options_case_sensitivity(self):
        """Test filter options with case-sensitive language codes."""
        region_translations = {
            "EN": {"region1": "Region 1"},  # Uppercase language code
            "en": {"region2": "Region 2"}   # Lowercase language code
        }
        
        data_source_translations = {
            "EN": {"source1": "Source 1"},
            "en": {"source2": "Source 2"}
        }

        # Test with lowercase 'en'
        result_lower = get_filter_options(
            lang="en",
            species_names=[],
            region_translations=region_translations,
            data_source_translations=data_source_translations
        )

        # Should only get lowercase 'en' translations
        assert len(result_lower.regions) == 1
        assert result_lower.regions[0].name == "Region 2"
        assert len(result_lower.data_sources) == 1
        assert result_lower.data_sources[0].name == "Source 2"

        # Test with uppercase 'EN'
        result_upper = get_filter_options(
            lang="EN",
            species_names=[],
            region_translations=region_translations,
            data_source_translations=data_source_translations
        )

        # Should only get uppercase 'EN' translations
        assert len(result_upper.regions) == 1
        assert result_upper.regions[0].name == "Region 1"
        assert len(result_upper.data_sources) == 1
        assert result_upper.data_sources[0].name == "Source 1"

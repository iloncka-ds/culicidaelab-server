# Datasets

This document provides comprehensive information about the datasets used in the CulicidaeLab Server platform, including sample data, training datasets, and data collection methodologies.

## Overview

CulicidaeLab utilizes multiple datasets to support mosquito species identification, disease mapping, and ecological research. The platform combines curated sample data with real-world observations to provide comprehensive mosquito surveillance capabilities.

## Sample Datasets

### Species Dataset

The species dataset contains comprehensive information about mosquito species worldwide, with multilingual support and detailed taxonomic information.

**Dataset Structure:**
- **Records**: 17 mosquito species across 4 genera
- **Languages**: English and Russian localization
- **Fields**: 16 attributes per species including taxonomy, ecology, and disease relationships

**Key Species Included:**

#### Aedes Genus (8 species)
- *Aedes aegypti* - Yellow Fever Mosquito
- *Aedes albopictus* - Asian Tiger Mosquito  
- *Aedes canadensis* - Canada Mosquito
- *Aedes dorsalis* - Coastal Rock Pool Mosquito
- *Aedes geniculatus* - Treehole Mosquito
- *Aedes koreicus* - Korean Bush Mosquito
- *Aedes triseriatus* - Eastern Treehole Mosquito
- *Aedes vexans* - Inland Floodwater Mosquito

#### Anopheles Genus (3 species)
- *Anopheles arabiensis* - Arabian Malaria Mosquito
- *Anopheles freeborni* - Western Malaria Mosquito
- *Anopheles sinensis* - Chinese Malaria Mosquito

#### Culex Genus (4 species)
- *Culex inatomii*
- *Culex pipiens* - Common House Mosquito
- *Culex quinquefasciatus* - Southern House Mosquito
- *Culex tritaeniorhynchus* - Japanese Encephalitis Mosquito

#### Culiseta Genus (2 species)
- *Culiseta annulata* - Ringed Mosquito
- *Culiseta longiareolata* - Striped Mosquito

**Data Attributes:**

```json
{
  "id": "species_identifier",
  "scientific_name": "Genus species",
  "vector_status": "High|Moderate|Low",
  "image_url": "path/to/species/image",
  "common_name_en": "English common name",
  "common_name_ru": "Russian common name",
  "description_en": "English description",
  "description_ru": "Russian description",
  "key_characteristics_en": ["characteristic1", "characteristic2"],
  "key_characteristics_ru": ["характеристика1", "характеристика2"],
  "habitat_preferences_en": ["habitat1", "habitat2"],
  "habitat_preferences_ru": ["среда1", "среда2"],
  "geographic_regions": ["region1", "region2"],
  "related_diseases": ["disease_id1", "disease_id2"]
}
```

### Disease Dataset

The disease dataset contains information about mosquito-borne diseases with comprehensive medical and epidemiological data.

**Dataset Structure:**
- **Records**: 13 major mosquito-borne diseases
- **Languages**: English and Russian medical terminology
- **Coverage**: Global disease distribution and vector relationships

**Diseases Included:**

#### Viral Diseases
- **Dengue Fever** - Transmitted by *Aedes aegypti*, *Aedes albopictus*
- **Zika Virus** - Transmitted by *Aedes aegypti*, *Aedes albopictus*
- **Chikungunya** - Transmitted by *Aedes aegypti*, *Aedes albopictus*
- **Yellow Fever** - Transmitted by *Aedes aegypti*
- **West Nile Virus** - Transmitted by *Culex pipiens*, *Culex quinquefasciatus*
- **Japanese Encephalitis** - Transmitted by *Culex tritaeniorhynchus*
- **Eastern Equine Encephalitis** - Transmitted by *Aedes canadensis*
- **St. Louis Encephalitis** - Transmitted by *Culex pipiens*, *Culex quinquefasciatus*
- **La Crosse Encephalitis** - Transmitted by *Aedes triseriatus*
- **Rift Valley Fever** - Transmitted by multiple Culex and Aedes species

#### Parasitic Diseases
- **Malaria** - Transmitted by *Anopheles* species
- **Filariasis** - Transmitted by *Culex quinquefasciatus*, *Aedes aegypti*
- **Avian Malaria** - Transmitted by *Culex* species

**Medical Information Fields:**
- Symptoms and clinical presentation
- Treatment protocols and medications
- Prevention strategies
- Epidemiological data and prevalence
- Geographic distribution
- Vector species relationships

### Observation Dataset

The observation dataset contains field observation records with geospatial information and metadata.

**Dataset Format**: GeoJSON Feature Collection
**Coordinate System**: WGS84 (EPSG:4326)
**Temporal Coverage**: Configurable date ranges

**GeoJSON Structure:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "id": "unique_observation_id",
        "species_scientific_name": "Genus species",
        "observed_at": "ISO_datetime_string",
        "count": "number_of_specimens",
        "observer_id": "observer_identifier",
        "data_source": "source_information",
        "location_accuracy_m": "accuracy_in_meters",
        "notes": "observation_notes",
        "image_filename": "associated_image_file",
        "model_id": "ai_model_identifier",
        "confidence": "prediction_confidence_score",
        "metadata": "additional_json_metadata"
      },
      "geometry": {
        "type": "Point",
        "coordinates": [longitude, latitude]
      }
    }
  ]
}
```

### Geographic Datasets

#### Regions Dataset
- **Administrative Boundaries**: Country, state/province, and local regions
- **Ecological Zones**: Biomes, climate zones, and habitat classifications
- **Multilingual Names**: English and Russian region names
- **Hierarchical Structure**: Nested geographic relationships

#### Data Sources Dataset
- **Research Institutions**: Universities and research organizations
- **Government Agencies**: Health departments and environmental agencies
- **Citizen Science**: Community-contributed observation platforms
- **Literature Sources**: Published research and survey data

## Training Datasets

### Image Classification Dataset

The AI model training utilizes curated image datasets from the culicidaelab library:

**Dataset Characteristics:**
- **Species Coverage**: 17+ mosquito species
- **Image Quality**: High-resolution microscopy and field photography
- **Standardization**: Consistent lighting, background, and orientation
- **Augmentation**: Synthetic variations for improved model robustness

**Training/Validation Split:**
- **Training Set**: 70% of images for model learning
- **Validation Set**: 15% for hyperparameter tuning
- **Test Set**: 15% for final performance evaluation

**Data Augmentation Techniques:**
- Rotation and flipping transformations
- Color space adjustments
- Noise injection and blur effects
- Scale and crop variations

### Model Performance Datasets

**Benchmark Datasets:**
- **Accuracy Testing**: Curated test sets with expert annotations
- **Confidence Calibration**: Datasets for confidence score validation
- **Cross-Validation**: Multiple dataset splits for robust evaluation
- **Real-World Testing**: Field images for practical performance assessment

## Data Collection Methodology

### Field Observation Protocols

#### Standardized Collection
- **GPS Coordinates**: Precise location recording (±5m accuracy)
- **Temporal Data**: Date, time, and environmental conditions
- **Specimen Counts**: Quantitative abundance measurements
- **Photography**: Standardized imaging protocols
- **Metadata**: Observer information and collection methods

#### Quality Assurance
- **Expert Validation**: Taxonomic verification by specialists
- **Data Verification**: Cross-checking of observation records
- **Outlier Detection**: Statistical analysis for anomalous data
- **Completeness Checks**: Validation of required fields

### Image Dataset Curation

#### Collection Standards
- **Resolution Requirements**: Minimum pixel dimensions for analysis
- **Focus Quality**: Sharpness and clarity standards
- **Lighting Conditions**: Consistent illumination protocols
- **Background Standards**: Neutral backgrounds for feature extraction

#### Annotation Process
- **Expert Labeling**: Species identification by taxonomists
- **Multi-Reviewer Validation**: Independent verification process
- **Confidence Scoring**: Annotation certainty levels
- **Morphological Features**: Detailed anatomical annotations

## Data Quality and Validation

### Quality Metrics

#### Completeness
- **Field Coverage**: Percentage of required fields populated
- **Geographic Coverage**: Spatial distribution of observations
- **Temporal Coverage**: Time series completeness
- **Species Representation**: Balanced coverage across taxa

#### Accuracy
- **Taxonomic Validation**: Expert verification of species identifications
- **Coordinate Accuracy**: GPS precision and validation
- **Temporal Accuracy**: Date/time verification protocols
- **Image Quality**: Technical quality assessments

#### Consistency
- **Naming Conventions**: Standardized taxonomic nomenclature
- **Unit Standardization**: Consistent measurement units
- **Format Compliance**: Schema adherence validation
- **Cross-Reference Integrity**: Relationship consistency checks

### Validation Procedures

#### Automated Validation
- **Schema Validation**: PyArrow schema compliance checking
- **Range Validation**: Acceptable value range verification
- **Format Validation**: Data type and structure verification
- **Relationship Validation**: Foreign key integrity checks

#### Manual Review
- **Expert Review**: Specialist validation of complex records
- **Statistical Analysis**: Outlier detection and trend analysis
- **Cross-Validation**: Independent verification processes
- **Feedback Integration**: User-reported corrections and updates

## Data Usage and Licensing

### Usage Guidelines

#### Research Applications
- **Academic Research**: Open access for educational institutions
- **Commercial Use**: Licensing terms for commercial applications
- **Attribution Requirements**: Proper citation and acknowledgment
- **Modification Rights**: Permissions for data enhancement

#### Privacy and Ethics
- **Personal Data**: Protection of observer personal information
- **Location Privacy**: Coordinate precision limitations for sensitive areas
- **Consent Management**: Observer consent for data sharing
- **Ethical Guidelines**: Compliance with research ethics standards

### Data Sharing Protocols

#### API Access
- **Rate Limiting**: Request throttling for fair usage
- **Authentication**: Secure access control mechanisms
- **Format Options**: Multiple export formats (JSON, CSV, GeoJSON)
- **Filtering Capabilities**: Query-based data subset access

#### Bulk Downloads
- **Dataset Packages**: Complete dataset downloads
- **Version Control**: Timestamped dataset releases
- **Change Logs**: Documentation of dataset updates
- **Integrity Verification**: Checksums and validation tools

## Future Dataset Enhancements

### Planned Expansions

#### Species Coverage
- **Additional Genera**: Expansion to other mosquito genera
- **Regional Variants**: Subspecies and geographic variants
- **Life Stages**: Egg, larva, pupa, and adult stage data
- **Morphological Variants**: Sexual dimorphism and seasonal variations

#### Geographic Expansion
- **Global Coverage**: Worldwide species distribution data
- **Climate Data Integration**: Environmental parameter correlation
- **Habitat Modeling**: Ecological niche modeling datasets
- **Temporal Dynamics**: Seasonal and annual variation data

#### Technology Integration
- **Molecular Data**: Genetic sequences and phylogenetic information
- **Acoustic Data**: Wing beat frequency and sound signatures
- **Behavioral Data**: Flight patterns and feeding behavior
- **Environmental Sensors**: Real-time environmental monitoring data

### Data Infrastructure Improvements

#### Performance Optimization
- **Indexing Strategies**: Advanced database indexing for faster queries
- **Caching Systems**: Intelligent data caching for improved response times
- **Compression Techniques**: Efficient storage of large datasets
- **Distributed Storage**: Scalable storage architecture

#### Integration Capabilities
- **External APIs**: Integration with global biodiversity databases
- **Real-time Feeds**: Live data streaming from monitoring networks
- **Collaborative Platforms**: Integration with citizen science platforms
- **Research Networks**: Connection to international research consortiums
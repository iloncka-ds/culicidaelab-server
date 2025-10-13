# User Guide Overview

Welcome to the CulicidaeLab Server user guide. This comprehensive guide will help you understand and effectively use all the features of the CulicidaeLab platform for mosquito research, surveillance, and data analysis.

## What is CulicidaeLab Server?

CulicidaeLab Server is a sophisticated web platform that combines artificial intelligence, geospatial visualization, and comprehensive data management to support mosquito research and public health initiatives. The platform provides tools for species identification, surveillance data analysis, and educational resources about mosquito-borne diseases.

## Key Features

### 🔬 AI-Powered Species Prediction

Upload mosquito images and get instant species identification using state-of-the-art machine learning models:

- **Classification Models:** Identify mosquito species from photographs
- **Detection Models:** Locate and identify mosquitoes in complex images
- **Segmentation Models:** Precise mosquito outline detection and analysis
- **Confidence Scoring:** Reliability indicators for each prediction
- **Multiple Model Support:** Access to top-performing models in the CulicidaeLab ecosystem

### 🗺️ Interactive Map Visualization

Explore mosquito distribution and surveillance data through dynamic maps:

- **Observation Mapping:** Visualize mosquito sightings and collection data
- **Species Distribution:** View geographic ranges of different species
- **Temporal Analysis:** Track changes in populations over time
- **Data Filtering:** Filter by species, date ranges, and geographic regions
- **Export Capabilities:** Download data and maps for further analysis

### 📚 Species Database

Access comprehensive information about mosquito species:

- **Species Profiles:** Detailed information about morphology, behavior, and habitat
- **High-Quality Images:** Reference photos for identification
- **Distribution Maps:** Geographic range information
- **Ecological Data:** Breeding preferences and environmental requirements
- **Medical Importance:** Disease vector status and public health relevance

### 🦠 Disease Information Hub

Learn about mosquito-borne diseases and their prevention:

- **Disease Profiles:** Comprehensive information about vector-borne diseases
- **Vector Relationships:** Which mosquito species transmit which diseases
- **Symptoms and Diagnosis:** Clinical information for healthcare providers
- **Prevention Strategies:** Evidence-based prevention and control measures
- **Epidemiological Data:** Disease distribution and outbreak information

## User Roles and Use Cases

### Researchers and Scientists

**Primary Use Cases:**
- Species identification for field studies
- Data collection and analysis for research projects
- Access to reference materials and taxonomic information
- Collaboration through shared datasets and observations

**Key Features:**
- High-accuracy AI models for species identification
- Comprehensive species database with scientific information
- Data export capabilities for statistical analysis
- API access for integration with research workflows

### Public Health Professionals

**Primary Use Cases:**
- Surveillance and monitoring of disease vectors
- Risk assessment and outbreak investigation
- Educational resource development
- Policy and intervention planning

**Key Features:**
- Disease vector identification and mapping
- Surveillance data visualization and analysis
- Disease information and prevention resources
- Geographic analysis tools for risk assessment

### Educators and Students

**Primary Use Cases:**
- Teaching mosquito biology and identification
- Learning about vector-borne diseases
- Hands-on experience with AI and data analysis
- Research project support

**Key Features:**
- User-friendly interface for learning
- Comprehensive educational resources
- Interactive tools for exploration
- Access to real scientific data and models

### Citizen Scientists and Enthusiasts

**Primary Use Cases:**
- Contributing to mosquito surveillance efforts
- Learning about local mosquito species
- Participating in community health initiatives
- Personal interest in entomology

**Key Features:**
- Easy-to-use species identification tools
- Educational content about mosquitoes and diseases
- Contribution opportunities for data collection
- Community features for sharing observations

## Platform Architecture

### Frontend Interface

The user interface is built with Solara, providing:

- **Responsive Design:** Works on desktop, tablet, and mobile devices
- **Interactive Components:** Dynamic maps, image upload, and data visualization
- **Real-time Updates:** Live data processing and results display
- **Accessibility:** Screen reader compatible and keyboard navigable

### Backend API

The backend provides robust data processing and AI inference:

- **FastAPI Framework:** High-performance API with automatic documentation
- **Vector Database:** Efficient similarity search and data retrieval
- **AI Model Integration:** Seamless access to machine learning models
- **Data Management:** Secure storage and retrieval of observations and metadata

### Data Storage

Efficient and scalable data management:

- **LanceDB:** Vector database for similarity search and embeddings
- **GeoJSON Support:** Standardized geospatial data formats
- **Metadata Management:** Comprehensive tracking of data provenance
- **Backup and Recovery:** Robust data protection mechanisms

## Getting Started

### For New Users

1. **Start with the [Quick Start Guide](../getting-started/quick-start.md)** to get the platform running
2. **Try Species Prediction:** Upload a mosquito image to see AI identification in action
3. **Explore the Map:** Browse existing observation data and species distributions
4. **Browse Species Information:** Learn about different mosquito species and their characteristics

### For Advanced Users

1. **Review the [API Documentation](../developer-guide/api-reference/index.md)** for programmatic access
2. **Explore Configuration Options:** Customize the platform for your specific needs
3. **Set Up Data Integration:** Connect your existing datasets and workflows
4. **Contribute Data:** Add your observations to the community database

## Data Quality and Accuracy

### AI Model Performance

The CulicidaeLab AI models are trained on high-quality, curated datasets:

- **Training Data:** 46 species with 3,139 unique images
- **Model Accuracy:** >90% accuracy for top-performing classification models
- **Continuous Improvement:** Regular model updates and retraining
- **Validation:** Rigorous testing on independent datasets

### Data Validation

Quality assurance measures ensure reliable data:

- **Expert Review:** Scientific validation of species identifications
- **Community Verification:** Peer review of contributed observations
- **Automated Checks:** Quality control algorithms for data consistency
- **Feedback Mechanisms:** User reporting of errors and corrections

## Privacy and Data Sharing

### Data Privacy

Your privacy is protected through:

- **Local Processing:** AI inference can be performed locally
- **Minimal Data Collection:** Only necessary information is stored
- **User Control:** You control what data is shared
- **Secure Storage:** Industry-standard security measures

### Open Science

CulicidaeLab supports open science principles:

- **Open Source:** All code is publicly available
- **Open Data:** Datasets are shared under permissive licenses
- **Open Models:** AI models are freely available for research
- **Community Contributions:** Collaborative development and improvement

## Support and Community

### Getting Help

- **Documentation:** Comprehensive guides and tutorials
- **GitHub Issues:** Report bugs and request features
- **Community Discussions:** Ask questions and share experiences
- **Direct Contact:** Email support for specific issues

### Contributing

Join the CulicidaeLab community:

- **Code Contributions:** Improve the platform through development
- **Data Contributions:** Share observations and datasets
- **Documentation:** Help improve guides and tutorials
- **Testing:** Report issues and test new features

## Next Steps

Explore specific features in detail:

- **[Species Prediction](species-prediction.md):** Learn how to use AI for mosquito identification
- **[Species Database](species-database.md):** Browse and search comprehensive species information
- **[Diseases Database](diseases-database.md):** Explore mosquito-borne diseases and prevention strategies
- **[Map Visualization](map-visualization.md):** Master the interactive mapping tools
- **[Data Management](data-management.md):** Understand data import, export, and organization
- **[Troubleshooting](troubleshooting.md):** Solve common issues and optimize performance
- **[FAQ](faq.md):** Find answers to frequently asked questions

For technical users, also check out:

- **[Developer Guide](../developer-guide/architecture.md):** Technical architecture and development information
- **[API Reference](../reference/api/index.md):** Complete API documentation
- **[Deployment Guide](../deployment/production.md):** Production deployment instructions
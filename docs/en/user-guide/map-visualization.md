# Map Visualization Guide

Master the interactive mapping tools to explore mosquito distribution patterns, surveillance data, and geographic trends in the CulicidaeLab platform.

## Overview

The Map Visualization feature provides powerful tools for exploring geospatial mosquito data, including species distributions, observation records, and surveillance patterns. The interactive map interface allows you to filter, analyze, and export geographic data for research and public health applications.

## Getting Started

### Accessing the Map

1. Click the **Map** tab in the main navigation
2. The interactive map will load showing global mosquito observation data
3. Use the controls to zoom, pan, and explore different regions

### Map Interface Components

**Main Map Area:**
- Interactive world map with observation markers
- Zoom controls (+ / - buttons or mouse wheel)
- Pan functionality (click and drag)
- Layer toggle controls

**Control Panel:**
- Species filters
- Date range selectors
- Data source filters
- Display options

**Information Panel:**
- Selected observation details
- Summary statistics
- Export options

## Basic Navigation

### Zooming and Panning

**Mouse Controls:**
- **Zoom In/Out:** Mouse wheel or double-click
- **Pan:** Click and drag to move around
- **Reset View:** Click home button to return to global view

**Touch Controls (Mobile/Tablet):**
- **Zoom:** Pinch to zoom in/out
- **Pan:** Single finger drag to move
- **Rotate:** Two-finger rotation (if enabled)

### Map Layers

**Base Map Options:**
- **Satellite:** High-resolution satellite imagery
- **Street Map:** Detailed street and city information
- **Terrain:** Topographic features and elevation
- **Hybrid:** Combination of satellite and street data

**Data Layers:**
- **Observations:** Individual mosquito collection points
- **Species Distribution:** Predicted species ranges
- **Surveillance Networks:** Monitoring station locations
- **Environmental Data:** Climate and habitat information

## Filtering and Searching

### Species Filters

**Filter by Species:**
1. Open the Species filter panel
2. Select specific species from the dropdown list
3. Use checkboxes to select multiple species
4. Apply filters to update map display

**Common Filter Combinations:**
- **Disease Vectors:** Filter for *Aedes aegypti*, *Aedes albopictus*, *Anopheles* species
- **Regional Species:** Focus on species common to your geographic area
- **Research Targets:** Select species relevant to your study

### Geographic Filters

**Region Selection:**
1. Use the region dropdown to select continents or countries
2. Draw custom boundaries using the polygon tool
3. Search for specific locations using the search box

**Coordinate-Based Filtering:**
- Enter latitude/longitude ranges
- Upload geographic boundary files (GeoJSON, KML)
- Use administrative boundaries (countries, states, provinces)

### Temporal Filters

**Date Range Selection:**
1. Use the date picker to set start and end dates
2. Select predefined ranges (last month, year, etc.)
3. Filter by seasons or specific time periods

**Temporal Analysis Options:**
- **Animation Mode:** Watch data changes over time
- **Seasonal Patterns:** Compare different seasons
- **Trend Analysis:** Identify long-term patterns

## Step-by-Step Tutorial: Analyzing Aedes aegypti Distribution

Let's explore the global distribution of *Aedes aegypti*, a major disease vector:

### Step 1: Set Up the Analysis

1. **Access the Map:** Navigate to the Map page
2. **Clear Existing Filters:** Reset any active filters
3. **Select Base Layer:** Choose "Satellite" for geographic context

### Step 2: Apply Species Filter

1. **Open Species Filter:** Click on the species dropdown
2. **Search for Aedes aegypti:** Type "aegypti" in the search box
3. **Select Species:** Check the box for *Aedes aegypti*
4. **Apply Filter:** Click "Apply" to update the map

**Expected Results:**
- Map shows only *Aedes aegypti* observations
- Markers concentrated in tropical and subtropical regions
- Clear absence from temperate and polar regions

### Step 3: Analyze Geographic Patterns

**Observe Distribution Patterns:**
- **Tropical Belt:** High concentration between 35°N and 35°S
- **Urban Areas:** Clusters around major cities
- **Coastal Regions:** Strong presence in coastal areas
- **Island Nations:** Widespread in Caribbean and Pacific islands

**Interactive Exploration:**
1. **Zoom to Regions:** Focus on specific continents or countries
2. **Click Markers:** View individual observation details
3. **Identify Hotspots:** Look for areas with high observation density

### Step 4: Temporal Analysis

1. **Set Date Range:** Filter to recent years (e.g., 2020-2024)
2. **Enable Animation:** Use time slider to see changes over time
3. **Seasonal Patterns:** Compare wet vs. dry seasons

**Key Observations:**
- **Seasonal Variation:** Higher activity during warm, wet months
- **Range Expansion:** Gradual spread to new geographic areas
- **Urban Spread:** Increasing presence in urban environments

### Step 5: Export and Save Results

1. **Generate Summary:** Click "Generate Report" for statistics
2. **Export Data:** Download filtered observations as CSV
3. **Save Map View:** Bookmark or save current map state
4. **Create Screenshots:** Capture map images for presentations

## Advanced Features

### Data Visualization Options

**Marker Styles:**
- **Point Markers:** Individual observation locations
- **Heatmaps:** Density visualization for large datasets
- **Choropleth:** Administrative region coloring by data values
- **Cluster Markers:** Grouped observations for better performance

**Symbology Options:**
- **Size by Abundance:** Larger markers for higher specimen counts
- **Color by Species:** Different colors for each species
- **Shape by Data Source:** Different symbols for various data sources
- **Transparency:** Adjust opacity for overlapping data

### Statistical Analysis

**Summary Statistics:**
- **Observation Counts:** Total observations by region/species
- **Density Calculations:** Observations per unit area
- **Temporal Trends:** Changes in observation frequency over time
- **Species Richness:** Number of species per geographic area

**Spatial Analysis:**
- **Hotspot Detection:** Identify areas of high activity
- **Range Estimation:** Calculate species distribution boundaries
- **Habitat Suitability:** Overlay environmental data
- **Connectivity Analysis:** Assess landscape connectivity

### Data Integration

**Environmental Layers:**
- **Climate Data:** Temperature, precipitation, humidity
- **Land Use:** Urban areas, agriculture, natural habitats
- **Elevation:** Topographic data and altitude zones
- **Water Bodies:** Rivers, lakes, and wetland areas

**Surveillance Networks:**
- **Monitoring Stations:** Active surveillance locations
- **Trap Networks:** Vector control monitoring systems
- **Research Sites:** Academic and institutional study areas
- **Public Health Facilities:** Hospitals and clinics

## Working with Observation Data

### Understanding Observation Records

**Data Fields:**
- **Species:** Scientific and common names
- **Location:** GPS coordinates and place names
- **Date/Time:** Collection date and time
- **Collector:** Person or organization responsible
- **Method:** Collection or observation method
- **Abundance:** Number of specimens observed
- **Life Stage:** Adult, larva, pupa, egg
- **Sex:** Male, female, or unknown
- **Notes:** Additional observations or comments

### Data Quality Indicators

**Quality Scores:**
- **High Quality:** GPS coordinates, expert identification, recent date
- **Medium Quality:** Approximate location, probable identification
- **Low Quality:** Uncertain location or identification

**Verification Status:**
- **Verified:** Expert-confirmed identification
- **Probable:** High-confidence automated identification
- **Unverified:** Requires additional confirmation

### Contributing Observations

**Adding New Data:**
1. **Click "Add Observation"** on the map
2. **Select Location:** Click on map or enter coordinates
3. **Enter Details:** Species, date, abundance, etc.
4. **Upload Photos:** Include specimen images if available
5. **Submit:** Add to community database

**Data Standards:**
- **Accurate Coordinates:** Use GPS when possible
- **Proper Identification:** Verify species identification
- **Complete Metadata:** Include all relevant information
- **Quality Photos:** Clear images for verification

## Troubleshooting Common Issues

### Performance Issues

**Problem:** Map loads slowly or becomes unresponsive

**Solutions:**
1. **Reduce Data Load:**
   - Apply more restrictive filters
   - Zoom to smaller geographic areas
   - Limit date ranges

2. **Browser Optimization:**
   - Close unnecessary browser tabs
   - Clear browser cache
   - Use modern browser versions
   - Disable browser extensions

3. **Network Issues:**
   - Check internet connection speed
   - Try different network connection
   - Use wired connection if possible

### Display Problems

**Problem:** Markers not showing or incorrect positioning

**Troubleshooting:**
1. **Check Filters:** Ensure filters aren't excluding all data
2. **Zoom Level:** Some data only visible at certain zoom levels
3. **Layer Settings:** Verify correct layers are enabled
4. **Browser Compatibility:** Try different browser

### Data Issues

**Problem:** Missing or unexpected data patterns

**Investigation Steps:**
1. **Verify Filters:** Check all active filter settings
2. **Data Sources:** Confirm expected data sources are included
3. **Geographic Scope:** Ensure study area is properly defined
4. **Temporal Range:** Verify date ranges include expected periods

## Export and Reporting

### Data Export Options

**Supported Formats:**
- **CSV:** Tabular data for spreadsheet analysis
- **GeoJSON:** Geographic data for GIS applications
- **KML:** Google Earth compatible format
- **Shapefile:** Professional GIS format

**Export Process:**
1. **Apply Filters:** Set up desired data subset
2. **Select Export Format:** Choose appropriate file type
3. **Configure Options:** Set coordinate system, field selection
4. **Download:** Save file to local computer

### Report Generation

**Automated Reports:**
- **Summary Statistics:** Observation counts and distributions
- **Species Lists:** Complete species inventories for regions
- **Temporal Summaries:** Seasonal and annual patterns
- **Quality Reports:** Data quality and completeness metrics

**Custom Reports:**
- **Research Summaries:** Tailored for specific studies
- **Surveillance Reports:** Public health monitoring summaries
- **Educational Materials:** Classroom and outreach resources

### Map Image Export

**Static Maps:**
1. **Set View:** Position and zoom to desired area
2. **Configure Display:** Set layers and symbology
3. **Export Image:** High-resolution PNG or PDF
4. **Add Annotations:** Include scale bars, legends, titles

**Interactive Maps:**
- **Embed Code:** HTML for websites
- **Shareable Links:** URLs for collaboration
- **Web Services:** API endpoints for applications

## Integration with Other Features

### Species Prediction Integration

**Workflow:**
1. **Identify Species:** Use prediction tool for unknown specimens
2. **Add to Map:** Contribute verified identifications
3. **Validate Patterns:** Compare predictions with known distributions
4. **Update Database:** Improve species range information

### Disease Information Links

**Vector Mapping:**
1. **Select Disease Vectors:** Filter for species of medical importance
2. **Overlay Disease Data:** Show disease occurrence patterns
3. **Risk Assessment:** Identify high-risk areas
4. **Prevention Planning:** Target control efforts

## Best Practices

### Data Analysis

**Statistical Considerations:**
- **Sample Bias:** Account for uneven sampling effort
- **Temporal Bias:** Consider seasonal collection patterns
- **Geographic Bias:** Recognize urban vs. rural sampling differences
- **Detection Probability:** Account for species detectability

**Quality Control:**
- **Verify Identifications:** Cross-check uncertain records
- **Check Coordinates:** Validate geographic accuracy
- **Review Outliers:** Investigate unusual observations
- **Document Methods:** Record analysis procedures

### Visualization Design

**Effective Maps:**
- **Clear Symbology:** Use intuitive colors and symbols
- **Appropriate Scale:** Match detail level to purpose
- **Informative Legends:** Include all necessary information
- **Context Layers:** Provide geographic reference

**Accessibility:**
- **Color-Blind Friendly:** Use accessible color schemes
- **High Contrast:** Ensure visibility for all users
- **Alternative Text:** Provide descriptions for images
- **Keyboard Navigation:** Support non-mouse interaction

## Frequently Asked Questions

### Data Questions

**Q: How current is the observation data?**
A: Data is updated regularly from contributing sources. Most recent observations are from ongoing surveillance and research programs. Check individual records for specific collection dates.

**Q: Can I trust the species identifications?**
A: Identification quality varies by source. Look for verification status and quality indicators. Expert-verified records are most reliable, while automated identifications should be used with appropriate caution.

**Q: Why are some regions missing data?**
A: Data availability reflects sampling effort and research activity. Some regions may have limited surveillance or research programs. Absence of data doesn't necessarily mean absence of species.

### Technical Questions

**Q: What coordinate systems are supported?**
A: The map uses WGS84 (EPSG:4326) by default. Data can be exported in various coordinate systems including UTM zones and local projections.

**Q: Can I upload my own data?**
A: Yes, you can contribute individual observations through the interface or contact administrators for bulk data uploads. Data must meet quality standards and include proper metadata.

**Q: Is there an API for programmatic access?**
A: Yes, the platform provides REST API endpoints for accessing map data. See the API documentation for details on authentication and usage.

### Usage Questions

**Q: Can I use the maps in publications?**
A: Yes, maps and data can be used in research publications with proper attribution. Check the data license for specific requirements and cite the CulicidaeLab platform.

**Q: How do I cite the data in my research?**
A: Use the provided citation format and include the access date. Individual datasets may have specific citation requirements listed in their metadata.

**Q: Can I collaborate with other researchers?**
A: The platform supports data sharing and collaboration. Contact the development team to set up research partnerships or data sharing agreements.

## Getting Help

### Support Resources

- **User Documentation:** Comprehensive guides and tutorials
- **Video Tutorials:** Step-by-step visual guides
- **FAQ Database:** Common questions and solutions
- **Community Forum:** User discussions and tips

### Technical Support

- **GitHub Issues:** Report bugs and request features
- **Email Support:** Direct contact for specific problems
- **Live Chat:** Real-time assistance during business hours
- **Training Sessions:** Scheduled group training opportunities

### Expert Consultation

- **GIS Specialists:** Spatial analysis and mapping expertise
- **Entomologists:** Species identification and ecology
- **Epidemiologists:** Disease vector and public health applications
- **Data Scientists:** Statistical analysis and modeling

## Next Steps

After mastering map visualization:

1. **Advanced Analysis:** Learn statistical analysis techniques
2. **Data Contribution:** Add your observations to the database
3. **API Integration:** Develop custom applications
4. **Research Collaboration:** Connect with other researchers

For technical users:
- **GIS Integration:** Connect with professional GIS software
- **Database Access:** Direct database queries and analysis
- **Custom Visualizations:** Develop specialized mapping tools
- **Automated Workflows:** Set up data processing pipelines
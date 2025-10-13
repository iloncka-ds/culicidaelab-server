# Data Management Guide

Learn how to effectively organize, import, export, and manage mosquito surveillance and research data within the CulicidaeLab platform.

## Overview

The Data Management system in CulicidaeLab provides comprehensive tools for handling mosquito observation data, research datasets, and surveillance records. Whether you're managing field collection data, laboratory results, or literature records, this guide will help you organize and maintain high-quality datasets.

## Data Types and Structures

### Observation Records

**Core Data Fields:**
- **Species Information:** Scientific name, common name, taxonomic details
- **Geographic Data:** Latitude, longitude, location description, administrative regions
- **Temporal Data:** Collection date, time, season
- **Collection Details:** Method, collector, institution, project
- **Specimen Data:** Life stage, sex, abundance, condition
- **Environmental Context:** Habitat type, weather conditions, associated species

**Optional Fields:**
- **Morphometric Data:** Size measurements, wing length, body proportions
- **Genetic Information:** DNA barcodes, molecular markers
- **Disease Status:** Pathogen testing results, infection rates
- **Images:** Specimen photographs, habitat photos
- **Notes:** Additional observations, behavioral notes

### Data Quality Standards

**Required Fields:**
- Species identification (minimum to genus level)
- Geographic coordinates or location description
- Collection date
- Data source and collector information

**Quality Indicators:**
- **Coordinate Precision:** GPS accuracy, coordinate uncertainty
- **Identification Confidence:** Expert verified, probable, uncertain
- **Data Completeness:** Percentage of fields populated
- **Temporal Accuracy:** Date precision and reliability

## Importing Data

### Supported File Formats

**Tabular Data:**
- **CSV (Comma-Separated Values):** Most common format for spreadsheet data
- **Excel (.xlsx, .xls):** Microsoft Excel workbooks
- **TSV (Tab-Separated Values):** Tab-delimited text files
- **JSON:** Structured data format for web applications

**Geographic Data:**
- **GeoJSON:** Geographic data with embedded attributes
- **KML/KMZ:** Google Earth format files
- **Shapefile:** Professional GIS format (requires all component files)
- **GPX:** GPS track and waypoint data

### Step-by-Step Import Process

#### Preparing Your Data

1. **Organize Your Spreadsheet:**
   ```
   species_name | latitude | longitude | date_collected | collector | abundance
   Aedes aegypti | 25.7617 | -80.1918 | 2024-03-15 | J. Smith | 12
   Culex quinquefasciatus | 25.7890 | -80.2264 | 2024-03-15 | J. Smith | 8
   ```

2. **Check Data Quality:**
   - Verify species names against accepted taxonomy
   - Validate coordinate formats (decimal degrees preferred)
   - Ensure date formats are consistent (YYYY-MM-DD recommended)
   - Remove duplicate records

3. **Standardize Field Names:**
   - Use consistent column headers
   - Follow Darwin Core standards when possible
   - Avoid special characters and spaces in column names

#### Import Workflow

1. **Access Import Tool:**
   - Navigate to Data Management section
   - Click "Import Data" button
   - Select file type and upload method

2. **Upload File:**
   - Drag and drop file onto upload area
   - Or click "Browse" to select file
   - Wait for file validation and preview

3. **Map Fields:**
   - Review detected column mappings
   - Adjust field assignments as needed
   - Set data types for each column
   - Configure coordinate system if needed

4. **Validate Data:**
   - Review data quality report
   - Address any validation errors
   - Preview imported records
   - Confirm import settings

5. **Complete Import:**
   - Click "Import Data" to finalize
   - Monitor import progress
   - Review import summary
   - Check for any warnings or errors

### Data Validation Rules

**Automatic Checks:**
- **Geographic Validation:** Coordinates within valid ranges (-90 to 90 latitude, -180 to 180 longitude)
- **Date Validation:** Dates in reasonable ranges (not future dates for historical data)
- **Species Validation:** Names checked against taxonomic databases
- **Format Validation:** Data types match expected formats

**Quality Warnings:**
- **Coordinate Precision:** Very precise coordinates may indicate GPS errors
- **Unusual Locations:** Species found outside known ranges
- **Temporal Outliers:** Very old or recent dates that seem unusual
- **Missing Data:** Important fields left blank

## Exporting Data

### Export Options

**Data Subsets:**
- **Filtered Data:** Export only records matching current filters
- **Selected Records:** Export manually selected observations
- **Complete Dataset:** Export all available data
- **Custom Queries:** Export based on complex criteria

**Format Selection:**
- **CSV:** Universal format for spreadsheet applications
- **Excel:** Formatted workbook with multiple sheets
- **GeoJSON:** Geographic data with spatial information
- **Darwin Core Archive:** Standardized biodiversity data format

### Step-by-Step Export Process

1. **Set Up Filters:**
   - Apply species, geographic, and temporal filters
   - Select data quality thresholds
   - Choose specific data sources if needed

2. **Configure Export:**
   - Select desired file format
   - Choose fields to include
   - Set coordinate system for geographic data
   - Configure date formats

3. **Generate Export:**
   - Click "Export Data" button
   - Wait for file generation
   - Download completed file
   - Verify export contents

### Custom Export Templates

**Research Templates:**
- **Ecological Survey:** Fields relevant for ecological studies
- **Medical Entomology:** Vector-focused data fields
- **Taxonomic Study:** Morphological and identification data
- **Surveillance Report:** Public health monitoring format

**Creating Custom Templates:**
1. Define required fields for your use case
2. Set default filters and quality criteria
3. Configure output format and styling
4. Save template for future use
5. Share templates with collaborators

## Data Organization

### Project Management

**Creating Projects:**
1. **Define Project Scope:** Geographic area, time period, objectives
2. **Set Data Standards:** Required fields, quality criteria, naming conventions
3. **Assign Permissions:** Control who can view, edit, or export data
4. **Configure Workflows:** Data entry, validation, and approval processes

**Project Structure:**
```
Project: Urban Aedes Survey 2024
├── Field Collections/
│   ├── Site A - Downtown
│   ├── Site B - Residential
│   └── Site C - Industrial
├── Laboratory Results/
│   ├── Species Confirmations
│   ├── Pathogen Testing
│   └── Morphometric Data
└── Analysis Results/
    ├── Species Distribution Maps
    ├── Abundance Trends
    └── Risk Assessment
```

### Data Categories

**By Collection Method:**
- **Active Surveillance:** Targeted collection efforts
- **Passive Surveillance:** Opportunistic observations
- **Citizen Science:** Community-contributed data
- **Literature Records:** Published observation data
- **Museum Specimens:** Historical collection records

**By Data Source:**
- **Field Collections:** Direct specimen collection
- **Trap Monitoring:** Systematic trap networks
- **Visual Observations:** Sight records without collection
- **Photographic Records:** Image-based identifications
- **Molecular Data:** DNA-based identifications

### Metadata Management

**Dataset Metadata:**
- **Title and Description:** Clear, descriptive names
- **Temporal Coverage:** Start and end dates
- **Geographic Coverage:** Bounding box or region names
- **Taxonomic Coverage:** Species or groups included
- **Collection Methods:** Sampling protocols used
- **Data Quality:** Completeness and accuracy metrics

**Record-Level Metadata:**
- **Data Provenance:** Source and collection history
- **Quality Assessments:** Confidence scores and validation status
- **Processing History:** Modifications and corrections made
- **Usage Rights:** Licensing and attribution requirements

## Data Quality Control

### Quality Assessment

**Automated Quality Checks:**
- **Completeness:** Percentage of required fields populated
- **Consistency:** Internal data consistency checks
- **Validity:** Values within acceptable ranges
- **Accuracy:** Comparison with reference datasets

**Manual Review Process:**
1. **Initial Screening:** Check for obvious errors
2. **Expert Review:** Taxonomic and geographic validation
3. **Cross-Validation:** Compare with other datasets
4. **Community Review:** Peer verification process

### Error Detection and Correction

**Common Data Errors:**
- **Coordinate Errors:** Swapped latitude/longitude, wrong decimal places
- **Date Errors:** Incorrect formats, impossible dates
- **Species Misidentification:** Incorrect taxonomic assignments
- **Duplicate Records:** Same observation entered multiple times

**Correction Workflow:**
1. **Identify Errors:** Use validation tools and expert review
2. **Document Issues:** Record error types and sources
3. **Implement Corrections:** Make necessary data changes
4. **Track Changes:** Maintain audit trail of modifications
5. **Verify Fixes:** Confirm corrections resolve issues

### Data Standardization

**Taxonomic Standardization:**
- **Authority Files:** Use accepted taxonomic databases
- **Synonym Resolution:** Map alternative names to accepted names
- **Hierarchical Validation:** Ensure taxonomic consistency
- **Regular Updates:** Keep taxonomy current with revisions

**Geographic Standardization:**
- **Coordinate Systems:** Standardize to WGS84 decimal degrees
- **Administrative Boundaries:** Use standard geographic codes
- **Place Names:** Standardize location descriptions
- **Precision Indicators:** Record coordinate uncertainty

## Collaboration and Sharing

### Data Sharing Protocols

**Access Levels:**
- **Public:** Open access for all users
- **Registered Users:** Access for platform members
- **Project Members:** Restricted to project participants
- **Private:** Access only for data owners

**Sharing Agreements:**
- **Data Use Agreements:** Terms and conditions for data use
- **Attribution Requirements:** How to cite data sources
- **Embargo Periods:** Temporary restrictions on data access
- **Commercial Use:** Policies for commercial applications

### Collaborative Workflows

**Multi-User Projects:**
1. **Role Assignment:** Define user roles and permissions
2. **Data Entry Standards:** Establish consistent protocols
3. **Review Processes:** Implement quality control workflows
4. **Communication Tools:** Coordinate team activities
5. **Version Control:** Track changes and updates

**Data Integration:**
- **Cross-Project Sharing:** Share data between related projects
- **External Databases:** Connect with other data sources
- **API Integration:** Programmatic data exchange
- **Federated Search:** Query multiple databases simultaneously

## Advanced Data Management

### Database Administration

**Performance Optimization:**
- **Indexing:** Optimize database queries
- **Archiving:** Move old data to long-term storage
- **Backup Procedures:** Regular data backup and recovery
- **Monitoring:** Track database performance and usage

**Data Lifecycle Management:**
- **Ingestion:** Automated data import processes
- **Processing:** Data cleaning and standardization
- **Storage:** Efficient data organization and retrieval
- **Archival:** Long-term preservation strategies
- **Disposal:** Secure deletion of obsolete data

### API and Programmatic Access

**REST API Endpoints:**
```python
# Get observations by species
GET /api/v1/observations?species=Aedes aegypti

# Upload new observations
POST /api/v1/observations
{
  "species": "Aedes aegypti",
  "latitude": 25.7617,
  "longitude": -80.1918,
  "date": "2024-03-15",
  "abundance": 12
}

# Export filtered data
GET /api/v1/export?format=csv&species=Aedes&start_date=2024-01-01
```

**Bulk Operations:**
- **Batch Import:** Upload large datasets efficiently
- **Bulk Updates:** Modify multiple records simultaneously
- **Mass Export:** Download large datasets
- **Automated Processing:** Schedule regular data operations

## Troubleshooting Common Issues

### Import Problems

**File Format Issues:**
- **Encoding Problems:** Use UTF-8 encoding for international characters
- **Delimiter Confusion:** Ensure correct separator (comma, tab, semicolon)
- **Quote Characters:** Handle embedded quotes and special characters
- **Line Endings:** Address Windows/Mac/Linux line ending differences

**Data Format Problems:**
- **Date Formats:** Standardize date representations
- **Coordinate Formats:** Convert to decimal degrees
- **Species Names:** Check spelling and taxonomic authority
- **Missing Values:** Handle empty cells appropriately

### Performance Issues

**Large Dataset Handling:**
- **Chunked Processing:** Process data in smaller batches
- **Streaming Import:** Handle files too large for memory
- **Progress Monitoring:** Track import/export progress
- **Error Recovery:** Resume interrupted operations

**Query Optimization:**
- **Efficient Filters:** Use indexed fields for filtering
- **Limit Results:** Paginate large result sets
- **Cache Results:** Store frequently accessed data
- **Parallel Processing:** Use multiple threads for operations

### Data Quality Issues

**Validation Failures:**
- **Coordinate Validation:** Check for reasonable geographic locations
- **Date Validation:** Ensure dates are within expected ranges
- **Species Validation:** Verify against taxonomic databases
- **Completeness Checks:** Identify missing required fields

**Consistency Problems:**
- **Duplicate Detection:** Identify and merge duplicate records
- **Conflicting Information:** Resolve contradictory data
- **Standardization Issues:** Ensure consistent data formats
- **Reference Mismatches:** Align with external databases

## Best Practices

### Data Entry

**Standardization:**
- **Controlled Vocabularies:** Use standardized terms and codes
- **Data Templates:** Provide consistent data entry forms
- **Validation Rules:** Implement real-time data validation
- **Training Materials:** Educate users on data standards

**Quality Control:**
- **Double Entry:** Verify critical data through re-entry
- **Expert Review:** Have specialists validate identifications
- **Cross-Validation:** Compare with independent sources
- **Regular Audits:** Periodic data quality assessments

### Data Preservation

**Backup Strategies:**
- **Multiple Copies:** Maintain redundant backups
- **Geographic Distribution:** Store backups in different locations
- **Regular Testing:** Verify backup integrity and restoration
- **Version Control:** Track data changes over time

**Long-term Preservation:**
- **Standard Formats:** Use widely supported file formats
- **Metadata Documentation:** Maintain comprehensive documentation
- **Migration Planning:** Prepare for technology changes
- **Access Preservation:** Ensure continued data accessibility

## Frequently Asked Questions

### General Questions

**Q: What data formats are supported for import?**
A: The platform supports CSV, Excel, JSON, GeoJSON, KML, and Shapefile formats. CSV is recommended for most tabular data imports.

**Q: How do I ensure my data meets quality standards?**
A: Use the built-in validation tools, follow the data entry guidelines, and consider expert review for critical identifications. The platform provides quality scores and validation reports.

**Q: Can I edit data after importing it?**
A: Yes, you can edit individual records or perform bulk updates. All changes are tracked in an audit trail for transparency and quality control.

### Technical Questions

**Q: What's the maximum file size for imports?**
A: File size limits depend on your account type and server configuration. Large datasets can be imported in chunks or through the API for better performance.

**Q: How do I handle coordinate system conversions?**
A: The platform automatically converts common coordinate systems to WGS84. For specialized projections, convert your data before import or contact support.

**Q: Can I automate data imports?**
A: Yes, use the REST API for automated imports. You can set up scheduled imports or integrate with existing data collection systems.

### Data Policy Questions

**Q: Who owns the data I upload?**
A: You retain ownership of your data. The platform provides tools for sharing and collaboration while respecting your data rights and privacy preferences.

**Q: How is sensitive location data protected?**
A: The platform offers options to obscure precise coordinates for sensitive species or locations. You can set privacy levels for different types of data.

**Q: Can I delete my data?**
A: Yes, you can delete your own data at any time. However, consider the impact on collaborative projects and published research before removing shared data.

## Getting Help

### Support Resources

- **Documentation:** Comprehensive guides and tutorials
- **Video Tutorials:** Step-by-step visual instructions
- **Template Downloads:** Standard data formats and examples
- **Community Forum:** User discussions and shared solutions

### Technical Support

- **Help Desk:** Direct support for technical issues
- **Training Sessions:** Scheduled group training
- **Consultation Services:** Expert assistance for complex projects
- **Custom Development:** Specialized features for institutional users

### Data Services

- **Data Cleaning:** Professional data quality improvement
- **Migration Services:** Help moving from other systems
- **Integration Support:** Connecting with existing workflows
- **Training Programs:** Comprehensive user education

## Next Steps

After mastering data management:

1. **Advanced Analysis:** Learn statistical analysis and modeling techniques
2. **API Development:** Build custom applications and integrations
3. **Data Contribution:** Share your datasets with the research community
4. **Quality Assurance:** Become a data validator and reviewer

For institutional users:
- **Enterprise Features:** Advanced permissions and workflow management
- **Custom Integrations:** Connect with institutional databases
- **Bulk Processing:** Handle large-scale data operations
- **Professional Services:** Dedicated support and consulting
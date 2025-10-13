# Frequently Asked Questions (FAQ)

Comprehensive answers to the most common questions about using the CulicidaeLab platform.

## Getting Started

### What is CulicidaeLab?

**Q: What is CulicidaeLab and what can I do with it?**

A: CulicidaeLab is a comprehensive web platform for mosquito research, surveillance, and education. You can:

- **Identify mosquito species** using AI-powered image recognition
- **Explore interactive maps** showing mosquito distributions and surveillance data
- **Access comprehensive species information** including morphology, ecology, and medical importance
- **Learn about mosquito-borne diseases** and prevention strategies
- **Contribute observations** to community surveillance efforts
- **Manage research data** with import/export tools
- **Collaborate** with other researchers and public health professionals

### System Requirements

**Q: What do I need to use CulicidaeLab?**

A: **Minimum Requirements:**
- Modern web browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- Internet connection (broadband recommended for image uploads)
- JavaScript enabled
- Cookies enabled

**Recommended Setup:**
- Desktop or laptop computer for full functionality
- High-resolution display for detailed image analysis
- Fast internet connection for large data operations
- Camera or scanner for specimen photography

**Q: Does CulicidaeLab work on mobile devices?**

A: Yes! The platform is mobile-responsive and works on smartphones and tablets. However, some features like detailed data analysis work better on larger screens. Mobile devices are excellent for field data collection and species identification.

### Account and Access

**Q: Do I need to create an account to use CulicidaeLab?**

A: Basic features like species identification and map browsing are available without an account. However, creating a free account allows you to:
- Save your prediction results
- Contribute observations to the database
- Access advanced filtering and export features
- Participate in collaborative projects
- Receive updates about new features

**Q: Is CulicidaeLab free to use?**

A: Yes, CulicidaeLab is completely free for research, education, and public health applications. The platform is open source and supported by the research community.

## Species Identification

### AI Prediction System

**Q: How accurate is the AI species identification?**

A: Our AI models achieve over 90% accuracy on test datasets with high-quality images. However, real-world accuracy depends on several factors:
- **Image quality** (lighting, focus, resolution)
- **Specimen condition** (complete, undamaged specimens work best)
- **Species complexity** (some species are harder to distinguish than others)
- **Geographic context** (consider if species occurs in your region)

Always check confidence scores and consider alternative predictions for verification.

**Q: What species can the AI identify?**

A: The current system can identify 46 mosquito species commonly encountered in research and surveillance, including:
- Major disease vectors (*Aedes aegypti*, *Aedes albopictus*, *Anopheles* species)
- Common pest species (*Culex* species)
- Regionally important species from various geographic areas

The species database is continuously expanding based on research needs and data availability.

**Q: Why do I get different results for the same mosquito?**

A: Prediction variations can occur due to:
- **Different image angles** showing different diagnostic features
- **Lighting conditions** affecting feature visibility
- **Image quality** differences between uploads
- **Model uncertainty** for specimens with ambiguous features

For best results, upload multiple high-quality images from different angles and compare results.

### Image Requirements

**Q: What makes a good mosquito photo for identification?**

A: **Essential Elements:**
- **Clear focus** on the mosquito specimen
- **Good lighting** (natural light preferred, avoid harsh shadows)
- **Appropriate size** (mosquito fills significant portion of frame)
- **Clean background** (minimal clutter or distractions)
- **Dorsal view** (top-down view showing wing patterns and body markings)

**Technical Specifications:**
- **Resolution:** Minimum 224x224 pixels (higher preferred)
- **Format:** JPEG, PNG, or WebP
- **File size:** Under 10MB
- **Color:** Full color images (avoid black and white)

**Q: Can I identify mosquito larvae or pupae?**

A: Currently, the AI system is optimized for adult mosquitoes. Larval and pupal identification requires different diagnostic features and specialized models that are not yet available. We recommend rearing specimens to adults for accurate identification.

**Q: What should I do if I get low confidence scores?**

A: **Improve Image Quality:**
- Use better lighting (natural daylight works best)
- Ensure sharp focus on diagnostic features
- Try different angles (dorsal, lateral, ventral views)
- Remove background clutter
- Use higher resolution images

**Verify Results:**
- Check alternative predictions
- Compare with reference images in species profiles
- Consider geographic probability (is species found in your area?)
- Seek expert verification for important identifications

## Map and Data Features

### Using the Interactive Map

**Q: What data is shown on the map?**

A: The interactive map displays:
- **Observation records** from research and surveillance programs
- **Species distribution data** showing where different species have been found
- **Surveillance network locations** indicating monitoring sites
- **Environmental context** through various base map layers

Data comes from multiple sources including research institutions, public health agencies, and community contributors.

**Q: Why don't I see data for my region?**

A: Data availability varies by geographic region based on:
- **Research activity** in the area
- **Surveillance programs** operated by public health agencies
- **Community contributions** from local users
- **Historical data collection** efforts

You can help fill gaps by contributing your own observations to the database.

**Q: How current is the map data?**

A: Data currency varies by source:
- **Recent observations** may be added within days or weeks
- **Research data** is typically added after study completion and publication
- **Surveillance data** depends on reporting schedules of contributing agencies
- **Historical data** includes records going back several decades

Check individual observation records for specific collection dates.

### Data Quality and Reliability

**Q: How reliable is the observation data?**

A: Data quality varies and is indicated by quality scores:
- **High quality:** Expert-verified identifications with precise coordinates
- **Medium quality:** Probable identifications with good location data
- **Low quality:** Uncertain identifications or approximate locations

Always consider quality indicators when using data for research or decision-making.

**Q: Can I trust species identifications in the database?**

A: Identification reliability varies by source:
- **Expert-verified:** Confirmed by professional entomologists
- **AI-predicted:** Automated identifications with confidence scores
- **Community-contributed:** Varying levels of expertise

Look for verification status and cross-reference with multiple sources for critical applications.

## Data Management

### Importing and Exporting Data

**Q: What file formats can I import?**

A: **Supported Import Formats:**
- **CSV** (Comma-Separated Values) - recommended for most data
- **Excel** (.xlsx, .xls) - Microsoft Excel workbooks
- **JSON** - Structured data format
- **GeoJSON** - Geographic data with spatial information
- **KML/KMZ** - Google Earth format files

**Q: How do I prepare my data for import?**

A: **Essential Steps:**
1. **Organize columns** with clear headers (species, latitude, longitude, date, etc.)
2. **Standardize formats** (use decimal degrees for coordinates, ISO dates)
3. **Validate data** (check for errors, missing values, duplicates)
4. **Include metadata** (collector, method, data source information)

See the Data Management guide for detailed preparation instructions.

**Q: What formats are available for data export?**

A: **Export Options:**
- **CSV** - Universal format for spreadsheet applications
- **Excel** - Formatted workbook with multiple sheets
- **GeoJSON** - Geographic data for GIS applications
- **Darwin Core Archive** - Standardized biodiversity data format

Choose the format that best matches your intended use and software requirements.

### Data Sharing and Collaboration

**Q: Can I share my data with other researchers?**

A: Yes! The platform supports various sharing options:
- **Public sharing** for open science initiatives
- **Project-based sharing** with specific research teams
- **Controlled access** with permission management
- **API access** for programmatic data sharing

You maintain control over your data and can set appropriate sharing permissions.

**Q: How do I cite data from CulicidaeLab in my research?**

A: **Platform Citation:**
```
CulicidaeLab Consortium. (2024). CulicidaeLab: A comprehensive platform for mosquito research and surveillance. Available at: [platform URL]. Accessed: [date].
```

**Individual Dataset Citation:**
Include specific dataset information, contributors, and access dates. Many datasets have their own preferred citation formats listed in their metadata.

## Technical Issues

### Common Problems

**Q: The platform is running slowly. What can I do?**

A: **Performance Optimization:**
- **Close unnecessary browser tabs** and applications
- **Clear browser cache** and cookies
- **Use a wired internet connection** when possible
- **Apply filters** to reduce data load on maps and searches
- **Try during off-peak hours** when server load is lower

**Q: My images won't upload. What's wrong?**

A: **Common Upload Issues:**
- **File size too large** (maximum 10MB per image)
- **Unsupported format** (use JPEG, PNG, or WebP)
- **Poor internet connection** (try smaller files or better connection)
- **Browser issues** (clear cache, try different browser)

**Q: I can't see the interactive map. How do I fix this?**

A: **Map Display Issues:**
- **Enable JavaScript** in your browser
- **Update graphics drivers** for WebGL support
- **Try a different browser** (Chrome or Firefox recommended)
- **Disable browser extensions** that might interfere
- **Check firewall settings** that might block map tiles

### Browser and Compatibility

**Q: Which browsers work best with CulicidaeLab?**

A: **Recommended Browsers:**
- **Google Chrome** (version 90+) - best overall performance
- **Mozilla Firefox** (version 88+) - good alternative
- **Safari** (version 14+) - works well on Mac/iOS
- **Microsoft Edge** (version 90+) - good on Windows

**Avoid:** Internet Explorer (not supported) and very old browser versions.

**Q: Can I use CulicidaeLab offline?**

A: The web platform requires internet connectivity for most features. However:
- **Cached pages** may work briefly offline
- **Downloaded data** can be analyzed offline in other software
- **Local deployment** is possible for institutional users
- **Mobile apps** with offline capabilities are under development

## Research and Scientific Use

### Academic and Research Applications

**Q: Can I use CulicidaeLab data in my research publication?**

A: Yes! CulicidaeLab supports open science principles:
- **Data is freely available** for research use
- **Proper attribution** is required (see citation guidelines)
- **Quality assessment** is your responsibility
- **Collaboration opportunities** are available with the development team

**Q: How do I ensure data quality for scientific research?**

A: **Quality Assurance Steps:**
- **Check data sources** and collection methods
- **Verify species identifications** with experts when possible
- **Cross-validate** with other datasets
- **Document limitations** and uncertainties in your analysis
- **Use appropriate statistical methods** for observational data

**Q: Can I contribute my research data to CulicidaeLab?**

A: Absolutely! We welcome high-quality research data:
- **Contact the development team** to discuss data contribution
- **Ensure proper permissions** and ethical approvals
- **Provide complete metadata** and documentation
- **Consider data sharing agreements** for collaborative projects

### Educational Use

**Q: Is CulicidaeLab suitable for teaching?**

A: Yes! The platform is excellent for education:
- **Interactive learning** with real scientific data
- **Species identification practice** with immediate feedback
- **Geographic analysis** of distribution patterns
- **Research skills development** with authentic datasets
- **Collaborative projects** between institutions

**Q: Are there educational resources available?**

A: **Teaching Materials:**
- **User guides and tutorials** for different skill levels
- **Video demonstrations** of key features
- **Example datasets** for classroom exercises
- **Lesson plan suggestions** for different educational levels
- **Training workshops** for educators

## Public Health Applications

### Vector Surveillance

**Q: How can public health agencies use CulicidaeLab?**

A: **Surveillance Applications:**
- **Species identification** for vector control programs
- **Distribution mapping** to identify high-risk areas
- **Data management** for surveillance records
- **Trend analysis** to track population changes
- **Risk assessment** for disease transmission

**Q: Is the platform suitable for operational surveillance?**

A: CulicidaeLab can support surveillance activities, but:
- **Verify critical identifications** with expert taxonomists
- **Validate AI predictions** against known local fauna
- **Maintain quality control** procedures for data entry
- **Consider local regulations** and reporting requirements
- **Integrate with existing systems** as appropriate

### Disease Vector Information

**Q: Does CulicidaeLab provide information about disease transmission?**

A: Yes! The platform includes:
- **Vector competence data** for different species
- **Disease profiles** with transmission information
- **Geographic risk maps** showing vector distributions
- **Prevention strategies** and control recommendations
- **Links to health resources** and expert networks

**Q: How current is the disease information?**

A: Disease information is regularly updated based on:
- **Recent scientific literature** and research findings
- **Public health reports** from agencies like WHO and CDC
- **Expert review** by medical entomologists
- **Community feedback** and corrections

## Privacy and Data Security

### Data Privacy

**Q: What happens to images I upload for identification?**

A: **Image Handling:**
- **Processing only** - images are analyzed but not permanently stored by default
- **Optional contribution** - you can choose to contribute images to improve the AI models
- **No personal information** is extracted from images
- **Secure transmission** using encrypted connections

**Q: Is my personal information protected?**

A: **Privacy Protection:**
- **Minimal data collection** - only necessary information is requested
- **Secure storage** with industry-standard encryption
- **No third-party sharing** without explicit consent
- **User control** over data sharing and deletion
- **Transparent policies** clearly explaining data use

### Data Ownership

**Q: Who owns the data I contribute?**

A: **Data Ownership:**
- **You retain ownership** of your contributed data
- **Usage rights** are granted for platform operation and research
- **Attribution requirements** ensure proper credit for contributions
- **Withdrawal options** allow data removal if needed

**Q: Can I delete my data from the platform?**

A: Yes, you can:
- **Delete individual records** you've contributed
- **Remove your account** and associated data
- **Request data export** before deletion
- **Consider impact** on collaborative projects before removing shared data

## Future Development

### Planned Features

**Q: What new features are being developed?**

A: **Upcoming Enhancements:**
- **Mobile applications** for field data collection
- **Additional species** and geographic coverage
- **Advanced AI models** with improved accuracy
- **Enhanced collaboration tools** for research teams
- **Integration capabilities** with other platforms and databases

**Q: How can I suggest new features or improvements?**

A: **Feedback Channels:**
- **GitHub issues** for technical suggestions and bug reports
- **Community forum** for feature discussions
- **Direct contact** with the development team
- **User surveys** and feedback forms
- **Collaborative development** opportunities for technical users

### Community Involvement

**Q: How can I get involved in CulicidaeLab development?**

A: **Contribution Opportunities:**
- **Data contribution** - share your research datasets
- **Code development** - contribute to open source codebase
- **Documentation** - help improve guides and tutorials
- **Testing** - participate in beta testing of new features
- **Outreach** - help spread awareness in your community

**Q: Is there a user community I can join?**

A: **Community Resources:**
- **Online forum** for discussions and questions
- **Social media groups** for updates and networking
- **Regional meetups** and conferences
- **Collaborative projects** with other users
- **Training workshops** and webinars

## Getting More Help

### Support Options

**Q: What should I do if I can't find the answer to my question?**

A: **Additional Support:**
1. **Search the documentation** - comprehensive guides available
2. **Check the community forum** - other users may have similar questions
3. **Contact support** - email or chat support available
4. **Report issues** - use GitHub for technical problems
5. **Request training** - workshops and consultation available

**Q: How do I report a bug or technical problem?**

A: **Bug Reporting:**
- **GitHub issues** - preferred for technical problems
- **Include details** - browser, operating system, steps to reproduce
- **Provide screenshots** - visual evidence helps diagnosis
- **Check existing reports** - avoid duplicate submissions

### Expert Consultation

**Q: Can I get expert help with species identification?**

A: **Expert Resources:**
- **Academic partnerships** - connections with university entomologists
- **Professional networks** - links to medical entomology experts
- **Consultation services** - paid expert review for critical identifications
- **Training opportunities** - workshops to improve identification skills

**Q: Is training available for institutional users?**

A: **Training Programs:**
- **Online tutorials** - self-paced learning materials
- **Live webinars** - interactive training sessions
- **On-site workshops** - customized training for organizations
- **Certification programs** - proficiency validation for professional use

This FAQ covers the most common questions about CulicidaeLab. For additional help, please consult the detailed user guides or contact our support team.
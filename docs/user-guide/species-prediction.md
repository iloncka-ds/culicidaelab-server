# Species Prediction Guide

Learn how to use CulicidaeLab's AI-powered species identification system to accurately identify mosquito species from photographs.

## Overview

The Species Prediction feature uses state-of-the-art machine learning models to identify mosquito species from uploaded images. The system provides confidence scores, alternative predictions, and detailed species information to help you make accurate identifications.

## Getting Started

### Step 1: Access the Prediction Page

1. Navigate to the **Predict** tab in the main navigation bar
2. You'll see the species prediction interface with an image upload area

### Step 2: Prepare Your Image

For best results, ensure your mosquito image meets these criteria:

**Image Quality Requirements:**
- **Resolution:** Minimum 224x224 pixels (higher resolution preferred)
- **Format:** JPEG, PNG, or WebP
- **File Size:** Maximum 10MB
- **Lighting:** Good, even lighting without harsh shadows
- **Focus:** Sharp focus on the mosquito specimen
- **Background:** Clean, uncluttered background preferred

**Specimen Positioning:**
- **Dorsal View:** Top-down view showing wing patterns and body markings
- **Lateral View:** Side view showing leg patterns and body profile
- **Full Specimen:** Complete mosquito visible in frame
- **Scale:** Mosquito should fill a significant portion of the image

### Step 3: Upload Your Image

1. **Drag and Drop:** Drag your image file directly onto the upload area
2. **File Browser:** Click "Choose File" to browse and select your image
3. **Camera Capture:** Use "Take Photo" to capture directly from your device camera (mobile/tablet)

The system will automatically process your image once uploaded.

## Understanding Prediction Results

### Confidence Scores

Each prediction includes a confidence percentage:

- **90-100%:** Very high confidence - likely accurate identification
- **70-89%:** High confidence - good identification with minor uncertainty
- **50-69%:** Moderate confidence - consider alternative predictions
- **Below 50%:** Low confidence - manual verification recommended

### Result Components

**Primary Prediction:**
- Species name (scientific and common names)
- Confidence percentage
- Thumbnail of reference image

**Alternative Predictions:**
- Up to 5 alternative species suggestions
- Ranked by confidence score
- Useful for verification and comparison

**Species Information:**
- Quick facts about the identified species
- Geographic distribution
- Medical importance
- Link to detailed species profile

## Advanced Features

### Model Selection

Choose from different AI models based on your needs:

**Classification Models:**
- **EfficientNet-B4:** Best overall accuracy for general identification
- **ResNet-50:** Fast processing with good accuracy
- **Vision Transformer:** Excellent for complex specimens

**Detection Models:**
- **YOLOv8:** Locates mosquitoes in complex images
- **Faster R-CNN:** High accuracy detection with bounding boxes

**Segmentation Models:**
- **Mask R-CNN:** Precise outline detection
- **U-Net:** Detailed specimen segmentation

### Batch Processing

Process multiple images simultaneously:

1. Select "Batch Upload" mode
2. Upload up to 20 images at once
3. Review results in a grid layout
4. Export results as CSV or JSON

### API Integration

For programmatic access, use the prediction API:

```python
import requests

# Upload image for prediction
url = "http://localhost:8000/api/v1/predict"
files = {"file": open("mosquito.jpg", "rb")}
response = requests.post(url, files=files)
result = response.json()

print(f"Species: {result['species']}")
print(f"Confidence: {result['confidence']:.2%}")
```

## Step-by-Step Tutorial: Identifying an Aedes aegypti

Let's walk through a complete identification process:

### Step 1: Image Preparation

**Scenario:** You have a mosquito specimen collected during field work and need to identify the species.

**Image Setup:**
- Place specimen on white background
- Use macro lens or close-up mode
- Ensure dorsal view is clearly visible
- Check that wing patterns and leg markings are sharp

### Step 2: Upload and Initial Prediction

1. Navigate to the Predict page
2. Upload your prepared image
3. Wait for processing (typically 2-3 seconds)
4. Review the initial prediction results

**Expected Results:**
- Primary prediction: *Aedes aegypti* (85% confidence)
- Alternative: *Aedes albopictus* (12% confidence)
- Other alternatives with lower confidence

### Step 3: Verify the Identification

**Key Features to Check:**
- **Lyre-shaped markings:** White scales forming lyre pattern on thorax
- **Leg banding:** White bands on legs, especially hind legs
- **Wing scales:** Dark scales with white patches
- **Size:** Medium-sized mosquito (4-7mm)

**Cross-Reference:**
1. Click on the species name to view detailed profile
2. Compare your specimen with reference images
3. Check geographic distribution - is *Aedes aegypti* found in your area?
4. Review morphological characteristics

### Step 4: Confirm or Adjust

**If Confident in Identification:**
- Record the species identification
- Note the confidence score for your records
- Save or export the results

**If Uncertain:**
- Try uploading additional angles of the same specimen
- Compare with alternative predictions
- Consult expert resources or seek professional verification
- Consider environmental context (habitat, season, location)

## Troubleshooting Common Issues

### Low Confidence Scores

**Problem:** All predictions show confidence below 50%

**Solutions:**
1. **Improve Image Quality:**
   - Use better lighting
   - Increase image resolution
   - Ensure sharp focus
   - Clean specimen if possible

2. **Try Different Angles:**
   - Upload dorsal (top) view
   - Include lateral (side) view
   - Capture close-up of diagnostic features

3. **Check Specimen Condition:**
   - Damaged specimens may be harder to identify
   - Missing parts (legs, antennae) affect accuracy
   - Consider if specimen is within model training data

### Unexpected Results

**Problem:** Prediction doesn't match expected species

**Troubleshooting Steps:**
1. **Verify Image Quality:** Ensure specimen is clearly visible
2. **Check Geographic Range:** Is predicted species found in your area?
3. **Review Alternatives:** Look at other high-confidence predictions
4. **Consider Morphological Variation:** Some species show significant variation
5. **Seek Expert Opinion:** Consult with entomologists for difficult cases

### Technical Issues

**Problem:** Upload fails or processing errors

**Solutions:**
1. **File Format:** Ensure image is in supported format (JPEG, PNG, WebP)
2. **File Size:** Reduce file size if over 10MB
3. **Internet Connection:** Check network connectivity
4. **Browser Compatibility:** Try different browser or clear cache
5. **Server Status:** Check if service is temporarily unavailable

## Best Practices

### Field Collection

**Documentation:**
- Record GPS coordinates of collection site
- Note date, time, and weather conditions
- Document habitat type and breeding sites
- Take multiple photos from different angles

**Specimen Handling:**
- Preserve specimens properly for photography
- Use appropriate mounting techniques
- Avoid damage to diagnostic features
- Store specimens in suitable conditions

### Photography Tips

**Equipment:**
- Use macro lens or close-up filters
- Employ ring flash or diffused lighting
- Use tripod for stability
- Consider focus stacking for depth of field

**Technique:**
- Fill frame with specimen
- Ensure even lighting
- Capture multiple angles
- Include scale reference when possible

### Data Management

**Record Keeping:**
- Save prediction results with metadata
- Link predictions to collection records
- Track confidence scores over time
- Note any manual verifications

**Quality Control:**
- Cross-reference with field guides
- Seek expert verification for important identifications
- Maintain database of verified specimens
- Regular calibration with known species

## Integration with Other Features

### Map Visualization

Link your predictions to geographic data:

1. After species identification, click "Add to Map"
2. Enter collection coordinates
3. View your observation on the interactive map
4. Contribute to community surveillance data

### Species Database

Explore detailed species information:

1. Click species name in prediction results
2. Access comprehensive species profile
3. View distribution maps and habitat information
4. Learn about medical importance and control measures

### Disease Information

Understand vector potential:

1. Check if identified species is a disease vector
2. Access disease profiles for relevant pathogens
3. Review prevention and control strategies
4. Understand public health implications

## Frequently Asked Questions

### General Questions

**Q: How accurate are the AI predictions?**
A: Our models achieve >90% accuracy on test datasets, but real-world performance varies based on image quality and specimen condition. Always consider confidence scores and verify important identifications.

**Q: Can I identify larvae or pupae?**
A: Currently, the system is optimized for adult mosquitoes. Larval and pupal identification requires different approaches and is not yet supported.

**Q: What species are included in the database?**
A: The system can identify 46 mosquito species commonly found in research and surveillance contexts. The database focuses on medically important species and common pest species.

### Technical Questions

**Q: Can I use the system offline?**
A: The web interface requires internet connectivity. However, the models can be deployed locally for offline use with appropriate technical setup.

**Q: Is there a mobile app?**
A: The web interface is mobile-responsive and works well on smartphones and tablets. A dedicated mobile app is under consideration for future development.

**Q: Can I contribute training data?**
A: Yes! We welcome high-quality, verified specimens to improve model performance. Contact the development team for contribution guidelines.

### Data and Privacy

**Q: What happens to my uploaded images?**
A: Images are processed for identification but not permanently stored unless you explicitly choose to contribute them to the database. See our privacy policy for details.

**Q: Can I access my prediction history?**
A: Currently, predictions are not stored long-term. We recommend saving important results locally. User accounts with history tracking are planned for future releases.

**Q: Is the service free to use?**
A: Yes, CulicidaeLab is open source and free for research, education, and public health applications.

## Getting Help

### Support Resources

- **Documentation:** Comprehensive guides and API documentation
- **GitHub Issues:** Report bugs and request features
- **Community Forum:** Ask questions and share experiences
- **Email Support:** Direct contact for specific issues

### Expert Consultation

For challenging identifications or research applications:

- **Academic Partnerships:** Collaborate with entomology departments
- **Professional Networks:** Connect with medical entomologists
- **Taxonomic Experts:** Consult with mosquito systematists
- **Public Health Agencies:** Work with vector control professionals

### Training and Workshops

- **Online Tutorials:** Video guides for common workflows
- **Webinars:** Regular training sessions for new users
- **Workshops:** In-person training for research groups
- **Certification:** Proficiency certification for professional use

## Next Steps

After mastering species prediction:

1. **Explore Map Visualization:** Learn to visualize and analyze geographic patterns
2. **Study Disease Information:** Understand vector-pathogen relationships
3. **Contribute Data:** Add your observations to the community database
4. **Advanced Analysis:** Use API for custom applications and research workflows

For technical users:
- **API Documentation:** Complete reference for programmatic access
- **Model Details:** Technical specifications and performance metrics
- **Integration Guides:** Connect with existing research workflows
- **Development:** Contribute to open source development
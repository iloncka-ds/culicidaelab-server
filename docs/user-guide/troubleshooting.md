# Troubleshooting Guide

Comprehensive solutions for common issues and problems encountered while using the CulicidaeLab platform.

## Quick Problem Solver

### Most Common Issues

1. **[Image Upload Problems](#image-upload-issues)** - Files won't upload or process
2. **[Map Not Loading](#map-display-problems)** - Interactive map fails to display
3. **[Slow Performance](#performance-issues)** - Platform responds slowly
4. **[Login/Access Issues](#authentication-problems)** - Can't access features
5. **[Data Import Errors](#data-import-problems)** - Files won't import properly

### Emergency Checklist

Before diving into detailed troubleshooting:

- [ ] **Refresh the page** (Ctrl+F5 or Cmd+Shift+R)
- [ ] **Check internet connection** - Try loading other websites
- [ ] **Clear browser cache** - Remove stored temporary files
- [ ] **Try different browser** - Test with Chrome, Firefox, or Safari
- [ ] **Disable browser extensions** - Turn off ad blockers and other extensions
- [ ] **Check file formats** - Ensure files meet platform requirements

## Browser and System Issues

### Browser Compatibility

**Supported Browsers:**
- **Chrome:** Version 90+ (Recommended)
- **Firefox:** Version 88+
- **Safari:** Version 14+
- **Edge:** Version 90+

**Unsupported Browsers:**
- Internet Explorer (all versions)
- Chrome versions below 90
- Mobile browsers with limited JavaScript support

### Browser Configuration

**Required Settings:**
- **JavaScript:** Must be enabled
- **Cookies:** Allow cookies from the platform domain
- **Local Storage:** Enable local storage for session data
- **WebGL:** Required for map visualization (usually enabled by default)

**Recommended Settings:**
- **Pop-up Blocker:** Allow pop-ups from the platform
- **Download Settings:** Allow automatic downloads for exports
- **Camera/Microphone:** Allow access for image capture features

### Clearing Browser Data

**Chrome:**
1. Press Ctrl+Shift+Delete (Cmd+Shift+Delete on Mac)
2. Select "All time" for time range
3. Check "Cookies and other site data" and "Cached images and files"
4. Click "Clear data"

**Firefox:**
1. Press Ctrl+Shift+Delete (Cmd+Shift+Delete on Mac)
2. Select "Everything" for time range
3. Check "Cookies" and "Cache"
4. Click "Clear Now"

**Safari:**
1. Go to Safari > Preferences > Privacy
2. Click "Manage Website Data"
3. Find the platform domain and click "Remove"
4. Or click "Remove All" for complete clearing

## Image Upload Issues

### File Format Problems

**Supported Formats:**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- TIFF (.tif, .tiff) - Limited support

**Common Format Issues:**
- **HEIC/HEIF:** iPhone photos in HEIC format need conversion
- **RAW Files:** Camera RAW files (.cr2, .nef, .arw) not supported
- **Animated Images:** GIF animations not supported for prediction
- **Corrupted Files:** Damaged image files won't process

**Solutions:**
1. **Convert Format:** Use image editing software to convert to JPEG or PNG
2. **iPhone Users:** Change camera settings to "Most Compatible" format
3. **Check File Integrity:** Try opening image in other applications first

### File Size Limitations

**Size Limits:**
- **Maximum File Size:** 10MB per image
- **Recommended Size:** 1-5MB for optimal performance
- **Minimum Resolution:** 224x224 pixels
- **Maximum Resolution:** 4096x4096 pixels (larger images auto-resized)

**Reducing File Size:**
1. **Resize Image:** Reduce pixel dimensions
2. **Compress JPEG:** Lower quality setting (70-85% recommended)
3. **Crop Image:** Remove unnecessary background areas
4. **Use Online Tools:** TinyPNG, JPEG-Optimizer, or similar services

### Upload Process Issues

**Problem:** Upload starts but fails partway through

**Solutions:**
1. **Check Internet Connection:** Ensure stable, fast connection
2. **Try Smaller Files:** Upload one image at a time
3. **Disable VPN:** VPN connections may cause timeouts
4. **Use Wired Connection:** More stable than WiFi for large uploads

**Problem:** Upload completes but processing fails

**Solutions:**
1. **Check Image Content:** Ensure image contains visible mosquito
2. **Improve Image Quality:** Better lighting and focus
3. **Try Different Angle:** Upload dorsal (top-down) view
4. **Reduce Background Clutter:** Crop to focus on specimen

## Map Display Problems

### Map Won't Load

**Symptoms:**
- Blank gray area where map should appear
- "Map failed to load" error message
- Infinite loading spinner

**Solutions:**
1. **Check WebGL Support:**
   - Visit webglreport.com to test WebGL
   - Update graphics drivers if WebGL fails
   - Try different browser if WebGL unavailable

2. **Network Issues:**
   - Check firewall settings
   - Disable VPN temporarily
   - Try different network connection

3. **Browser Issues:**
   - Clear browser cache and cookies
   - Disable browser extensions
   - Try incognito/private browsing mode

### Map Performance Issues

**Problem:** Map is slow or unresponsive

**Solutions:**
1. **Reduce Data Load:**
   - Apply more restrictive filters
   - Zoom to smaller geographic areas
   - Limit date ranges to recent periods

2. **Browser Optimization:**
   - Close unnecessary browser tabs
   - Restart browser
   - Free up system memory

3. **Graphics Settings:**
   - Update graphics drivers
   - Reduce browser zoom level
   - Disable hardware acceleration if causing issues

### Missing Map Data

**Problem:** Map loads but shows no observation points

**Troubleshooting:**
1. **Check Filters:** Verify filters aren't excluding all data
2. **Zoom Level:** Some data only visible at certain zoom levels
3. **Date Range:** Ensure date filters include periods with data
4. **Geographic Area:** Confirm you're looking at areas with observations

## Performance Issues

### Slow Loading Times

**Common Causes:**
- Large datasets being processed
- Slow internet connection
- Browser performance issues
- Server load during peak times

**Solutions:**
1. **Optimize Filters:**
   - Use more specific species filters
   - Limit geographic scope
   - Reduce date ranges

2. **Browser Optimization:**
   - Close unused tabs and applications
   - Clear browser cache
   - Restart browser periodically

3. **Connection Optimization:**
   - Use wired internet connection
   - Close bandwidth-heavy applications
   - Try during off-peak hours

### Memory Issues

**Symptoms:**
- Browser becomes unresponsive
- "Out of memory" error messages
- Frequent browser crashes

**Solutions:**
1. **Reduce Memory Usage:**
   - Close unnecessary browser tabs
   - Restart browser regularly
   - Use 64-bit browser version

2. **System Optimization:**
   - Close other applications
   - Increase virtual memory
   - Add more RAM if possible

3. **Data Management:**
   - Process smaller datasets
   - Use pagination for large results
   - Export data for offline analysis

## Authentication Problems

### Login Issues

**Problem:** Can't log in or access restricted features

**Solutions:**
1. **Check Credentials:**
   - Verify username/email and password
   - Check for caps lock or typing errors
   - Try password reset if needed

2. **Browser Issues:**
   - Enable cookies and JavaScript
   - Clear browser cache
   - Try different browser

3. **Account Status:**
   - Check email for account verification
   - Ensure account hasn't been suspended
   - Contact support for account issues

### Session Timeouts

**Problem:** Frequently logged out or session expires

**Solutions:**
1. **Browser Settings:**
   - Enable cookies for the platform
   - Don't use private/incognito mode for long sessions
   - Keep browser tab active

2. **Security Settings:**
   - Check if security software is blocking cookies
   - Whitelist the platform domain
   - Disable overly aggressive privacy settings

## Data Import Problems

### File Format Issues

**Problem:** Import file rejected or fails validation

**Solutions:**
1. **Check File Format:**
   - Use CSV format for best compatibility
   - Ensure proper encoding (UTF-8 recommended)
   - Verify column headers match expected format

2. **Data Validation:**
   - Check for required fields (species, coordinates, date)
   - Validate coordinate formats (decimal degrees)
   - Ensure date formats are consistent

3. **File Structure:**
   - Remove empty rows and columns
   - Check for special characters in data
   - Ensure consistent delimiter usage

### Data Quality Errors

**Common Validation Errors:**
- Invalid coordinates (outside valid ranges)
- Unrecognized species names
- Invalid date formats
- Missing required fields

**Solutions:**
1. **Coordinate Issues:**
   - Use decimal degrees format (e.g., 25.7617, -80.1918)
   - Check latitude/longitude aren't swapped
   - Ensure coordinates are within valid ranges

2. **Species Names:**
   - Use full scientific names
   - Check spelling against taxonomic databases
   - Include authority information if available

3. **Date Formats:**
   - Use ISO format (YYYY-MM-DD)
   - Ensure dates are reasonable (not future dates)
   - Check for typos in date fields

## Species Prediction Issues

### Low Confidence Predictions

**Problem:** All predictions show low confidence scores

**Solutions:**
1. **Improve Image Quality:**
   - Use better lighting (natural light preferred)
   - Ensure sharp focus on specimen
   - Remove background clutter
   - Try different angles (dorsal view recommended)

2. **Specimen Preparation:**
   - Clean specimen if possible
   - Position for clear view of diagnostic features
   - Ensure specimen is complete (not damaged)

3. **Technical Factors:**
   - Use higher resolution images
   - Ensure proper file format
   - Check internet connection for upload

### Unexpected Predictions

**Problem:** Prediction doesn't match expected species

**Troubleshooting:**
1. **Verify Image Quality:** Ensure specimen is clearly visible
2. **Check Geographic Range:** Is predicted species found in your area?
3. **Review Alternatives:** Look at other high-confidence predictions
4. **Consider Variation:** Some species show significant morphological variation

### Processing Errors

**Problem:** Image uploads but prediction fails

**Solutions:**
1. **Image Content:** Ensure image contains visible mosquito
2. **File Integrity:** Try re-saving and uploading image
3. **Browser Issues:** Clear cache and try again
4. **Server Load:** Try again during off-peak hours

## Mobile Device Issues

### Touch Interface Problems

**Common Issues:**
- Difficulty with map navigation
- Upload buttons not responding
- Text input problems

**Solutions:**
1. **Browser Choice:** Use Chrome or Safari on mobile
2. **Screen Orientation:** Try both portrait and landscape modes
3. **Touch Sensitivity:** Ensure screen is clean and responsive
4. **Zoom Level:** Adjust browser zoom for better touch targets

### Camera Integration

**Problem:** Can't access device camera for image capture

**Solutions:**
1. **Permissions:** Allow camera access when prompted
2. **Browser Settings:** Check camera permissions in browser settings
3. **App Conflicts:** Close other camera apps
4. **Hardware Issues:** Test camera in other apps

### Performance on Mobile

**Optimization Tips:**
- Close other apps to free memory
- Use WiFi instead of cellular data when possible
- Reduce image sizes before upload
- Use simplified map views for better performance

## Network and Connectivity Issues

### Slow Internet Connection

**Symptoms:**
- Long loading times
- Upload timeouts
- Incomplete data loading

**Solutions:**
1. **Connection Optimization:**
   - Use wired connection when possible
   - Move closer to WiFi router
   - Avoid peak usage times

2. **Data Management:**
   - Upload smaller files
   - Use lower resolution images
   - Process data in smaller batches

### Firewall and Security Software

**Problem:** Platform blocked by security software

**Solutions:**
1. **Whitelist Domain:** Add platform URL to allowed sites
2. **Disable Temporarily:** Turn off security software for testing
3. **Check Corporate Firewall:** Contact IT department for access
4. **VPN Issues:** Try disabling VPN temporarily

## Error Messages and Codes

### Common Error Messages

**"Network Error" or "Connection Failed"**
- Check internet connection
- Try refreshing the page
- Disable VPN or proxy

**"File Too Large"**
- Reduce image file size
- Use image compression tools
- Try uploading smaller batches

**"Invalid File Format"**
- Convert to supported format (JPEG, PNG)
- Check file isn't corrupted
- Ensure proper file extension

**"Processing Failed"**
- Try uploading different image
- Check image contains visible specimen
- Wait and try again (may be temporary server issue)

### HTTP Error Codes

**404 - Not Found**
- Check URL spelling
- Clear browser cache
- Try accessing from main page

**500 - Internal Server Error**
- Temporary server issue
- Try again in a few minutes
- Contact support if persistent

**503 - Service Unavailable**
- Server maintenance in progress
- Check status page for updates
- Try again later

## Getting Additional Help

### Self-Help Resources

**Documentation:**
- User guides and tutorials
- FAQ database
- Video tutorials
- Community forum

**Diagnostic Tools:**
- Browser compatibility checker
- Network speed test
- File format validator
- System requirements checker

### Contact Support

**Before Contacting Support:**
1. Try the solutions in this guide
2. Note exact error messages
3. Record steps to reproduce the problem
4. Check browser and system information

**Support Channels:**
- **Email Support:** Include detailed problem description
- **GitHub Issues:** For bug reports and feature requests
- **Community Forum:** For general questions and discussions
- **Live Chat:** Available during business hours

**Information to Include:**
- Operating system and version
- Browser type and version
- Exact error messages
- Steps to reproduce the problem
- Screenshots if helpful

### Community Resources

**User Forum:**
- Search existing discussions
- Ask questions and share solutions
- Connect with other users
- Share tips and best practices

**Documentation Feedback:**
- Report errors or unclear instructions
- Suggest improvements
- Contribute examples and tutorials
- Help maintain accuracy

## Prevention and Best Practices

### Regular Maintenance

**Browser Maintenance:**
- Clear cache and cookies weekly
- Keep browser updated
- Manage extensions and add-ons
- Regular restart of browser

**System Maintenance:**
- Keep operating system updated
- Maintain adequate free disk space
- Regular antivirus scans
- Monitor system performance

### Data Backup

**Important Data:**
- Export important datasets regularly
- Save prediction results locally
- Backup custom configurations
- Document important workflows

### Optimal Usage Patterns

**Performance Tips:**
- Use platform during off-peak hours
- Process data in reasonable batch sizes
- Close unnecessary applications
- Use recommended browsers and settings

**Quality Practices:**
- Prepare data before import
- Validate results regularly
- Follow naming conventions
- Document procedures and settings

## Frequently Asked Questions

### General Troubleshooting

**Q: Why is the platform running slowly?**
A: Performance can be affected by internet speed, browser performance, dataset size, and server load. Try the optimization steps in the Performance Issues section.

**Q: My browser says the site is not secure. Is it safe?**
A: Ensure you're accessing the correct URL with HTTPS. If you see security warnings, don't enter sensitive information and contact support.

**Q: Can I use the platform on my tablet or phone?**
A: Yes, the platform is mobile-responsive, but some features work better on desktop computers. Use the latest version of Chrome or Safari on mobile devices.

### Technical Issues

**Q: What should I do if I get a "JavaScript error"?**
A: Enable JavaScript in your browser, clear the cache, and try again. If the problem persists, try a different browser.

**Q: Why can't I see the map?**
A: This usually indicates a WebGL or graphics issue. Update your graphics drivers, try a different browser, or check if WebGL is supported at webglreport.com.

**Q: My uploads keep failing. What's wrong?**
A: Check file size (under 10MB), format (JPEG/PNG), and internet connection. Try uploading one file at a time and ensure the image contains a clear mosquito specimen.

### Data and Results

**Q: Why are my prediction results inconsistent?**
A: Prediction accuracy depends on image quality, specimen condition, and species complexity. Use high-quality images and consider confidence scores when interpreting results.

**Q: Can I recover deleted data?**
A: Deleted data cannot be recovered unless you have local backups. Always export important data before making changes.

**Q: Why don't I see any data on the map for my region?**
A: Data availability varies by region based on research and surveillance activities. You can contribute observations to help fill gaps in coverage.

This troubleshooting guide covers the most common issues users encounter. If you can't find a solution here, don't hesitate to contact our support team or check the community forum for additional help.
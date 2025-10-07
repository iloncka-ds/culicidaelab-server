# Documentation Scripts

This directory contains comprehensive automation scripts for building, validating, and maintaining the CulicidaeLab Server documentation with advanced quality assurance features.

## Scripts Overview

### `build_docs.py`
Comprehensive documentation build script that handles the complete build process.

**Usage:**
```bash
# Basic build
python scripts/build_docs.py

# Clean build with link checking
python scripts/build_docs.py --clean

# Build without strict mode
python scripts/build_docs.py --no-strict

# Build and serve locally
python scripts/build_docs.py --serve
```

**Features:**
- Pre-build validation
- Clean build option
- Post-build validation
- Link checking integration
- Performance reporting
- Error handling and recovery

### `validate_docs.py`
Validates documentation content for common issues and standards compliance.

**Usage:**
```bash
# Validate all documentation
python scripts/validate_docs.py
```

**Checks:**
- Markdown syntax validation
- YAML frontmatter validation
- Internal link checking
- Image reference validation
- MkDocs configuration validation
- Common formatting issues

### `check_links.py`
Comprehensive link checker for both internal and external links.

**Usage:**
```bash
# Check all links
python scripts/check_links.py

# Check only internal links
python scripts/check_links.py --no-external

# Custom site directory
python scripts/check_links.py --site-dir custom_site

# Add delay between requests
python scripts/check_links.py --delay 0.5
```

**Features:**
- Internal link validation
- External link checking with rate limiting
- Concurrent processing for performance
- Detailed error reporting
- Support for different site structures

## Integration with Build Tools

### Make Commands
The scripts integrate with the project Makefile:

```bash
# Build documentation
make docs-build

# Validate content
make docs-validate

# Check links
make docs-links

# Full workflow
make docs-full
```

### Pre-commit Hooks
The scripts are integrated with pre-commit hooks for automatic validation:

- `validate-docs`: Runs on markdown file changes
- `check-mkdocs-build`: Validates build on config changes
- `markdownlint`: Lints markdown files

### CI/CD Integration
The scripts are used in GitHub Actions workflows:

- **docs.yml**: Main documentation workflow
- **pages.yml**: GitHub Pages deployment

## Configuration

### Environment Variables
- `MKDOCS_STRICT`: Enable strict mode (default: true)
- `DOCS_CHECK_LINKS`: Enable link checking (default: true)
- `DOCS_EXTERNAL_LINKS`: Check external links (default: false in CI)

### Dependencies
Required Python packages (included in `docs` dependency group):
- `mkdocs` and plugins
- `beautifulsoup4` for HTML parsing
- `requests` for link checking
- `pyyaml` for configuration parsing
- `markdown` for content validation

## Error Handling

### Common Issues and Solutions

**Build Failures:**
- Check mkdocs.yml syntax
- Verify all referenced files exist
- Ensure proper navigation structure

**Link Check Failures:**
- Update broken internal links
- Remove or replace broken external links
- Check for moved or renamed files

**Validation Errors:**
- Fix markdown syntax issues
- Correct YAML frontmatter
- Update image references

### Debugging

Enable verbose output:
```bash
# Verbose build
python scripts/build_docs.py --verbose

# Debug link checking
python scripts/check_links.py --debug
```

Check logs in CI:
- GitHub Actions logs show detailed output
- Pre-commit hooks show validation results
- Local builds show real-time progress

## Development

### Adding New Validations
To add new validation checks:

1. Add check method to `DocumentationValidator` class
2. Call from `validate_all()` method
3. Add appropriate error/warning messages
4. Update tests and documentation

### Extending Link Checking
To extend link checking capabilities:

1. Add new check methods to `LinkChecker` class
2. Update result reporting
3. Add configuration options
4. Test with various link types

### Performance Optimization
Current optimizations:
- Concurrent external link checking
- Caching of validation results
- Incremental builds when possible
- Rate limiting for external requests

## Testing

### Manual Testing
```bash
# Test build process
python scripts/build_docs.py --clean

# Test validation
python scripts/validate_docs.py

# Test link checking
mkdocs build && python scripts/check_links.py
```

### Automated Testing
The scripts are tested through:
- Pre-commit hooks on every commit
- CI/CD pipeline on pull requests
- Nightly builds for comprehensive testing

## Maintenance

### Regular Tasks
- Update dependency versions
- Review and update validation rules
- Monitor build performance
- Update error messages and help text

### Monitoring
- Track build success rates
- Monitor link health over time
- Review validation error patterns
- Analyze build performance metrics
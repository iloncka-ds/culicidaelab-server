# CulicidaeLab Server Documentation

This directory contains the source files for the CulicidaeLab Server documentation built with MkDocs.

## Structure

- `index.md` - Main landing page
- `getting-started/` - Installation and setup guides
- `user-guide/` - End-user documentation
- `developer-guide/` - Technical documentation for developers
- `deployment/` - Production deployment guides
- `research/` - Scientific and research documentation
- `reference/` - API reference and configuration docs
- `stylesheets/` - Custom CSS files
- `javascripts/` - Custom JavaScript files

## Building the Documentation

To build and serve the documentation locally:

```bash
# Install dependencies (will be added in task 2)
pip install mkdocs mkdocs-material

# Serve locally
mkdocs serve

# Build static site
mkdocs build
```

The documentation will be available at `http://localhost:8000` when serving locally.

## Contributing

When adding new documentation:

1. Follow the existing structure and naming conventions
2. Use clear, descriptive headings
3. Include code examples where appropriate
4. Test locally before committing
5. Update navigation in `mkdocs.yml` if adding new pages
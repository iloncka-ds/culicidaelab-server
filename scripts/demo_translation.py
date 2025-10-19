#!/usr/bin/env python3
"""
Demonstration script for the documentation translation system.

This script shows how to use the translation system components.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from markdown_parser import MarkdownParser
from content_translator import ContentTranslator
from metadata_translator import MetadataTranslator
from translation_system import TranslationSystem


def demo_markdown_parsing():
    """Demonstrate markdown parsing capabilities."""
    print("=== Markdown Parsing Demo ===")
    
    sample_content = '''---
title: Getting Started Guide
description: A comprehensive guide to get you started
tags: [guide, tutorial, beginner]
---

# Getting Started

Welcome to our documentation! This guide will help you get started quickly.

## Prerequisites

Before you begin, make sure you have:

- Python 3.8 or higher
- Git installed
- A text editor

## Installation

Run the following command:

```bash
pip install our-package
```

## Configuration

Create a configuration file:

```python
config = {
    "api_key": "your-api-key",
    "debug": True
}
```

That's it! You're ready to go.
'''
    
    parser = MarkdownParser()
    parsed = parser.parse_content(sample_content, "demo.md")
    
    print(f"Frontmatter: {parsed.frontmatter}")
    print(f"Total sections: {len(parsed.sections)}")
    print(f"Code blocks: {len(parsed.code_blocks)}")
    
    translatable_sections = [s for s in parsed.sections if s.is_translatable]
    print(f"Translatable sections: {len(translatable_sections)}")
    
    for i, section in enumerate(translatable_sections[:3]):
        print(f"Section {i+1} ({section.section_type}): {section.content[:50]}...")


def demo_content_translation():
    """Demonstrate content translation capabilities."""
    print("\n=== Content Translation Demo ===")
    
    sample_text = "This is a sample text with `inline code` and a database connection."
    
    translator = ContentTranslator()
    
    # Show technical term translation
    translated = translator._translate_text(sample_text, 'ru')
    print(f"Original: {sample_text}")
    print(f"Translated: {translated}")


def demo_metadata_translation():
    """Demonstrate metadata translation capabilities."""
    print("\n=== Metadata Translation Demo ===")
    
    sample_metadata = {
        'title': 'API Documentation',
        'description': 'Complete guide to our REST API',
        'tags': ['api', 'rest', 'documentation'],
        'author': 'John Doe',
        'date': '2024-01-01'
    }
    
    translator = MetadataTranslator()
    translated_metadata = translator.translate_metadata(sample_metadata, 'ru')
    
    print("Original metadata:")
    for key, value in sample_metadata.items():
        print(f"  {key}: {value}")
    
    print("\nTranslated metadata:")
    for key, value in translated_metadata.items():
        print(f"  {key}: {value}")


def demo_full_system():
    """Demonstrate the complete translation system."""
    print("\n=== Full System Demo ===")
    
    # Create a temporary test file
    test_content = '''---
title: User Guide
description: How to use our application
---

# User Guide

This guide explains how to use the application effectively.

## Database Setup

Configure your database connection:

```python
DATABASE_URL = "postgresql://user:pass@localhost/db"
```

## API Usage

Make requests to our REST API endpoints.
'''
    
    # Write test file
    test_file = "temp_test.md"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        system = TranslationSystem()
        preview = system.get_translation_preview(test_file, 'ru')
        
        print("Translation preview:")
        print(f"  File: {preview['file_path']}")
        print(f"  Translatable sections: {preview['translatable_sections_count']}")
        print(f"  Code blocks: {preview['code_blocks_count']}")
        print(f"  Has frontmatter: {preview['has_frontmatter']}")
        print(f"  Translatable metadata fields: {preview['translatable_metadata_fields']}")
        
        if preview['preview_text_samples']:
            print("  Sample translatable text:")
            for i, sample in enumerate(preview['preview_text_samples'][:2]):
                print(f"    {i+1}: {sample[:60]}...")
    
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)


if __name__ == "__main__":
    print("Documentation Translation System Demo")
    print("=" * 50)
    
    demo_markdown_parsing()
    demo_content_translation()
    demo_metadata_translation()
    demo_full_system()
    
    print("\n" + "=" * 50)
    print("Demo completed successfully!")
    print("\nThe translation system is ready for use.")
    print("Key components:")
    print("- MarkdownParser: Parses markdown files while preserving structure")
    print("- ContentTranslator: Translates content while preserving code and technical terms")
    print("- MetadataTranslator: Handles YAML frontmatter translation")
    print("- TranslationSystem: Integrates all components for complete file translation")
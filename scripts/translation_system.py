"""
Integrated translation system that combines all translation components.

This module provides a unified interface for the complete translation system:
- Markdown parsing
- Content translation
- Metadata translation
- File processing

Requirements: 3.1, 3.2, 3.3
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import os

from markdown_parser import MarkdownParser, ParsedMarkdown
from content_translator import ContentTranslator
from metadata_translator import MetadataTranslator
from translation_utils import TranslationLogger, PathUtils


class TranslationSystem:
    """Integrated translation system for documentation."""
    
    def __init__(self, source_root: str = "docs/en", target_root: str = "docs/ru"):
        """
        Initialize the translation system.
        
        Args:
            source_root: Root directory for source documentation
            target_root: Root directory for target documentation
        """
        self.source_root = Path(source_root)
        self.target_root = Path(target_root)
        
        # Initialize components
        self.parser = MarkdownParser()
        self.content_translator = ContentTranslator()
        self.metadata_translator = MetadataTranslator()
        self.logger = TranslationLogger()
    
    def translate_file(self, source_file: str, target_file: str, 
                      target_language: str = 'ru') -> bool:
        """
        Translate a single markdown file completely.
        
        Args:
            source_file: Path to source file
            target_file: Path to target file
            target_language: Target language code
            
        Returns:
            bool: True if translation was successful
        """
        try:
            # Ensure target directory exists
            target_dir = os.path.dirname(target_file)
            if not PathUtils.ensure_directory_exists(target_dir):
                self.logger.log_file_processed(source_file, False, "Failed to create target directory")
                return False
            
            # Parse the source file
            parsed = self.parser.parse_file(source_file)
            
            # Translate content
            translated_content = self.content_translator.translate_content(parsed, target_language)
            
            # Translate metadata
            if parsed.frontmatter:
                translated_metadata = self.metadata_translator.create_language_specific_metadata(
                    parsed.frontmatter, target_language
                )
                translated_content.frontmatter = translated_metadata
            
            # Reconstruct and save
            final_content = self.content_translator.reconstruct_markdown(translated_content)
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            self.logger.log_file_processed(source_file, True)
            return True
            
        except Exception as e:
            self.logger.log_file_processed(source_file, False, str(e))
            return False
    
    def get_translation_preview(self, source_file: str, 
                               target_language: str = 'ru') -> Dict[str, Any]:
        """
        Get a preview of what would be translated in a file.
        
        Args:
            source_file: Path to source file
            target_language: Target language code
            
        Returns:
            Dict: Translation preview information
        """
        try:
            parsed = self.parser.parse_file(source_file)
            
            # Get content statistics
            content_stats = self.content_translator.get_translation_statistics(parsed)
            
            # Get translatable metadata fields
            translatable_metadata = []
            if parsed.frontmatter:
                translatable_metadata = self.metadata_translator.extract_translatable_metadata_fields(
                    parsed.frontmatter
                )
            
            # Get translatable text sections
            translatable_text = self.parser.get_translatable_text(parsed)
            
            return {
                'file_path': source_file,
                'content_statistics': content_stats,
                'translatable_metadata_fields': translatable_metadata,
                'translatable_sections_count': len([s for s in parsed.sections if s.is_translatable]),
                'code_blocks_count': len(parsed.code_blocks),
                'has_frontmatter': parsed.frontmatter is not None,
                'preview_text_samples': translatable_text[:3] if translatable_text else []  # First 3 samples
            }
            
        except Exception as e:
            return {
                'file_path': source_file,
                'error': str(e),
                'content_statistics': {},
                'translatable_metadata_fields': [],
                'translatable_sections_count': 0,
                'code_blocks_count': 0,
                'has_frontmatter': False,
                'preview_text_samples': []
            }


# Convenience functions
def translate_single_file(source_file: str, target_file: str, 
                         target_language: str = 'ru') -> bool:
    """
    Translate a single file using the integrated system.
    
    Args:
        source_file: Source file path
        target_file: Target file path
        target_language: Target language code
        
    Returns:
        bool: True if successful
    """
    system = TranslationSystem()
    return system.translate_file(source_file, target_file, target_language)


def preview_file_translation(source_file: str, target_language: str = 'ru') -> Dict[str, Any]:
    """
    Preview what would be translated in a file.
    
    Args:
        source_file: Source file path
        target_language: Target language code
        
    Returns:
        Dict: Translation preview
    """
    system = TranslationSystem()
    return system.get_translation_preview(source_file, target_language)
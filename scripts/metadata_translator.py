"""
Metadata translation handler for documentation translation system.

This module provides functionality to:
- Translate appropriate YAML frontmatter fields
- Preserve technical tags and identifiers
- Maintain MkDocs compatibility

Requirements: 3.2, 3.3
"""

import re
import yaml
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass


@dataclass
class MetadataTranslationRule:
    """Rule for translating specific metadata fields."""
    field_name: str
    should_translate: bool
    preserve_structure: bool = True
    custom_handler: Optional[str] = None


class MetadataTranslator:
    """Translator for YAML frontmatter metadata."""
    
    def __init__(self):
        """Initialize the metadata translator."""
        # Define which fields should be translated
        self.translation_rules = {
            # Translatable fields
            'title': MetadataTranslationRule('title', True),
            'description': MetadataTranslationRule('description', True),
            'summary': MetadataTranslationRule('summary', True),
            'excerpt': MetadataTranslationRule('excerpt', True),
            'subtitle': MetadataTranslationRule('subtitle', True),
            'abstract': MetadataTranslationRule('abstract', True),
            
            # Preserve technical fields
            'date': MetadataTranslationRule('date', False),
            'author': MetadataTranslationRule('author', False),
            'authors': MetadataTranslationRule('authors', False),
            'tags': MetadataTranslationRule('tags', False),
            'categories': MetadataTranslationRule('categories', False),
            'slug': MetadataTranslationRule('slug', False),
            'permalink': MetadataTranslationRule('permalink', False),
            'layout': MetadataTranslationRule('layout', False),
            'template': MetadataTranslationRule('template', False),
            'type': MetadataTranslationRule('type', False),
            'status': MetadataTranslationRule('status', False),
            'draft': MetadataTranslationRule('draft', False),
            'published': MetadataTranslationRule('published', False),
            'weight': MetadataTranslationRule('weight', False),
            'order': MetadataTranslationRule('order', False),
            'priority': MetadataTranslationRule('priority', False),
            'featured': MetadataTranslationRule('featured', False),
            'toc': MetadataTranslationRule('toc', False),
            'comments': MetadataTranslationRule('comments', False),
            'share': MetadataTranslationRule('share', False),
            'math': MetadataTranslationRule('math', False),
            'mermaid': MetadataTranslationRule('mermaid', False),
            'highlight': MetadataTranslationRule('highlight', False),
            'code_fold': MetadataTranslationRule('code_fold', False),
            'code_summary': MetadataTranslationRule('code_summary', False),
            
            # MkDocs specific fields
            'nav_title': MetadataTranslationRule('nav_title', True),
            'hide': MetadataTranslationRule('hide', False),
            'search': MetadataTranslationRule('search', False),
            'icon': MetadataTranslationRule('icon', False),
            'logo': MetadataTranslationRule('logo', False),
            'repo_url': MetadataTranslationRule('repo_url', False),
            'repo_name': MetadataTranslationRule('repo_name', False),
            'edit_uri': MetadataTranslationRule('edit_uri', False),
            'site_url': MetadataTranslationRule('site_url', False),
            'site_name': MetadataTranslationRule('site_name', True),
            'site_description': MetadataTranslationRule('site_description', True),
            'copyright': MetadataTranslationRule('copyright', True),
            'theme': MetadataTranslationRule('theme', False),
            'plugins': MetadataTranslationRule('plugins', False),
            'markdown_extensions': MetadataTranslationRule('markdown_extensions', False),
            'extra': MetadataTranslationRule('extra', False),
            'extra_css': MetadataTranslationRule('extra_css', False),
            'extra_javascript': MetadataTranslationRule('extra_javascript', False),
        }
        
        # Technical terms for metadata translation
        self.metadata_technical_terms = {
            'API': 'API',
            'REST': 'REST',
            'HTTP': 'HTTP',
            'JSON': 'JSON',
            'database': 'база данных',
            'server': 'сервер',
            'client': 'клиент',
            'configuration': 'конфигурация',
            'deployment': 'развертывание',
            'development': 'разработка',
            'production': 'продакшн',
            'testing': 'тестирование',
            'documentation': 'документация',
            'guide': 'руководство',
            'tutorial': 'учебник',
            'reference': 'справочник',
            'overview': 'обзор',
            'introduction': 'введение',
            'getting started': 'начало работы',
            'installation': 'установка',
            'setup': 'настройка',
            'quickstart': 'быстрый старт',
            'examples': 'примеры',
            'troubleshooting': 'устранение неполадок',
            'FAQ': 'FAQ',
            'changelog': 'список изменений',
            'release notes': 'примечания к выпуску',
        }
    
    def translate_metadata(self, metadata: Optional[Dict[str, Any]], 
                          target_language: str = 'ru') -> Optional[Dict[str, Any]]:
        """
        Translate YAML frontmatter metadata.
        
        Args:
            metadata: Original metadata dictionary
            target_language: Target language code
            
        Returns:
            Optional[Dict]: Translated metadata dictionary
        """
        if not metadata:
            return metadata
        
        translated_metadata = {}
        
        for key, value in metadata.items():
            rule = self.translation_rules.get(key)
            
            if rule and rule.should_translate:
                # Translate this field
                translated_value = self._translate_metadata_value(value, target_language)
                translated_metadata[key] = translated_value
            else:
                # Preserve this field unchanged
                translated_metadata[key] = value
        
        return translated_metadata    
  
    def _translate_metadata_value(self, value: Any, target_language: str) -> Any:
        """
        Translate a metadata value based on its type.
        
        Args:
            value: Value to translate
            target_language: Target language code
            
        Returns:
            Any: Translated value
        """
        if isinstance(value, str):
            return self._translate_metadata_string(value, target_language)
        elif isinstance(value, list):
            return [self._translate_metadata_value(item, target_language) for item in value]
        elif isinstance(value, dict):
            return {k: self._translate_metadata_value(v, target_language) for k, v in value.items()}
        else:
            # For other types (int, bool, None), return unchanged
            return value
    
    def _translate_metadata_string(self, text: str, target_language: str) -> str:
        """
        Translate a metadata string value.
        
        Args:
            text: String to translate
            target_language: Target language code
            
        Returns:
            str: Translated string
        """
        if not text or not isinstance(text, str):
            return text
        
        translated = text
        
        # Apply technical term translations
        for english_term, russian_term in self.metadata_technical_terms.items():
            # Use case-insensitive replacement
            pattern = re.compile(re.escape(english_term), re.IGNORECASE)
            translated = pattern.sub(russian_term, translated)
        
        # TODO: Integrate with actual translation service
        # For now, add marker for manual translation if needed
        if target_language == 'ru' and self._needs_translation(translated):
            translated = f"[RU_META_TRANSLATION_NEEDED] {translated}"
        
        return translated
    
    def _needs_translation(self, text: str) -> bool:
        """
        Determine if a text needs translation.
        
        Args:
            text: Text to check
            
        Returns:
            bool: True if text needs translation
        """
        # Check if text contains English words that aren't technical terms
        english_words = re.findall(r'\b[a-zA-Z]+\b', text)
        
        if not english_words:
            return False
        
        # Check if all words are technical terms or common abbreviations
        for word in english_words:
            word_lower = word.lower()
            if (word_lower not in [term.lower() for term in self.metadata_technical_terms.keys()] and
                len(word) > 2 and  # Skip very short words
                not word.isupper()):  # Skip all-caps abbreviations
                return True
        
        return False
    
    def validate_mkdocs_compatibility(self, metadata: Dict[str, Any]) -> List[str]:
        """
        Validate that translated metadata maintains MkDocs compatibility.
        
        Args:
            metadata: Metadata dictionary to validate
            
        Returns:
            List[str]: List of validation warnings/errors
        """
        warnings = []
        
        # Check for required MkDocs fields
        if 'title' in metadata and not isinstance(metadata['title'], str):
            warnings.append("Title field should be a string for MkDocs compatibility")
        
        # Check navigation-related fields
        if 'nav_title' in metadata and not isinstance(metadata['nav_title'], str):
            warnings.append("nav_title field should be a string")
        
        # Check boolean fields
        boolean_fields = ['draft', 'published', 'featured', 'toc', 'comments', 'share', 'math', 'mermaid']
        for field in boolean_fields:
            if field in metadata and not isinstance(metadata[field], bool):
                warnings.append(f"{field} field should be a boolean value")
        
        # Check list fields
        list_fields = ['tags', 'categories', 'authors', 'extra_css', 'extra_javascript']
        for field in list_fields:
            if field in metadata and not isinstance(metadata[field], list):
                warnings.append(f"{field} field should be a list")
        
        # Check numeric fields
        numeric_fields = ['weight', 'order', 'priority']
        for field in numeric_fields:
            if field in metadata and not isinstance(metadata[field], (int, float)):
                warnings.append(f"{field} field should be a number")
        
        return warnings
    
    def create_language_specific_metadata(self, original_metadata: Optional[Dict[str, Any]], 
                                        target_language: str = 'ru') -> Optional[Dict[str, Any]]:
        """
        Create language-specific metadata with additional language indicators.
        
        Args:
            original_metadata: Original metadata
            target_language: Target language code
            
        Returns:
            Optional[Dict]: Language-specific metadata
        """
        if not original_metadata:
            return original_metadata
        
        # Start with translated metadata
        translated = self.translate_metadata(original_metadata, target_language)
        
        # Add language-specific fields
        if translated:
            translated['lang'] = target_language
            translated['language'] = target_language
            
            # Add alternate language links if not present
            if 'alternate' not in translated:
                translated['alternate'] = []
            
            # Ensure alternate is a list
            if not isinstance(translated['alternate'], list):
                translated['alternate'] = []
            
            # Add reference to original language
            original_lang_ref = {
                'lang': 'en',
                'name': 'English',
                'link': self._convert_ru_path_to_en(translated.get('canonical_url', ''))
            }
            
            if original_lang_ref not in translated['alternate']:
                translated['alternate'].append(original_lang_ref)
        
        return translated
    
    def _convert_ru_path_to_en(self, ru_path: str) -> str:
        """
        Convert Russian documentation path to English equivalent.
        
        Args:
            ru_path: Russian documentation path
            
        Returns:
            str: English documentation path
        """
        if not ru_path:
            return ru_path
        
        return ru_path.replace('/ru/', '/en/').replace('\\ru\\', '/en/')
    
    def extract_translatable_metadata_fields(self, metadata: Optional[Dict[str, Any]]) -> List[str]:
        """
        Extract list of metadata fields that should be translated.
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            List[str]: Field names that should be translated
        """
        if not metadata:
            return []
        
        translatable_fields = []
        
        for field_name, value in metadata.items():
            rule = self.translation_rules.get(field_name)
            if rule and rule.should_translate and isinstance(value, str) and value.strip():
                translatable_fields.append(field_name)
        
        return translatable_fields
    
    def get_metadata_translation_summary(self, original: Optional[Dict[str, Any]], 
                                       translated: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get summary of metadata translation changes.
        
        Args:
            original: Original metadata
            translated: Translated metadata
            
        Returns:
            Dict: Translation summary
        """
        summary = {
            'total_fields': 0,
            'translated_fields': 0,
            'preserved_fields': 0,
            'added_fields': 0,
            'field_changes': {}
        }
        
        if not original and not translated:
            return summary
        
        original = original or {}
        translated = translated or {}
        
        all_fields = set(original.keys()) | set(translated.keys())
        summary['total_fields'] = len(all_fields)
        
        for field in all_fields:
            original_value = original.get(field)
            translated_value = translated.get(field)
            
            if field not in original:
                summary['added_fields'] += 1
                summary['field_changes'][field] = {'action': 'added', 'value': translated_value}
            elif field not in translated:
                summary['field_changes'][field] = {'action': 'removed', 'original': original_value}
            elif original_value != translated_value:
                summary['translated_fields'] += 1
                summary['field_changes'][field] = {
                    'action': 'translated',
                    'original': original_value,
                    'translated': translated_value
                }
            else:
                summary['preserved_fields'] += 1
                summary['field_changes'][field] = {'action': 'preserved', 'value': original_value}
        
        return summary


# Convenience functions
def translate_frontmatter(metadata: Optional[Dict[str, Any]], 
                         target_language: str = 'ru') -> Optional[Dict[str, Any]]:
    """
    Translate YAML frontmatter using default translator settings.
    
    Args:
        metadata: Original metadata dictionary
        target_language: Target language code
        
    Returns:
        Optional[Dict]: Translated metadata
    """
    translator = MetadataTranslator()
    return translator.translate_metadata(metadata, target_language)


def validate_translated_metadata(metadata: Dict[str, Any]) -> List[str]:
    """
    Validate translated metadata for MkDocs compatibility.
    
    Args:
        metadata: Metadata to validate
        
    Returns:
        List[str]: Validation warnings
    """
    translator = MetadataTranslator()
    return translator.validate_mkdocs_compatibility(metadata)


def create_bilingual_metadata(original_metadata: Optional[Dict[str, Any]], 
                             target_language: str = 'ru') -> Optional[Dict[str, Any]]:
    """
    Create metadata with bilingual support and language indicators.
    
    Args:
        original_metadata: Original metadata
        target_language: Target language code
        
    Returns:
        Optional[Dict]: Bilingual metadata
    """
    translator = MetadataTranslator()
    return translator.create_language_specific_metadata(original_metadata, target_language)
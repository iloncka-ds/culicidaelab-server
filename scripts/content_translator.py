"""
Content translation logic for documentation translation system.

This module provides functionality to:
- Create translation function for text content
- Preserve code blocks, file paths, and technical identifiers
- Maintain markdown formatting and structure
- Handle special markdown elements (tables, lists, links)

Requirements: 3.1, 3.2, 3.3
"""

import re
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from markdown_parser import ParsedMarkdown, MarkdownSection, MarkdownParser


@dataclass
class TranslationRule:
    """Rule for handling specific translation patterns."""
    pattern: str
    replacement: str
    preserve_original: bool = True


@dataclass
class TranslationContext:
    """Context information for translation process."""
    file_path: str
    section_type: str
    preserve_patterns: List[str]
    technical_terms: Dict[str, str]


class ContentTranslator:
    """Translator for markdown content with structure preservation."""
    
    def __init__(self):
        """Initialize the content translator."""
        self.parser = MarkdownParser()
        
        # Technical terms that should be preserved or have consistent translations
        self.technical_terms = {
            # Programming terms
            'API': 'API',
            'REST': 'REST',
            'HTTP': 'HTTP',
            'HTTPS': 'HTTPS',
            'JSON': 'JSON',
            'XML': 'XML',
            'URL': 'URL',
            'URI': 'URI',
            'SQL': 'SQL',
            'HTML': 'HTML',
            'CSS': 'CSS',
            'JavaScript': 'JavaScript',
            'Python': 'Python',
            'Docker': 'Docker',
            'Git': 'Git',
            'GitHub': 'GitHub',
            'CLI': 'CLI',
            'GUI': 'GUI',
            'IDE': 'IDE',
            'SDK': 'SDK',
            'UUID': 'UUID',
            'JWT': 'JWT',
            'OAuth': 'OAuth',
            'CORS': 'CORS',
            'CRUD': 'CRUD',
            'MVC': 'MVC',
            'ORM': 'ORM',
            'TCP': 'TCP',
            'UDP': 'UDP',
            'SSH': 'SSH',
            'SSL': 'SSL',
            'TLS': 'TLS',
            'DNS': 'DNS',
            'CDN': 'CDN',
            'VPN': 'VPN',
            'AWS': 'AWS',
            'Azure': 'Azure',
            'GCP': 'GCP',
            
            # File extensions and formats
            '.py': '.py',
            '.js': '.js',
            '.html': '.html',
            '.css': '.css',
            '.json': '.json',
            '.xml': '.xml',
            '.yml': '.yml',
            '.yaml': '.yaml',
            '.md': '.md',
            '.txt': '.txt',
            '.csv': '.csv',
            '.pdf': '.pdf',
            '.png': '.png',
            '.jpg': '.jpg',
            '.jpeg': '.jpeg',
            '.gif': '.gif',
            '.svg': '.svg',
            
            # Common technical terms with Russian translations
            'database': 'база данных',
            'server': 'сервер',
            'client': 'клиент',
            'endpoint': 'конечная точка',
            'middleware': 'промежуточное ПО',
            'framework': 'фреймворк',
            'library': 'библиотека',
            'module': 'модуль',
            'package': 'пакет',
            'repository': 'репозиторий',
            'branch': 'ветка',
            'commit': 'коммит',
            'merge': 'слияние',
            'pull request': 'запрос на слияние',
            'issue': 'задача',
            'bug': 'ошибка',
            'feature': 'функция',
            'deployment': 'развертывание',
            'configuration': 'конфигурация',
            'environment': 'окружение',
            'production': 'продакшн',
            'development': 'разработка',
            'testing': 'тестирование',
            'staging': 'промежуточная среда',
            'localhost': 'localhost',
            'container': 'контейнер',
            'image': 'образ',
            'volume': 'том',
            'network': 'сеть',
            'port': 'порт',
            'host': 'хост',
            'domain': 'домен',
            'subdomain': 'поддомен',
            'protocol': 'протокол',
            'request': 'запрос',
            'response': 'ответ',
            'header': 'заголовок',
            'body': 'тело',
            'payload': 'полезная нагрузка',
            'authentication': 'аутентификация',
            'authorization': 'авторизация',
            'permission': 'разрешение',
            'role': 'роль',
            'user': 'пользователь',
            'admin': 'администратор',
            'session': 'сессия',
            'token': 'токен',
            'cookie': 'куки',
            'cache': 'кэш',
            'log': 'лог',
            'debug': 'отладка',
            'error': 'ошибка',
            'warning': 'предупреждение',
            'info': 'информация',
            'trace': 'трассировка',
            'exception': 'исключение',
            'timeout': 'таймаут',
            'retry': 'повтор',
            'fallback': 'резервный вариант',
            'backup': 'резервная копия',
            'restore': 'восстановление',
            'migration': 'миграция',
            'schema': 'схема',
            'table': 'таблица',
            'column': 'столбец',
            'row': 'строка',
            'index': 'индекс',
            'query': 'запрос',
            'transaction': 'транзакция',
            'connection': 'соединение',
            'pool': 'пул',
            'thread': 'поток',
            'process': 'процесс',
            'service': 'сервис',
            'microservice': 'микросервис',
            'monolith': 'монолит',
            'scalability': 'масштабируемость',
            'performance': 'производительность',
            'optimization': 'оптимизация',
            'monitoring': 'мониторинг',
            'metrics': 'метрики',
            'analytics': 'аналитика',
            'dashboard': 'панель управления',
            'widget': 'виджет',
            'component': 'компонент',
            'template': 'шаблон',
            'layout': 'макет',
            'theme': 'тема',
            'style': 'стиль',
            'responsive': 'адаптивный',
            'mobile': 'мобильный',
            'desktop': 'настольный',
            'tablet': 'планшет',
            'browser': 'браузер',
            'plugin': 'плагин',
            'extension': 'расширение',
            'addon': 'дополнение',
            'integration': 'интеграция',
            'webhook': 'вебхук',
            'callback': 'обратный вызов',
            'event': 'событие',
            'listener': 'слушатель',
            'handler': 'обработчик',
            'trigger': 'триггер',
            'scheduler': 'планировщик',
            'queue': 'очередь',
            'worker': 'воркер',
            'job': 'задание',
            'task': 'задача',
            'pipeline': 'конвейер',
            'workflow': 'рабочий процесс',
            'automation': 'автоматизация',
            'script': 'скрипт',
            'command': 'команда',
            'argument': 'аргумент',
            'parameter': 'параметр',
            'option': 'опция',
            'flag': 'флаг',
            'variable': 'переменная',
            'constant': 'константа',
            'function': 'функция',
            'method': 'метод',
            'class': 'класс',
            'object': 'объект',
            'instance': 'экземпляр',
            'property': 'свойство',
            'attribute': 'атрибут',
            'field': 'поле',
            'value': 'значение',
            'key': 'ключ',
            'pair': 'пара',
            'array': 'массив',
            'list': 'список',
            'dictionary': 'словарь',
            'map': 'карта',
            'set': 'множество',
            'tuple': 'кортеж',
            'string': 'строка',
            'integer': 'целое число',
            'float': 'число с плавающей точкой',
            'boolean': 'логическое значение',
            'null': 'null',
            'undefined': 'undefined',
            'true': 'true',
            'false': 'false',
        }
        
        # Patterns that should never be translated
        self.preserve_patterns = [
            # URLs and email addresses
            r'https?://[^\s]+',
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            
            # File paths
            r'[a-zA-Z]:[\\\/][^\s]*',  # Windows paths
            r'\/[^\s]*',               # Unix paths
            r'\.[a-zA-Z0-9]+',         # File extensions
            
            # Code-like patterns
            r'`[^`]+`',                # Inline code
            r'\$[a-zA-Z_][a-zA-Z0-9_]*',  # Variables
            r'[a-zA-Z_][a-zA-Z0-9_]*\([^)]*\)',  # Function calls
            r'[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*',  # Object.property
            
            # Version numbers and IDs
            r'\d+\.\d+\.\d+',          # Semantic versions
            r'v\d+\.\d+',              # Version tags
            r'[a-fA-F0-9]{8,}',        # Hex IDs
            
            # Special markdown syntax
            r'\{[^}]+\}',              # Curly braces content
            r'\[[^\]]+\]\([^)]+\)',    # Markdown links
            r'!\[[^\]]*\]\([^)]+\)',   # Markdown images
        ]
    
    def translate_content(self, parsed_markdown: ParsedMarkdown, 
                         target_language: str = 'ru') -> ParsedMarkdown:
        """
        Translate parsed markdown content while preserving structure.
        
        Args:
            parsed_markdown: Parsed markdown structure
            target_language: Target language code (default: 'ru')
            
        Returns:
            ParsedMarkdown: Translated markdown structure
        """
        # Create translation context
        context = TranslationContext(
            file_path=parsed_markdown.file_path,
            section_type='',
            preserve_patterns=self.preserve_patterns,
            technical_terms=self.technical_terms
        )
        
        # Translate sections
        translated_sections = []
        for section in parsed_markdown.sections:
            context.section_type = section.section_type
            translated_section = self._translate_section(section, context, target_language)
            translated_sections.append(translated_section)
        
        # Create new ParsedMarkdown with translated content
        return ParsedMarkdown(
            frontmatter=parsed_markdown.frontmatter,  # Will be handled separately
            sections=translated_sections,
            code_blocks=parsed_markdown.code_blocks,  # Preserved unchanged
            original_content=parsed_markdown.original_content,
            file_path=parsed_markdown.file_path
        )
    
    def _translate_section(self, section: MarkdownSection, 
                          context: TranslationContext, 
                          target_language: str) -> MarkdownSection:
        """
        Translate a single markdown section.
        
        Args:
            section: Section to translate
            context: Translation context
            target_language: Target language code
            
        Returns:
            MarkdownSection: Translated section
        """
        if not section.is_translatable:
            return section
        
        # Preserve inline code and technical elements
        preserved_content, placeholders = self._preserve_technical_content(section.content)
        
        # Translate the content based on section type
        if section.section_type == 'header':
            translated_content = self._translate_header(preserved_content, target_language)
        elif section.section_type == 'list':
            translated_content = self._translate_list(preserved_content, target_language)
        elif section.section_type == 'table':
            translated_content = self._translate_table(preserved_content, target_language)
        else:
            translated_content = self._translate_text(preserved_content, target_language)
        
        # Restore preserved content
        final_content = self._restore_technical_content(translated_content, placeholders)
        
        return MarkdownSection(
            content=final_content,
            section_type=section.section_type,
            line_start=section.line_start,
            line_end=section.line_end,
            is_translatable=section.is_translatable
        )
    
    def _preserve_technical_content(self, content: str) -> Tuple[str, Dict[str, str]]:
        """
        Replace technical content with placeholders for preservation.
        
        Args:
            content: Original content
            
        Returns:
            Tuple of (content with placeholders, placeholder mapping)
        """
        placeholders = {}
        placeholder_counter = 0
        processed_content = content
        
        # Preserve patterns that shouldn't be translated
        for pattern in self.preserve_patterns:
            def replace_match(match):
                nonlocal placeholder_counter
                original = match.group(0)
                placeholder = f"__PRESERVE_{placeholder_counter}__"
                placeholders[placeholder] = original
                placeholder_counter += 1
                return placeholder
            
            processed_content = re.sub(pattern, replace_match, processed_content)
        
        return processed_content, placeholders
    
    def _restore_technical_content(self, content: str, placeholders: Dict[str, str]) -> str:
        """
        Restore technical content from placeholders.
        
        Args:
            content: Content with placeholders
            placeholders: Placeholder mapping
            
        Returns:
            str: Content with restored technical elements
        """
        for placeholder, original in placeholders.items():
            content = content.replace(placeholder, original)
        return content
    
    def _translate_text(self, text: str, target_language: str) -> str:
        """
        Translate plain text content.
        
        Args:
            text: Text to translate
            target_language: Target language code
            
        Returns:
            str: Translated text
        """
        # This is a placeholder for actual translation logic
        # In a real implementation, this would call a translation service
        # For now, we'll apply technical term translations and return
        
        translated = text
        
        # Apply technical term translations
        for english_term, russian_term in self.technical_terms.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(english_term) + r'\b'
            translated = re.sub(pattern, russian_term, translated, flags=re.IGNORECASE)
        
        # TODO: Integrate with actual translation service (Google Translate, DeepL, etc.)
        # For now, add a marker to indicate this needs translation
        if target_language == 'ru' and translated.strip():
            # Only add marker if content has actual text (not just whitespace/punctuation)
            if re.search(r'[a-zA-Z]', translated):
                translated = f"[RU_TRANSLATION_NEEDED] {translated}"
        
        return translated
    
    def _translate_header(self, header: str, target_language: str) -> str:
        """
        Translate markdown header while preserving formatting.
        
        Args:
            header: Header text with markdown formatting
            target_language: Target language code
            
        Returns:
            str: Translated header
        """
        # Extract header level and text
        match = re.match(r'^(#{1,6})\s+(.+)$', header.strip())
        if not match:
            return self._translate_text(header, target_language)
        
        header_level = match.group(1)
        header_text = match.group(2)
        
        # Translate the header text
        translated_text = self._translate_text(header_text, target_language)
        
        return f"{header_level} {translated_text}"
    
    def _translate_list(self, list_content: str, target_language: str) -> str:
        """
        Translate markdown list while preserving formatting.
        
        Args:
            list_content: List content with markdown formatting
            target_language: Target language code
            
        Returns:
            str: Translated list
        """
        lines = list_content.split('\n')
        translated_lines = []
        
        for line in lines:
            # Match list item pattern
            match = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.+)$', line)
            if match:
                indent = match.group(1)
                marker = match.group(2)
                text = match.group(3)
                
                # Translate the list item text
                translated_text = self._translate_text(text, target_language)
                translated_lines.append(f"{indent}{marker} {translated_text}")
            else:
                # Non-list line, translate as regular text
                translated_lines.append(self._translate_text(line, target_language))
        
        return '\n'.join(translated_lines)
    
    def _translate_table(self, table_content: str, target_language: str) -> str:
        """
        Translate markdown table while preserving structure.
        
        Args:
            table_content: Table content with markdown formatting
            target_language: Target language code
            
        Returns:
            str: Translated table
        """
        lines = table_content.split('\n')
        translated_lines = []
        
        for line in lines:
            if re.match(r'^\|.*\|$', line.strip()):
                # This is a table row
                cells = [cell.strip() for cell in line.split('|')[1:-1]]  # Remove empty first/last
                
                # Check if this is a separator row (contains only dashes and spaces)
                if all(re.match(r'^[-\s:]*$', cell) for cell in cells):
                    # Separator row, don't translate
                    translated_lines.append(line)
                else:
                    # Data row, translate each cell
                    translated_cells = []
                    for cell in cells:
                        translated_cell = self._translate_text(cell, target_language)
                        translated_cells.append(translated_cell)
                    
                    translated_line = '| ' + ' | '.join(translated_cells) + ' |'
                    translated_lines.append(translated_line)
            else:
                # Non-table line
                translated_lines.append(self._translate_text(line, target_language))
        
        return '\n'.join(translated_lines)
    
    def reconstruct_markdown(self, parsed: ParsedMarkdown) -> str:
        """
        Reconstruct markdown content from parsed structure.
        
        Args:
            parsed: Parsed markdown structure
            
        Returns:
            str: Reconstructed markdown content
        """
        content_parts = []
        
        # Add frontmatter if present
        if parsed.frontmatter:
            import yaml
            frontmatter_yaml = yaml.dump(parsed.frontmatter, default_flow_style=False, allow_unicode=True)
            content_parts.append(f"---\n{frontmatter_yaml}---\n")
        
        # Add sections
        for section in parsed.sections:
            content_parts.append(section.content)
        
        return '\n'.join(content_parts)
    
    def translate_file(self, input_path: str, output_path: str, 
                      target_language: str = 'ru') -> bool:
        """
        Translate a complete markdown file.
        
        Args:
            input_path: Path to input markdown file
            output_path: Path to output translated file
            target_language: Target language code
            
        Returns:
            bool: True if translation was successful
        """
        try:
            # Parse the input file
            parsed = self.parser.parse_file(input_path)
            
            # Translate the content
            translated = self.translate_content(parsed, target_language)
            
            # Reconstruct the markdown
            translated_content = self.reconstruct_markdown(translated)
            
            # Write to output file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            
            return True
            
        except Exception as e:
            print(f"Error translating file {input_path}: {e}")
            return False
    
    def get_translation_statistics(self, parsed: ParsedMarkdown) -> Dict[str, int]:
        """
        Get statistics about translatable content.
        
        Args:
            parsed: Parsed markdown structure
            
        Returns:
            Dict: Translation statistics
        """
        stats = {
            'total_sections': len(parsed.sections),
            'translatable_sections': 0,
            'code_blocks': len(parsed.code_blocks),
            'headers': 0,
            'lists': 0,
            'tables': 0,
            'text_sections': 0,
            'total_characters': 0,
            'translatable_characters': 0
        }
        
        for section in parsed.sections:
            stats['total_characters'] += len(section.content)
            
            if section.is_translatable:
                stats['translatable_sections'] += 1
                stats['translatable_characters'] += len(section.content)
            
            if section.section_type == 'header':
                stats['headers'] += 1
            elif section.section_type == 'list':
                stats['lists'] += 1
            elif section.section_type == 'table':
                stats['tables'] += 1
            elif section.section_type == 'text':
                stats['text_sections'] += 1
        
        return stats


# Convenience functions
def translate_markdown_file(input_path: str, output_path: str, 
                           target_language: str = 'ru') -> bool:
    """
    Translate a markdown file using default translator settings.
    
    Args:
        input_path: Path to input file
        output_path: Path to output file
        target_language: Target language code
        
    Returns:
        bool: True if successful
    """
    translator = ContentTranslator()
    return translator.translate_file(input_path, output_path, target_language)


def get_file_translation_stats(file_path: str) -> Dict[str, int]:
    """
    Get translation statistics for a markdown file.
    
    Args:
        file_path: Path to markdown file
        
    Returns:
        Dict: Translation statistics
    """
    parser = MarkdownParser()
    translator = ContentTranslator()
    parsed = parser.parse_file(file_path)
    return translator.get_translation_statistics(parsed)
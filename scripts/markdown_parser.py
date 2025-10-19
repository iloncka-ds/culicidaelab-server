"""
Markdown file parser for documentation translation system.

This module provides functionality to:
- Parse markdown files while preserving structure
- Separate YAML frontmatter from content
- Identify and preserve code blocks
- Extract translatable text sections

Requirements: 3.1, 3.2, 3.3
"""

import re
import yaml
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CodeBlock:
    """Represents a code block in markdown content."""
    content: str
    language: Optional[str]
    start_line: int
    end_line: int
    block_type: str  # 'fenced' or 'indented'


@dataclass
class MarkdownSection:
    """Represents a section of markdown content."""
    content: str
    section_type: str  # 'text', 'code', 'table', 'list', 'header'
    line_start: int
    line_end: int
    is_translatable: bool


@dataclass
class ParsedMarkdown:
    """Complete parsed markdown file structure."""
    frontmatter: Optional[Dict[str, Any]]
    sections: List[MarkdownSection]
    code_blocks: List[CodeBlock]
    original_content: str
    file_path: str


class MarkdownParser:
    """Parser for markdown files with translation-aware structure preservation."""
    
    def __init__(self):
        """Initialize the markdown parser."""
        # Regex patterns for markdown elements
        self.fenced_code_pattern = re.compile(
            r'^```(\w+)?\s*\n(.*?)^```\s*$', 
            re.MULTILINE | re.DOTALL
        )
        self.inline_code_pattern = re.compile(r'`([^`]+)`')
        self.header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        self.link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        self.image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
        self.table_pattern = re.compile(r'^\|.*\|$', re.MULTILINE)
        self.list_pattern = re.compile(r'^(\s*)([-*+]|\d+\.)\s+(.+)$', re.MULTILINE)
        
    def parse_file(self, file_path: str) -> ParsedMarkdown:
        """
        Parse a markdown file into structured components.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            ParsedMarkdown: Parsed markdown structure
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            UnicodeDecodeError: If the file can't be decoded as UTF-8
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Markdown file not found: {file_path}")
        except UnicodeDecodeError:
            raise UnicodeDecodeError(f"Unable to decode file as UTF-8: {file_path}")
        
        return self.parse_content(content, file_path)
    
    def parse_content(self, content: str, file_path: str = "") -> ParsedMarkdown:
        """
        Parse markdown content into structured components.
        
        Args:
            content: Raw markdown content
            file_path: Optional file path for reference
            
        Returns:
            ParsedMarkdown: Parsed markdown structure
        """
        # Separate frontmatter from content
        frontmatter, main_content = self._extract_frontmatter(content)
        
        # Extract code blocks first (to preserve them)
        code_blocks = self._extract_code_blocks(main_content)
        
        # Parse content into sections
        sections = self._parse_sections(main_content, code_blocks)
        
        return ParsedMarkdown(
            frontmatter=frontmatter,
            sections=sections,
            code_blocks=code_blocks,
            original_content=content,
            file_path=file_path
        )
    
    def _extract_frontmatter(self, content: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        Extract YAML frontmatter from markdown content.
        
        Args:
            content: Raw markdown content
            
        Returns:
            Tuple of (frontmatter dict, remaining content)
        """
        if not content.startswith('---'):
            return None, content
        
        # Find the end of frontmatter
        lines = content.split('\n')
        end_index = -1
        
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_index = i
                break
        
        if end_index == -1:
            return None, content
        
        # Extract and parse frontmatter
        frontmatter_text = '\n'.join(lines[1:end_index])
        remaining_content = '\n'.join(lines[end_index + 1:])
        
        try:
            frontmatter = yaml.safe_load(frontmatter_text)
            return frontmatter, remaining_content
        except yaml.YAMLError:
            # If YAML parsing fails, treat as regular content
            return None, content
    
    def _extract_code_blocks(self, content: str) -> List[CodeBlock]:
        """
        Extract all code blocks from markdown content.
        
        Args:
            content: Markdown content without frontmatter
            
        Returns:
            List[CodeBlock]: All code blocks found
        """
        code_blocks = []
        lines = content.split('\n')
        
        # Find fenced code blocks
        for match in self.fenced_code_pattern.finditer(content):
            language = match.group(1) if match.group(1) else None
            code_content = match.group(2)
            
            # Calculate line numbers
            start_pos = match.start()
            start_line = content[:start_pos].count('\n')
            end_line = start_line + code_content.count('\n') + 2  # +2 for fence lines
            
            code_blocks.append(CodeBlock(
                content=code_content,
                language=language,
                start_line=start_line,
                end_line=end_line,
                block_type='fenced'
            ))
        
        # Find indented code blocks (4+ spaces)
        in_code_block = False
        code_start = -1
        code_lines = []
        
        for i, line in enumerate(lines):
            is_code_line = line.startswith('    ') and line.strip()
            is_empty_line = not line.strip()
            
            if is_code_line and not in_code_block:
                # Start of indented code block
                in_code_block = True
                code_start = i
                code_lines = [line[4:]]  # Remove 4-space indent
            elif is_code_line and in_code_block:
                # Continue code block
                code_lines.append(line[4:])
            elif is_empty_line and in_code_block:
                # Empty line in code block
                code_lines.append('')
            elif not is_code_line and in_code_block:
                # End of code block
                if code_lines and any(line.strip() for line in code_lines):
                    code_blocks.append(CodeBlock(
                        content='\n'.join(code_lines),
                        language=None,
                        start_line=code_start,
                        end_line=i - 1,
                        block_type='indented'
                    ))
                in_code_block = False
                code_lines = []
        
        # Handle code block at end of file
        if in_code_block and code_lines:
            code_blocks.append(CodeBlock(
                content='\n'.join(code_lines),
                language=None,
                start_line=code_start,
                end_line=len(lines) - 1,
                block_type='indented'
            ))
        
        return code_blocks
    
    def _parse_sections(self, content: str, code_blocks: List[CodeBlock]) -> List[MarkdownSection]:
        """
        Parse markdown content into translatable and non-translatable sections.
        
        Args:
            content: Markdown content without frontmatter
            code_blocks: List of identified code blocks
            
        Returns:
            List[MarkdownSection]: Parsed sections
        """
        sections = []
        lines = content.split('\n')
        
        # Create a map of code block line ranges
        code_line_ranges = set()
        for block in code_blocks:
            for line_num in range(block.start_line, block.end_line + 1):
                code_line_ranges.add(line_num)
        
        current_section = []
        current_type = 'text'
        current_start = 0
        
        for i, line in enumerate(lines):
            # Skip lines that are part of code blocks
            if i in code_line_ranges:
                if current_section:
                    sections.append(self._create_section(
                        current_section, current_type, current_start, i - 1
                    ))
                    current_section = []
                
                # Add code block as non-translatable section
                sections.append(MarkdownSection(
                    content=line,
                    section_type='code',
                    line_start=i,
                    line_end=i,
                    is_translatable=False
                ))
                continue
            
            # Determine section type
            section_type = self._determine_line_type(line)
            
            # If section type changes, finalize current section
            if section_type != current_type and current_section:
                sections.append(self._create_section(
                    current_section, current_type, current_start, i - 1
                ))
                current_section = []
                current_start = i
                current_type = section_type
            
            current_section.append(line)
        
        # Add final section
        if current_section:
            sections.append(self._create_section(
                current_section, current_type, current_start, len(lines) - 1
            ))
        
        return sections
    
    def _determine_line_type(self, line: str) -> str:
        """
        Determine the type of a markdown line.
        
        Args:
            line: Single line of markdown
            
        Returns:
            str: Line type ('header', 'list', 'table', 'text')
        """
        stripped = line.strip()
        
        if not stripped:
            return 'text'
        
        # Check for headers
        if self.header_pattern.match(line):
            return 'header'
        
        # Check for lists
        if self.list_pattern.match(line):
            return 'list'
        
        # Check for tables
        if self.table_pattern.match(line):
            return 'table'
        
        return 'text'
    
    def _create_section(self, lines: List[str], section_type: str, 
                       start_line: int, end_line: int) -> MarkdownSection:
        """
        Create a MarkdownSection from lines.
        
        Args:
            lines: List of lines for this section
            section_type: Type of section
            start_line: Starting line number
            end_line: Ending line number
            
        Returns:
            MarkdownSection: Created section
        """
        content = '\n'.join(lines)
        
        # Determine if section is translatable
        is_translatable = self._is_section_translatable(content, section_type)
        
        return MarkdownSection(
            content=content,
            section_type=section_type,
            line_start=start_line,
            line_end=end_line,
            is_translatable=is_translatable
        )
    
    def _is_section_translatable(self, content: str, section_type: str) -> bool:
        """
        Determine if a section should be translated.
        
        Args:
            content: Section content
            section_type: Type of section
            
        Returns:
            bool: True if section should be translated
        """
        # Code sections are never translatable
        if section_type == 'code':
            return False
        
        # Check for technical identifiers that shouldn't be translated
        technical_patterns = [
            r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=',  # Variable assignments
            r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\(',     # Function calls
            r'^\s*\$[a-zA-Z_]',                  # Shell variables
            r'^\s*https?://',                    # URLs
            r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_]',  # File paths with extensions
        ]
        
        for pattern in technical_patterns:
            if re.search(pattern, content, re.MULTILINE):
                return False
        
        # Check if content is mostly code-like (high ratio of special characters)
        if len(content.strip()) > 0:
            special_chars = sum(1 for c in content if c in '{}[]()=<>|&;')
            ratio = special_chars / len(content.strip())
            if ratio > 0.3:  # More than 30% special characters
                return False
        
        return True
    
    def get_translatable_text(self, parsed: ParsedMarkdown) -> List[str]:
        """
        Extract all translatable text from parsed markdown.
        
        Args:
            parsed: Parsed markdown structure
            
        Returns:
            List[str]: All translatable text sections
        """
        translatable_texts = []
        
        for section in parsed.sections:
            if section.is_translatable and section.content.strip():
                translatable_texts.append(section.content)
        
        return translatable_texts
    
    def preserve_inline_code(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Replace inline code with placeholders to preserve during translation.
        
        Args:
            text: Text containing inline code
            
        Returns:
            Tuple of (text with placeholders, placeholder mapping)
        """
        placeholders = {}
        placeholder_counter = 0
        
        def replace_code(match):
            nonlocal placeholder_counter
            code_content = match.group(1)
            placeholder = f"__INLINE_CODE_{placeholder_counter}__"
            placeholders[placeholder] = f"`{code_content}`"
            placeholder_counter += 1
            return placeholder
        
        processed_text = self.inline_code_pattern.sub(replace_code, text)
        return processed_text, placeholders
    
    def restore_inline_code(self, text: str, placeholders: Dict[str, str]) -> str:
        """
        Restore inline code from placeholders after translation.
        
        Args:
            text: Translated text with placeholders
            placeholders: Mapping of placeholders to original code
            
        Returns:
            str: Text with restored inline code
        """
        for placeholder, original_code in placeholders.items():
            text = text.replace(placeholder, original_code)
        return text


# Convenience functions
def parse_markdown_file(file_path: str) -> ParsedMarkdown:
    """
    Parse a markdown file using default parser settings.
    
    Args:
        file_path: Path to markdown file
        
    Returns:
        ParsedMarkdown: Parsed markdown structure
    """
    parser = MarkdownParser()
    return parser.parse_file(file_path)


def extract_translatable_content(file_path: str) -> List[str]:
    """
    Extract only translatable content from a markdown file.
    
    Args:
        file_path: Path to markdown file
        
    Returns:
        List[str]: Translatable text sections
    """
    parser = MarkdownParser()
    parsed = parser.parse_file(file_path)
    return parser.get_translatable_text(parsed)
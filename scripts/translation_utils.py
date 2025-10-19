"""
Translation utilities for documentation translation system.

This module provides core utilities for:
- Directory structure scanning
- File path manipulation
- Logging and progress tracking

Requirements: 2.1, 2.2
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DirectoryMapping:
    """Data structure for directory mapping between source and target."""
    en_path: str
    ru_path: str
    files: List[str]
    subdirectories: List['DirectoryMapping']
    creation_status: str = "pending"


@dataclass
class TranslationFile:
    """Data structure for individual file translation tracking."""
    source_path: str
    target_path: str
    content_type: str
    translation_status: str = "pending"


class DirectoryScanner:
    """Utility class for scanning and mapping directory structures."""
    
    def __init__(self, source_root: str = "docs/en", target_root: str = "docs/ru"):
        """
        Initialize directory scanner.
        
        Args:
            source_root: Root directory for English documentation
            target_root: Root directory for Russian documentation
        """
        self.source_root = Path(source_root)
        self.target_root = Path(target_root)
    
    def scan_directory_structure(self) -> DirectoryMapping:
        """
        Recursively scan the source directory structure.
        
        Returns:
            DirectoryMapping: Complete mapping of source to target structure
        """
        return self._scan_recursive(self.source_root, self.target_root)
    
    def _scan_recursive(self, source_dir: Path, target_dir: Path) -> DirectoryMapping:
        """
        Recursively scan directory and create mapping.
        
        Args:
            source_dir: Source directory path
            target_dir: Target directory path
            
        Returns:
            DirectoryMapping: Mapping for this directory level
        """
        files = []
        subdirectories = []
        
        if not source_dir.exists():
            return DirectoryMapping(
                en_path=str(source_dir),
                ru_path=str(target_dir),
                files=[],
                subdirectories=[]
            )
        
        for item in source_dir.iterdir():
            if item.is_file():
                # Only include markdown files for translation
                if item.suffix.lower() == '.md':
                    files.append(item.name)
            elif item.is_dir():
                # Recursively scan subdirectories
                sub_target = target_dir / item.name
                sub_mapping = self._scan_recursive(item, sub_target)
                subdirectories.append(sub_mapping)
        
        return DirectoryMapping(
            en_path=str(source_dir),
            ru_path=str(target_dir),
            files=files,
            subdirectories=subdirectories
        )
    
    def get_all_markdown_files(self, mapping: DirectoryMapping) -> List[TranslationFile]:
        """
        Extract all markdown files from directory mapping.
        
        Args:
            mapping: Directory mapping structure
            
        Returns:
            List[TranslationFile]: All markdown files for translation
        """
        files = []
        
        # Add files from current directory
        for filename in mapping.files:
            source_path = os.path.join(mapping.en_path, filename)
            target_path = os.path.join(mapping.ru_path, filename)
            files.append(TranslationFile(
                source_path=source_path,
                target_path=target_path,
                content_type="markdown"
            ))
        
        # Recursively add files from subdirectories
        for subdir in mapping.subdirectories:
            files.extend(self.get_all_markdown_files(subdir))
        
        return files


class PathUtils:
    """Utility class for file path manipulation operations."""
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """
        Normalize file path for cross-platform compatibility.
        
        Args:
            path: File path to normalize
            
        Returns:
            str: Normalized path
        """
        return os.path.normpath(path).replace('\\', '/')
    
    @staticmethod
    def get_relative_path(file_path: str, base_path: str) -> str:
        """
        Get relative path from base path to file path.
        
        Args:
            file_path: Target file path
            base_path: Base directory path
            
        Returns:
            str: Relative path
        """
        return os.path.relpath(file_path, base_path).replace('\\', '/')
    
    @staticmethod
    def ensure_directory_exists(directory_path: str) -> bool:
        """
        Ensure directory exists, create if necessary.
        
        Args:
            directory_path: Directory path to create
            
        Returns:
            bool: True if directory exists or was created successfully
        """
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logging.error(f"Failed to create directory {directory_path}: {e}")
            return False
    
    @staticmethod
    def convert_en_path_to_ru(en_path: str) -> str:
        """
        Convert English documentation path to Russian equivalent.
        
        Args:
            en_path: English documentation path
            
        Returns:
            str: Corresponding Russian documentation path
        """
        return en_path.replace('docs/en', 'docs/ru').replace('docs\\en', 'docs/ru')
    
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """
        Get file extension from file path.
        
        Args:
            file_path: File path
            
        Returns:
            str: File extension (including dot)
        """
        return Path(file_path).suffix


class TranslationLogger:
    """Logging and progress tracking utility for translation operations."""
    
    def __init__(self, log_file: str = "translation.log", log_level: int = logging.INFO):
        """
        Initialize translation logger.
        
        Args:
            log_file: Log file path
            log_level: Logging level
        """
        self.log_file = log_file
        self.start_time = datetime.now()
        self.processed_files = 0
        self.total_files = 0
        self.errors = []
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log_start(self, total_files: int):
        """
        Log translation process start.
        
        Args:
            total_files: Total number of files to process
        """
        self.total_files = total_files
        self.start_time = datetime.now()
        self.logger.info(f"Starting translation process for {total_files} files")
    
    def log_file_processed(self, file_path: str, success: bool = True, error_msg: str = None):
        """
        Log individual file processing result.
        
        Args:
            file_path: Path of processed file
            success: Whether processing was successful
            error_msg: Error message if processing failed
        """
        self.processed_files += 1
        
        if success:
            self.logger.info(f"Processed ({self.processed_files}/{self.total_files}): {file_path}")
        else:
            error_info = f"Failed to process {file_path}: {error_msg}"
            self.errors.append(error_info)
            self.logger.error(error_info)
    
    def log_directory_created(self, directory_path: str, success: bool = True, error_msg: str = None):
        """
        Log directory creation result.
        
        Args:
            directory_path: Path of created directory
            success: Whether creation was successful
            error_msg: Error message if creation failed
        """
        if success:
            self.logger.info(f"Created directory: {directory_path}")
        else:
            error_info = f"Failed to create directory {directory_path}: {error_msg}"
            self.errors.append(error_info)
            self.logger.error(error_info)
    
    def get_progress_percentage(self) -> float:
        """
        Get current progress percentage.
        
        Returns:
            float: Progress percentage (0-100)
        """
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100
    
    def get_elapsed_time(self) -> str:
        """
        Get elapsed time since process start.
        
        Returns:
            str: Formatted elapsed time
        """
        elapsed = datetime.now() - self.start_time
        return str(elapsed).split('.')[0]  # Remove microseconds
    
    def log_completion(self):
        """Log translation process completion with summary."""
        elapsed_time = self.get_elapsed_time()
        success_count = self.processed_files - len(self.errors)
        
        self.logger.info(f"Translation process completed in {elapsed_time}")
        self.logger.info(f"Successfully processed: {success_count}/{self.total_files} files")
        
        if self.errors:
            self.logger.warning(f"Encountered {len(self.errors)} errors:")
            for error in self.errors:
                self.logger.warning(f"  - {error}")
        else:
            self.logger.info("All files processed successfully!")
    
    def get_summary(self) -> Dict[str, any]:
        """
        Get translation process summary.
        
        Returns:
            Dict: Summary information
        """
        return {
            "total_files": self.total_files,
            "processed_files": self.processed_files,
            "successful_files": self.processed_files - len(self.errors),
            "errors": len(self.errors),
            "progress_percentage": self.get_progress_percentage(),
            "elapsed_time": self.get_elapsed_time(),
            "error_details": self.errors
        }


# Convenience functions for common operations
def scan_docs_structure() -> DirectoryMapping:
    """
    Scan the default documentation structure.
    
    Returns:
        DirectoryMapping: Complete documentation structure mapping
    """
    scanner = DirectoryScanner()
    return scanner.scan_directory_structure()


def get_all_translation_files() -> List[TranslationFile]:
    """
    Get all markdown files that need translation.
    
    Returns:
        List[TranslationFile]: All files for translation
    """
    scanner = DirectoryScanner()
    mapping = scanner.scan_directory_structure()
    return scanner.get_all_markdown_files(mapping)


def setup_translation_logging(log_file: str = "translation.log") -> TranslationLogger:
    """
    Set up translation logging with default configuration.
    
    Args:
        log_file: Log file path
        
    Returns:
        TranslationLogger: Configured logger instance
    """
    return TranslationLogger(log_file)
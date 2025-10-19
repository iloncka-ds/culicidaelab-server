#!/usr/bin/env python3
"""
Directory scanner for docs/en structure.

This module provides functionality to recursively scan the docs/en directory
and generate directory mapping data structures for translation purposes.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DirectoryScanner:
    """Scanner for documentation directory structure."""
    
    def __init__(self, source_root: str = "docs/en"):
        """
        Initialize the directory scanner.
        
        Args:
            source_root: Root directory to scan (default: docs/en)
        """
        self.source_root = Path(source_root)
        if not self.source_root.exists():
            raise FileNotFoundError(f"Source directory {source_root} does not exist")
    
    def scan_directory_structure(self) -> Dict[str, Any]:
        """
        Recursively scan the source directory and generate mapping structure.
        
        Returns:
            Dictionary containing complete directory mapping with files and subdirectories
        """
        logger.info(f"Starting directory scan of {self.source_root}")
        
        mapping = self._scan_recursive(self.source_root)
        
        logger.info(f"Directory scan completed. Found {self._count_files(mapping)} files")
        return mapping
    
    def _scan_recursive(self, directory: Path) -> Dict[str, Any]:
        """
        Recursively scan a directory and return its structure.
        
        Args:
            directory: Directory path to scan
            
        Returns:
            Dictionary containing directory structure information
        """
        structure = {
            "path": str(directory),
            "relative_path": str(directory.relative_to(self.source_root.parent)),
            "name": directory.name,
            "files": [],
            "subdirectories": [],
            "is_directory": True
        }
        
        try:
            # Get all items in the directory
            items = list(directory.iterdir())
            
            # Separate files and directories
            for item in sorted(items):
                if item.is_file():
                    file_info = {
                        "path": str(item),
                        "relative_path": str(item.relative_to(self.source_root.parent)),
                        "name": item.name,
                        "extension": item.suffix,
                        "is_directory": False
                    }
                    structure["files"].append(file_info)
                    logger.debug(f"Found file: {item.relative_to(self.source_root.parent)}")
                
                elif item.is_dir():
                    # Recursively scan subdirectory
                    subdir_structure = self._scan_recursive(item)
                    structure["subdirectories"].append(subdir_structure)
                    logger.debug(f"Found directory: {item.relative_to(self.source_root.parent)}")
        
        except PermissionError as e:
            logger.warning(f"Permission denied accessing {directory}: {e}")
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {e}")
        
        return structure
    
    def _count_files(self, structure: Dict[str, Any]) -> int:
        """
        Count total number of files in the structure.
        
        Args:
            structure: Directory structure dictionary
            
        Returns:
            Total number of files
        """
        count = len(structure.get("files", []))
        
        for subdir in structure.get("subdirectories", []):
            count += self._count_files(subdir)
        
        return count
    
    def get_file_list(self, structure: Dict[str, Any] = None) -> List[Dict[str, str]]:
        """
        Get a flat list of all files in the directory structure.
        
        Args:
            structure: Directory structure (if None, will scan first)
            
        Returns:
            List of file information dictionaries
        """
        if structure is None:
            structure = self.scan_directory_structure()
        
        files = []
        
        # Add files from current directory
        for file_info in structure.get("files", []):
            files.append(file_info)
        
        # Recursively add files from subdirectories
        for subdir in structure.get("subdirectories", []):
            files.extend(self.get_file_list(subdir))
        
        return files
    
    def get_directory_list(self, structure: Dict[str, Any] = None) -> List[Dict[str, str]]:
        """
        Get a flat list of all directories in the structure.
        
        Args:
            structure: Directory structure (if None, will scan first)
            
        Returns:
            List of directory information dictionaries
        """
        if structure is None:
            structure = self.scan_directory_structure()
        
        directories = [structure]  # Include root directory
        
        # Recursively add subdirectories
        for subdir in structure.get("subdirectories", []):
            directories.extend(self.get_directory_list(subdir))
        
        return directories


class DirectoryReplicator:
    """Creates Russian directory structure based on English structure."""
    
    def __init__(self, source_root: str = "docs/en", target_root: str = "docs/ru"):
        """
        Initialize the directory replicator.
        
        Args:
            source_root: Source directory to replicate from
            target_root: Target directory to create structure in
        """
        self.source_root = Path(source_root)
        self.target_root = Path(target_root)
        
        if not self.source_root.exists():
            raise FileNotFoundError(f"Source directory {source_root} does not exist")
    
    def create_directory_structure(self, structure: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create the Russian directory structure based on English structure.
        
        Args:
            structure: Directory structure dictionary (if None, will scan source first)
            
        Returns:
            Dictionary containing creation results and status
        """
        if structure is None:
            scanner = DirectoryScanner(str(self.source_root))
            structure = scanner.scan_directory_structure()
        
        logger.info(f"Creating Russian directory structure at {self.target_root}")
        
        results = {
            "target_root": str(self.target_root),
            "created_directories": [],
            "failed_directories": [],
            "total_directories": 0,
            "success_count": 0,
            "error_count": 0
        }
        
        # Create the target root directory if it doesn't exist
        try:
            self.target_root.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created target root directory: {self.target_root}")
        except Exception as e:
            logger.error(f"Failed to create target root directory {self.target_root}: {e}")
            results["failed_directories"].append({
                "path": str(self.target_root),
                "error": str(e)
            })
            return results
        
        # Recursively create directory structure
        self._create_directories_recursive(structure, results)
        
        logger.info(f"Directory creation completed. Success: {results['success_count']}, Failed: {results['error_count']}")
        return results
    
    def _create_directories_recursive(self, structure: Dict[str, Any], results: Dict[str, Any]):
        """
        Recursively create directories based on structure.
        
        Args:
            structure: Directory structure dictionary
            results: Results dictionary to update
        """
        # Convert source path to target path
        source_path = Path(structure["path"])
        relative_to_source_root = source_path.relative_to(self.source_root)
        target_path = self.target_root / relative_to_source_root
        
        results["total_directories"] += 1
        
        try:
            # Create the directory
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Set permissions to match source directory (if possible)
            try:
                source_stat = source_path.stat()
                os.chmod(target_path, source_stat.st_mode)
            except (OSError, AttributeError):
                # Permission setting might not work on all systems, continue anyway
                pass
            
            results["created_directories"].append({
                "source_path": str(source_path),
                "target_path": str(target_path),
                "relative_path": str(relative_to_source_root)
            })
            results["success_count"] += 1
            
            logger.debug(f"Created directory: {target_path}")
            
        except Exception as e:
            logger.error(f"Failed to create directory {target_path}: {e}")
            results["failed_directories"].append({
                "source_path": str(source_path),
                "target_path": str(target_path),
                "relative_path": str(relative_to_source_root),
                "error": str(e)
            })
            results["error_count"] += 1
        
        # Recursively create subdirectories
        for subdir in structure.get("subdirectories", []):
            self._create_directories_recursive(subdir, results)
    
    def verify_structure(self, structure: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Verify that the Russian directory structure matches the English structure.
        
        Args:
            structure: Directory structure dictionary (if None, will scan source first)
            
        Returns:
            Dictionary containing verification results
        """
        if structure is None:
            scanner = DirectoryScanner(str(self.source_root))
            structure = scanner.scan_directory_structure()
        
        logger.info("Verifying Russian directory structure")
        
        verification = {
            "verified_directories": [],
            "missing_directories": [],
            "total_expected": 0,
            "verified_count": 0,
            "missing_count": 0
        }
        
        self._verify_directories_recursive(structure, verification)
        
        logger.info(f"Verification completed. Verified: {verification['verified_count']}, Missing: {verification['missing_count']}")
        return verification
    
    def _verify_directories_recursive(self, structure: Dict[str, Any], verification: Dict[str, Any]):
        """
        Recursively verify directories exist.
        
        Args:
            structure: Directory structure dictionary
            verification: Verification results dictionary to update
        """
        # Convert source path to target path
        source_path = Path(structure["path"])
        relative_to_source_root = source_path.relative_to(self.source_root)
        target_path = self.target_root / relative_to_source_root
        
        verification["total_expected"] += 1
        
        if target_path.exists() and target_path.is_dir():
            verification["verified_directories"].append({
                "source_path": str(source_path),
                "target_path": str(target_path),
                "relative_path": str(relative_to_source_root)
            })
            verification["verified_count"] += 1
            logger.debug(f"Verified directory exists: {target_path}")
        else:
            verification["missing_directories"].append({
                "source_path": str(source_path),
                "target_path": str(target_path),
                "relative_path": str(relative_to_source_root)
            })
            verification["missing_count"] += 1
            logger.warning(f"Missing directory: {target_path}")
        
        # Recursively verify subdirectories
        for subdir in structure.get("subdirectories", []):
            self._verify_directories_recursive(subdir, verification)


def main():
    """Main function for testing the directory scanner and replicator."""
    try:
        # Test directory scanner
        print("=== Testing Directory Scanner ===")
        scanner = DirectoryScanner()
        structure = scanner.scan_directory_structure()
        
        print("Directory Structure:")
        print(f"Root: {structure['path']}")
        print(f"Total files: {scanner._count_files(structure)}")
        print(f"Total directories: {len(scanner.get_directory_list(structure))}")
        
        # Print directory tree
        print("\nDirectory Tree:")
        _print_tree(structure, indent="")
        
        # Test directory replicator
        print("\n=== Testing Directory Replicator ===")
        replicator = DirectoryReplicator()
        
        # Create Russian directory structure
        creation_results = replicator.create_directory_structure(structure)
        print(f"\nCreation Results:")
        print(f"Target root: {creation_results['target_root']}")
        print(f"Total directories: {creation_results['total_directories']}")
        print(f"Successfully created: {creation_results['success_count']}")
        print(f"Failed to create: {creation_results['error_count']}")
        
        if creation_results['failed_directories']:
            print("\nFailed directories:")
            for failed in creation_results['failed_directories']:
                print(f"  {failed['relative_path']}: {failed['error']}")
        
        # Verify the structure
        verification_results = replicator.verify_structure(structure)
        print(f"\nVerification Results:")
        print(f"Total expected: {verification_results['total_expected']}")
        print(f"Verified: {verification_results['verified_count']}")
        print(f"Missing: {verification_results['missing_count']}")
        
        if verification_results['missing_directories']:
            print("\nMissing directories:")
            for missing in verification_results['missing_directories']:
                print(f"  {missing['relative_path']}")
        
        # Show created structure
        if Path("docs/ru").exists():
            print("\n=== Created Russian Directory Structure ===")
            ru_scanner = DirectoryScanner("docs/ru")
            ru_structure = ru_scanner.scan_directory_structure()
            _print_tree(ru_structure, indent="")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        return 1
    
    return 0


def _print_tree(structure: Dict[str, Any], indent: str = ""):
    """Helper function to print directory tree structure."""
    print(f"{indent}{structure['name']}/")
    
    # Print files
    for file_info in structure.get("files", []):
        print(f"{indent}  {file_info['name']}")
    
    # Print subdirectories
    for subdir in structure.get("subdirectories", []):
        _print_tree(subdir, indent + "  ")


if __name__ == "__main__":
    exit(main())
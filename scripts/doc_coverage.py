#!/usr/bin/env python3
"""
Documentation coverage analysis script.

This script analyzes documentation coverage by comparing:
- API endpoints vs documented endpoints
- Code modules vs documented modules
- Configuration options vs documented options
"""

import os
import sys
import ast
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
import yaml


@dataclass
class APIEndpoint:
    """Represents an API endpoint."""
    path: str
    method: str
    function_name: str
    module: str
    documented: bool = False
    doc_location: Optional[str] = None


@dataclass
class CodeModule:
    """Represents a code module."""
    name: str
    path: str
    functions: List[str]
    classes: List[str]
    documented: bool = False
    doc_location: Optional[str] = None


@dataclass
class CoverageReport:
    """Complete coverage report."""
    api_coverage: float
    module_coverage: float
    overall_coverage: float
    total_endpoints: int
    documented_endpoints: int
    total_modules: int
    documented_modules: int
    missing_api_docs: List[str]
    missing_module_docs: List[str]
    suggestions: List[str]


class DocumentationCoverageAnalyzer:
    """Analyzes documentation coverage for the project."""
    
    def __init__(self, 
                 backend_dir: str = "backend",
                 docs_dir: str = "docs",
                 frontend_dir: str = "frontend"):
        self.backend_dir = Path(backend_dir)
        self.docs_dir = Path(docs_dir)
        self.frontend_dir = Path(frontend_dir)
        
        self.api_endpoints: List[APIEndpoint] = []
        self.code_modules: List[CodeModule] = []
        self.documented_apis: Set[str] = set()
        self.documented_modules: Set[str] = set()
    
    def analyze_coverage(self) -> CoverageReport:
        """Perform complete coverage analysis."""
        print("📊 Analyzing documentation coverage...")
        
        # Discover API endpoints
        self._discover_api_endpoints()
        
        # Discover code modules
        self._discover_code_modules()
        
        # Find documented APIs and modules
        self._find_documented_items()
        
        # Calculate coverage
        return self._calculate_coverage()
    
    def _discover_api_endpoints(self):
        """Discover API endpoints from FastAPI routers."""
        print("🔍 Discovering API endpoints...")
        
        if not self.backend_dir.exists():
            print(f"⚠️  Backend directory '{self.backend_dir}' not found")
            return
        
        # Look for router files
        router_files = list(self.backend_dir.rglob("*router*.py"))
        router_files.extend(list(self.backend_dir.rglob("*routes*.py"))
        
        for router_file in router_files:
            self._parse_router_file(router_file)
    
    def _parse_router_file(self, file_path: Path):
        """Parse a router file to extract API endpoints."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Look for FastAPI decorators
                    for decorator in node.decorator_list:
                        if self._is_fastapi_decorator(decorator):
                            endpoint = self._extract_endpoint_info(
                                node, decorator, file_path
                            )
                            if endpoint:
                                self.api_endpoints.append(endpoint)
                                
        except Exception as e:
            print(f"⚠️  Error parsing {file_path}: {e}")
    
    def _is_fastapi_decorator(self, decorator) -> bool:
        """Check if a decorator is a FastAPI route decorator."""
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute):
                # router.get, router.post, etc.
                return decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch']
            elif isinstance(decorator.func, ast.Name):
                # @get, @post, etc. (if imported directly)
                return decorator.func.id in ['get', 'post', 'put', 'delete', 'patch']
        return False
    
    def _extract_endpoint_info(self, 
                              func_node: ast.FunctionDef, 
                              decorator: ast.Call, 
                              file_path: Path) -> Optional[APIEndpoint]:
        """Extract endpoint information from function and decorator."""
        try:
            # Get HTTP method
            if isinstance(decorator.func, ast.Attribute):
                method = decorator.func.attr.upper()
            elif isinstance(decorator.func, ast.Name):
                method = decorator.func.id.upper()
            else:
                return None
            
            # Get path from decorator arguments
            path = "/"
            if decorator.args:
                if isinstance(decorator.args[0], ast.Constant):
                    path = decorator.args[0].value
                elif isinstance(decorator.args[0], ast.Str):  # Python < 3.8
                    path = decorator.args[0].s
            
            return APIEndpoint(
                path=path,
                method=method,
                function_name=func_node.name,
                module=str(file_path.relative_to(self.backend_dir))
            )
            
        except Exception as e:
            print(f"⚠️  Error extracting endpoint info: {e}")
            return None
    
    def _discover_code_modules(self):
        """Discover code modules that should be documented."""
        print("🔍 Discovering code modules...")
        
        # Backend modules
        if self.backend_dir.exists():
            self._scan_python_modules(self.backend_dir, "backend")
        
        # Frontend modules
        if self.frontend_dir.exists():
            self._scan_python_modules(self.frontend_dir, "frontend")
    
    def _scan_python_modules(self, directory: Path, prefix: str):
        """Scan Python modules in a directory."""
        for py_file in directory.rglob("*.py"):
            # Skip __pycache__, tests, and private files
            if any(part.startswith('__pycache__') or part.startswith('.') 
                   for part in py_file.parts):
                continue
            
            if 'test' in py_file.name.lower():
                continue
            
            module = self._analyze_python_module(py_file)
            if module:
                self.code_modules.append(module)
    
    def _analyze_python_module(self, file_path: Path) -> Optional[CodeModule]:
        """Analyze a Python module to extract functions and classes."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Skip private functions
                    if not node.name.startswith('_'):
                        functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    # Skip private classes
                    if not node.name.startswith('_'):
                        classes.append(node.name)
            
            # Only include modules with public functions or classes
            if functions or classes:
                return CodeModule(
                    name=file_path.stem,
                    path=str(file_path),
                    functions=functions,
                    classes=classes
                )
            
        except Exception as e:
            print(f"⚠️  Error analyzing {file_path}: {e}")
        
        return None
    
    def _find_documented_items(self):
        """Find which APIs and modules are documented."""
        print("📚 Finding documented items...")
        
        if not self.docs_dir.exists():
            print(f"⚠️  Documentation directory '{self.docs_dir}' not found")
            return
        
        # Scan documentation files
        for doc_file in self.docs_dir.rglob("*.md"):
            self._scan_doc_file(doc_file)
    
    def _scan_doc_file(self, doc_file: Path):
        """Scan a documentation file for API and module references."""
        try:
            content = doc_file.read_text(encoding='utf-8')
            
            # Look for API endpoint references
            for endpoint in self.api_endpoints:
                # Check for path references
                if endpoint.path in content:
                    endpoint.documented = True
                    endpoint.doc_location = str(doc_file.relative_to(self.docs_dir))
                    self.documented_apis.add(f"{endpoint.method} {endpoint.path}")
                
                # Check for function name references
                if endpoint.function_name in content:
                    endpoint.documented = True
                    endpoint.doc_location = str(doc_file.relative_to(self.docs_dir))
            
            # Look for module references
            for module in self.code_modules:
                # Check for module name or class/function references
                if (module.name in content or 
                    any(func in content for func in module.functions) or
                    any(cls in content for cls in module.classes)):
                    module.documented = True
                    module.doc_location = str(doc_file.relative_to(self.docs_dir))
                    self.documented_modules.add(module.name)
                    
        except Exception as e:
            print(f"⚠️  Error scanning {doc_file}: {e}")
    
    def _calculate_coverage(self) -> CoverageReport:
        """Calculate coverage statistics."""
        print("📈 Calculating coverage...")
        
        # API coverage
        total_endpoints = len(self.api_endpoints)
        documented_endpoints = len([ep for ep in self.api_endpoints if ep.documented])
        api_coverage = (documented_endpoints / total_endpoints * 100) if total_endpoints > 0 else 100
        
        # Module coverage
        total_modules = len(self.code_modules)
        documented_modules = len([mod for mod in self.code_modules if mod.documented])
        module_coverage = (documented_modules / total_modules * 100) if total_modules > 0 else 100
        
        # Overall coverage
        overall_coverage = (api_coverage + module_coverage) / 2
        
        # Missing documentation
        missing_api_docs = [
            f"{ep.method} {ep.path} ({ep.function_name})"
            for ep in self.api_endpoints if not ep.documented
        ]
        
        missing_module_docs = [
            f"{mod.name} ({mod.path})"
            for mod in self.code_modules if not mod.documented
        ]
        
        # Generate suggestions
        suggestions = self._generate_suggestions(missing_api_docs, missing_module_docs)
        
        return CoverageReport(
            api_coverage=api_coverage,
            module_coverage=module_coverage,
            overall_coverage=overall_coverage,
            total_endpoints=total_endpoints,
            documented_endpoints=documented_endpoints,
            total_modules=total_modules,
            documented_modules=documented_modules,
            missing_api_docs=missing_api_docs,
            missing_module_docs=missing_module_docs,
            suggestions=suggestions
        )
    
    def _generate_suggestions(self, 
                            missing_apis: List[str], 
                            missing_modules: List[str]) -> List[str]:
        """Generate suggestions for improving documentation coverage."""
        suggestions = []
        
        if missing_apis:
            suggestions.append(
                f"Add API documentation for {len(missing_apis)} endpoints in docs/reference/api/"
            )
            
        if missing_modules:
            suggestions.append(
                f"Add module documentation for {len(missing_modules)} modules in docs/developer-guide/"
            )
        
        if len(missing_apis) > 5:
            suggestions.append(
                "Consider using automated API documentation generation with mkdocstrings"
            )
        
        if len(missing_modules) > 10:
            suggestions.append(
                "Consider adding docstrings to modules and using automated documentation"
            )
        
        return suggestions
    
    def generate_report(self, output_file: Optional[str] = None) -> CoverageReport:
        """Generate and optionally save coverage report."""
        report = self.analyze_coverage()
        
        # Print report
        self._print_report(report)
        
        # Save to file if requested
        if output_file:
            self._save_report(report, output_file)
        
        return report
    
    def _print_report(self, report: CoverageReport):
        """Print coverage report to console."""
        print("\n" + "="*60)
        print("📊 DOCUMENTATION COVERAGE REPORT")
        print("="*60)
        
        print(f"\n📈 Overall Coverage: {report.overall_coverage:.1f}%")
        print(f"🔌 API Coverage: {report.api_coverage:.1f}% ({report.documented_endpoints}/{report.total_endpoints})")
        print(f"📦 Module Coverage: {report.module_coverage:.1f}% ({report.documented_modules}/{report.total_modules})")
        
        if report.missing_api_docs:
            print(f"\n❌ Missing API Documentation ({len(report.missing_api_docs)}):")
            for api in report.missing_api_docs[:10]:  # Show first 10
                print(f"  • {api}")
            if len(report.missing_api_docs) > 10:
                print(f"  ... and {len(report.missing_api_docs) - 10} more")
        
        if report.missing_module_docs:
            print(f"\n❌ Missing Module Documentation ({len(report.missing_module_docs)}):")
            for module in report.missing_module_docs[:10]:  # Show first 10
                print(f"  • {module}")
            if len(report.missing_module_docs) > 10:
                print(f"  ... and {len(report.missing_module_docs) - 10} more")
        
        if report.suggestions:
            print(f"\n💡 Suggestions:")
            for suggestion in report.suggestions:
                print(f"  • {suggestion}")
        
        print("\n" + "="*60)
    
    def _save_report(self, report: CoverageReport, output_file: str):
        """Save coverage report to JSON file."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(report), f, indent=2, ensure_ascii=False)
            print(f"📋 Coverage report saved to: {output_file}")
        except Exception as e:
            print(f"⚠️  Error saving report: {e}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze documentation coverage")
    parser.add_argument("--backend-dir", default="backend", help="Backend directory path")
    parser.add_argument("--frontend-dir", default="frontend", help="Frontend directory path")
    parser.add_argument("--docs-dir", default="docs", help="Documentation directory path")
    parser.add_argument("--output", help="Output file for JSON report")
    parser.add_argument("--min-coverage", type=float, default=70.0, 
                       help="Minimum coverage threshold")
    
    args = parser.parse_args()
    
    analyzer = DocumentationCoverageAnalyzer(
        backend_dir=args.backend_dir,
        docs_dir=args.docs_dir,
        frontend_dir=args.frontend_dir
    )
    
    report = analyzer.generate_report(args.output)
    
    # Exit with error if coverage is below threshold
    if report.overall_coverage < args.min_coverage:
        print(f"\n❌ Coverage {report.overall_coverage:.1f}% is below threshold {args.min_coverage}%")
        sys.exit(1)
    else:
        print(f"\n✅ Coverage {report.overall_coverage:.1f}% meets threshold {args.min_coverage}%")
        sys.exit(0)


if __name__ == "__main__":
    main()
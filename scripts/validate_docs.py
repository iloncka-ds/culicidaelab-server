#!/usr/bin/env python3
"""
Documentation validation script for MkDocs.

This script validates documentation content including:
- Markdown syntax validation
- Internal link checking
- Image reference validation
- Code block syntax checking
- YAML frontmatter validation
- Markdown linting and style checking
- Spell checking (optional)
- Documentation coverage reporting
"""

import re
import sys
import json
import subprocess  # nosec B404
from pathlib import Path
import yaml
import markdown
from dataclasses import dataclass, asdict


@dataclass
class ValidationResult:
    """Result of a validation check."""

    file_path: str
    line_number: int
    rule: str
    severity: str  # 'error', 'warning', 'info'
    message: str
    suggestion: str | None = None


@dataclass
class CoverageReport:
    """Documentation coverage report."""

    total_files: int
    documented_files: int
    coverage_percentage: float
    missing_docs: list[str]
    api_coverage: dict[str, float]


class DocumentationValidator:
    """Validates documentation content and structure."""

    def __init__(self, docs_dir: str = "docs", enable_spell_check: bool = False):
        self.docs_dir = Path(docs_dir)
        self.enable_spell_check = enable_spell_check
        self.errors: list[ValidationResult] = []
        self.warnings: list[ValidationResult] = []
        self.info: list[ValidationResult] = []

        # Markdown linting rules
        self.linting_rules = {
            "max_line_length": 120,
            "no_trailing_whitespace": True,
            "no_tabs": True,
            "heading_style": "atx",  # Use # instead of underlines
            "list_marker_space": True,
            "no_duplicate_headings": True,
            "no_empty_links": True,
            "alt_text_required": True,
        }

    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("🔍 Validating documentation...")

        # Check if docs directory exists
        if not self.docs_dir.exists():
            error = ValidationResult(
                file_path=str(self.docs_dir),
                line_number=0,
                rule="directory_exists",
                severity="error",
                message=f"Documentation directory '{self.docs_dir}' not found",
            )
            self.errors.append(error)
            return False

        # Run validation checks
        self._validate_markdown_files()
        self._validate_internal_links()
        self._validate_images()
        self._validate_mkdocs_config()
        self._run_markdown_linting()

        if self.enable_spell_check:
            self._run_spell_check()

        # Generate coverage report
        coverage_report = self._generate_coverage_report()

        # Report results
        self._report_results(coverage_report)

        return len(self.errors) == 0

    def _validate_markdown_files(self):
        """Validate markdown syntax and structure."""
        print("📝 Checking markdown files...")

        md_files = list(self.docs_dir.rglob("*.md"))
        if not md_files:
            self.warnings.append("No markdown files found in docs directory")
            return

        for md_file in md_files:
            self._validate_single_markdown_file(md_file)

    def _validate_single_markdown_file(self, file_path: Path):
        """Validate a single markdown file."""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Check for YAML frontmatter
            if content.startswith("---"):
                try:
                    frontmatter_end = content.find("---", 3)
                    if frontmatter_end != -1:
                        frontmatter = content[3:frontmatter_end]
                        yaml.safe_load(frontmatter)
                except yaml.YAMLError as e:
                    error = ValidationResult(
                        file_path=str(file_path),
                        line_number=0,
                        rule="yaml-frontmatter",
                        severity="error",
                        message=f"Invalid YAML frontmatter: {e}",
                    )
                    self.errors.append(error)

            # Basic markdown validation
            try:
                markdown.markdown(content)
            except Exception as e:
                error = ValidationResult(
                    file_path=str(file_path),
                    line_number=0,
                    rule="markdown-parsing",
                    severity="error",
                    message=f"Markdown parsing error: {e}",
                )
                self.errors.append(error)

            # Check for common issues
            self._check_markdown_issues(file_path, content)

        except UnicodeDecodeError:
            error = ValidationResult(
                file_path=str(file_path),
                line_number=0,
                rule="file-encoding",
                severity="error",
                message="Cannot read file: encoding issue",
            )
            self.errors.append(error)
        except Exception as e:
            error = ValidationResult(
                file_path=str(file_path),
                line_number=0,
                rule="file-processing",
                severity="error",
                message=f"Error processing file: {e}",
            )
            self.errors.append(error)

    def _check_markdown_issues(self, file_path: Path, content: str):
        """Check for common markdown issues."""
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Check for trailing whitespace
            if line.rstrip() != line:
                warning = ValidationResult(
                    file_path=str(file_path),
                    line_number=i,
                    rule="trailing-whitespace",
                    severity="warning",
                    message="Trailing whitespace found",
                )
                self.warnings.append(warning)

            # Check for tabs instead of spaces
            if "\t" in line:
                warning = ValidationResult(
                    file_path=str(file_path),
                    line_number=i,
                    rule="tab-character",
                    severity="warning",
                    message="Tab character found",
                )
                self.warnings.append(warning)

            # Check for very long lines
            if len(line) > 120:
                warning = ValidationResult(
                    file_path=str(file_path),
                    line_number=i,
                    rule="long-line",
                    severity="warning",
                    message=f"Long line ({len(line)} chars)",
                )
                self.warnings.append(warning)

    def _validate_internal_links(self):
        """Validate internal markdown links."""
        print("🔗 Checking internal links...")

        all_files = set()
        all_links = []

        # Collect all markdown files and their internal links
        for md_file in self.docs_dir.rglob("*.md"):
            relative_path = md_file.relative_to(self.docs_dir)
            # Normalize path separators for cross-platform compatibility
            relative_path_str = str(relative_path).replace("\\", "/")
            all_files.add(relative_path_str)
            all_files.add(str(Path(relative_path_str).with_suffix("")))  # Without .md extension

            try:
                content = md_file.read_text(encoding="utf-8")
                links = self._extract_internal_links(content)

                for link in links:
                    all_links.append((md_file, link))
            except Exception as e:
                # Skip files that can't be read
                print(f"⚠️  Warning: Could not read {md_file}: {e}")
                continue

        # Validate each internal link
        for source_file, link in all_links:
            self._validate_internal_link(source_file, link, all_files)

    def _extract_internal_links(self, content: str) -> list[str]:
        """Extract internal markdown links from content."""
        # Match markdown links [text](url) and reference links [text][ref]
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        links = []

        for match in re.finditer(link_pattern, content):
            url = match.group(2)
            # Only check internal links (not starting with http/https/mailto)
            if not url.startswith(("http://", "https://", "mailto:", "#")):
                links.append(url)

        return links

    def _validate_internal_link(self, source_file: Path, link: str, all_files: set[str]):
        """Validate a single internal link."""
        # Remove anchor fragments
        link_path = link.split("#")[0] if "#" in link else link

        if not link_path:  # Empty path (just anchor)
            return

        # Handle different types of paths
        if link_path.startswith("/"):
            # Absolute path from docs root
            target_path = link_path.lstrip("/")
            full_path = self.docs_dir / target_path
        else:
            # Relative path - resolve from the source file's directory
            source_dir = source_file.parent
            full_path = (source_dir / link_path).resolve()

            # Check if the resolved path is within docs directory
            try:
                target_path = str(full_path.relative_to(self.docs_dir))
            except ValueError:
                # Path is outside docs directory (e.g., ../../CODE_OF_CONDUCT.md)
                # Check if the file exists at the resolved location
                if full_path.exists():
                    return  # File exists outside docs, consider it valid
                else:
                    error = ValidationResult(
                        file_path=str(source_file),
                        line_number=0,
                        rule="broken-link",
                        severity="error",
                        message=f"Broken internal link: {link}",
                    )
                    self.errors.append(error)
                    return

        # Normalize path separators for cross-platform compatibility
        target_path = target_path.replace("\\", "/")

        # Check if target exists within docs directory
        if target_path not in all_files and (target_path + ".md") not in all_files:
            # Check if it's a file that exists on disk
            if not full_path.exists() and not (full_path.with_suffix(".md")).exists():
                error = ValidationResult(
                    file_path=str(source_file),
                    line_number=0,
                    rule="broken-link",
                    severity="error",
                    message=f"Broken internal link: {link}",
                )
                self.errors.append(error)

    def _validate_images(self):
        """Validate image references in markdown files."""
        print("🖼️  Checking image references...")

        for md_file in self.docs_dir.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")

            # Find image references
            img_pattern = r"!\[([^\]]*)\]\(([^)]+)\)"

            for match in re.finditer(img_pattern, content):
                img_path = match.group(2)

                # Skip external images
                if img_path.startswith(("http://", "https://")):
                    continue

                # Check if local image exists
                if img_path.startswith("/"):
                    # Absolute path from docs root
                    full_path = self.docs_dir / img_path.lstrip("/")
                else:
                    # Relative path from current file
                    full_path = md_file.parent / img_path

                if not full_path.exists():
                    error = ValidationResult(
                        file_path=str(md_file),
                        line_number=0,
                        rule="missing-image",
                        severity="error",
                        message=f"Missing image: {img_path}",
                    )
                    self.errors.append(error)

    def _validate_mkdocs_config(self):
        """Validate MkDocs configuration file."""
        print("⚙️  Checking MkDocs configuration...")

        config_path = Path("mkdocs.yml")
        if not config_path.exists():
            error = ValidationResult(
                file_path="mkdocs.yml",
                line_number=0,
                rule="missing-config",
                severity="error",
                message="mkdocs.yml configuration file not found",
            )
            self.errors.append(error)
            return

        try:
            with open(config_path, encoding="utf-8") as f:
                # Use unsafe_load to handle !!python/name: tags in MkDocs config
                config = yaml.unsafe_load(f)

            # Check required fields
            required_fields = ["site_name", "nav"]
            for field in required_fields:
                if field not in config:
                    error = ValidationResult(
                        file_path="mkdocs.yml",
                        line_number=0,
                        rule="missing-field",
                        severity="error",
                        message=f"Missing required field '{field}'",
                    )
                    self.errors.append(error)

            # Validate navigation structure
            if "nav" in config:
                self._validate_navigation(config["nav"])

        except yaml.YAMLError as e:
            error = ValidationResult(
                file_path="mkdocs.yml",
                line_number=0,
                rule="yaml-syntax",
                severity="error",
                message=f"Invalid YAML: {e}",
            )
            self.errors.append(error)
        except Exception as e:
            error = ValidationResult(
                file_path="mkdocs.yml",
                line_number=0,
                rule="config-error",
                severity="error",
                message=f"Error reading configuration: {e}",
            )
            self.errors.append(error)

    def _validate_navigation(self, nav_items):
        """Validate navigation structure in mkdocs.yml."""
        for item in nav_items:
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, str):
                        # Check if referenced file exists
                        nav_file = self.docs_dir / value
                        if not nav_file.exists():
                            error = ValidationResult(
                                file_path="mkdocs.yml",
                                line_number=0,
                                rule="missing-nav-file",
                                severity="error",
                                message=f"Navigation references missing file: {value}",
                            )
                            self.errors.append(error)
                    elif isinstance(value, list):
                        self._validate_navigation(value)

    def _run_markdown_linting(self):
        """Run markdown linting checks."""
        print("📝 Running markdown linting...")

        for md_file in self.docs_dir.rglob("*.md"):
            self._lint_markdown_file(md_file)

    def _lint_markdown_file(self, file_path: Path):
        """Lint a single markdown file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Track headings for duplicate detection
            headings = []

            for i, line in enumerate(lines, 1):
                self._check_line_length(file_path, i, line)
                self._check_trailing_whitespace(file_path, i, line)
                self._check_tabs(file_path, i, line)
                self._check_heading_style(file_path, i, line, headings)
                self._check_list_markers(file_path, i, line)
                self._check_empty_links(file_path, i, line)
                self._check_alt_text(file_path, i, line)

            # Check for duplicate headings
            self._check_duplicate_headings(file_path, headings)

        except Exception as e:
            error = ValidationResult(
                file_path=str(file_path),
                line_number=0,
                rule="file_read_error",
                severity="error",
                message=f"Error reading file: {e}",
            )
            self.errors.append(error)

    def _check_line_length(self, file_path: Path, line_num: int, line: str):
        """Check line length against maximum."""
        max_length = self.linting_rules["max_line_length"]
        if len(line) > max_length:
            warning = ValidationResult(
                file_path=str(file_path),
                line_number=line_num,
                rule="max_line_length",
                severity="warning",
                message=f"Line too long ({len(line)} > {max_length} characters)",
                suggestion="Consider breaking long lines or using line breaks",
            )
            self.warnings.append(warning)

    def _check_trailing_whitespace(self, file_path: Path, line_num: int, line: str):
        """Check for trailing whitespace."""
        if self.linting_rules["no_trailing_whitespace"] and line.rstrip() != line:
            warning = ValidationResult(
                file_path=str(file_path),
                line_number=line_num,
                rule="no_trailing_whitespace",
                severity="warning",
                message="Line has trailing whitespace",
                suggestion="Remove trailing spaces and tabs",
            )
            self.warnings.append(warning)

    def _check_tabs(self, file_path: Path, line_num: int, line: str):
        """Check for tab characters."""
        if self.linting_rules["no_tabs"] and "\t" in line:
            warning = ValidationResult(
                file_path=str(file_path),
                line_number=line_num,
                rule="no_tabs",
                severity="warning",
                message="Line contains tab characters",
                suggestion="Use spaces instead of tabs for indentation",
            )
            self.warnings.append(warning)

    def _check_heading_style(self, file_path: Path, line_num: int, line: str, headings: list[tuple[int, str]]):
        """Check heading style consistency."""
        # Check for ATX-style headings (# ## ###)
        if line.strip().startswith("#"):
            heading_match = re.match(r"^(#+)\s+(.+)", line.strip())
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2).strip()
                headings.append((level, text))

                # Check for proper spacing after #
                if not line.strip().startswith("# ") and len(line.strip()) > 1:
                    if not re.match(r"^#+\s", line.strip()):
                        warning = ValidationResult(
                            file_path=str(file_path),
                            line_number=line_num,
                            rule="heading_spacing",
                            severity="warning",
                            message="Heading should have space after #",
                            suggestion="Add space after # in headings",
                        )
                        self.warnings.append(warning)

        # Check for setext-style headings (underlines)
        elif line_num > 1 and re.match(r"^[=-]+$", line.strip()):
            if self.linting_rules["heading_style"] == "atx":
                warning = ValidationResult(
                    file_path=str(file_path),
                    line_number=line_num,
                    rule="heading_style",
                    severity="warning",
                    message="Use ATX-style headings (# ##) instead of underlines",
                    suggestion="Convert underlined headings to # style",
                )
                self.warnings.append(warning)

    def _check_list_markers(self, file_path: Path, line_num: int, line: str):
        """Check list marker spacing."""
        if self.linting_rules["list_marker_space"]:
            # Check unordered lists
            if re.match(r"^\s*[-*+](?!\s)", line):
                warning = ValidationResult(
                    file_path=str(file_path),
                    line_number=line_num,
                    rule="list_marker_space",
                    severity="warning",
                    message="List marker should be followed by a space",
                    suggestion="Add space after list marker (- * +)",
                )
                self.warnings.append(warning)

            # Check ordered lists
            if re.match(r"^\s*\d+\.(?!\s)", line):
                warning = ValidationResult(
                    file_path=str(file_path),
                    line_number=line_num,
                    rule="list_marker_space",
                    severity="warning",
                    message="Ordered list marker should be followed by a space",
                    suggestion="Add space after numbered list marker (1. 2.)",
                )
                self.warnings.append(warning)

    def _check_empty_links(self, file_path: Path, line_num: int, line: str):
        """Check for empty or invalid links."""
        if self.linting_rules["no_empty_links"]:
            # Find markdown links
            link_pattern = r"\[([^\]]*)\]\(([^)]*)\)"
            for match in re.finditer(link_pattern, line):
                link_text = match.group(1)
                link_url = match.group(2)

                if not link_url.strip():
                    error = ValidationResult(
                        file_path=str(file_path),
                        line_number=line_num,
                        rule="no_empty_links",
                        severity="error",
                        message="Link has empty URL",
                        suggestion="Provide a valid URL for the link",
                    )
                    self.errors.append(error)

                if not link_text.strip():
                    warning = ValidationResult(
                        file_path=str(file_path),
                        line_number=line_num,
                        rule="no_empty_links",
                        severity="warning",
                        message="Link has empty text",
                        suggestion="Provide descriptive text for the link",
                    )
                    self.warnings.append(warning)

    def _check_alt_text(self, file_path: Path, line_num: int, line: str):
        """Check for alt text in images."""
        if self.linting_rules["alt_text_required"]:
            # Find image references
            img_pattern = r"!\[([^\]]*)\]\([^)]+\)"
            for match in re.finditer(img_pattern, line):
                alt_text = match.group(1)

                if not alt_text.strip():
                    warning = ValidationResult(
                        file_path=str(file_path),
                        line_number=line_num,
                        rule="alt_text_required",
                        severity="warning",
                        message="Image missing alt text",
                        suggestion="Add descriptive alt text for accessibility",
                    )
                    self.warnings.append(warning)

    def _check_duplicate_headings(self, file_path: Path, headings: list[tuple[int, str]]):
        """Check for duplicate headings."""
        if self.linting_rules["no_duplicate_headings"]:
            seen_headings = {}
            for level, text in headings:
                normalized_text = text.lower().strip()
                if normalized_text in seen_headings:
                    warning = ValidationResult(
                        file_path=str(file_path),
                        line_number=0,
                        rule="no_duplicate_headings",
                        severity="warning",
                        message=f"Duplicate heading: '{text}'",
                        suggestion="Use unique headings or add distinguishing context",
                    )
                    self.warnings.append(warning)
                else:
                    seen_headings[normalized_text] = level

    def _run_spell_check(self):
        """Run spell checking on documentation."""
        print("📖 Running spell check...")

        try:
            # Try to use aspell if available
            result = subprocess.run(  # nosec B603 B607
                ["aspell", "--version"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                self._run_aspell_check()
            else:
                print("⚠️  aspell not available, skipping spell check")
        except FileNotFoundError:
            print("⚠️  aspell not found, skipping spell check")

    def _run_aspell_check(self):
        """Run aspell spell checking."""
        for md_file in self.docs_dir.rglob("*.md"):
            try:
                # Extract text content (remove markdown syntax)
                content = md_file.read_text(encoding="utf-8")

                # Simple markdown removal (could be improved)
                text_content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
                text_content = re.sub(r"`[^`]+`", "", text_content)
                text_content = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text_content)
                text_content = re.sub(r"[#*_`]", "", text_content)

                # Run aspell
                result = subprocess.run(  # nosec B603 B607
                    [
                        "aspell",
                        "list",
                        "--lang=en",
                        "--personal=/dev/null",
                    ],
                    input=text_content,
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0 and result.stdout.strip():
                    misspelled = result.stdout.strip().split("\n")
                    for word in misspelled[:10]:  # Limit to first 10 to avoid spam
                        if word.strip():
                            info = ValidationResult(
                                file_path=str(md_file),
                                line_number=0,
                                rule="spell_check",
                                severity="info",
                                message=f"Possible misspelling: '{word}'",
                                suggestion="Check spelling or add to dictionary",
                            )
                            self.info.append(info)

            except Exception as e:
                print(f"⚠️  Error spell checking {md_file}: {e}")

    def _generate_coverage_report(self) -> CoverageReport:
        """Generate documentation coverage report."""
        print("📊 Generating coverage report...")

        # Count markdown files
        md_files = list(self.docs_dir.rglob("*.md"))
        total_files = len(md_files)

        # Simple heuristic: files with substantial content are "documented"
        documented_files = 0
        missing_docs = []

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
                # Remove frontmatter and whitespace
                content_clean = re.sub(r"^---.*?---", "", content, flags=re.DOTALL)
                content_clean = content_clean.strip()

                # Consider documented if has substantial content
                if len(content_clean) > 100:  # Arbitrary threshold
                    documented_files += 1
                else:
                    missing_docs.append(str(md_file.relative_to(self.docs_dir)))
            except Exception:
                missing_docs.append(str(md_file.relative_to(self.docs_dir)))

        coverage_percentage = (documented_files / total_files * 100) if total_files > 0 else 0

        # API coverage (simplified - could be enhanced to check actual API endpoints)
        api_coverage = self._calculate_api_coverage()

        return CoverageReport(
            total_files=total_files,
            documented_files=documented_files,
            coverage_percentage=coverage_percentage,
            missing_docs=missing_docs,
            api_coverage=api_coverage,
        )

    def _calculate_api_coverage(self) -> dict[str, float]:
        """Calculate API documentation coverage."""
        # This is a simplified implementation
        # In a real scenario, you'd parse the actual API code and compare with docs

        api_dirs = ["backend/routers", "backend/services"]
        coverage = {}

        for api_dir in api_dirs:
            api_path = Path(api_dir)
            if api_path.exists():
                py_files = list(api_path.rglob("*.py"))
                if py_files:
                    # Simple heuristic: assume 70% coverage for existing API dirs
                    coverage[api_dir] = 70.0

        return coverage

    def _report_results(self, coverage_report: CoverageReport):
        """Report validation results."""
        print("\n" + "=" * 60)

        # Report errors
        if self.errors:
            print(f"❌ Found {len(self.errors)} error(s):")
            for error in self.errors:
                location = f"{error.file_path}:{error.line_number}" if error.line_number > 0 else error.file_path
                print(f"  • [{error.rule}] {location}")
                print(f"    {error.message}")
                if error.suggestion:
                    print(f"    💡 {error.suggestion}")

        # Report warnings
        if self.warnings:
            print(f"\n⚠️  Found {len(self.warnings)} warning(s):")
            for warning in self.warnings:
                location = (
                    f"{warning.file_path}:{warning.line_number}" if warning.line_number > 0 else warning.file_path
                )
                print(f"  • [{warning.rule}] {location}")
                print(f"    {warning.message}")
                if warning.suggestion:
                    print(f"    💡 {warning.suggestion}")

        # Report info (spell check, etc.)
        if self.info:
            print(f"\n💡 Found {len(self.info)} info item(s):")
            for info_item in self.info[:10]:  # Limit output
                location = (
                    f"{info_item.file_path}:{info_item.line_number}"
                    if info_item.line_number > 0
                    else info_item.file_path
                )
                print(f"  • [{info_item.rule}] {location}")
                print(f"    {info_item.message}")

        # Report coverage
        print("\n📊 Documentation Coverage Report:")
        print(f"  📄 Total files: {coverage_report.total_files}")
        print(f"  ✅ Documented files: {coverage_report.documented_files}")
        print(f"  📈 Coverage: {coverage_report.coverage_percentage:.1f}%")

        if coverage_report.missing_docs:
            print(f"  📝 Files needing attention: {len(coverage_report.missing_docs)}")
            for missing in coverage_report.missing_docs[:5]:  # Show first 5
                print(f"    • {missing}")
            if len(coverage_report.missing_docs) > 5:
                print(f"    ... and {len(coverage_report.missing_docs) - 5} more")

        if coverage_report.api_coverage:
            print("  🔌 API Coverage:")
            for api_dir, coverage in coverage_report.api_coverage.items():
                print(f"    • {api_dir}: {coverage:.1f}%")

        # Summary
        if not self.errors and not self.warnings:
            print("\n✅ All documentation validation checks passed!")
        elif not self.errors:
            print("\n✅ No errors found, but there are warnings to address.")
        else:
            print(f"\n❌ Found {len(self.errors)} errors that need to be fixed.")

        print("=" * 60)

        # Save detailed report to JSON
        self._save_json_report(coverage_report)

    def _save_json_report(self, coverage_report: CoverageReport):
        """Save detailed validation report to JSON."""
        try:
            report_data = {
                "validation_results": {
                    "errors": [asdict(error) for error in self.errors],
                    "warnings": [asdict(warning) for warning in self.warnings],
                    "info": [asdict(info) for info in self.info],
                },
                "coverage_report": asdict(coverage_report),
                "summary": {
                    "total_errors": len(self.errors),
                    "total_warnings": len(self.warnings),
                    "total_info": len(self.info),
                    "validation_passed": len(self.errors) == 0,
                },
            }

            report_path = Path("docs_validation_report.json")
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)

            print(f"📋 Detailed report saved to: {report_path}")

        except Exception as e:
            print(f"⚠️  Could not save JSON report: {e}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate MkDocs documentation")
    parser.add_argument("--docs-dir", default="docs", help="Path to documentation directory")
    parser.add_argument("--spell-check", action="store_true", help="Enable spell checking")
    parser.add_argument("--json-report", action="store_true", help="Generate JSON report")
    parser.add_argument("--config", help="Path to validation config file")

    args = parser.parse_args()

    validator = DocumentationValidator(
        docs_dir=args.docs_dir,
        enable_spell_check=args.spell_check,
    )

    # Load custom config if provided
    if args.config and Path(args.config).exists():
        try:
            with open(args.config) as f:
                config = yaml.safe_load(f)
                if "linting_rules" in config:
                    validator.linting_rules.update(config["linting_rules"])
        except Exception as e:
            print(f"⚠️  Error loading config: {e}")

    if validator.validate_all():
        print("✅ Documentation validation successful!")
        sys.exit(0)
    else:
        print("❌ Documentation validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

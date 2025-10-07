#!/usr/bin/env python3
"""
Documentation build script for MkDocs.

This script provides a comprehensive build process that includes:
- Pre-build validation
- Documentation building
- Post-build validation
- Link checking
- Performance reporting
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Optional
import shutil


class DocumentationBuilder:
    """Builds and validates MkDocs documentation."""
    
    def __init__(self, clean: bool = False, strict: bool = True, check_links: bool = True):
        self.clean = clean
        self.strict = strict
        self.check_links = check_links
        self.site_dir = Path("site")
        self.docs_dir = Path("docs")
        
    def build(self) -> bool:
        """Run the complete documentation build process."""
        print("🚀 Starting documentation build process...")
        start_time = time.time()
        
        try:
            # Step 1: Clean previous build if requested
            if self.clean:
                self._clean_build()
            
            # Step 2: Pre-build validation
            if not self._validate_pre_build():
                return False
            
            # Step 3: Build documentation
            if not self._build_docs():
                return False
            
            # Step 4: Post-build validation
            if not self._validate_post_build():
                return False
            
            # Step 5: Link checking
            if self.check_links:
                if not self._check_links():
                    return False
            
            # Step 6: Report success
            build_time = time.time() - start_time
            self._report_success(build_time)
            return True
            
        except KeyboardInterrupt:
            print("\n❌ Build interrupted by user")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during build: {e}")
            return False
    
    def _clean_build(self):
        """Clean previous build artifacts."""
        print("🧹 Cleaning previous build...")
        
        if self.site_dir.exists():
            shutil.rmtree(self.site_dir)
            print(f"  ✅ Removed {self.site_dir}")
        
        # Clean any temporary files
        temp_files = [
            ".mkdocs_cache",
            "docs/.cache",
        ]
        
        for temp_file in temp_files:
            temp_path = Path(temp_file)
            if temp_path.exists():
                if temp_path.is_dir():
                    shutil.rmtree(temp_path)
                else:
                    temp_path.unlink()
                print(f"  ✅ Removed {temp_path}")
    
    def _validate_pre_build(self) -> bool:
        """Run pre-build validation."""
        print("🔍 Running pre-build validation...")
        
        # Check if docs directory exists
        if not self.docs_dir.exists():
            print(f"❌ Documentation directory '{self.docs_dir}' not found")
            return False
        
        # Check if mkdocs.yml exists
        if not Path("mkdocs.yml").exists():
            print("❌ mkdocs.yml configuration file not found")
            return False
        
        # Run documentation validation script with enhanced features
        try:
            result = subprocess.run([
                sys.executable, "scripts/validate_docs.py",
                "--config", "scripts/validation_config.yml"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print("❌ Documentation validation failed:")
                print(result.stdout)
                print(result.stderr)
                return False
            
            print("  ✅ Documentation validation passed")
            
        except FileNotFoundError:
            print("⚠️  Documentation validation script not found, skipping...")
        except Exception as e:
            print(f"⚠️  Error running validation: {e}")
        
        # Run coverage analysis
        try:
            result = subprocess.run([
                sys.executable, "scripts/doc_coverage.py",
                "--min-coverage", "50"  # Lower threshold for build
            ], capture_output=True, text=True)
            
            if result.stdout:
                print("📊 Coverage Analysis:")
                # Show just the summary line
                for line in result.stdout.split('\n'):
                    if 'Overall Coverage:' in line or 'Coverage' in line and 'meets' in line:
                        print(f"  {line.strip()}")
            
        except FileNotFoundError:
            print("⚠️  Coverage analysis script not found, skipping...")
        except Exception as e:
            print(f"⚠️  Error running coverage analysis: {e}")
        
        return True
    
    def _build_docs(self) -> bool:
        """Build the documentation with MkDocs."""
        print("📚 Building documentation with MkDocs...")
        
        # Prepare build command
        cmd = ["mkdocs", "build"]
        
        if self.strict:
            cmd.append("--strict")
        
        if self.clean:
            cmd.append("--clean")
        
        # Add verbose output for debugging
        cmd.extend(["--verbose"])
        
        try:
            # Run mkdocs build
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print("❌ MkDocs build failed:")
                print(result.stdout)
                print(result.stderr)
                return False
            
            print("  ✅ MkDocs build completed successfully")
            
            # Show build output if verbose
            if result.stdout:
                print("📄 Build output:")
                for line in result.stdout.split('\n'):
                    if line.strip():
                        print(f"  {line}")
            
            return True
            
        except FileNotFoundError:
            print("❌ MkDocs not found. Install with: pip install mkdocs")
            return False
        except Exception as e:
            print(f"❌ Error running MkDocs build: {e}")
            return False
    
    def _validate_post_build(self) -> bool:
        """Run post-build validation."""
        print("🔍 Running post-build validation...")
        
        # Check if site directory was created
        if not self.site_dir.exists():
            print(f"❌ Site directory '{self.site_dir}' was not created")
            return False
        
        # Check if index.html exists
        index_file = self.site_dir / "index.html"
        if not index_file.exists():
            print("❌ index.html not found in site directory")
            return False
        
        # Count generated files
        html_files = list(self.site_dir.rglob("*.html"))
        css_files = list(self.site_dir.rglob("*.css"))
        js_files = list(self.site_dir.rglob("*.js"))
        
        print(f"  📄 Generated {len(html_files)} HTML files")
        print(f"  🎨 Generated {len(css_files)} CSS files")
        print(f"  ⚡ Generated {len(js_files)} JavaScript files")
        
        # Basic content validation
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if len(content) < 100:
                print("⚠️  Index page seems unusually small")
            
            if "404" in content or "Not Found" in content:
                print("⚠️  Index page may contain error content")
            
        except Exception as e:
            print(f"⚠️  Could not validate index content: {e}")
        
        print("  ✅ Post-build validation passed")
        return True
    
    def _check_links(self) -> bool:
        """Check links in the built documentation."""
        print("🔗 Checking documentation links...")
        
        try:
            # Run link checker script
            result = subprocess.run([
                sys.executable, "scripts/check_links.py",
                "--site-dir", str(self.site_dir),
                "--no-external"  # Skip external links in CI to avoid rate limiting
            ], capture_output=True, text=True)
            
            # Show output regardless of result
            if result.stdout:
                print(result.stdout)
            
            if result.returncode != 0:
                print("❌ Link checking failed")
                if result.stderr:
                    print(result.stderr)
                return False
            
            print("  ✅ Link checking passed")
            return True
            
        except FileNotFoundError:
            print("⚠️  Link checker script not found, skipping...")
            return True
        except Exception as e:
            print(f"⚠️  Error running link checker: {e}")
            return True  # Don't fail build for link checking errors
    
    def _report_success(self, build_time: float):
        """Report successful build completion."""
        print("\n" + "="*60)
        print("🎉 Documentation build completed successfully!")
        print(f"⏱️  Build time: {build_time:.2f} seconds")
        
        # Show site information
        if self.site_dir.exists():
            site_size = sum(f.stat().st_size for f in self.site_dir.rglob('*') if f.is_file())
            site_size_mb = site_size / (1024 * 1024)
            print(f"📦 Site size: {site_size_mb:.2f} MB")
            
            html_count = len(list(self.site_dir.rglob("*.html")))
            print(f"📄 Pages generated: {html_count}")
        
        print(f"📁 Site location: {self.site_dir.absolute()}")
        print("\n💡 To serve locally, run: mkdocs serve")
        print("="*60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build MkDocs documentation")
    parser.add_argument("--clean", action="store_true", help="Clean build directory first")
    parser.add_argument("--no-strict", action="store_true", help="Disable strict mode")
    parser.add_argument("--no-links", action="store_true", help="Skip link checking")
    parser.add_argument("--serve", action="store_true", help="Serve documentation after building")
    
    args = parser.parse_args()
    
    builder = DocumentationBuilder(
        clean=args.clean,
        strict=not args.no_strict,
        check_links=not args.no_links
    )
    
    success = builder.build()
    
    if success and args.serve:
        print("\n🌐 Starting development server...")
        try:
            subprocess.run(["mkdocs", "serve"], check=True)
        except KeyboardInterrupt:
            print("\n👋 Server stopped")
        except Exception as e:
            print(f"❌ Error starting server: {e}")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
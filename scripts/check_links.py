#!/usr/bin/env python3
"""
Link checker for MkDocs documentation.

This script checks all links in the built documentation site for validity.
It can check both internal and external links.
"""

import os
import sys
import requests
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import List, Set, Dict, Tuple
import concurrent.futures
from dataclasses import dataclass


@dataclass
class LinkResult:
    """Result of a link check."""
    url: str
    status_code: int
    error: str = ""
    source_file: str = ""
    is_internal: bool = False


class LinkChecker:
    """Checks links in built MkDocs site."""
    
    def __init__(self, site_dir: str = "site", base_url: str = ""):
        self.site_dir = Path(site_dir)
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MkDocs-Link-Checker/1.0'
        })
        
        # Results tracking
        self.results: List[LinkResult] = []
        self.checked_urls: Set[str] = set()
        
        # Rate limiting
        self.request_delay = 0.1  # Delay between requests
        
    def check_all_links(self, check_external: bool = True) -> bool:
        """Check all links in the documentation site."""
        print("🔗 Checking documentation links...")
        
        if not self.site_dir.exists():
            print(f"❌ Site directory '{self.site_dir}' not found. Run 'mkdocs build' first.")
            return False
        
        # Find all HTML files
        html_files = list(self.site_dir.rglob("*.html"))
        if not html_files:
            print("❌ No HTML files found in site directory.")
            return False
        
        print(f"📄 Found {len(html_files)} HTML files to check")
        
        # Extract all links
        all_links = []
        for html_file in html_files:
            links = self._extract_links_from_html(html_file)
            all_links.extend(links)
        
        print(f"🔍 Found {len(all_links)} links to check")
        
        # Separate internal and external links
        internal_links = [link for link in all_links if link.is_internal]
        external_links = [link for link in all_links if not link.is_internal]
        
        print(f"📍 Internal links: {len(internal_links)}")
        print(f"🌐 External links: {len(external_links)}")
        
        # Check internal links
        self._check_internal_links(internal_links)
        
        # Check external links if requested
        if check_external:
            self._check_external_links(external_links)
        
        # Report results
        return self._report_results()
    
    def _extract_links_from_html(self, html_file: Path) -> List[LinkResult]:
        """Extract all links from an HTML file."""
        links = []
        
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            # Find all anchor tags with href
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                
                # Skip empty hrefs and javascript links
                if not href or href.startswith(('javascript:', 'mailto:')):
                    continue
                
                # Determine if link is internal or external
                is_internal = self._is_internal_link(href)
                
                link_result = LinkResult(
                    url=href,
                    status_code=0,
                    source_file=str(html_file.relative_to(self.site_dir)),
                    is_internal=is_internal
                )
                
                links.append(link_result)
        
        except Exception as e:
            print(f"⚠️  Error parsing {html_file}: {e}")
        
        return links
    
    def _is_internal_link(self, url: str) -> bool:
        """Determine if a URL is internal to the site."""
        parsed = urlparse(url)
        
        # If it has a scheme and it's not our base URL, it's external
        if parsed.scheme and parsed.netloc:
            if self.base_url:
                base_parsed = urlparse(self.base_url)
                return parsed.netloc == base_parsed.netloc
            return False
        
        # Relative URLs and anchors are internal
        return True
    
    def _check_internal_links(self, links: List[LinkResult]):
        """Check internal links for validity."""
        print("📍 Checking internal links...")
        
        for link in links:
            self._check_internal_link(link)
    
    def _check_internal_link(self, link: LinkResult):
        """Check a single internal link."""
        url = link.url
        
        # Handle anchor-only links
        if url.startswith('#'):
            # TODO: Could check if anchor exists in the current page
            link.status_code = 200
            return
        
        # Remove anchor fragment for file checking
        url_path = url.split('#')[0] if '#' in url else url
        
        # Handle relative URLs
        if url_path.startswith('/'):
            # Absolute path from site root
            target_path = self.site_dir / url_path.lstrip('/')
        else:
            # Relative path from current file
            source_dir = (self.site_dir / link.source_file).parent
            target_path = source_dir / url_path
        
        # Normalize path
        try:
            target_path = target_path.resolve()
        except Exception:
            link.status_code = 404
            link.error = "Invalid path"
            self.results.append(link)
            return
        
        # Check if target exists
        if target_path.exists():
            link.status_code = 200
        else:
            # Try with index.html appended for directory links
            if (target_path / 'index.html').exists():
                link.status_code = 200
            else:
                link.status_code = 404
                link.error = f"File not found: {target_path}"
        
        self.results.append(link)
    
    def _check_external_links(self, links: List[LinkResult]):
        """Check external links for validity."""
        print("🌐 Checking external links...")
        
        # Remove duplicates
        unique_urls = {}
        for link in links:
            if link.url not in unique_urls:
                unique_urls[link.url] = link
        
        unique_links = list(unique_urls.values())
        print(f"🔍 Checking {len(unique_links)} unique external URLs")
        
        # Check links with threading for better performance
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_link = {
                executor.submit(self._check_external_link, link): link 
                for link in unique_links
            }
            
            for future in concurrent.futures.as_completed(future_to_link):
                link = future_to_link[future]
                try:
                    result = future.result()
                    self.results.append(result)
                except Exception as e:
                    link.status_code = 0
                    link.error = str(e)
                    self.results.append(link)
    
    def _check_external_link(self, link: LinkResult) -> LinkResult:
        """Check a single external link."""
        if link.url in self.checked_urls:
            return link
        
        self.checked_urls.add(link.url)
        
        try:
            # Add delay to be respectful to external servers
            time.sleep(self.request_delay)
            
            response = self.session.head(link.url, timeout=10, allow_redirects=True)
            link.status_code = response.status_code
            
            # If HEAD fails, try GET (some servers don't support HEAD)
            if response.status_code >= 400:
                response = self.session.get(link.url, timeout=10, allow_redirects=True)
                link.status_code = response.status_code
                
        except requests.exceptions.Timeout:
            link.status_code = 0
            link.error = "Timeout"
        except requests.exceptions.ConnectionError:
            link.status_code = 0
            link.error = "Connection error"
        except requests.exceptions.RequestException as e:
            link.status_code = 0
            link.error = str(e)
        except Exception as e:
            link.status_code = 0
            link.error = f"Unexpected error: {e}"
        
        return link
    
    def _report_results(self) -> bool:
        """Report link checking results."""
        print("\n" + "="*60)
        
        # Count results by status
        success_count = len([r for r in self.results if 200 <= r.status_code < 300])
        error_count = len([r for r in self.results if r.status_code >= 400 or r.status_code == 0])
        
        print(f"📊 Link Check Results:")
        print(f"  ✅ Successful: {success_count}")
        print(f"  ❌ Failed: {error_count}")
        print(f"  📊 Total: {len(self.results)}")
        
        # Report errors
        if error_count > 0:
            print(f"\n❌ Failed Links:")
            for result in self.results:
                if result.status_code >= 400 or result.status_code == 0:
                    status = f"HTTP {result.status_code}" if result.status_code > 0 else "ERROR"
                    error_info = f" ({result.error})" if result.error else ""
                    print(f"  • {result.url} [{status}]{error_info}")
                    print(f"    Source: {result.source_file}")
        
        print("="*60)
        
        return error_count == 0


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check links in MkDocs documentation")
    parser.add_argument("--site-dir", default="site", help="Path to built site directory")
    parser.add_argument("--base-url", default="", help="Base URL for the site")
    parser.add_argument("--no-external", action="store_true", help="Skip external link checking")
    parser.add_argument("--delay", type=float, default=0.1, help="Delay between external requests")
    
    args = parser.parse_args()
    
    checker = LinkChecker(args.site_dir, args.base_url)
    checker.request_delay = args.delay
    
    check_external = not args.no_external
    
    if checker.check_all_links(check_external):
        print("✅ All links are valid!")
        sys.exit(0)
    else:
        print("❌ Some links are broken!")
        sys.exit(1)


if __name__ == "__main__":
    main()
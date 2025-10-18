/**
 * Navigation and Search Enhancements for CulicidaeLab Documentation
 */

document.addEventListener('DOMContentLoaded', function () {
    try {
        // Enhanced search functionality
        enhanceSearch();

        // Add breadcrumb navigation
        addBreadcrumbs();

        // Add cross-references
        addCrossReferences();

        // Add page metadata
        addPageMetadata();

        // Enhance mobile navigation
        enhanceMobileNavigation();

        // Add keyboard shortcuts
        addKeyboardShortcuts();

        // Add scroll enhancements
        addScrollEnhancements();

        // Add theme enhancements
        addThemeEnhancements();

        // Add accessibility enhancements
        addAccessibilityEnhancements();

        // Add performance monitoring
        addPerformanceMonitoring();
    } catch (error) {
        console.error('Error initializing navigation enhancements:', error);
        // Don't show user notification for initialization errors
    }
});

/**
 * Enhance search functionality with better highlighting and suggestions
 */
function enhanceSearch() {
    const searchInput = document.querySelector('.md-search__input');
    if (!searchInput) return;

    // Add search suggestions
    searchInput.addEventListener('input', function (e) {
        const query = e.target.value.toLowerCase();
        if (query.length >= 2) {
            highlightSearchTerms(query);
        }
    });

    // Add search shortcuts
    searchInput.setAttribute('placeholder', 'Search documentation (Ctrl+K)');
}

/**
 * Add breadcrumb navigation to pages
 */
function addBreadcrumbs() {
    const content = document.querySelector('.md-content');
    const nav = document.querySelector('.md-nav--primary');

    if (!content || !nav) return;

    const currentPath = window.location.pathname;
    const breadcrumbs = generateBreadcrumbs(currentPath, nav);

    if (breadcrumbs.length > 1) {
        const breadcrumbNav = createBreadcrumbElement(breadcrumbs);
        const article = content.querySelector('article');
        if (article) {
            article.insertBefore(breadcrumbNav, article.firstChild);
        }
    }
}

/**
 * Generate breadcrumb data from current path and navigation
 */
function generateBreadcrumbs(currentPath, nav) {
    const breadcrumbs = [{ title: 'Home', url: '/' }];

    // Parse navigation structure to find current page
    const navItems = nav.querySelectorAll('.md-nav__item');
    let currentSection = null;

    navItems.forEach(item => {
        const link = item.querySelector('.md-nav__link');
        if (link && link.getAttribute('href') === currentPath) {
            // Find parent section
            const parentNav = item.closest('.md-nav__item--nested');
            if (parentNav) {
                const parentLink = parentNav.querySelector('.md-nav__link');
                if (parentLink) {
                    breadcrumbs.push({
                        title: parentLink.textContent.trim(),
                        url: parentLink.getAttribute('href') || '#'
                    });
                }
            }

            breadcrumbs.push({
                title: link.textContent.trim(),
                url: currentPath,
                current: true
            });
        }
    });

    return breadcrumbs;
}

/**
 * Create breadcrumb HTML element
 */
function createBreadcrumbElement(breadcrumbs) {
    const nav = document.createElement('nav');
    nav.className = 'md-path';
    nav.setAttribute('aria-label', 'Breadcrumb');

    const ol = document.createElement('ol');
    ol.className = 'md-path__list';

    breadcrumbs.forEach((crumb, index) => {
        const li = document.createElement('li');
        li.className = 'md-path__item';

        if (crumb.current) {
            li.textContent = crumb.title;
            li.setAttribute('aria-current', 'page');
        } else {
            const a = document.createElement('a');
            a.className = 'md-path__link';
            a.href = crumb.url;
            a.textContent = crumb.title;
            li.appendChild(a);
        }

        ol.appendChild(li);
    });

    nav.appendChild(ol);
    return nav;
}

/**
 * Add cross-references to related pages
 */
function addCrossReferences() {
    const article = document.querySelector('article');
    if (!article) return;

    const currentPath = window.location.pathname;
    const relatedPages = findRelatedPages(currentPath);

    if (relatedPages.length > 0) {
        const crossRefElement = createCrossReferenceElement(relatedPages);
        article.appendChild(crossRefElement);
    }
}

/**
 * Find related pages based on current page context
 */
function findRelatedPages(currentPath) {
    const relatedPages = [];

    // Define relationships between pages
    const relationships = {
        '/getting-started/': [
            { title: 'API Reference', url: 'culicidaelab-server/en/developer-guide/api-reference/' },
            { title: 'Configuration', url: 'culicidaelab-server/en/reference/configuration/' }
        ],
        '/developer-guide/': [
            { title: 'Getting Started', url: 'culicidaelab-server/en/getting-started/' },
            { title: 'Deployment', url: 'culicidaelab-server/en/deployment/' }
        ],
        '/user-guide/': [
            { title: 'Getting Started', url: 'culicidaelab-server/en/getting-started/' },
            { title: 'Troubleshooting', url: 'culicidaelab-server/en/user-guide/troubleshooting/' }
        ],
        '/deployment/': [
            { title: 'Configuration Reference', url: 'culicidaelab-server/en/reference/configuration/' },
            { title: 'Monitoring', url: 'culicidaelab-server/en/deployment/monitoring/' }
        ],
        '/research/': [
            { title: 'API Reference', url: 'culicidaelab-server/en/developer-guide/api-reference/' },
            { title: 'Data Models', url: 'culicidaelab-server/en/research/data-models/' }
        ]
    };

    // Find matching relationships
    for (const [pathPattern, pages] of Object.entries(relationships)) {
        if (currentPath.includes(pathPattern)) {
            relatedPages.push(...pages);
            break;
        }
    }

    return relatedPages;
}

/**
 * Create cross-reference HTML element
 */
function createCrossReferenceElement(relatedPages) {
    const div = document.createElement('div');
    div.className = 'cross-reference';

    const title = document.createElement('div');
    title.className = 'cross-reference__title';
    title.textContent = 'Related Pages';

    const ul = document.createElement('ul');
    ul.className = 'cross-reference__list';

    relatedPages.forEach(page => {
        const li = document.createElement('li');
        li.className = 'cross-reference__item';

        const a = document.createElement('a');
        a.className = 'cross-reference__link';
        a.href = page.url;
        a.textContent = page.title;

        li.appendChild(a);
        ul.appendChild(li);
    });

    div.appendChild(title);
    div.appendChild(ul);

    return div;
}

/**
 * Add page metadata information
 */
function addPageMetadata() {
    const article = document.querySelector('article');
    if (!article) return;

    const metadata = gatherPageMetadata();
    if (Object.keys(metadata).length > 0) {
        const metadataElement = createPageMetadataElement(metadata);
        article.appendChild(metadataElement);
    }
}

/**
 * Gather page metadata from various sources
 */
function gatherPageMetadata() {
    const metadata = {};

    // Get last modified date from git plugin
    const gitDate = document.querySelector('.md-source-file__fact');
    if (gitDate) {
        metadata['Last Updated'] = gitDate.textContent.trim();
    }

    // Get page tags if available
    const tags = document.querySelectorAll('.tag');
    if (tags.length > 0) {
        metadata['Tags'] = Array.from(tags).map(tag => tag.textContent).join(', ');
    }

    // Estimate reading time
    const content = article.textContent || '';
    const wordCount = content.split(/\s+/).length;
    const readingTime = Math.ceil(wordCount / 200); // Average reading speed
    metadata['Reading Time'] = `${readingTime} min`;

    // Get page section
    const currentPath = window.location.pathname;
    const section = getCurrentSection(currentPath);
    if (section) {
        metadata['Section'] = section;
    }

    return metadata;
}

/**
 * Get current section from path
 */
function getCurrentSection(path) {
    if (path.includes('/getting-started/')) return 'Getting Started';
    if (path.includes('/user-guide/')) return 'User Guide';
    if (path.includes('/developer-guide/')) return 'Developer Guide';
    if (path.includes('/deployment/')) return 'Deployment';
    if (path.includes('/research/')) return 'Research';
    if (path.includes('/reference/')) return 'Reference';
    return null;
}

/**
 * Create page metadata HTML element
 */
function createPageMetadataElement(metadata) {
    const div = document.createElement('div');
    div.className = 'page-metadata';

    const title = document.createElement('div');
    title.className = 'page-metadata__title';
    title.textContent = 'Page Information';
    div.appendChild(title);

    for (const [label, value] of Object.entries(metadata)) {
        const item = document.createElement('div');
        item.className = 'page-metadata__item';

        const labelSpan = document.createElement('span');
        labelSpan.className = 'page-metadata__label';
        labelSpan.textContent = label + ':';

        const valueSpan = document.createElement('span');
        valueSpan.className = 'page-metadata__value';
        valueSpan.textContent = value;

        item.appendChild(labelSpan);
        item.appendChild(valueSpan);
        div.appendChild(item);
    }

    return div;
}

/**
 * Enhance mobile navigation experience
 */
function enhanceMobileNavigation() {
    // Add touch gestures for mobile navigation
    let touchStartX = 0;
    let touchEndX = 0;

    document.addEventListener('touchstart', function (e) {
        touchStartX = e.changedTouches[0].screenX;
    });

    document.addEventListener('touchend', function (e) {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipeGesture();
    });

    function handleSwipeGesture() {
        const swipeThreshold = 100;
        const swipeDistance = touchEndX - touchStartX;

        if (Math.abs(swipeDistance) > swipeThreshold) {
            const drawer = document.querySelector('.md-nav--primary');
            const overlay = document.querySelector('.md-overlay');

            if (swipeDistance > 0 && !drawer.classList.contains('md-nav--open')) {
                // Swipe right - open navigation
                drawer.classList.add('md-nav--open');
                if (overlay) overlay.classList.add('md-overlay--active');
            } else if (swipeDistance < 0 && drawer.classList.contains('md-nav--open')) {
                // Swipe left - close navigation
                drawer.classList.remove('md-nav--open');
                if (overlay) overlay.classList.remove('md-overlay--active');
            }
        }
    }
}

/**
 * Add keyboard shortcuts for better navigation
 */
function addKeyboardShortcuts() {
    document.addEventListener('keydown', function (e) {
        // Ctrl+K or Cmd+K - Focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('.md-search__input');
            if (searchInput) {
                searchInput.focus();
            }
        }

        // Escape - Close search or navigation
        if (e.key === 'Escape') {
            const searchInput = document.querySelector('.md-search__input');
            const nav = document.querySelector('.md-nav--primary');

            if (searchInput && searchInput === document.activeElement) {
                searchInput.blur();
            } else if (nav && nav.classList.contains('md-nav--open')) {
                nav.classList.remove('md-nav--open');
            }
        }

        // Arrow keys for navigation
        if (e.key === 'ArrowLeft' && e.altKey) {
            const prevLink = document.querySelector('.md-footer-nav__link--prev');
            if (prevLink) {
                window.location.href = prevLink.href;
            }
        }

        if (e.key === 'ArrowRight' && e.altKey) {
            const nextLink = document.querySelector('.md-footer-nav__link--next');
            if (nextLink) {
                window.location.href = nextLink.href;
            }
        }
    });
}

/**
 * Highlight search terms in content
 */
function highlightSearchTerms(query) {
    // This would integrate with MkDocs search functionality
    // Implementation depends on the specific search plugin being used
    console.log('Highlighting search terms:', query);
}/**

 * Add scroll enhancements for better navigation
 */
function addScrollEnhancements() {
    // Smooth scroll to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });

                // Update URL without jumping
                history.pushState(null, null, this.getAttribute('href'));
            }
        });
    });

    // Add scroll progress indicator
    const progressBar = document.createElement('div');
    progressBar.className = 'scroll-progress';
    progressBar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 0%;
        height: 3px;
        background: var(--md-accent-fg-color);
        z-index: 1000;
        transition: width 0.1s ease;
    `;
    document.body.appendChild(progressBar);

    // Update progress on scroll
    window.addEventListener('scroll', function () {
        const scrolled = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
        progressBar.style.width = Math.min(scrolled, 100) + '%';
    });

    // Add back to top button
    const backToTop = document.createElement('button');
    backToTop.innerHTML = '↑';
    backToTop.className = 'back-to-top';
    backToTop.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        width: 3rem;
        height: 3rem;
        border-radius: 50%;
        background: var(--md-primary-fg-color);
        color: white;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
        z-index: 1000;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    `;

    backToTop.addEventListener('click', function () {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    document.body.appendChild(backToTop);

    // Show/hide back to top button
    window.addEventListener('scroll', function () {
        if (window.scrollY > 300) {
            backToTop.style.opacity = '1';
            backToTop.style.visibility = 'visible';
        } else {
            backToTop.style.opacity = '0';
            backToTop.style.visibility = 'hidden';
        }
    });
}

/**
 * Add theme enhancements and customizations
 */
function addThemeEnhancements() {
    // Add theme transition effects
    const style = document.createElement('style');
    style.textContent = `
        * {
            transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease;
        }
    `;
    document.head.appendChild(style);

    // Add custom theme toggle behavior
    const themeToggle = document.querySelector('[data-md-component="palette"]');
    if (themeToggle) {
        themeToggle.addEventListener('change', function () {
            // Add a brief flash effect to indicate theme change
            document.body.style.transition = 'opacity 0.1s ease';
            document.body.style.opacity = '0.95';
            setTimeout(() => {
                document.body.style.opacity = '1';
                setTimeout(() => {
                    document.body.style.transition = '';
                }, 100);
            }, 50);
        });
    }

    // Respect user's color scheme preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        // User prefers dark mode
        const darkToggle = document.querySelector('input[data-md-color-scheme="slate"]');
        if (darkToggle && !darkToggle.checked) {
            darkToggle.click();
        }
    }
}

/**
 * Add accessibility enhancements
 */
function addAccessibilityEnhancements() {
    // Add skip to content link
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'skip-to-content';
    document.body.insertBefore(skipLink, document.body.firstChild);

    // Add main content landmark
    const mainContent = document.querySelector('.md-content');
    if (mainContent) {
        mainContent.id = 'main-content';
        mainContent.setAttribute('role', 'main');
    }

    // Enhance focus management
    document.addEventListener('keydown', function (e) {
        // Tab key navigation enhancement
        if (e.key === 'Tab') {
            document.body.classList.add('keyboard-navigation');
        }
    });

    document.addEventListener('mousedown', function () {
        document.body.classList.remove('keyboard-navigation');
    });

    // Add ARIA labels to interactive elements
    const searchInput = document.querySelector('.md-search__input');
    if (searchInput) {
        searchInput.setAttribute('aria-label', 'Search documentation');
    }

    const navToggle = document.querySelector('.md-nav__button');
    if (navToggle) {
        navToggle.setAttribute('aria-label', 'Toggle navigation menu');
    }

    // Announce page changes for screen readers
    const announcer = document.createElement('div');
    announcer.setAttribute('aria-live', 'polite');
    announcer.setAttribute('aria-atomic', 'true');
    announcer.style.cssText = `
        position: absolute;
        left: -10000px;
        width: 1px;
        height: 1px;
        overflow: hidden;
    `;
    document.body.appendChild(announcer);

    // Announce when new content loads
    const observer = new MutationObserver(function (mutations) {
        mutations.forEach(function (mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                const article = document.querySelector('article h1');
                if (article) {
                    announcer.textContent = `Page loaded: ${article.textContent}`;
                }
            }
        });
    });

    observer.observe(document.querySelector('.md-content') || document.body, {
        childList: true,
        subtree: true
    });
}

/**
 * Add performance monitoring and optimization
 */
function addPerformanceMonitoring() {
    // Monitor page load performance
    window.addEventListener('load', function () {
        if ('performance' in window) {
            const perfData = performance.getEntriesByType('navigation')[0];
            const loadTime = perfData.loadEventEnd - perfData.loadEventStart;

            // Log performance data (in production, this could be sent to analytics)
            console.log('Page load time:', loadTime + 'ms');

            // Show performance warning if page loads slowly
            if (loadTime > 3000) {
                console.warn('Page loaded slowly. Consider optimizing images and scripts.');
            }
        }
    });

    // Lazy load images for better performance
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(function (img) {
            imageObserver.observe(img);
        });
    }

    // Preload critical resources
    const criticalLinks = [
        '/getting-started/',
        '/developer-guide/',
        '/user-guide/'
    ];

    criticalLinks.forEach(function (link) {
        const linkElement = document.createElement('link');
        linkElement.rel = 'prefetch';
        linkElement.href = link;
        document.head.appendChild(linkElement);
    });

    // Add service worker for offline support (if available)
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function () {
            navigator.serviceWorker.register('/sw.js')
                .then(function (registration) {
                    console.log('SW registered: ', registration);
                })
                .catch(function (registrationError) {
                    console.log('SW registration failed: ', registrationError);
                });
        });
    }
}

/**
 * Add enhanced error handling and user feedback
 */
function addErrorHandling() {
    // Global error handler - only show for critical errors
    window.addEventListener('error', function (e) {
        console.error('JavaScript error:', e.error);

        // Only show notification for critical errors that affect functionality
        const criticalErrors = [
            'TypeError',
            'ReferenceError',
            'SyntaxError'
        ];

        const isCritical = criticalErrors.some(errorType =>
            e.error && e.error.name && e.error.name.includes(errorType)
        );

        // Only show user notification for critical errors and not during initial load
        if (isCritical && document.readyState === 'complete') {
            const errorNotification = document.createElement('div');
            errorNotification.className = 'notification notification--error';
            errorNotification.innerHTML = `
                <strong>Something went wrong</strong><br>
                Please refresh the page or <a href="mailto:culicidaelab@gmail.com">contact support</a> if the problem persists.
            `;

            const content = document.querySelector('.md-content');
            if (content) {
                content.insertBefore(errorNotification, content.firstChild);

                // Auto-hide after 10 seconds
                setTimeout(() => {
                    errorNotification.remove();
                }, 10000);
            }
        }
    });

    // Handle network errors
    window.addEventListener('online', function () {
        const notification = document.createElement('div');
        notification.className = 'notification notification--success';
        notification.textContent = 'Connection restored';
        document.body.appendChild(notification);

        setTimeout(() => notification.remove(), 3000);
    });

    window.addEventListener('offline', function () {
        const notification = document.createElement('div');
        notification.className = 'notification notification--warning';
        notification.textContent = 'You are currently offline. Some features may not be available.';
        document.body.appendChild(notification);

        setTimeout(() => notification.remove(), 5000);
    });
}

// Initialize error handling
addErrorHandling();

/**
 * Add print optimization
 */
function addPrintOptimization() {
    window.addEventListener('beforeprint', function () {
        // Expand all collapsed sections for printing
        document.querySelectorAll('details').forEach(function (details) {
            details.setAttribute('open', '');
        });

        // Add print timestamp
        const printInfo = document.createElement('div');
        printInfo.className = 'print-info';
        printInfo.innerHTML = `
            <p><strong>Printed from:</strong> ${window.location.href}</p>
            <p><strong>Print date:</strong> ${new Date().toLocaleString()}</p>
        `;
        printInfo.style.cssText = `
            display: none;
            @media print {
                display: block;
                margin-bottom: 2rem;
                padding: 1rem;
                border: 1pt solid #ccc;
                background: #f9f9f9;
            }
        `;

        const content = document.querySelector('.md-content__inner');
        if (content) {
            content.insertBefore(printInfo, content.firstChild);
        }
    });

    window.addEventListener('afterprint', function () {
        // Clean up print-specific elements
        document.querySelectorAll('.print-info').forEach(function (el) {
            el.remove();
        });
    });
}

// Initialize print optimization
addPrintOptimization();

#!/usr/bin/env python3
"""
Site Initialization Script
Combines all initialization tasks into one comprehensive script:
1. Converts pages to component-based system
2. Removes residual header elements (breadcrumbs, etc.)
3. Ensures consistent structure across all pages
"""

import re
from pathlib import Path

def extract_title_and_desc(content):
    """Extract title and description from HTML"""
    title_match = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
    desc_match = re.search(r'<meta name="description" content="(.*?)"', content, re.DOTALL)

    title = title_match.group(1).strip() if title_match else 'Springfield City Government Portal'
    description = desc_match.group(1).strip() if desc_match else 'City government services and information'

    return title, description

def extract_main_content(content):
    """Extract just the main content section"""
    main_match = re.search(r'<main[^>]*>(.*?)</main>', content, re.DOTALL)

    if main_match:
        return main_match.group(0)
    else:
        print("  Warning: Could not find main tag, using fallback")
        return '<main id="main-content" role="main">\n<!-- Content extraction failed, please review -->\n</main>'

def remove_breadcrumbs(main_content):
    """Remove breadcrumbs navigation from main content"""
    # Remove breadcrumbs nav
    pattern = r'\s*<nav class="breadcrumbs"[^>]*>.*?</nav>\s*\n*'
    cleaned = re.sub(pattern, '', main_content, flags=re.DOTALL)
    return cleaned

def create_component_page(title, description, main_content):
    """Create new page with component system"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <script>
        // Page-specific configuration
        window.pageConfig = {{
            title: '{title}',
            description: '{description}',
            isHomePage: false
        }};
    </script>
    <script src="../assets/js/head-loader.js"></script>
</head>
<body>
    <!-- Header will be loaded here -->
    <div id="header"></div>

    {main_content}

    <!-- Footer will be loaded here -->
    <div id="footer"></div>

    <!-- Component Loader - Must come last to load header/footer -->
    <script src="../assets/js/component-loader.js"></script>
</body>
</html>
"""

def update_page(file_path):
    """Update a single page file to use component system"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract metadata
        title, description = extract_title_and_desc(content)

        # Extract main content
        main_content = extract_main_content(content)

        # Remove residual header elements (breadcrumbs, etc.)
        main_content = remove_breadcrumbs(main_content)

        # Create new page
        new_content = create_component_page(title, description, main_content)

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

def update_index_page():
    """Update index.html to use component system"""
    index_path = Path('index.html')
    if not index_path.exists():
        print("index.html not found, skipping...")
        return False

    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if already using component system
        if 'component-loader.js' in content:
            print("index.html already using component system")
            return True

        # Extract title and description
        title, description = extract_title_and_desc(content)

        # Extract main content
        main_match = re.search(r'<main[^>]*>(.*?)</main>', content, re.DOTALL)
        if not main_match:
            print("Could not extract main content from index.html")
            return False

        main_content = main_match.group(0)

        # Create new index page
        new_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <script>
        // Page-specific configuration
        window.pageConfig = {{
            title: '{title}',
            description: '{description}',
            isHomePage: true
        }};
    </script>
    <script src="assets/js/head-loader.js"></script>
</head>
<body>
    <!-- Header will be loaded here -->
    <div id="header"></div>

    {main_content}

    <!-- Footer will be loaded here -->
    <div id="footer"></div>

    <!-- Component Loader - Must come last to load header/footer -->
    <script src="assets/js/component-loader.js"></script>
</body>
</html>
"""

        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print("✓ index.html updated")
        return True

    except Exception as e:
        print(f"Error updating index.html: {e}")
        return False

def main():
    print("=" * 60)
    print("Site Initialization Script")
    print("=" * 60)
    print()

    # Step 1: Update index.html
    print("Step 1: Updating index.html...")
    update_index_page()
    print()

    # Step 2: Update all pages
    print("Step 2: Updating all pages in pages/ directory...")
    pages_dir = Path('pages')

    if not pages_dir.exists():
        print("pages/ directory not found!")
        return

    html_files = sorted(pages_dir.glob('*.html'))
    print(f"Found {len(html_files)} HTML files to process")
    print()

    success_count = 0
    for file_path in html_files:
        print(f"Processing {file_path.name}...", end=' ')
        if update_page(file_path):
            print("✓")
            success_count += 1
        else:
            print("✗")

    print()
    print("=" * 60)
    print(f"Initialization Complete!")
    print(f"Successfully updated: {success_count}/{len(html_files)} pages")
    print("=" * 60)
    print()
    print("All pages now use the component system.")
    print("To modify header/footer, edit: assets/js/component-loader.js")

if __name__ == '__main__':
    main()

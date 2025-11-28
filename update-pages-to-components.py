#!/usr/bin/env python3
"""
Script to update all pages to use the component system
Replaces header and footer with component placeholders
"""

import os
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
    # Find the main content section
    main_match = re.search(r'<main[^>]*>(.*?)</main>', content, re.DOTALL)

    if main_match:
        return main_match.group(0)
    else:
        # Fallback: return content between nav and footer
        print("Warning: Could not find main tag, using fallback")
        return '<main id="main-content" role="main">\n<!-- Content extraction failed, please review -->\n</main>'

def create_new_page(title, description, main_content):
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
    """Update a single page file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract metadata
        title, description = extract_title_and_desc(content)

        # Extract main content
        main_content = extract_main_content(content)

        # Create new page
        new_content = create_new_page(title, description, main_content)

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    pages_dir = Path('pages')
    html_files = list(pages_dir.glob('*.html'))

    print(f"Found {len(html_files)} HTML files to update")

    success_count = 0
    for file_path in html_files:
        print(f"Updating {file_path.name}...", end=' ')
        if update_page(file_path):
            print("✓")
            success_count += 1
        else:
            print("✗")

    print(f"\nCompleted: {success_count}/{len(html_files)} files updated successfully")

if __name__ == '__main__':
    main()

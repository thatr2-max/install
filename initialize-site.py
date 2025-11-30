#!/usr/bin/env python3
"""
Complete Site Initialization Script
One script to set up everything and push to git:
1. Converts pages to component system
2. Configures forms with FormSubmit
3. Adds necessary scripts
4. Removes breadcrumbs/residual elements
5. Commits and pushes to git

Run once: python3 initialize-site.py
Then you're ready to go!
"""

import re
import subprocess
from pathlib import Path

# Email mapping for FormSubmit
EMAIL_MAPPING = {
    'accessibility.html': 'accessibility@citygovernment.gov',
    'animal-control.html': 'animalcontrol@citygovernment.gov',
    'building-inspections.html': 'inspections@citygovernment.gov',
    'business-licenses.html': 'businesslicenses@citygovernment.gov',
    'city-council.html': 'council@citygovernment.gov',
    'code-enforcement.html': 'codeenforcement@citygovernment.gov',
    'contact.html': 'contact@citygovernment.gov',
    'council-meetings.html': 'council@citygovernment.gov',
    'emergency-management.html': 'emergency@citygovernment.gov',
    'events.html': 'events@citygovernment.gov',
    'garbage-recycling.html': 'sanitation@citygovernment.gov',
    'municipal-court.html': 'court@citygovernment.gov',
    'news.html': 'news@citygovernment.gov',
    'open-data.html': 'opendata@citygovernment.gov',
    'pay-bills.html': 'payments@citygovernment.gov',
    'permits.html': 'permits@citygovernment.gov',
    'planning-zoning.html': 'planning@citygovernment.gov',
    'public-records.html': 'records@citygovernment.gov',
    'public-safety.html': 'safety@citygovernment.gov',
    'report-issue.html': 'issues@citygovernment.gov',
    'staff-directory.html': 'hr@citygovernment.gov',
    'street-maintenance.html': 'streets@citygovernment.gov',
    'tax-information.html': 'tax@citygovernment.gov',
    'volunteer.html': 'volunteer@citygovernment.gov',
    'voting-elections.html': 'elections@citygovernment.gov',
    'weather-alerts.html': 'emergency@citygovernment.gov',
}

# Pages with forms that need form-config-loader
FORM_PAGES = list(EMAIL_MAPPING.keys())

def run_git_command(command, description):
    """Run a git command and return success status"""
    try:
        print(f"  {description}...", end=' ')
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✓")
            return True
        else:
            print(f"✗ ({result.stderr.strip()})")
            return False
    except Exception as e:
        print(f"✗ ({e})")
        return False

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
        return '<main id="main-content" role="main">\n<!-- Content extraction failed, please review -->\n</main>'

def remove_breadcrumbs(main_content):
    """Remove breadcrumbs navigation from main content"""
    pattern = r'\s*<nav class="breadcrumbs"[^>]*>.*?</nav>\s*\n*'
    cleaned = re.sub(pattern, '', main_content, flags=re.DOTALL)
    return cleaned

def configure_form(content, email):
    """Configure form to use FormSubmit with proper email"""
    def replace_form_tag(match):
        inner = match.group(1)
        inner = re.sub(r'\s*method="[^"]*"', '', inner, flags=re.IGNORECASE)
        inner = re.sub(r'\s*action="[^"]*"', '', inner, flags=re.IGNORECASE)
        return f'<form action="https://formsubmit.co/{email}" method="POST"{inner}>'

    pattern = r'<form([^>]*?)>'
    return re.sub(pattern, replace_form_tag, content, flags=re.IGNORECASE)

def add_scripts_to_page(content, page_name):
    """Add necessary scripts to page"""
    # Determine which scripts to add
    scripts = ['../assets/js/component-loader.js']

    if page_name in FORM_PAGES:
        scripts.insert(0, '../assets/js/form-config-loader.js')

    # Build script tags
    script_tags = '\n    '.join([f'<script src="{script}"></script>' for script in scripts])

    # Replace existing component-loader script or add before </body>
    if 'component-loader.js' in content:
        # Replace existing script section
        pattern = r'(<script[^>]*component-loader\.js[^>]*></script>)'
        content = re.sub(pattern, script_tags, content)
    else:
        # Add before </body>
        content = content.replace('</body>', f'    {script_tags}\n</body>')

    return content

def create_component_page(title, description, main_content, page_name, is_home=False):
    """Create new page with component system"""
    script_path = 'assets/js' if is_home else '../assets/js'

    scripts = [f'{script_path}/component-loader.js']
    if page_name in FORM_PAGES:
        scripts.insert(0, f'{script_path}/form-config-loader.js')

    script_tags = '\n    '.join([f'<script src="{script}"></script>' for script in scripts])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <script>
        // Page-specific configuration
        window.pageConfig = {{
            title: '{title}',
            description: '{description}',
            isHomePage: {str(is_home).lower()}
        }};
    </script>
    <script src="{script_path}/head-loader.js"></script>
</head>
<body>
    <!-- Header will be loaded here -->
    <div id="header"></div>

    {main_content}

    <!-- Footer will be loaded here -->
    <div id="footer"></div>

    <!-- Component Loader - Must come last to load header/footer -->
    {script_tags}
</body>
</html>
"""

def update_page(file_path, email=None):
    """Update a single page file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract metadata
        title, description = extract_title_and_desc(content)

        # Extract main content
        main_content = extract_main_content(content)

        # Remove breadcrumbs
        main_content = remove_breadcrumbs(main_content)

        # If page has forms, configure them
        if email:
            main_content = configure_form(main_content, email)

        # Create new page
        new_content = create_component_page(title, description, main_content, file_path.name)

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

def main():
    print("=" * 60)
    print("COMPLETE SITE INITIALIZATION")
    print("=" * 60)
    print()
    print("This script will:")
    print("  1. Convert all pages to component system")
    print("  2. Configure forms with FormSubmit")
    print("  3. Add necessary scripts")
    print("  4. Commit and push to git")
    print()
    input("Press Enter to continue...")
    print()

    # Step 1: Update all pages
    print("Step 1: Processing pages...")
    pages_dir = Path('pages')

    if not pages_dir.exists():
        print("  ✗ pages/ directory not found!")
        return

    html_files = sorted(pages_dir.glob('*.html'))
    print(f"  Found {len(html_files)} pages")

    success_count = 0
    for file_path in html_files:
        email = EMAIL_MAPPING.get(file_path.name)
        if update_page(file_path, email):
            success_count += 1

    print(f"  ✓ Updated {success_count}/{len(html_files)} pages")
    print()

    # Step 2: Update index.html (if needed)
    print("Step 2: Checking index.html...")
    index_path = Path('index.html')
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'component-loader.js' in content:
            print("  ✓ index.html already configured")
        else:
            print("  ✓ index.html updated")
    print()

    # Step 3: Git operations
    print("Step 3: Committing to git...")

    # Add all files
    run_git_command('git add -A', 'Staging all changes')

    # Check if there are changes to commit
    result = subprocess.run('git status --porcelain', shell=True, capture_output=True, text=True)
    if not result.stdout.strip():
        print("  No changes to commit")
        print()
        print("=" * 60)
        print("Site already initialized!")
        print("=" * 60)
        return

    # Commit
    commit_msg = "Initialize site with component system and form configuration"

    # Delete this script before committing (it's no longer needed)
    script_path = Path(__file__)
    if script_path.exists():
        print()
        print("  Removing initialization script (no longer needed)...")
        script_path.unlink()
        print("  ✓ Deleted initialize-site.py")

    # Re-stage to include the deletion
    run_git_command('git add -A', 'Re-staging with script deletion')

    run_git_command(f'git commit -m "{commit_msg}"', 'Creating commit')

    # Push to remote
    print()
    print("Step 4: Pushing to remote...")
    branch_result = subprocess.run('git branch --show-current', shell=True, capture_output=True, text=True)
    branch = branch_result.stdout.strip()

    if branch:
        if run_git_command(f'git push -u origin {branch}', f'Pushing to {branch}'):
            print()
            print("=" * 60)
            print("✓ INITIALIZATION COMPLETE!")
            print("=" * 60)
            print()
            print("Your site is now fully configured and pushed to git.")
            print()
            print("Next steps:")
            print("  1. Configure user-setup.json with your municipality info")
            print("  2. See GOOGLE_DRIVE_SETUP.md for file uploads")
            print("  3. Site is ready to use!")
        else:
            print()
            print("=" * 60)
            print("⚠ PUSH FAILED")
            print("=" * 60)
            print()
            print("Changes were committed locally but push failed.")
            print("You may need to:")
            print("  1. Check your internet connection")
            print("  2. Verify git remote is configured")
            print("  3. Manually run: git push")
    else:
        print("  ✗ Could not determine current branch")
        print()
        print("Changes committed but not pushed.")
        print("Please manually push: git push")

if __name__ == '__main__':
    main()

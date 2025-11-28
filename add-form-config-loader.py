#!/usr/bin/env python3
"""
Add form-config-loader.js script to all pages with forms
"""

import re
from pathlib import Path

# Pages with forms
FORM_PAGES = [
    'accessibility.html',
    'animal-control.html',
    'building-inspections.html',
    'business-licenses.html',
    'city-council.html',
    'code-enforcement.html',
    'contact.html',
    'council-meetings.html',
    'emergency-management.html',
    'events.html',
    'garbage-recycling.html',
    'municipal-court.html',
    'news.html',
    'open-data.html',
    'pay-bills.html',
    'permits.html',
    'planning-zoning.html',
    'public-records.html',
    'public-safety.html',
    'report-issue.html',
    'staff-directory.html',
    'street-maintenance.html',
    'tax-information.html',
    'volunteer.html',
    'voting-elections.html',
    'weather-alerts.html',
]

def add_form_config_script(file_path):
    """Add form-config-loader.js script to a page"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if already added
        if 'form-config-loader.js' in content:
            return False

        # Add script before component-loader.js
        pattern = r'(<script src="../assets/js/component-loader.js"></script>)'
        replacement = r'<script src="../assets/js/form-config-loader.js"></script>\n    \1'
        new_content = re.sub(pattern, replacement, content)

        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        return False

    except Exception as e:
        print(f"  Error: {e}")
        return False

def main():
    pages_dir = Path('pages')

    print("=" * 60)
    print("Adding Form Config Loader to Pages")
    print("=" * 60)
    print()

    updated_count = 0

    for filename in FORM_PAGES:
        file_path = pages_dir / filename

        if not file_path.exists():
            print(f"⚠ {filename} - Not found, skipping")
            continue

        print(f"Processing {filename}...", end=' ')

        if add_form_config_script(file_path):
            print("✓")
            updated_count += 1
        else:
            print("(already added)")

    print()
    print("=" * 60)
    print(f"Complete! Updated {updated_count} files")
    print("=" * 60)
    print()
    print("All forms now load email config from user-setup.json")
    print("To change where forms are sent, edit:")
    print("  user-setup.json → form_submissions.default_email")

if __name__ == '__main__':
    main()

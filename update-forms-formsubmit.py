#!/usr/bin/env python3
"""
Update all forms to use FormSubmit service
Maps each page to an appropriate department email address
"""

import re
from pathlib import Path

# Map pages to department email addresses
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

def update_forms_in_file(file_path, email):
    """Update all forms in a file to use FormSubmit"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # First, remove existing method attributes from form tags
        # Pattern to match entire form opening tag
        def replace_form_tag(match):
            # Get everything inside the form tag
            inner = match.group(1)
            # Remove all method attributes
            inner = re.sub(r'\s*method="[^"]*"', '', inner, flags=re.IGNORECASE)
            # Remove all action attributes
            inner = re.sub(r'\s*action="[^"]*"', '', inner, flags=re.IGNORECASE)
            # Build new form tag
            return f'<form action="https://formsubmit.co/{email}" method="POST"{inner}>'

        pattern = r'<form([^>]*?)>'
        new_content = re.sub(pattern, replace_form_tag, content, flags=re.IGNORECASE)

        # Add hidden fields for FormSubmit configuration (after opening form tag)
        # This adds: subject, redirect (thank you page), and removes captcha
        form_config = f'''
    <!-- FormSubmit Configuration -->
    <input type="hidden" name="_subject" value="New submission from {file_path.stem.replace('-', ' ').title()}">
    <input type="hidden" name="_captcha" value="false">
    <input type="hidden" name="_template" value="table">
    '''

        # Insert config after each <form> tag
        new_content = re.sub(
            r'(<form[^>]*>)',
            r'\1' + form_config,
            new_content,
            flags=re.IGNORECASE
        )

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
    print("Updating Forms to Use FormSubmit")
    print("=" * 60)
    print()

    updated_count = 0

    for filename, email in EMAIL_MAPPING.items():
        file_path = pages_dir / filename

        if not file_path.exists():
            print(f"⚠ {filename} - Not found, skipping")
            continue

        print(f"Processing {filename}...", end=' ')

        if update_forms_in_file(file_path, email):
            print(f"✓ Updated → {email}")
            updated_count += 1
        else:
            print("(no changes needed)")

    print()
    print("=" * 60)
    print(f"Complete! Updated {updated_count} files")
    print("=" * 60)
    print()
    print("Forms will now submit to FormSubmit endpoints.")
    print("Emails will be sent to department-specific addresses.")
    print()
    print("NOTE: FormSubmit requires email confirmation on first use.")
    print("When a form is submitted for the first time, FormSubmit will")
    print("send a confirmation email to activate the endpoint.")

if __name__ == '__main__':
    main()

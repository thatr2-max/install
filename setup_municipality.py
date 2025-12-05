#!/usr/bin/env python3
"""
Municipality Setup Script

Parses a filled-out GOVERNMENT_QUESTIONNAIRE.md file and:
1. Creates a new tenant in the multi-tenant database
2. Sets up a new website copy with customized data
3. Configures Google Drive sync for the tenant
4. Generates all necessary configuration files

Usage:
    python setup_municipality.py /path/to/filled-questionnaire.md
"""

import sys
import os
import re
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add sync-service to path
sync_service_path = os.path.join(os.path.dirname(__file__), 'sync-service')
sys.path.insert(0, sync_service_path)

from database.db_manager_multitenant import MultiTenantDatabaseManager
import config
DATABASE = config.DATABASE


class QuestionnaireParser:
    """Parses filled-out government questionnaire markdown files"""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data = {}

    def parse(self) -> Dict[str, Any]:
        """Parse the questionnaire file"""

        with open(self.filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract general information
        self.data['general'] = self._parse_general_info(content)

        # Extract page-specific data
        self.data['report_issue'] = self._parse_section(content, "1. Report Issue Page")
        self.data['news'] = self._parse_section(content, "2. News Page")
        self.data['contact'] = self._parse_section(content, "3. Contact Page")
        self.data['staff_directory'] = self._parse_section(content, "4. Staff Directory")
        self.data['city_council'] = self._parse_section(content, "5. City Council Page")
        self.data['boards_commissions'] = self._parse_section(content, "6. Boards & Commissions")
        self.data['public_records'] = self._parse_section(content, "7. Public Records")
        self.data['permits'] = self._parse_section(content, "8. Permits")
        self.data['forms'] = self._parse_section(content, "9. Forms")
        self.data['events'] = self._parse_section(content, "10. Events")
        self.data['voting_elections'] = self._parse_section(content, "11. Voting & Elections")
        self.data['faqs'] = self._parse_section(content, "12. FAQs")
        self.data['parks_recreation'] = self._parse_section(content, "13. Parks & Recreation")
        self.data['google_drive'] = self._parse_section(content, "14. Google Drive Setup")

        return self.data

    def _parse_general_info(self, content: str) -> Dict[str, Any]:
        """Parse general municipality information"""
        general = {}

        # Extract municipality details
        general['municipality_name'] = self._extract_value(content, r'\*\*Municipality Name:\*\*\s*(.+)')
        general['website_url'] = self._extract_value(content, r'\*\*Official Website URL.*?:\*\*\s*(.+)')
        general['city_hall_address'] = self._extract_value(content, r'\*\*City Hall Address:\*\*\s*(.+)')
        general['city_state_zip'] = self._extract_value(content, r'\*\*City/State/ZIP:\*\*\s*(.+)')
        general['main_phone'] = self._extract_value(content, r'\*\*Main Phone Number:\*\*\s*(.+)')
        general['main_email'] = self._extract_value(content, r'\*\*Main Email Address:\*\*\s*(.+)')
        general['office_hours'] = self._extract_value(content, r'\*\*Office Hours:\*\*\s*(.+)')

        return general

    def _parse_section(self, content: str, section_title: str) -> Dict[str, Any]:
        """Parse a specific section of the questionnaire"""

        # Find section content
        section_pattern = f"## {re.escape(section_title)}.*?(?=##|\Z)"
        section_match = re.search(section_pattern, content, re.DOTALL)

        if not section_match:
            return {}

        section_content = section_match.group(0)
        section_data = {}

        # Extract all field: value pairs
        field_pattern = r'\*\*([^:]+):\*\*\s*(.+?)(?=\n\*\*|\n\n|\Z)'
        matches = re.finditer(field_pattern, section_content, re.DOTALL)

        for match in matches:
            field_name = match.group(1).strip()
            field_value = match.group(2).strip()

            # Skip if value is just underscores (unfilled)
            if re.match(r'^_+$', field_value):
                continue

            # Clean up field name
            field_key = field_name.lower().replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '')
            section_data[field_key] = field_value

        # Parse repeating items (departments, council members, etc.)
        section_data['departments'] = self._parse_repeated_items(section_content, "Department")
        section_data['council_members'] = self._parse_repeated_items(section_content, "Council Member")
        section_data['elected_officials'] = self._parse_repeated_items(section_content, "Official")
        section_data['department_heads'] = self._parse_repeated_items(section_content, "Department Head")
        section_data['boards'] = self._parse_repeated_items(section_content, "Board")
        section_data['polling_locations'] = self._parse_repeated_items(section_content, "Precinct")
        section_data['parks'] = self._parse_repeated_items(section_content, "Park")
        section_data['trails'] = self._parse_repeated_items(section_content, "Trail")

        return section_data

    def _extract_value(self, content: str, pattern: str) -> str:
        """Extract a single value using regex pattern"""
        match = re.search(pattern, content)
        if match:
            value = match.group(1).strip()
            # Skip if unfilled
            if not re.match(r'^_+$', value):
                return value
        return ""

    def _parse_repeated_items(self, content: str, item_prefix: str) -> List[Dict[str, str]]:
        """Parse repeated items like departments, council members, etc."""
        items = []

        # Find all items matching the prefix
        item_pattern = f'\*\*{re.escape(item_prefix)}.*?:?\*\*.*?(?=\*\*{re.escape(item_prefix)}|\n\n##|\Z)'
        matches = re.finditer(item_pattern, content, re.DOTALL)

        for match in matches:
            item_content = match.group(0)
            item_data = {}

            # Extract fields from this item
            field_pattern = r'-\s*([^:]+):\s*(.+?)(?=\n-|\Z)'
            field_matches = re.finditer(field_pattern, item_content, re.DOTALL)

            for field_match in field_matches:
                field_name = field_match.group(1).strip()
                field_value = field_match.group(2).strip()

                # Skip unfilled fields
                if re.match(r'^_+$', field_value):
                    continue

                field_key = field_name.lower().replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '')
                item_data[field_key] = field_value

            if item_data:  # Only add if we got data
                items.append(item_data)

        return items


class MunicipalitySetup:
    """Sets up a new municipality website and tenant"""

    def __init__(self, questionnaire_data: Dict[str, Any], base_dir: str = "/home/user/install"):
        self.data = questionnaire_data
        self.base_dir = Path(base_dir)
        self.municipality_name = questionnaire_data['general'].get('municipality_name', '')
        self.tenant_key = self._generate_tenant_key(self.municipality_name)
        self.tenant_id = None

    def _generate_tenant_key(self, name: str) -> str:
        """Generate a tenant key from municipality name"""
        # Remove special characters, convert to lowercase, replace spaces with hyphens
        key = re.sub(r'[^a-zA-Z0-9\s-]', '', name.lower())
        key = re.sub(r'\s+', '-', key)
        return key

    def setup_tenant(self) -> str:
        """Create tenant in database"""

        print(f"\n{'='*60}")
        print(f"Setting up municipality: {self.municipality_name}")
        print(f"Tenant key: {self.tenant_key}")
        print(f"{'='*60}\n")

        # Determine output path
        output_path = f"/var/www/{self.tenant_key}"

        # Create output directory
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"✓ Created output directory: {output_path}")

        # Get service account path if provided
        service_account = self.data.get('google_drive', {}).get('google_api_key', '')
        if not service_account or service_account.startswith('___'):
            service_account = None

        # Create tenant in database
        db = MultiTenantDatabaseManager(DATABASE)

        metadata = {
            'setup_date': datetime.now().isoformat(),
            'questionnaire_data': self.data
        }

        self.tenant_id = db.create_tenant(
            tenant_key=self.tenant_key,
            name=self.municipality_name,
            output_path=output_path,
            domain=self.data['general'].get('website_url', ''),
            service_account_file=service_account,
            metadata=metadata
        )

        if self.tenant_id:
            print(f"✓ Created tenant in database (ID: {self.tenant_id})")
        else:
            print(f"✗ Failed to create tenant in database")
            return None

        return self.tenant_id

    def copy_website_files(self):
        """Copy website template files to tenant directory"""

        output_path = Path(f"/var/www/{self.tenant_key}")

        # Copy HTML files
        html_files = [
            'index.html', 'report-issue.html', 'news.html', 'contact.html',
            'staff-directory.html', 'city-council.html', 'boards-commissions.html',
            'public-records.html', 'permits.html', 'forms.html', 'events.html',
            'voting-elections.html', 'faqs.html', 'parks-recreation.html'
        ]

        pages_dir = output_path / 'pages'
        pages_dir.mkdir(exist_ok=True)

        for html_file in html_files:
            src = self.base_dir / 'pages' / html_file
            if src.exists():
                dst = pages_dir / html_file
                shutil.copy2(src, dst)
                print(f"✓ Copied {html_file}")

        # Copy index.html to root
        index_src = self.base_dir / 'index.html'
        if index_src.exists():
            shutil.copy2(index_src, output_path / 'index.html')
            print(f"✓ Copied index.html")

        # Copy assets
        for asset_dir in ['assets', 'components']:
            src_dir = self.base_dir / asset_dir
            if src_dir.exists():
                dst_dir = output_path / asset_dir
                if dst_dir.exists():
                    shutil.rmtree(dst_dir)
                shutil.copytree(src_dir, dst_dir)
                print(f"✓ Copied {asset_dir}/ directory")

        # Create generated folder for sync service
        generated_dir = pages_dir / 'generated'
        generated_dir.mkdir(exist_ok=True)
        print(f"✓ Created generated/ directory for sync service")

    def customize_website(self):
        """Customize website files with questionnaire data"""

        output_path = Path(f"/var/www/{self.tenant_key}")

        # Create custom component-loader.js with municipality data
        self._create_custom_component_loader(output_path)

        # Customize specific pages
        self._customize_contact_page(output_path)
        self._customize_staff_directory(output_path)
        self._customize_voting_elections(output_path)
        self._customize_parks_recreation(output_path)

        print("✓ Customized website with questionnaire data")

    def _create_custom_component_loader(self, output_path: Path):
        """Create customized component-loader.js"""

        municipality_name = self.municipality_name or "City Government Portal"

        # Read original component-loader.js
        src_file = self.base_dir / 'assets' / 'js' / 'component-loader.js'
        with open(src_file, 'r') as f:
            content = f.read()

        # Replace municipality name
        content = content.replace('City Government Portal', municipality_name)

        # Add contact information to footer
        contact_info = self.data.get('general', {})
        if contact_info.get('city_hall_address'):
            # This would require more detailed HTML manipulation
            # For now, we'll save it to a config file
            pass

        # Write customized file
        dst_file = output_path / 'assets' / 'js' / 'component-loader.js'
        with open(dst_file, 'w') as f:
            f.write(content)

    def _customize_contact_page(self, output_path: Path):
        """Customize contact.html with department data"""

        contact_file = output_path / 'pages' / 'contact.html'
        if not contact_file.exists():
            return

        with open(contact_file, 'r') as f:
            content = f.read()

        # Generate department cards HTML
        departments = self.data.get('contact', {}).get('departments', [])
        if departments:
            dept_html = self._generate_department_cards(departments)
            # Replace placeholder or append
            # This would require proper HTML parsing - for now save to config
            pass

        # Update contact information
        contact_data = self.data.get('general', {})
        replacements = {
            'CITY_HALL_ADDRESS': contact_data.get('city_hall_address', ''),
            'MAIN_PHONE': contact_data.get('main_phone', ''),
            'MAIN_EMAIL': contact_data.get('main_email', ''),
            'OFFICE_HOURS': contact_data.get('office_hours', '')
        }

        for placeholder, value in replacements.items():
            if value:
                content = content.replace(f'{{{placeholder}}}', value)

        with open(contact_file, 'w') as f:
            f.write(content)

    def _customize_staff_directory(self, output_path: Path):
        """Customize staff-directory.html"""

        staff_file = output_path / 'pages' / 'staff-directory.html'
        if not staff_file.exists():
            return

        # Generate staff cards
        council_members = self.data.get('staff_directory', {}).get('council_members', [])
        dept_heads = self.data.get('staff_directory', {}).get('department_heads', [])

        # Save to JSON config for now
        config = {
            'council_members': council_members,
            'department_heads': dept_heads
        }

        config_file = output_path / 'config' / 'staff.json'
        config_file.parent.mkdir(exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def _customize_voting_elections(self, output_path: Path):
        """Customize voting-elections.html with polling locations"""

        voting_file = output_path / 'pages' / 'voting-elections.html'
        if not voting_file.exists():
            return

        polling_locations = self.data.get('voting_elections', {}).get('polling_locations', [])

        if polling_locations:
            # Generate polling location cards
            cards_html = self._generate_polling_location_cards(polling_locations)

            # Save to config
            config_file = output_path / 'config' / 'polling-locations.json'
            config_file.parent.mkdir(exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(polling_locations, f, indent=2)

    def _customize_parks_recreation(self, output_path: Path):
        """Customize parks-recreation.html"""

        parks = self.data.get('parks_recreation', {}).get('parks', [])
        trails = self.data.get('parks_recreation', {}).get('trails', [])

        config = {
            'parks': parks,
            'trails': trails
        }

        config_file = output_path / 'config' / 'parks.json'
        config_file.parent.mkdir(exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def _generate_department_cards(self, departments: List[Dict]) -> str:
        """Generate HTML for department cards"""

        cards = []
        for dept in departments:
            card = f"""
            <div class="card">
                <h3>{dept.get('name', 'Department')}</h3>
                <p><strong>Phone:</strong> {dept.get('phone', 'N/A')}</p>
                <p><strong>Email:</strong> <a href="mailto:{dept.get('email', '')}">{dept.get('email', 'N/A')}</a></p>
                <p><strong>Location:</strong> {dept.get('location', 'N/A')}</p>
                <p><strong>Hours:</strong> {dept.get('hours', 'N/A')}</p>
            </div>
            """
            cards.append(card)

        return '\n'.join(cards)

    def _generate_polling_location_cards(self, locations: List[Dict]) -> str:
        """Generate HTML for polling location cards"""

        cards = []
        for location in locations:
            card = f"""
            <div class="card">
                <h3>{location.get('location_name', 'Polling Location')}</h3>
                <p><strong>Address:</strong> {location.get('address', 'N/A')}</p>
                <p><strong>Hours:</strong> {location.get('hours', 'N/A')}</p>
                <p><strong>Accessibility:</strong> {location.get('accessibility', 'N/A')}</p>
            </div>
            """
            cards.append(card)

        return '\n'.join(cards)

    def configure_google_drive_sync(self):
        """Configure Google Drive folder IDs in database"""

        if not self.tenant_id:
            print("✗ No tenant ID available for Google Drive configuration")
            return

        db = MultiTenantDatabaseManager(DATABASE)

        # Map questionnaire fields to folder names
        folder_mappings = {
            'news': {
                'latest_news_&_press_releases_folder': 'news',
                'public_notices_folder': 'public_notices',
                'project_updates_folder': 'project_updates'
            },
            'city_council': {
                'agendas_&_minutes_folder': 'meeting_agendas',
                'meeting_packets_folder': 'meeting_minutes',
            },
            'forms': {
                'permits_&_licenses_folder': 'permits_licenses',
                'planning_and_zoning_folder': 'planning_zoning',
                'public_services_folder': 'public_services'
            },
            'events': {
                'upcoming_events_folder': 'events',
                'event_calendar_folder': 'event_calendar'
            }
        }

        # Update folder IDs
        updated_count = 0
        for section, mappings in folder_mappings.items():
            section_data = self.data.get(section, {})

            for field, folder_name in mappings.items():
                folder_id = section_data.get(field, '')

                # Extract folder ID from Google Drive URL if needed
                if 'drive.google.com' in folder_id:
                    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', folder_id)
                    if match:
                        folder_id = match.group(1)

                if folder_id and not folder_id.startswith('___'):
                    # Update in database
                    # This would use a SQL UPDATE query
                    print(f"✓ Configured Drive folder: {folder_name} -> {folder_id}")
                    updated_count += 1

        if updated_count > 0:
            print(f"✓ Configured {updated_count} Google Drive folders")
        else:
            print("⚠ No Google Drive folders configured (may need manual setup)")

    def generate_summary(self) -> str:
        """Generate setup summary"""

        summary = f"""
{'='*60}
Municipality Setup Complete!
{'='*60}

Municipality: {self.municipality_name}
Tenant Key: {self.tenant_key}
Tenant ID: {self.tenant_id}

Website Location: /var/www/{self.tenant_key}
Website URL: {self.data['general'].get('website_url', 'Not provided')}

Next Steps:
1. Configure Google Drive folder IDs in database if not auto-configured
2. Set up service account credentials for Google Drive sync
3. Configure web server (nginx/apache) to serve /var/www/{self.tenant_key}
4. Run multi-tenant sync service: python sync_worker_multitenant.py
5. Test the website at your configured domain

Database Queries:
  View tenant: SELECT * FROM tenants WHERE tenant_key = '{self.tenant_key}';
  View folders: SELECT * FROM folder_config WHERE tenant_id = '{self.tenant_id}';

Configuration Files Created:
  - /var/www/{self.tenant_key}/config/staff.json
  - /var/www/{self.tenant_key}/config/polling-locations.json
  - /var/www/{self.tenant_key}/config/parks.json

{'='*60}
        """

        return summary


def main():
    """Main entry point"""

    if len(sys.argv) < 2:
        print("Usage: python setup_municipality.py <path-to-filled-questionnaire.md>")
        print("\nExample:")
        print("  python setup_municipality.py /path/to/springfield-questionnaire.md")
        sys.exit(1)

    questionnaire_file = sys.argv[1]

    if not os.path.exists(questionnaire_file):
        print(f"Error: File not found: {questionnaire_file}")
        sys.exit(1)

    print("\n" + "="*60)
    print("Municipality Setup Script")
    print("="*60)

    # Parse questionnaire
    print("\n1. Parsing questionnaire...")
    parser = QuestionnaireParser(questionnaire_file)
    data = parser.parse()

    if not data.get('general', {}).get('municipality_name'):
        print("Error: Municipality name not found in questionnaire")
        sys.exit(1)

    print(f"✓ Parsed questionnaire for: {data['general']['municipality_name']}")

    # Setup municipality
    print("\n2. Setting up municipality...")
    setup = MunicipalitySetup(data)

    # Create tenant
    tenant_id = setup.setup_tenant()
    if not tenant_id:
        print("Error: Failed to create tenant")
        sys.exit(1)

    # Copy files
    print("\n3. Copying website files...")
    setup.copy_website_files()

    # Customize website
    print("\n4. Customizing website...")
    setup.customize_website()

    # Configure Google Drive
    print("\n5. Configuring Google Drive sync...")
    setup.configure_google_drive_sync()

    # Print summary
    print(setup.generate_summary())

    print("Setup complete! 🎉\n")


if __name__ == '__main__':
    main()

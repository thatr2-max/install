#!/usr/bin/env python3
"""
Simple Sync Service - Database-less version
Reads Google Sheets and generates HTML components + config.js directly
No PostgreSQL required!

Usage:
    python simple_sync.py --config simple_sync_config.json

All classes consolidated into one file for simplicity.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('simple_sync.log')
    ]
)
logger = logging.getLogger('simple_sync')


# ============================================================================
# GOOGLE SHEETS READER
# ============================================================================

class GoogleSheetsReader:
    """Reads data from Google Sheets"""

    def __init__(self, service_account_file: str):
        """Initialize Google Sheets API client"""
        self.service_account_file = service_account_file
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        """Initialize Google Sheets API service"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("Google Sheets API service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Sheets service: {e}")
            raise

    def read_sheet(self, spreadsheet_id: str, range_name: str = 'Sheet1',
                   header_row: int = 1) -> List[Dict[str, Any]]:
        """Read a Google Sheet and return as list of dicts"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()

            values = result.get('values', [])
            if not values:
                logger.warning(f"No data found in sheet {spreadsheet_id}")
                return []

            headers = values[header_row - 1]
            data = []

            for row in values[header_row:]:
                while len(row) < len(headers):
                    row.append('')
                row_dict = {headers[i]: row[i] if i < len(row) else '' for i in range(len(headers))}
                data.append(row_dict)

            logger.info(f"Read {len(data)} rows from sheet {spreadsheet_id}")
            return data

        except HttpError as e:
            logger.error(f"HTTP error reading sheet {spreadsheet_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error reading sheet {spreadsheet_id}: {e}")
            return []

    def read_staff_directory(self, spreadsheet_id: str) -> List[Dict[str, Any]]:
        """Read staff directory sheet"""
        data = self.read_sheet(spreadsheet_id, 'Sheet1')
        staff = []
        for row in data:
            if not row.get('Name', '').strip():
                continue
            staff.append({
                'name': row.get('Name', '').strip(),
                'title': row.get('Title', '').strip(),
                'department': row.get('Department', '').strip(),
                'email': row.get('Email', '').strip(),
                'phone': row.get('Phone', '').strip(),
                'photo': row.get('Photo', '').strip(),
                'type': 'staff'
            })
        return staff

    def read_events(self, spreadsheet_id: str) -> List[Dict[str, Any]]:
        """Read events sheet"""
        data = self.read_sheet(spreadsheet_id, 'Sheet1')
        events = []
        for row in data:
            if not row.get('Event Name', '').strip():
                continue
            events.append({
                'title': row.get('Event Name', '').strip(),
                'date': row.get('Date', '').strip(),
                'time': row.get('Time', '').strip(),
                'location': row.get('Location', '').strip(),
                'description': row.get('Description', '').strip(),
                'link': row.get('Link', '').strip(),
                'type': 'event'
            })
        return events

    def read_public_notices(self, spreadsheet_id: str) -> List[Dict[str, Any]]:
        """Read public notices sheet"""
        data = self.read_sheet(spreadsheet_id, 'Sheet1')
        notices = []
        for row in data:
            if not row.get('Title', '').strip():
                continue
            notices.append({
                'title': row.get('Title', '').strip(),
                'date': row.get('Date Posted', '').strip(),
                'description': row.get('Description', '').strip(),
                'link': row.get('Link', '').strip(),
                'category': row.get('Category', '').strip(),
                'type': 'notice'
            })
        return notices

    def read_job_postings(self, spreadsheet_id: str) -> List[Dict[str, Any]]:
        """Read job postings sheet"""
        data = self.read_sheet(spreadsheet_id, 'Sheet1')
        jobs = []
        for row in data:
            if not row.get('Job Title', '').strip():
                continue
            jobs.append({
                'title': row.get('Job Title', '').strip(),
                'department': row.get('Department', '').strip(),
                'job_type': row.get('Type', 'Full-time').strip(),
                'salary_range': row.get('Salary Range', '').strip(),
                'posted_date': row.get('Posted Date', '').strip(),
                'deadline': row.get('Deadline', '').strip(),
                'description': row.get('Description', '').strip(),
                'link': row.get('Link', '').strip(),
                'type': 'job'
            })
        return jobs

    def read_boards_commissions(self, spreadsheet_id: str) -> List[Dict[str, Any]]:
        """Read boards & commissions sheet"""
        data = self.read_sheet(spreadsheet_id, 'Sheet1')
        boards = []
        for row in data:
            if not row.get('Name', '').strip():
                continue
            boards.append({
                'name': row.get('Name', '').strip(),
                'description': row.get('Description', '').strip(),
                'meeting_schedule': row.get('Meeting Schedule', '').strip(),
                'contact': row.get('Contact', '').strip(),
                'link': row.get('Link', '').strip(),
                'type': 'board'
            })
        return boards

    def read_news(self, spreadsheet_id: str) -> List[Dict[str, Any]]:
        """Read news/press releases sheet"""
        data = self.read_sheet(spreadsheet_id, 'Sheet1')
        news = []
        for row in data:
            if not row.get('Title', '').strip():
                continue
            news.append({
                'title': row.get('Title', '').strip(),
                'date': row.get('Date', '').strip(),
                'summary': row.get('Summary', '').strip(),
                'link': row.get('Link', '').strip(),
                'category': row.get('Category', '').strip(),
                'type': 'news'
            })
        return news

    def read_municipality_config(self, spreadsheet_id: str) -> Dict[str, Any]:
        """Read municipality configuration sheet"""
        data = self.read_sheet(spreadsheet_id, 'Sheet1')
        config = {}
        google_drive_folders = {}
        google_sheets = {}

        for row in data:
            key = row.get('Key', '').strip()
            if not key:
                continue

            value = row.get('Value', '').strip()
            category = row.get('Category', '').strip().lower()

            if category == 'google_drive_folder':
                google_drive_folders[key] = value
            elif category == 'google_sheet':
                google_sheets[key] = value
            else:
                config[key] = value

        if google_drive_folders:
            config['google_drive_folders'] = google_drive_folders
        if google_sheets:
            config['google_sheets'] = google_sheets

        return config


# ============================================================================
# HTML GENERATOR
# ============================================================================

class SimpleHTMLGenerator:
    """Generates HTML components from sheet data"""

    def __init__(self, output_dir: Path):
        """Initialize HTML generator"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_staff_card(self, staff: Dict[str, Any]) -> str:
        """Generate HTML card for a staff member"""
        name = staff.get('name', '')
        title = staff.get('title', '')
        department = staff.get('department', '')
        email = staff.get('email', '')
        phone = staff.get('phone', '')
        photo = staff.get('photo', '')

        contact_items = []
        if department:
            contact_items.append(f'<li><strong>Department:</strong> {department}</li>')
        if email:
            contact_items.append(f'<li><strong>Email:</strong> <a href="mailto:{email}">{email}</a></li>')
        if phone:
            contact_items.append(f'<li><strong>Phone:</strong> <a href="tel:{phone}">{phone}</a></li>')

        contact_html = '\n'.join(contact_items) if contact_items else ''

        return f'''<div class="card staff-card">
    {f'<img src="{photo}" alt="{name}" class="staff-photo">' if photo else ''}
    <h3>{name}</h3>
    <p class="staff-title">{title}</p>
    {f'<ul class="contact-info">{contact_html}</ul>' if contact_html else ''}
</div>'''

    def generate_event_card(self, event: Dict[str, Any]) -> str:
        """Generate HTML card for an event"""
        title = event.get('title', '')
        date = event.get('date', '')
        time = event.get('time', '')
        location = event.get('location', '')
        description = event.get('description', '')
        link = event.get('link', '')

        details = []
        if date:
            details.append(f'<li><strong>Date:</strong> {date}</li>')
        if time:
            details.append(f'<li><strong>Time:</strong> {time}</li>')
        if location:
            details.append(f'<li><strong>Location:</strong> {location}</li>')

        details_html = '\n'.join(details) if details else ''

        return f'''<div class="card event-card">
    <h3>{title}</h3>
    {f'<p>{description}</p>' if description else ''}
    {f'<ul class="event-details">{details_html}</ul>' if details_html else ''}
    {f'<a href="{link}" class="btn">Learn More</a>' if link else ''}
</div>'''

    def generate_notice_card(self, notice: Dict[str, Any]) -> str:
        """Generate HTML card for a public notice"""
        title = notice.get('title', '')
        date = notice.get('date', '')
        description = notice.get('description', '')
        link = notice.get('link', '')
        category = notice.get('category', '')

        return f'''<div class="card notice-card">
    {f'<span class="category-badge">{category}</span>' if category else ''}
    <h3>{title}</h3>
    {f'<p class="notice-date"><strong>Posted:</strong> {date}</p>' if date else ''}
    {f'<p>{description}</p>' if description else ''}
    {f'<a href="{link}" class="btn">View Notice</a>' if link else ''}
</div>'''

    def generate_job_card(self, job: Dict[str, Any]) -> str:
        """Generate HTML card for a job posting"""
        title = job.get('title', '')
        department = job.get('department', '')
        job_type = job.get('job_type', 'Full-time')
        salary_range = job.get('salary_range', '')
        deadline = job.get('deadline', '')
        description = job.get('description', '')
        link = job.get('link', '')

        details = []
        if department:
            details.append(f'<li><strong>Department:</strong> {department}</li>')
        if job_type:
            details.append(f'<li><strong>Type:</strong> {job_type}</li>')
        if salary_range:
            details.append(f'<li><strong>Salary:</strong> {salary_range}</li>')
        if deadline:
            details.append(f'<li><strong>Deadline:</strong> {deadline}</li>')

        details_html = '\n'.join(details) if details else ''

        return f'''<div class="card job-card">
    <h3>{title}</h3>
    {f'<ul class="job-details">{details_html}</ul>' if details_html else ''}
    {f'<p>{description}</p>' if description else ''}
    {f'<a href="{link}" class="btn">Apply Now</a>' if link else ''}
</div>'''

    def generate_board_card(self, board: Dict[str, Any]) -> str:
        """Generate HTML card for a board/commission"""
        name = board.get('name', '')
        description = board.get('description', '')
        meeting_schedule = board.get('meeting_schedule', '')
        contact = board.get('contact', '')
        link = board.get('link', '')

        details = []
        if meeting_schedule:
            details.append(f'<li><strong>Meetings:</strong> {meeting_schedule}</li>')
        if contact:
            details.append(f'<li><strong>Contact:</strong> {contact}</li>')

        details_html = '\n'.join(details) if details else ''

        return f'''<div class="card board-card">
    <h3>{name}</h3>
    {f'<p>{description}</p>' if description else ''}
    {f'<ul class="board-details">{details_html}</ul>' if details_html else ''}
    {f'<a href="{link}" class="btn">More Info</a>' if link else ''}
</div>'''

    def generate_news_card(self, news: Dict[str, Any]) -> str:
        """Generate HTML card for news/press release"""
        title = news.get('title', '')
        date = news.get('date', '')
        summary = news.get('summary', '')
        link = news.get('link', '')
        category = news.get('category', '')

        return f'''<div class="card news-card">
    {f'<span class="category-badge">{category}</span>' if category else ''}
    <h3>{title}</h3>
    {f'<p class="news-date">{date}</p>' if date else ''}
    {f'<p>{summary}</p>' if summary else ''}
    {f'<a href="{link}" class="btn">Read More</a>' if link else ''}
</div>'''

    def generate_cards(self, items: List[Dict[str, Any]]) -> List[str]:
        """Generate HTML cards for a list of items"""
        cards = []
        for item in items:
            item_type = item.get('type', '')
            try:
                if item_type == 'staff':
                    cards.append(self.generate_staff_card(item))
                elif item_type == 'event':
                    cards.append(self.generate_event_card(item))
                elif item_type == 'notice':
                    cards.append(self.generate_notice_card(item))
                elif item_type == 'job':
                    cards.append(self.generate_job_card(item))
                elif item_type == 'board':
                    cards.append(self.generate_board_card(item))
                elif item_type == 'news':
                    cards.append(self.generate_news_card(item))
            except Exception as e:
                logger.error(f"Error generating card for {item_type}: {e}")
                continue
        return cards

    def generate_component_html(self, items: List[Dict[str, Any]], component_name: str) -> str:
        """Generate complete component HTML file"""
        if not items:
            return '<p><em>No items available at this time.</em></p>'

        cards = self.generate_cards(items)
        if not cards:
            return '<p><em>No items available at this time.</em></p>'

        cards_html = '\n'.join(cards)
        return f'''<!-- Generated by Simple Sync Service on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} -->
<!-- Component: {component_name} -->
<div class="grid">
{cards_html}
</div>'''

    def save_component(self, items: List[Dict[str, Any]], filename: str) -> bool:
        """Generate and save component HTML file"""
        try:
            html = self.generate_component_html(items, filename)
            output_file = self.output_dir / filename
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"Generated component: {output_file} ({len(items)} items)")
            return True
        except Exception as e:
            logger.error(f"Failed to save component {filename}: {e}")
            return False

    def save_table_html(self, items: List[Dict[str, Any]], filename: str, columns: List[str]) -> bool:
        """Generate and save table HTML"""
        try:
            if not items:
                html = '<p><em>No data available at this time.</em></p>'
            else:
                header_cells = ''.join([f'<th>{col}</th>' for col in columns])
                header = f'<thead><tr>{header_cells}</tr></thead>'

                rows = []
                for item in items:
                    cells = []
                    for col in columns:
                        value = item.get(col, '') or item.get(col.lower(), '')
                        if 'email' in col.lower() and value:
                            value = f'<a href="mailto:{value}">{value}</a>'
                        elif 'phone' in col.lower() and value:
                            value = f'<a href="tel:{value}">{value}</a>'
                        cells.append(f'<td>{value}</td>')
                    rows.append(f'<tr>{"".join(cells)}</tr>')

                body = f'<tbody>{chr(10).join(rows)}</tbody>'
                html = f'''<!-- Generated by Simple Sync Service on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} -->
<div class="table-responsive">
    <table class="data-table">
        {header}
        {body}
    </table>
</div>'''

            output_file = self.output_dir / filename
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"Generated table: {output_file} ({len(items)} rows)")
            return True
        except Exception as e:
            logger.error(f"Failed to save table {filename}: {e}")
            return False


# ============================================================================
# CONFIG GENERATOR
# ============================================================================

class ConfigGenerator:
    """Generates JavaScript config file from sheet data"""

    def __init__(self, output_dir: Path):
        """Initialize config generator"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _escape_js_string(self, value: str) -> str:
        """Escape string for use in JavaScript"""
        value = value.replace('\\', '\\\\')
        value = value.replace('"', '\\"')
        value = value.replace("'", "\\'")
        value = value.replace('\n', '\\n')
        value = value.replace('\r', '\\r')
        value = value.replace('\t', '\\t')
        return value

    def generate_config_js(self, config_data: Dict[str, Any]) -> str:
        """Generate config.js content from config data"""
        js_content = f'''/**
 * Municipality Configuration
 *
 * This file is AUTO-GENERATED from Google Sheets.
 * DO NOT EDIT MANUALLY - Your changes will be overwritten!
 *
 * To update configuration, edit the Municipality Config Google Sheet.
 * Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
 */

const MunicipalityConfig = {{
'''

        for key, value in sorted(config_data.items()):
            if isinstance(value, dict):
                js_content += f'    {key}: {{\n'
                for sub_key, sub_value in sorted(value.items()):
                    js_content += f'        {sub_key}: "{self._escape_js_string(sub_value)}",\n'
                js_content += '    },\n\n'
            elif isinstance(value, bool):
                js_content += f'    {key}: {str(value).lower()},\n'
            elif isinstance(value, (int, float)):
                js_content += f'    {key}: {value},\n'
            else:
                js_content += f'    {key}: "{self._escape_js_string(str(value))}",\n'

        js_content += '''};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MunicipalityConfig;
}
'''
        return js_content

    def save_config_js(self, config_data: Dict[str, Any]) -> bool:
        """Generate and save config.js file"""
        try:
            js_content = self.generate_config_js(config_data)
            output_file = self.output_dir / 'config.js'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(js_content)
            logger.info(f"Generated config.js: {output_file} ({len(config_data)} config values)")
            return True
        except Exception as e:
            logger.error(f"Failed to save config.js: {e}")
            return False

    def save_config_json(self, config_data: Dict[str, Any]) -> bool:
        """Also save as JSON for easier debugging/inspection"""
        try:
            output_file = self.output_dir / 'config.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
            logger.info(f"Generated config.json: {output_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save config.json: {e}")
            return False


# ============================================================================
# SYNC SERVICE
# ============================================================================

class SimpleSyncService:
    """Simple sync service that reads sheets and generates HTML"""

    def __init__(self, config_file: str):
        """Initialize sync service"""
        self.config = self._load_config(config_file)
        self.sheets_reader = GoogleSheetsReader(self.config['service_account_file'])
        self.html_generator = SimpleHTMLGenerator(Path(self.config['output_dir']))
        config_output_dir = Path(self.config.get('config_output_dir', '../assets/js'))
        self.config_generator = ConfigGenerator(config_output_dir)

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded config from {config_file}")
            return config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    def sync_municipality_config(self):
        """Sync municipality config from Google Sheets and generate config.js"""
        sheet_id = self.config['sheets'].get('municipality_config')
        if not sheet_id:
            logger.warning("No municipality_config sheet ID configured - skipping config.js generation")
            return

        logger.info("Syncing municipality config...")
        try:
            config_data = self.sheets_reader.read_municipality_config(sheet_id)
            self.config_generator.save_config_js(config_data)
            self.config_generator.save_config_json(config_data)
            logger.info(f"✓ Municipality config synced ({len(config_data)} config values)")
        except Exception as e:
            logger.error(f"✗ Failed to sync municipality config: {e}")

    def sync_staff_directory(self):
        """Sync staff directory from Google Sheets"""
        sheet_id = self.config['sheets'].get('staff_directory')
        if not sheet_id:
            logger.warning("No staff_directory sheet ID configured")
            return

        logger.info("Syncing staff directory...")
        try:
            staff_data = self.sheets_reader.read_staff_directory(sheet_id)
            self.html_generator.save_component(staff_data, 'staff_directory.html')
            self.html_generator.save_table_html(staff_data, 'staff_directory_table.html',
                                               columns=['Name', 'Title', 'Department', 'Email', 'Phone'])
            logger.info(f"✓ Staff directory synced ({len(staff_data)} employees)")
        except Exception as e:
            logger.error(f"✗ Failed to sync staff directory: {e}")

    def sync_events(self):
        """Sync events from Google Sheets"""
        sheet_id = self.config['sheets'].get('events')
        if not sheet_id:
            logger.warning("No events sheet ID configured")
            return

        logger.info("Syncing events...")
        try:
            events_data = self.sheets_reader.read_events(sheet_id)
            self.html_generator.save_component(events_data, 'events.html')
            logger.info(f"✓ Events synced ({len(events_data)} events)")
        except Exception as e:
            logger.error(f"✗ Failed to sync events: {e}")

    def sync_public_notices(self):
        """Sync public notices from Google Sheets"""
        sheet_id = self.config['sheets'].get('public_notices')
        if not sheet_id:
            logger.warning("No public_notices sheet ID configured")
            return

        logger.info("Syncing public notices...")
        try:
            notices_data = self.sheets_reader.read_public_notices(sheet_id)
            self.html_generator.save_component(notices_data, 'public_notices.html')
            logger.info(f"✓ Public notices synced ({len(notices_data)} notices)")
        except Exception as e:
            logger.error(f"✗ Failed to sync public notices: {e}")

    def sync_job_postings(self):
        """Sync job postings from Google Sheets"""
        sheet_id = self.config['sheets'].get('job_postings')
        if not sheet_id:
            logger.warning("No job_postings sheet ID configured")
            return

        logger.info("Syncing job postings...")
        try:
            jobs_data = self.sheets_reader.read_job_postings(sheet_id)
            self.html_generator.save_component(jobs_data, 'job_postings.html')
            logger.info(f"✓ Job postings synced ({len(jobs_data)} jobs)")
        except Exception as e:
            logger.error(f"✗ Failed to sync job postings: {e}")

    def sync_boards_commissions(self):
        """Sync boards & commissions from Google Sheets"""
        sheet_id = self.config['sheets'].get('boards_commissions')
        if not sheet_id:
            logger.warning("No boards_commissions sheet ID configured")
            return

        logger.info("Syncing boards & commissions...")
        try:
            boards_data = self.sheets_reader.read_boards_commissions(sheet_id)
            self.html_generator.save_component(boards_data, 'boards_commissions.html')
            logger.info(f"✓ Boards & commissions synced ({len(boards_data)} boards)")
        except Exception as e:
            logger.error(f"✗ Failed to sync boards & commissions: {e}")

    def sync_news(self):
        """Sync news from Google Sheets"""
        sheet_id = self.config['sheets'].get('news')
        if not sheet_id:
            logger.warning("No news sheet ID configured")
            return

        logger.info("Syncing news...")
        try:
            news_data = self.sheets_reader.read_news(sheet_id)
            self.html_generator.save_component(news_data, 'news_press_releases.html')
            logger.info(f"✓ News synced ({len(news_data)} articles)")
        except Exception as e:
            logger.error(f"✗ Failed to sync news: {e}")

    def sync_all(self):
        """Sync all configured sheets"""
        logger.info("=" * 60)
        logger.info("Starting Simple Sync Service")
        logger.info("=" * 60)

        self.sync_municipality_config()
        self.sync_staff_directory()
        self.sync_events()
        self.sync_public_notices()
        self.sync_job_postings()
        self.sync_boards_commissions()
        self.sync_news()

        logger.info("=" * 60)
        logger.info("Sync complete!")
        logger.info("=" * 60)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Simple Sync Service - No Database Required'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='simple_sync_config.json',
        help='Path to config file (default: simple_sync_config.json)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (default: continuous monitoring)'
    )

    args = parser.parse_args()

    try:
        sync_service = SimpleSyncService(args.config)

        if args.once:
            sync_service.sync_all()
        else:
            import time
            while True:
                sync_service.sync_all()
                logger.info("Waiting 5 minutes before next sync...")
                time.sleep(300)

    except KeyboardInterrupt:
        logger.info("Sync service stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

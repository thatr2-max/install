#!/usr/bin/env python3
"""
Simple Sync Service - Database-less version
Reads Google Sheets and generates HTML components directly
No PostgreSQL required!

Usage:
    python simple_sync.py --config config.json

Config file format:
{
    "service_account_file": "path/to/service-account.json",
    "output_dir": "../components",
    "sheets": {
        "staff_directory": "SPREADSHEET_ID_HERE",
        "events": "SPREADSHEET_ID_HERE",
        "public_notices": "SPREADSHEET_ID_HERE",
        "job_postings": "SPREADSHEET_ID_HERE",
        "boards_commissions": "SPREADSHEET_ID_HERE",
        "news": "SPREADSHEET_ID_HERE"
    }
}
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sheets_reader import GoogleSheetsReader
from simple_html_generator import SimpleHTMLGenerator

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


class SimpleSyncService:
    """Simple sync service that reads sheets and generates HTML"""

    def __init__(self, config_file: str):
        """
        Initialize sync service

        Args:
            config_file: Path to JSON config file
        """
        self.config = self._load_config(config_file)
        self.sheets_reader = GoogleSheetsReader(
            self.config['service_account_file']
        )
        self.html_generator = SimpleHTMLGenerator(
            Path(self.config['output_dir'])
        )

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

    def sync_staff_directory(self):
        """Sync staff directory from Google Sheets"""
        sheet_id = self.config['sheets'].get('staff_directory')

        if not sheet_id:
            logger.warning("No staff_directory sheet ID configured")
            return

        logger.info("Syncing staff directory...")

        try:
            # Read sheet data
            staff_data = self.sheets_reader.read_staff_directory(sheet_id)

            # Generate HTML component
            self.html_generator.save_component(
                staff_data,
                'staff_directory.html'
            )

            # Also generate as table
            self.html_generator.save_table_html(
                staff_data,
                'staff_directory_table.html',
                columns=['Name', 'Title', 'Department', 'Email', 'Phone']
            )

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
            # Read sheet data
            events_data = self.sheets_reader.read_events(sheet_id)

            # Generate HTML component
            self.html_generator.save_component(
                events_data,
                'events.html'
            )

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
            # Read sheet data
            notices_data = self.sheets_reader.read_public_notices(sheet_id)

            # Generate HTML component
            self.html_generator.save_component(
                notices_data,
                'public_notices.html'
            )

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
            # Read sheet data
            jobs_data = self.sheets_reader.read_job_postings(sheet_id)

            # Generate HTML component
            self.html_generator.save_component(
                jobs_data,
                'job_postings.html'
            )

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
            # Read sheet data
            boards_data = self.sheets_reader.read_boards_commissions(sheet_id)

            # Generate HTML component
            self.html_generator.save_component(
                boards_data,
                'boards_commissions.html'
            )

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
            # Read sheet data
            news_data = self.sheets_reader.read_news(sheet_id)

            # Generate HTML component
            self.html_generator.save_component(
                news_data,
                'news_press_releases.html'
            )

            logger.info(f"✓ News synced ({len(news_data)} articles)")

        except Exception as e:
            logger.error(f"✗ Failed to sync news: {e}")

    def sync_all(self):
        """Sync all configured sheets"""
        logger.info("=" * 60)
        logger.info("Starting Simple Sync Service")
        logger.info("=" * 60)

        self.sync_staff_directory()
        self.sync_events()
        self.sync_public_notices()
        self.sync_job_postings()
        self.sync_boards_commissions()
        self.sync_news()

        logger.info("=" * 60)
        logger.info("Sync complete!")
        logger.info("=" * 60)


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
            # Run once and exit
            sync_service.sync_all()
        else:
            # Run continuously (could add scheduling here)
            import time
            while True:
                sync_service.sync_all()
                logger.info("Waiting 5 minutes before next sync...")
                time.sleep(300)  # 5 minutes

    except KeyboardInterrupt:
        logger.info("Sync service stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

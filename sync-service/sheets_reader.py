"""
Google Sheets Reader
Reads Google Sheets data and converts to structured format
No database required - direct sheet to HTML generation
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger('sheets_reader')


class GoogleSheetsReader:
    """Reads data from Google Sheets"""

    def __init__(self, service_account_file: str):
        """
        Initialize Google Sheets API client

        Args:
            service_account_file: Path to service account JSON file
        """
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

    def read_sheet(
        self,
        spreadsheet_id: str,
        range_name: str = 'Sheet1',
        header_row: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Read a Google Sheet and return as list of dicts

        Args:
            spreadsheet_id: The ID of the spreadsheet
            range_name: The range to read (default: Sheet1)
            header_row: Which row contains headers (default: 1)

        Returns:
            List of dicts where keys are column headers
        """
        try:
            # Read the sheet
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()

            values = result.get('values', [])

            if not values:
                logger.warning(f"No data found in sheet {spreadsheet_id}")
                return []

            # First row is headers
            headers = values[header_row - 1]

            # Convert remaining rows to dicts
            data = []
            for row in values[header_row:]:
                # Pad row if it's shorter than headers
                while len(row) < len(headers):
                    row.append('')

                # Create dict from row
                row_dict = {
                    headers[i]: row[i] if i < len(row) else ''
                    for i in range(len(headers))
                }
                data.append(row_dict)

            logger.info(f"Read {len(data)} rows from sheet {spreadsheet_id}")
            return data

        except HttpError as e:
            logger.error(f"HTTP error reading sheet {spreadsheet_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error reading sheet {spreadsheet_id}: {e}")
            return []

    def read_multiple_sheets(
        self,
        spreadsheet_id: str,
        sheet_names: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Read multiple sheets from one spreadsheet

        Args:
            spreadsheet_id: The ID of the spreadsheet
            sheet_names: List of sheet names to read

        Returns:
            Dict mapping sheet names to their data
        """
        results = {}

        for sheet_name in sheet_names:
            data = self.read_sheet(spreadsheet_id, sheet_name)
            results[sheet_name] = data

        return results

    def read_staff_directory(self, spreadsheet_id: str) -> List[Dict[str, Any]]:
        """
        Read staff directory sheet with expected columns:
        Name, Title, Department, Email, Phone, Photo

        Args:
            spreadsheet_id: The ID of the staff directory spreadsheet

        Returns:
            List of staff member dicts
        """
        data = self.read_sheet(spreadsheet_id, 'Staff Directory')

        # Normalize and validate data
        staff = []
        for row in data:
            # Skip empty rows
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
        """
        Read events sheet with expected columns:
        Event Name, Date, Time, Location, Description, Link

        Args:
            spreadsheet_id: The ID of the events spreadsheet

        Returns:
            List of event dicts
        """
        data = self.read_sheet(spreadsheet_id, 'Events')

        events = []
        for row in data:
            # Skip empty rows
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
        """
        Read public notices sheet with expected columns:
        Title, Date Posted, Description, Link, Category

        Args:
            spreadsheet_id: The ID of the public notices spreadsheet

        Returns:
            List of notice dicts
        """
        data = self.read_sheet(spreadsheet_id, 'Public Notices')

        notices = []
        for row in data:
            # Skip empty rows
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
        """
        Read job postings sheet with expected columns:
        Job Title, Department, Type, Salary Range, Posted Date, Deadline, Description, Link

        Args:
            spreadsheet_id: The ID of the job postings spreadsheet

        Returns:
            List of job posting dicts
        """
        data = self.read_sheet(spreadsheet_id, 'Job Postings')

        jobs = []
        for row in data:
            # Skip empty rows
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
        """
        Read boards & commissions sheet with expected columns:
        Name, Description, Meeting Schedule, Contact, Link

        Args:
            spreadsheet_id: The ID of the boards & commissions spreadsheet

        Returns:
            List of board/commission dicts
        """
        data = self.read_sheet(spreadsheet_id, 'Boards & Commissions')

        boards = []
        for row in data:
            # Skip empty rows
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
        """
        Read news/press releases sheet with expected columns:
        Title, Date, Summary, Link, Category

        Args:
            spreadsheet_id: The ID of the news spreadsheet

        Returns:
            List of news article dicts
        """
        data = self.read_sheet(spreadsheet_id, 'News')

        news = []
        for row in data:
            # Skip empty rows
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

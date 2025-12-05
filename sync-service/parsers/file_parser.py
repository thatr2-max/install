"""
File Parsers for Different File Types
Converts Google Drive files into structured data
"""

import logging
from typing import Dict, Any, Optional
import io
from datetime import datetime

logger = logging.getLogger('sync_worker')


class FileParser:
    """Base class for file parsers"""

    def __init__(self, drive_service):
        self.drive_service = drive_service

    def parse(self, file_metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse a file and return structured data

        Args:
            file_metadata: Google Drive file metadata

        Returns:
            Structured data dict or None if parsing failed
        """
        raise NotImplementedError("Subclasses must implement parse()")


class SpreadsheetParser(FileParser):
    """Parser for Google Sheets and Excel files"""

    def parse(self, file_metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse spreadsheet data"""
        try:
            file_id = file_metadata['id']
            file_name = file_metadata['name']

            # Export Google Sheets as CSV
            if file_metadata['mimeType'] == 'application/vnd.google-apps.spreadsheet':
                request = self.drive_service.files().export_media(
                    fileId=file_id,
                    mimeType='text/csv'
                )
            else:
                request = self.drive_service.files().get_media(fileId=file_id)

            file_content = request.execute()

            # Parse CSV content
            import csv
            csv_reader = csv.DictReader(io.StringIO(file_content.decode('utf-8')))
            rows = list(csv_reader)

            return {
                'type': 'spreadsheet',
                'name': file_name,
                'rows': rows,
                'row_count': len(rows),
                'columns': list(rows[0].keys()) if rows else [],
                'last_modified': file_metadata.get('modifiedTime'),
                'web_view_link': file_metadata.get('webViewLink'),
            }

        except Exception as e:
            logger.error(f"Failed to parse spreadsheet {file_metadata.get('name')}: {e}")
            return None


class MarkdownParser(FileParser):
    """Parser for Markdown files"""

    def parse(self, file_metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse markdown content"""
        try:
            file_id = file_metadata['id']
            file_name = file_metadata['name']

            request = self.drive_service.files().get_media(fileId=file_id)
            file_content = request.execute().decode('utf-8')

            # Extract title from first H1 or use filename
            title = file_name.replace('.md', '')
            lines = file_content.split('\n')
            for line in lines:
                if line.startswith('# '):
                    title = line[2:].strip()
                    break

            return {
                'type': 'markdown',
                'name': file_name,
                'title': title,
                'content': file_content,
                'html': self._markdown_to_html(file_content),
                'last_modified': file_metadata.get('modifiedTime'),
                'web_view_link': file_metadata.get('webViewLink'),
            }

        except Exception as e:
            logger.error(f"Failed to parse markdown {file_metadata.get('name')}: {e}")
            return None

    def _markdown_to_html(self, markdown_text: str) -> str:
        """Convert markdown to HTML (basic conversion)"""
        try:
            # Try to use markdown library if available
            import markdown
            return markdown.markdown(markdown_text)
        except ImportError:
            # Fallback: wrap in pre tag
            return f'<pre>{markdown_text}</pre>'


class DocumentParser(FileParser):
    """Parser for Google Docs and Word documents"""

    def parse(self, file_metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse document content"""
        try:
            file_id = file_metadata['id']
            file_name = file_metadata['name']

            # Export Google Docs as plain text
            if file_metadata['mimeType'] == 'application/vnd.google-apps.document':
                request = self.drive_service.files().export_media(
                    fileId=file_id,
                    mimeType='text/plain'
                )
                content = request.execute().decode('utf-8')
            else:
                # For Word docs, just get metadata
                content = "[Word document - view in Google Drive]"

            return {
                'type': 'document',
                'name': file_name,
                'title': file_name.rsplit('.', 1)[0],
                'content': content[:500],  # First 500 chars
                'preview': content[:200] if content else '',
                'last_modified': file_metadata.get('modifiedTime'),
                'web_view_link': file_metadata.get('webViewLink'),
                'size': file_metadata.get('size', 0),
            }

        except Exception as e:
            logger.error(f"Failed to parse document {file_metadata.get('name')}: {e}")
            return None


class PDFParser(FileParser):
    """Parser for PDF files"""

    def parse(self, file_metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse PDF metadata"""
        try:
            return {
                'type': 'pdf',
                'name': file_metadata['name'],
                'title': file_metadata['name'].replace('.pdf', ''),
                'last_modified': file_metadata.get('modifiedTime'),
                'web_view_link': file_metadata.get('webViewLink'),
                'download_link': file_metadata.get('webContentLink'),
                'size': file_metadata.get('size', 0),
                'thumbnail_link': file_metadata.get('thumbnailLink'),
            }

        except Exception as e:
            logger.error(f"Failed to parse PDF {file_metadata.get('name')}: {e}")
            return None


class TextParser(FileParser):
    """Parser for plain text files"""

    def parse(self, file_metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse text content"""
        try:
            file_id = file_metadata['id']
            file_name = file_metadata['name']

            request = self.drive_service.files().get_media(fileId=file_id)
            content = request.execute().decode('utf-8')

            return {
                'type': 'text',
                'name': file_name,
                'title': file_name,
                'content': content,
                'preview': content[:200] if content else '',
                'last_modified': file_metadata.get('modifiedTime'),
                'web_view_link': file_metadata.get('webViewLink'),
            }

        except Exception as e:
            logger.error(f"Failed to parse text file {file_metadata.get('name')}: {e}")
            return None


class VideoParser(FileParser):
    """Parser for video files"""

    def parse(self, file_metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse video metadata"""
        try:
            return {
                'type': 'video',
                'name': file_metadata['name'],
                'title': file_metadata['name'],
                'last_modified': file_metadata.get('modifiedTime'),
                'web_view_link': file_metadata.get('webViewLink'),
                'thumbnail_link': file_metadata.get('thumbnailLink'),
                'size': file_metadata.get('size', 0),
                'mime_type': file_metadata.get('mimeType'),
            }

        except Exception as e:
            logger.error(f"Failed to parse video {file_metadata.get('name')}: {e}")
            return None


def get_parser(mime_type: str, drive_service) -> FileParser:
    """
    Get appropriate parser for a file type

    Args:
        mime_type: MIME type of the file
        drive_service: Google Drive service instance

    Returns:
        FileParser instance
    """
    if mime_type in ['application/vnd.google-apps.spreadsheet',
                     'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     'text/csv']:
        return SpreadsheetParser(drive_service)

    elif mime_type in ['text/markdown']:
        return MarkdownParser(drive_service)

    elif mime_type in ['application/vnd.google-apps.document',
                       'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
        return DocumentParser(drive_service)

    elif mime_type == 'application/pdf':
        return PDFParser(drive_service)

    elif mime_type.startswith('video/'):
        return VideoParser(drive_service)

    elif mime_type.startswith('text/'):
        return TextParser(drive_service)

    else:
        # Return a generic parser that just gets metadata
        return PDFParser(drive_service)

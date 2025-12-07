"""
HTML Generator
Generates static HTML cards from database data
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import json

logger = logging.getLogger('html_generator')


class HTMLGenerator:
    """Generates HTML cards from structured data"""

    def __init__(self, output_dir: Path, template_dir: Optional[Path] = None):
        """
        Initialize HTML generator

        Args:
            output_dir: Directory to output generated HTML files
            template_dir: Directory containing HTML templates
        """
        self.output_dir = Path(output_dir)
        self.template_dir = template_dir or Path(__file__).parent / 'templates'
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def generate_card(self, data: Dict[str, Any], template_type: str = 'document_card') -> str:
        """
        Generate HTML card from data

        Args:
            data: Structured data dict
            template_type: Type of template to use

        Returns:
            HTML string
        """
        try:
            data_type = data.get('type', 'document')

            if data_type == 'pdf':
                return self._generate_document_card(data)
            elif data_type == 'spreadsheet':
                return self._generate_spreadsheet_card(data)
            elif data_type == 'markdown':
                return self._generate_markdown_card(data)
            elif data_type == 'video':
                return self._generate_video_card(data)
            else:
                return self._generate_document_card(data)

        except Exception as e:
            logger.error(f"Failed to generate card for {data.get('name')}: {e}")
            return self._generate_error_card(data.get('name', 'Unknown'))

    def _generate_document_card(self, data: Dict[str, Any]) -> str:
        """Generate a document card"""
        name = self._escape_html(data.get('name', 'Untitled'))
        title = self._escape_html(data.get('title', name))
        last_modified = self._format_date(data.get('last_modified'))
        web_view_link = data.get('web_view_link', '#')
        download_link = data.get('download_link', web_view_link)
        size = self._format_file_size(data.get('size', 0))

        html = f'''
        <div class="card document-card" data-file-type="pdf">
            <div class="card-icon">📄</div>
            <h3><a href="{web_view_link}" target="_blank">{title}</a></h3>
            <div class="card-meta">
                <span class="date">{last_modified}</span>
                {f'<span class="size">{size}</span>' if size else ''}
            </div>
            <div class="card-actions">
                <a href="{web_view_link}" target="_blank" class="btn btn-secondary">View</a>
                {f'<a href="{download_link}" target="_blank" class="btn btn-secondary">Download</a>' if download_link != '#' else ''}
            </div>
        </div>
        '''
        return html.strip()

    def _generate_spreadsheet_card(self, data: Dict[str, Any]) -> str:
        """Generate a spreadsheet/data card"""
        name = self._escape_html(data.get('name', 'Untitled'))
        title = self._escape_html(data.get('title', name))
        row_count = data.get('row_count', 0)
        columns = data.get('columns', [])
        last_modified = self._format_date(data.get('last_modified'))
        web_view_link = data.get('web_view_link', '#')

        html = f'''
        <div class="card data-card" data-file-type="spreadsheet">
            <div class="card-icon">📊</div>
            <h3><a href="{web_view_link}" target="_blank">{title}</a></h3>
            <div class="card-meta">
                <span class="row-count">{row_count} rows</span>
                <span class="date">{last_modified}</span>
            </div>
            <div class="card-actions">
                <a href="{web_view_link}" target="_blank" class="btn btn-secondary">View Data</a>
            </div>
        </div>
        '''
        return html.strip()

    def _generate_markdown_card(self, data: Dict[str, Any]) -> str:
        """Generate a markdown/article card"""
        title = self._escape_html(data.get('title', 'Untitled'))
        preview = data.get('html', data.get('content', ''))[:200]
        last_modified = self._format_date(data.get('last_modified'))
        web_view_link = data.get('web_view_link', '#')

        html = f'''
        <div class="card article-card" data-file-type="markdown">
            <div class="card-icon">📝</div>
            <h3><a href="{web_view_link}" target="_blank">{title}</a></h3>
            <div class="card-preview">
                {preview}...
            </div>
            <div class="card-meta">
                <span class="date">{last_modified}</span>
            </div>
            <div class="card-actions">
                <a href="{web_view_link}" target="_blank" class="btn btn-secondary">Read More</a>
            </div>
        </div>
        '''
        return html.strip()

    def _generate_video_card(self, data: Dict[str, Any]) -> str:
        """Generate a video card"""
        name = self._escape_html(data.get('name', 'Untitled'))
        title = self._escape_html(data.get('title', name))
        last_modified = self._format_date(data.get('last_modified'))
        web_view_link = data.get('web_view_link', '#')
        thumbnail = data.get('thumbnail_link', '')
        size = self._format_file_size(data.get('size', 0))

        html = f'''
        <div class="card video-card" data-file-type="video">
            <div class="card-icon">🎥</div>
            {f'<img src="{thumbnail}" alt="{title}" class="card-thumbnail">' if thumbnail else ''}
            <h3><a href="{web_view_link}" target="_blank">{title}</a></h3>
            <div class="card-meta">
                <span class="date">{last_modified}</span>
                {f'<span class="size">{size}</span>' if size else ''}
            </div>
            <div class="card-actions">
                <a href="{web_view_link}" target="_blank" class="btn btn-secondary">Watch</a>
            </div>
        </div>
        '''
        return html.strip()

    def _generate_error_card(self, filename: str) -> str:
        """Generate an error card"""
        html = f'''
        <div class="card error-card">
            <div class="card-icon">⚠️</div>
            <h3>{self._escape_html(filename)}</h3>
            <p>Error loading this file. Please try again later.</p>
        </div>
        '''
        return html.strip()

    def generate_component_html(
        self,
        folder_name: str,
        files_data: List[Dict[str, Any]]
    ) -> str:
        """
        Generate component HTML (just cards, no page wrapper) for a folder

        Args:
            folder_name: Name of the folder
            files_data: List of file data dicts

        Returns:
            HTML string containing just the cards
        """
        cards_html = []
        for file_data in files_data:
            try:
                data = json.loads(file_data['data']) if isinstance(file_data['data'], str) else file_data['data']
                card = self.generate_card(data)
                cards_html.append(card)
            except Exception as e:
                logger.error(f"Error generating card for {file_data.get('file_name')}: {e}")
                cards_html.append(self._generate_error_card(file_data.get('file_name', 'Unknown')))

        if cards_html:
            # Return just the cards wrapped in a grid div
            return f'<div class="grid">\n{chr(10).join(cards_html)}\n</div>'
        else:
            return '<p><em>No files available at this time.</em></p>'

    def generate_folder_html(
        self,
        folder_name: str,
        files_data: List[Dict[str, Any]]
    ) -> str:
        """
        Generate complete HTML file for a folder

        Args:
            folder_name: Name of the folder
            files_data: List of file data dicts

        Returns:
            Complete HTML document as string
        """
        cards_html = []
        for file_data in files_data:
            try:
                data = json.loads(file_data['data']) if isinstance(file_data['data'], str) else file_data['data']
                card = self.generate_card(data)
                cards_html.append(card)
            except Exception as e:
                logger.error(f"Error generating card for {file_data.get('file_name')}: {e}")
                cards_html.append(self._generate_error_card(file_data.get('file_name', 'Unknown')))

        folder_title = folder_name.replace('_', ' ').title()

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{folder_title} - Government Portal</title>
    <link rel="stylesheet" href="../assets/css/styles.css">
</head>
<body>
    <div id="header"></div>

    <main id="main-content" role="main">
        <h1>{folder_title}</h1>

        <div class="grid">
            {chr(10).join(cards_html) if cards_html else '<p><em>No files available at this time.</em></p>'}
        </div>
    </main>

    <div id="footer"></div>

    <script src="../assets/js/component-loader.js"></script>
</body>
</html>'''

        return html

    def save_component_html(
        self,
        folder_name: str,
        files_data: List[Dict[str, Any]]
    ) -> bool:
        """
        Generate and save component HTML file (just cards) for a folder

        Args:
            folder_name: Name of the folder
            files_data: List of file data dicts

        Returns:
            True if successful
        """
        try:
            html = self.generate_component_html(folder_name, files_data)
            output_file = self.output_dir / f"{folder_name}.html"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)

            logger.info(f"Generated component HTML file: {output_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save component HTML for folder {folder_name}: {e}")
            return False

    def save_folder_html(
        self,
        folder_name: str,
        files_data: List[Dict[str, Any]]
    ) -> bool:
        """
        Generate and save HTML file for a folder

        Args:
            folder_name: Name of the folder
            files_data: List of file data dicts

        Returns:
            True if successful
        """
        try:
            html = self.generate_folder_html(folder_name, files_data)
            output_file = self.output_dir / f"{folder_name}.html"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)

            logger.info(f"Generated HTML file: {output_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save HTML for folder {folder_name}: {e}")
            return False

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        if not text:
            return ''
        return (str(text)
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#x27;'))

    def _format_date(self, date_str: Optional[str]) -> str:
        """Format ISO date string to readable format"""
        if not date_str:
            return 'Unknown'

        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%B %d, %Y')
        except:
            return date_str

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in bytes to human-readable format"""
        if size_bytes == 0:
            return ''

        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0

        return f"{size_bytes:.1f} TB"

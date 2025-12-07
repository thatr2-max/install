"""
Simple HTML Generator
Generates HTML directly from Google Sheets data
No database required
"""

import logging
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger('html_generator')


class SimpleHTMLGenerator:
    """Generates HTML components from sheet data"""

    def __init__(self, output_dir: Path):
        """
        Initialize HTML generator

        Args:
            output_dir: Directory to output HTML files
        """
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

        # Build contact info list
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

        card_content = f'''<div class="card event-card">
    <h3>{title}</h3>
    {f'<p>{description}</p>' if description else ''}
    {f'<ul class="event-details">{details_html}</ul>' if details_html else ''}
    {f'<a href="{link}" class="btn">Learn More</a>' if link else ''}
</div>'''

        return card_content

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
        """
        Generate HTML cards for a list of items

        Args:
            items: List of data dicts with 'type' field

        Returns:
            List of HTML card strings
        """
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
                else:
                    logger.warning(f"Unknown item type: {item_type}")

            except Exception as e:
                logger.error(f"Error generating card for {item_type}: {e}")
                continue

        return cards

    def generate_component_html(
        self,
        items: List[Dict[str, Any]],
        component_name: str
    ) -> str:
        """
        Generate complete component HTML file

        Args:
            items: List of data items
            component_name: Name of the component

        Returns:
            Complete HTML string with cards wrapped in grid
        """
        if not items:
            return '<p><em>No items available at this time.</em></p>'

        cards = self.generate_cards(items)

        if not cards:
            return '<p><em>No items available at this time.</em></p>'

        cards_html = '\n'.join(cards)
        return f'''<!-- Generated by Simple HTML Generator on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} -->
<!-- Component: {component_name} -->
<div class="grid">
{cards_html}
</div>'''

    def save_component(
        self,
        items: List[Dict[str, Any]],
        filename: str
    ) -> bool:
        """
        Generate and save component HTML file

        Args:
            items: List of data items
            filename: Output filename (e.g., 'staff_directory.html')

        Returns:
            True if successful, False otherwise
        """
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

    def save_table_html(
        self,
        items: List[Dict[str, Any]],
        filename: str,
        columns: List[str]
    ) -> bool:
        """
        Generate and save table HTML (for staff directory, etc.)

        Args:
            items: List of data items
            filename: Output filename
            columns: List of column names to include

        Returns:
            True if successful, False otherwise
        """
        try:
            if not items:
                html = '<p><em>No data available at this time.</em></p>'
            else:
                # Generate table header
                header_cells = ''.join([f'<th>{col}</th>' for col in columns])
                header = f'<thead><tr>{header_cells}</tr></thead>'

                # Generate table rows
                rows = []
                for item in items:
                    cells = []
                    for col in columns:
                        # Get value from item (case-insensitive key match)
                        value = item.get(col, '') or item.get(col.lower(), '')

                        # Format email and phone as links
                        if 'email' in col.lower() and value:
                            value = f'<a href="mailto:{value}">{value}</a>'
                        elif 'phone' in col.lower() and value:
                            value = f'<a href="tel:{value}">{value}</a>'

                        cells.append(f'<td>{value}</td>')

                    rows.append(f'<tr>{"".join(cells)}</tr>')

                body = f'<tbody>{chr(10).join(rows)}</tbody>'
                html = f'''<!-- Generated by Simple HTML Generator on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} -->
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

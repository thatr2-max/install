"""
Configuration for Government Portal Sync Service
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
LOG_DIR = BASE_DIR / 'logs'
HTML_OUTPUT_DIR = PROJECT_ROOT / 'components'

# Create directories if they don't exist
LOG_DIR.mkdir(exist_ok=True)
HTML_OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Database configuration
DATABASE = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'gov_portal_sync'),
    'user': os.getenv('DB_USER', 'sync_user'),
    'password': os.getenv('DB_PASSWORD', 'your_password_here'),
}

# Google Drive API configuration
GOOGLE_DRIVE = {
    'service_account_file': os.getenv(
        'GOOGLE_SERVICE_ACCOUNT',
        str(BASE_DIR / 'credentials' / 'service-account.json')
    ),
    'scopes': ['https://www.googleapis.com/auth/drive.readonly'],
    'root_folder_id': os.getenv('DRIVE_ROOT_FOLDER_ID', ''),
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(asctime)s | %(levelname)s | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'sync.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed',
            'level': 'DEBUG',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'error.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed',
            'level': 'ERROR',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'INFO',
        }
    },
    'loggers': {
        'sync_worker': {
            'handlers': ['file', 'error_file', 'console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'html_generator': {
            'handlers': ['file', 'error_file', 'console'],
            'level': 'DEBUG',
            'propagate': False
        },
        'database': {
            'handlers': ['file', 'error_file', 'console'],
            'level': 'DEBUG',
            'propagate': False
        }
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO'
    }
}

# Sync configuration
SYNC_CONFIG = {
    'poll_interval': int(os.getenv('SYNC_POLL_INTERVAL', '300')),  # 5 minutes
    'max_retries': int(os.getenv('MAX_RETRIES', '3')),
    'retry_delay': int(os.getenv('RETRY_DELAY', '60')),  # 1 minute
    'batch_size': int(os.getenv('BATCH_SIZE', '50')),
    'enable_push_notifications': os.getenv('ENABLE_PUSH_NOTIFICATIONS', 'false').lower() == 'true',
}

# Supported file types and parsers
FILE_PARSERS = {
    'application/vnd.google-apps.spreadsheet': 'spreadsheet',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'spreadsheet',
    'text/csv': 'csv',
    'text/markdown': 'markdown',
    'text/plain': 'text',
    'application/pdf': 'pdf',
    'application/vnd.google-apps.document': 'document',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'document',
}

# HTML template configuration
HTML_TEMPLATES = {
    'card': 'card_template.html',
    'document_card': 'document_card_template.html',
    'event_card': 'event_card_template.html',
    'news_card': 'news_card_template.html',
    'job_card': 'job_card_template.html',
    'notice_card': 'notice_card_template.html',
    'video_card': 'video_card_template.html',
}

# Notification configuration (optional)
NOTIFICATIONS = {
    'enabled': os.getenv('NOTIFICATIONS_ENABLED', 'false').lower() == 'true',
    'email': {
        'smtp_host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
        'smtp_port': int(os.getenv('SMTP_PORT', '587')),
        'smtp_user': os.getenv('SMTP_USER', ''),
        'smtp_password': os.getenv('SMTP_PASSWORD', ''),
        'from_email': os.getenv('FROM_EMAIL', ''),
        'to_emails': os.getenv('TO_EMAILS', '').split(','),
    }
}

# Folder name mapping (Drive folder name to local folder name)
FOLDER_MAPPING = {
    'Meeting Agendas': 'meeting_agendas',
    'Meeting Minutes': 'meeting_minutes',
    'Meeting Packets': 'meeting_packets',
    'Meeting Recordings': 'meeting_recordings',
    'Budgets': 'budgets',
    'Financial Reports': 'financial_reports',
    'Ordinances': 'ordinances',
    'Resolutions': 'resolutions',
    'Public Notices': 'public_notices',
    'Event Flyers': 'event_flyers',
    'Job Postings': 'job_postings',
    'News & Press Releases': 'news_press_releases',
    'Boards & Commissions': 'boards_commissions',
}

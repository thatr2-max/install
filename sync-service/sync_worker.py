"""
Sync Worker - Main service that monitors Google Drive and syncs files
"""

import logging
import logging.config
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sys
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from database.db_manager import DatabaseManager
from parsers.file_parser import get_parser
from generators.html_generator import HTMLGenerator

# Configure logging
logging.config.dictConfig(config.LOGGING)
logger = logging.getLogger('sync_worker')


class SyncWorker:
    """Main sync worker that monitors Google Drive and syncs files"""

    def __init__(self):
        """Initialize sync worker"""
        logger.info("Initializing Sync Worker...")

        # Initialize database
        self.db = DatabaseManager(config.DATABASE)

        # Initialize HTML generator
        self.html_generator = HTMLGenerator(config.HTML_OUTPUT_DIR)

        # Initialize Google Drive API
        self.drive_service = self._init_drive_service()

        # Track last sync times
        self.last_sync_times = {}

        logger.info("Sync Worker initialized successfully")

    def _init_drive_service(self):
        """Initialize Google Drive API service"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                config.GOOGLE_DRIVE['service_account_file'],
                scopes=config.GOOGLE_DRIVE['scopes']
            )

            service = build('drive', 'v3', credentials=credentials)
            logger.info("Google Drive API service initialized")
            return service

        except Exception as e:
            logger.error(f"Failed to initialize Google Drive API: {e}")
            raise

    def sync_folder(self, folder_config: Dict[str, Any]) -> bool:
        """
        Sync a single folder from Google Drive

        Args:
            folder_config: Folder configuration dict

        Returns:
            True if sync was successful
        """
        start_time = time.time()
        folder_name = folder_config['folder_name']
        drive_folder_id = folder_config['drive_folder_id']

        logger.info(f"Starting sync for folder: {folder_name}")

        try:
            # Skip if folder ID is empty
            if not drive_folder_id:
                logger.warning(f"Skipping {folder_name} - no Drive folder ID configured")
                return False

            # Get files from Google Drive
            files = self._list_drive_files(drive_folder_id)
            logger.info(f"Found {len(files)} files in {folder_name}")

            # Track file IDs we've seen
            synced_file_ids = set()

            # Process each file
            for file_metadata in files:
                try:
                    file_id = file_metadata['id']
                    file_name = file_metadata['name']
                    mime_type = file_metadata['mimeType']

                    synced_file_ids.add(file_id)

                    # Check if file needs update
                    existing_file = self.db.get_file_by_id(file_id)
                    if existing_file:
                        # Compare modification times
                        existing_modified = existing_file.get('last_updated')
                        new_modified = file_metadata.get('modifiedTime')

                        if existing_modified and new_modified:
                            if new_modified <= str(existing_modified):
                                logger.debug(f"Skipping {file_name} - no changes")
                                continue

                    # Parse file
                    logger.info(f"Processing file: {file_name} ({mime_type})")
                    parser = get_parser(mime_type, self.drive_service)
                    parsed_data = parser.parse(file_metadata)

                    if not parsed_data:
                        logger.warning(f"Failed to parse {file_name}")
                        self.db.mark_file_error(
                            file_id,
                            f"Failed to parse file of type {mime_type}"
                        )
                        continue

                    # Generate HTML
                    html_output = self.html_generator.generate_card(parsed_data)

                    # Save to database
                    success = self.db.insert_sync_data(
                        folder_name=folder_name,
                        file_name=file_name,
                        file_id=file_id,
                        mime_type=mime_type,
                        data=parsed_data,
                        html_output=html_output
                    )

                    if success:
                        logger.info(f"Successfully synced: {file_name}")
                    else:
                        logger.error(f"Failed to save to database: {file_name}")

                except Exception as e:
                    logger.error(f"Error processing file {file_metadata.get('name')}: {e}")
                    self.db.mark_file_error(
                        file_metadata['id'],
                        f"Processing error: {str(e)}"
                    )

            # Mark deleted files
            self._mark_deleted_files(folder_name, synced_file_ids)

            # Generate HTML file for this folder
            files_data = self.db.get_files_by_folder(folder_name)
            self.html_generator.save_folder_html(folder_name, files_data)

            # Update folder check time
            self.db.update_folder_check_time(folder_name)

            duration_ms = int((time.time() - start_time) * 1000)
            self.db.log_operation(
                operation='sync_folder',
                status='success',
                message=f"Synced {len(files)} files",
                folder_name=folder_name,
                duration_ms=duration_ms
            )

            logger.info(f"Completed sync for {folder_name} in {duration_ms}ms")
            return True

        except HttpError as e:
            logger.error(f"Google Drive API error for {folder_name}: {e}")
            self.db.log_operation(
                operation='sync_folder',
                status='error',
                message=f"API error: {e}",
                folder_name=folder_name,
                error_details=str(e)
            )
            return False

        except Exception as e:
            logger.error(f"Unexpected error syncing {folder_name}: {e}")
            self.db.log_operation(
                operation='sync_folder',
                status='error',
                message=f"Unexpected error: {e}",
                folder_name=folder_name,
                error_details=str(e)
            )
            return False

    def _list_drive_files(self, folder_id: str) -> List[Dict[str, Any]]:
        """
        List all files in a Google Drive folder

        Args:
            folder_id: Google Drive folder ID

        Returns:
            List of file metadata dicts
        """
        try:
            query = f"'{folder_id}' in parents and trashed = false"
            results = self.drive_service.files().list(
                q=query,
                fields="files(id, name, mimeType, modifiedTime, size, webViewLink, webContentLink, thumbnailLink)",
                pageSize=100
            ).execute()

            return results.get('files', [])

        except Exception as e:
            logger.error(f"Error listing files in folder {folder_id}: {e}")
            return []

    def _mark_deleted_files(self, folder_name: str, current_file_ids: set):
        """Mark files that no longer exist in Drive as deleted"""
        try:
            existing_files = self.db.get_files_by_folder(folder_name, status='active')

            for file_data in existing_files:
                if file_data['file_id'] not in current_file_ids:
                    logger.info(f"Marking file as deleted: {file_data['file_name']}")
                    self.db.mark_file_deleted(file_data['file_id'])

        except Exception as e:
            logger.error(f"Error marking deleted files: {e}")

    def retry_failed_files(self):
        """Retry processing files that previously failed"""
        logger.info("Checking for failed files to retry...")

        failed_files = self.db.get_files_needing_retry(config.SYNC_CONFIG['max_retries'])

        if not failed_files:
            logger.debug("No files need retry")
            return

        logger.info(f"Found {len(failed_files)} files to retry")

        for file_data in failed_files:
            try:
                logger.info(f"Retrying file: {file_data['file_name']}")

                # Get fresh file metadata from Drive
                file_metadata = self.drive_service.files().get(
                    fileId=file_data['file_id'],
                    fields="id, name, mimeType, modifiedTime, size, webViewLink, webContentLink, thumbnailLink"
                ).execute()

                # Reprocess the file
                parser = get_parser(file_metadata['mimeType'], self.drive_service)
                parsed_data = parser.parse(file_metadata)

                if parsed_data:
                    html_output = self.html_generator.generate_card(parsed_data)

                    self.db.insert_sync_data(
                        folder_name=file_data['folder_name'],
                        file_name=file_metadata['name'],
                        file_id=file_metadata['id'],
                        mime_type=file_metadata['mimeType'],
                        data=parsed_data,
                        html_output=html_output
                    )
                    logger.info(f"Successfully retried: {file_data['file_name']}")
                else:
                    self.db.mark_file_error(
                        file_data['file_id'],
                        "Retry failed - could not parse file",
                        increment_retry=True
                    )

            except Exception as e:
                logger.error(f"Error retrying file {file_data['file_name']}: {e}")
                self.db.mark_file_error(
                    file_data['file_id'],
                    f"Retry error: {str(e)}",
                    increment_retry=True
                )

    def run_sync_cycle(self):
        """Run a complete sync cycle for all folders"""
        logger.info("=" * 60)
        logger.info("Starting sync cycle")
        logger.info("=" * 60)

        start_time = time.time()

        # Get all enabled folder configurations
        folder_configs = self.db.get_folder_configs(enabled_only=True)

        logger.info(f"Found {len(folder_configs)} folders to sync")

        success_count = 0
        error_count = 0

        for folder_config in folder_configs:
            if self.sync_folder(folder_config):
                success_count += 1
            else:
                error_count += 1

        # Retry failed files
        self.retry_failed_files()

        duration = time.time() - start_time
        logger.info("=" * 60)
        logger.info(f"Sync cycle complete in {duration:.2f}s")
        logger.info(f"Success: {success_count} | Errors: {error_count}")
        logger.info("=" * 60)

    def run(self):
        """Main run loop"""
        logger.info("Starting Sync Worker main loop")
        logger.info(f"Poll interval: {config.SYNC_CONFIG['poll_interval']} seconds")

        try:
            while True:
                try:
                    self.run_sync_cycle()

                    # Wait for next cycle
                    logger.info(f"Waiting {config.SYNC_CONFIG['poll_interval']} seconds until next sync...")
                    time.sleep(config.SYNC_CONFIG['poll_interval'])

                except KeyboardInterrupt:
                    logger.info("Received shutdown signal")
                    break

                except Exception as e:
                    logger.error(f"Error in sync cycle: {e}")
                    # Wait before retrying
                    time.sleep(config.SYNC_CONFIG['retry_delay'])

        finally:
            logger.info("Shutting down Sync Worker...")
            self.db.close()
            logger.info("Sync Worker stopped")


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("Government Portal Sync Service")
    logger.info("=" * 60)

    try:
        worker = SyncWorker()
        worker.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

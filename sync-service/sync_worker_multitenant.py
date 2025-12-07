"""
Multi-Tenant Sync Worker
Main service that monitors Google Drive for multiple tenants and syncs files
"""

import logging
import logging.config
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from database.db_manager_multitenant import MultiTenantDatabaseManager
from parsers.file_parser import get_parser
from generators.html_generator import HTMLGenerator

# Configure logging
logging.config.dictConfig(config.LOGGING)
logger = logging.getLogger('sync_worker')


class MultiTenantSyncWorker:
    """Main sync worker that monitors Google Drive for multiple tenants"""

    def __init__(self):
        """Initialize multi-tenant sync worker"""
        logger.info("Initializing Multi-Tenant Sync Worker...")

        # Initialize database
        self.db = MultiTenantDatabaseManager(config.DATABASE)

        # Cache for Drive service instances per tenant
        self.drive_services = {}

        # Cache for HTML generators per tenant
        self.html_generators = {}

        logger.info("Multi-Tenant Sync Worker initialized successfully")

    def _get_drive_service(self, tenant: Dict[str, Any]):
        """
        Get or create Google Drive API service for a tenant

        Args:
            tenant: Tenant configuration dict

        Returns:
            Google Drive service instance
        """
        tenant_id = str(tenant['id'])

        # Return cached service if available
        if tenant_id in self.drive_services:
            return self.drive_services[tenant_id]

        try:
            service_account_file = tenant.get('google_service_account_file')

            if not service_account_file or not Path(service_account_file).exists():
                logger.warning(f"No service account file for tenant {tenant['tenant_key']}")
                return None

            credentials = service_account.Credentials.from_service_account_file(
                service_account_file,
                scopes=config.GOOGLE_DRIVE['scopes']
            )

            service = build('drive', 'v3', credentials=credentials)

            # Cache the service
            self.drive_services[tenant_id] = service

            logger.info(f"Google Drive API service initialized for tenant: {tenant['tenant_key']}")
            return service

        except Exception as e:
            logger.error(f"Failed to initialize Drive service for tenant {tenant['tenant_key']}: {e}")
            return None

    def _get_html_generator(self, tenant: Dict[str, Any]) -> HTMLGenerator:
        """
        Get or create HTML generator for a tenant

        Args:
            tenant: Tenant configuration dict

        Returns:
            HTML generator instance
        """
        tenant_id = str(tenant['id'])

        # Return cached generator if available
        if tenant_id in self.html_generators:
            return self.html_generators[tenant_id]

        output_dir = Path(tenant['output_path'])
        generator = HTMLGenerator(output_dir)

        # Cache the generator
        self.html_generators[tenant_id] = generator

        logger.info(f"HTML generator initialized for tenant: {tenant['tenant_key']}")
        return generator

    def sync_tenant_folder(
        self,
        tenant: Dict[str, Any],
        folder_config: Dict[str, Any]
    ) -> bool:
        """
        Sync a single folder for a tenant

        Args:
            tenant: Tenant configuration dict
            folder_config: Folder configuration dict

        Returns:
            True if sync was successful
        """
        start_time = time.time()
        tenant_id = str(tenant['id'])
        tenant_key = tenant['tenant_key']
        folder_name = folder_config['folder_name']
        drive_folder_id = folder_config['drive_folder_id']

        logger.info(f"[{tenant_key}] Starting sync for folder: {folder_name}")

        try:
            # Skip if folder ID is empty
            if not drive_folder_id:
                logger.debug(f"[{tenant_key}] Skipping {folder_name} - no Drive folder ID")
                return False

            # Get Drive service for this tenant
            drive_service = self._get_drive_service(tenant)
            if not drive_service:
                logger.error(f"[{tenant_key}] No Drive service available")
                return False

            # Get HTML generator for this tenant
            html_generator = self._get_html_generator(tenant)

            # Get files from Google Drive
            files = self._list_drive_files(drive_service, drive_folder_id)
            logger.info(f"[{tenant_key}] Found {len(files)} files in {folder_name}")

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
                    existing_file = self.db.get_file_by_id(file_id, tenant_id)
                    if existing_file:
                        # Compare modification times
                        existing_modified = existing_file.get('last_updated')
                        new_modified = file_metadata.get('modifiedTime')

                        if existing_modified and new_modified:
                            if new_modified <= str(existing_modified):
                                logger.debug(f"[{tenant_key}] Skipping {file_name} - no changes")
                                continue

                    # Parse file
                    logger.info(f"[{tenant_key}] Processing: {file_name} ({mime_type})")
                    parser = get_parser(mime_type, drive_service)
                    parsed_data = parser.parse(file_metadata)

                    if not parsed_data:
                        logger.warning(f"[{tenant_key}] Failed to parse {file_name}")
                        self.db.mark_file_error(
                            file_id,
                            f"Failed to parse file of type {mime_type}",
                            tenant_id=tenant_id
                        )
                        continue

                    # Generate HTML
                    html_output = html_generator.generate_card(parsed_data)

                    # Save to database
                    success = self.db.insert_sync_data(
                        tenant_id=tenant_id,
                        folder_name=folder_name,
                        file_name=file_name,
                        file_id=file_id,
                        mime_type=mime_type,
                        data=parsed_data,
                        html_output=html_output
                    )

                    if success:
                        logger.info(f"[{tenant_key}] Successfully synced: {file_name}")
                    else:
                        logger.error(f"[{tenant_key}] Failed to save: {file_name}")

                except Exception as e:
                    logger.error(f"[{tenant_key}] Error processing {file_metadata.get('name')}: {e}")
                    self.db.mark_file_error(
                        file_metadata['id'],
                        f"Processing error: {str(e)}",
                        tenant_id=tenant_id
                    )

            # Mark deleted files
            self._mark_deleted_files(tenant_id, tenant_key, folder_name, synced_file_ids)

            # Generate component HTML file for this folder
            files_data = self.db.get_files_by_folder(tenant_id, folder_name)
            html_generator.save_component_html(folder_name, files_data)

            # Update folder check time
            self.db.update_folder_check_time(tenant_id, folder_name)

            duration_ms = int((time.time() - start_time) * 1000)
            self.db.log_operation(
                operation='sync_folder',
                status='success',
                message=f"Synced {len(files)} files",
                tenant_id=tenant_id,
                folder_name=folder_name,
                duration_ms=duration_ms
            )

            logger.info(f"[{tenant_key}] Completed {folder_name} in {duration_ms}ms")
            return True

        except HttpError as e:
            logger.error(f"[{tenant_key}] Google Drive API error for {folder_name}: {e}")
            self.db.log_operation(
                operation='sync_folder',
                status='error',
                message=f"API error: {e}",
                tenant_id=tenant_id,
                folder_name=folder_name,
                error_details=str(e)
            )
            return False

        except Exception as e:
            logger.error(f"[{tenant_key}] Unexpected error syncing {folder_name}: {e}")
            self.db.log_operation(
                operation='sync_folder',
                status='error',
                message=f"Unexpected error: {e}",
                tenant_id=tenant_id,
                folder_name=folder_name,
                error_details=str(e)
            )
            return False

    def _list_drive_files(self, drive_service, folder_id: str) -> List[Dict[str, Any]]:
        """List all files in a Google Drive folder"""
        try:
            query = f"'{folder_id}' in parents and trashed = false"
            results = drive_service.files().list(
                q=query,
                fields="files(id, name, mimeType, modifiedTime, size, webViewLink, webContentLink, thumbnailLink)",
                pageSize=100
            ).execute()

            return results.get('files', [])

        except Exception as e:
            logger.error(f"Error listing files in folder {folder_id}: {e}")
            return []

    def _mark_deleted_files(
        self,
        tenant_id: str,
        tenant_key: str,
        folder_name: str,
        current_file_ids: set
    ):
        """Mark files that no longer exist in Drive as deleted"""
        try:
            existing_files = self.db.get_files_by_folder(tenant_id, folder_name, status='active')

            for file_data in existing_files:
                if file_data['file_id'] not in current_file_ids:
                    logger.info(f"[{tenant_key}] Marking file as deleted: {file_data['file_name']}")
                    self.db.mark_file_deleted(file_data['file_id'], tenant_id)

        except Exception as e:
            logger.error(f"[{tenant_key}] Error marking deleted files: {e}")

    def sync_tenant(self, tenant: Dict[str, Any]) -> Dict[str, int]:
        """
        Sync all folders for a single tenant

        Args:
            tenant: Tenant configuration dict

        Returns:
            Dict with success and error counts
        """
        tenant_key = tenant['tenant_key']
        tenant_id = str(tenant['id'])

        logger.info(f"{'='*60}")
        logger.info(f"Syncing tenant: {tenant_key} ({tenant['name']})")
        logger.info(f"{'='*60}")

        start_time = time.time()

        # Get folder configurations for this tenant
        folder_configs = self.db.get_folder_configs(tenant_id, enabled_only=True)

        if not folder_configs:
            logger.warning(f"[{tenant_key}] No enabled folders configured")
            return {'success': 0, 'error': 0}

        logger.info(f"[{tenant_key}] Found {len(folder_configs)} folders to sync")

        success_count = 0
        error_count = 0

        for folder_config in folder_configs:
            if self.sync_tenant_folder(tenant, folder_config):
                success_count += 1
            else:
                error_count += 1

        # Update tenant last sync time
        self.db.update_tenant_sync_time(tenant_id)

        duration = time.time() - start_time
        logger.info(f"[{tenant_key}] Sync complete in {duration:.2f}s | "
                   f"Success: {success_count} | Errors: {error_count}")

        return {'success': success_count, 'error': error_count}

    def retry_failed_files(self):
        """Retry processing files that previously failed (all tenants)"""
        logger.info("Checking for failed files to retry...")

        failed_files = self.db.get_files_needing_retry(config.SYNC_CONFIG['max_retries'])

        if not failed_files:
            logger.debug("No files need retry")
            return

        logger.info(f"Found {len(failed_files)} files to retry across all tenants")

        # Group by tenant
        files_by_tenant = {}
        for file_data in failed_files:
            tenant_id = str(file_data['tenant_id'])
            if tenant_id not in files_by_tenant:
                files_by_tenant[tenant_id] = []
            files_by_tenant[tenant_id].append(file_data)

        # Retry each tenant's files
        for tenant_id, tenant_files in files_by_tenant.items():
            tenant = self.db.get_tenant_by_id(tenant_id)
            if not tenant:
                continue

            tenant_key = tenant['tenant_key']
            drive_service = self._get_drive_service(tenant)
            html_generator = self._get_html_generator(tenant)

            if not drive_service:
                logger.error(f"[{tenant_key}] No Drive service for retry")
                continue

            logger.info(f"[{tenant_key}] Retrying {len(tenant_files)} failed files")

            for file_data in tenant_files:
                try:
                    # Get fresh file metadata
                    file_metadata = drive_service.files().get(
                        fileId=file_data['file_id'],
                        fields="id, name, mimeType, modifiedTime, size, webViewLink, webContentLink, thumbnailLink"
                    ).execute()

                    # Reprocess
                    parser = get_parser(file_metadata['mimeType'], drive_service)
                    parsed_data = parser.parse(file_metadata)

                    if parsed_data:
                        html_output = html_generator.generate_card(parsed_data)

                        self.db.insert_sync_data(
                            tenant_id=tenant_id,
                            folder_name=file_data['folder_name'],
                            file_name=file_metadata['name'],
                            file_id=file_metadata['id'],
                            mime_type=file_metadata['mimeType'],
                            data=parsed_data,
                            html_output=html_output
                        )
                        logger.info(f"[{tenant_key}] Successfully retried: {file_data['file_name']}")
                    else:
                        self.db.mark_file_error(
                            file_data['file_id'],
                            "Retry failed - could not parse file",
                            increment_retry=True,
                            tenant_id=tenant_id
                        )

                except Exception as e:
                    logger.error(f"[{tenant_key}] Error retrying {file_data['file_name']}: {e}")
                    self.db.mark_file_error(
                        file_data['file_id'],
                        f"Retry error: {str(e)}",
                        increment_retry=True,
                        tenant_id=tenant_id
                    )

    def run_sync_cycle(self):
        """Run a complete sync cycle for all tenants"""
        logger.info("=" * 80)
        logger.info("STARTING MULTI-TENANT SYNC CYCLE")
        logger.info("=" * 80)

        start_time = time.time()

        # Get all enabled tenants
        tenants = self.db.get_all_tenants(enabled_only=True)

        if not tenants:
            logger.warning("No tenants configured or enabled")
            return

        logger.info(f"Found {len(tenants)} enabled tenants")

        total_success = 0
        total_errors = 0

        # Sync each tenant
        for tenant in tenants:
            try:
                result = self.sync_tenant(tenant)
                total_success += result['success']
                total_errors += result['error']
            except Exception as e:
                logger.error(f"Failed to sync tenant {tenant['tenant_key']}: {e}")
                total_errors += 1

        # Retry failed files across all tenants
        self.retry_failed_files()

        duration = time.time() - start_time
        logger.info("=" * 80)
        logger.info(f"MULTI-TENANT SYNC CYCLE COMPLETE in {duration:.2f}s")
        logger.info(f"Total Success: {total_success} | Total Errors: {total_errors}")
        logger.info("=" * 80)

    def run(self):
        """Main run loop"""
        logger.info("Starting Multi-Tenant Sync Worker main loop")
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
            logger.info("Shutting down Multi-Tenant Sync Worker...")
            self.db.close()
            logger.info("Multi-Tenant Sync Worker stopped")


def main():
    """Main entry point"""
    logger.info("=" * 80)
    logger.info("GOVERNMENT PORTAL MULTI-TENANT SYNC SERVICE")
    logger.info("=" * 80)

    try:
        worker = MultiTenantSyncWorker()
        worker.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

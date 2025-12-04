"""
Multi-Tenant Database Manager for Government Portal Sync Service
Handles all PostgreSQL database operations with multi-tenant support
"""

import psycopg2
from psycopg2 import pool, extras
from psycopg2.extras import RealDictCursor
import logging
from contextlib import contextmanager
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger('database')


class MultiTenantDatabaseManager:
    """Manages database connections and operations for multiple tenants"""

    def __init__(self, config: Dict[str, str], min_conn=2, max_conn=20):
        """
        Initialize database connection pool

        Args:
            config: Database configuration dict
            min_conn: Minimum number of connections in pool
            max_conn: Maximum number of connections in pool
        """
        self.config = config
        try:
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                min_conn,
                max_conn,
                host=config['host'],
                port=config['port'],
                database=config['database'],
                user=config['user'],
                password=config['password']
            )
            logger.info("Multi-tenant database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = self.pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error, rolling back: {e}")
            raise
        finally:
            self.pool.putconn(conn)

    # ==================== TENANT MANAGEMENT ====================

    def get_all_tenants(self, enabled_only: bool = True) -> List[Dict[str, Any]]:
        """Get all tenants"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    if enabled_only:
                        query = "SELECT * FROM tenants WHERE sync_enabled = TRUE ORDER BY tenant_key"
                    else:
                        query = "SELECT * FROM tenants ORDER BY tenant_key"
                    cur.execute(query)
                    results = cur.fetchall()
                    return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Failed to get tenants: {e}")
            return []

    def get_tenant_by_key(self, tenant_key: str) -> Optional[Dict[str, Any]]:
        """Get tenant by tenant_key"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    query = "SELECT * FROM tenants WHERE tenant_key = %s"
                    cur.execute(query, (tenant_key,))
                    result = cur.fetchone()
                    return dict(result) if result else None
        except Exception as e:
            logger.error(f"Failed to get tenant {tenant_key}: {e}")
            return None

    def get_tenant_by_id(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant by ID"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    query = "SELECT * FROM tenants WHERE id = %s"
                    cur.execute(query, (tenant_id,))
                    result = cur.fetchone()
                    return dict(result) if result else None
        except Exception as e:
            logger.error(f"Failed to get tenant by ID {tenant_id}: {e}")
            return None

    def create_tenant(
        self,
        tenant_key: str,
        name: str,
        output_path: str,
        domain: Optional[str] = None,
        service_account_file: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Create a new tenant

        Args:
            tenant_key: Unique tenant identifier (e.g., 'springfield')
            name: Display name (e.g., 'Springfield City Government')
            output_path: Path where HTML files should be output
            domain: Optional domain name
            service_account_file: Path to Google service account JSON
            metadata: Additional metadata as dict

        Returns:
            Tenant ID (UUID) or None if failed
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                        INSERT INTO tenants (
                            tenant_key, name, domain, output_path,
                            google_service_account_file, metadata
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """
                    cur.execute(query, (
                        tenant_key,
                        name,
                        domain,
                        output_path,
                        service_account_file,
                        json.dumps(metadata or {})
                    ))
                    tenant_id = cur.fetchone()[0]

                    # Initialize default folders for this tenant
                    cur.execute("SELECT initialize_tenant_folders(%s)", (tenant_id,))

                    logger.info(f"Created new tenant: {tenant_key} (ID: {tenant_id})")
                    return str(tenant_id)

        except Exception as e:
            logger.error(f"Failed to create tenant {tenant_key}: {e}")
            return None

    def update_tenant_sync_time(self, tenant_id: str) -> bool:
        """Update last_synced timestamp for a tenant"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    query = "UPDATE tenants SET last_synced = CURRENT_TIMESTAMP WHERE id = %s"
                    cur.execute(query, (tenant_id,))
                    return True
        except Exception as e:
            logger.error(f"Failed to update tenant sync time: {e}")
            return False

    # ==================== SYNC DATA OPERATIONS ====================

    def insert_sync_data(
        self,
        tenant_id: str,
        folder_name: str,
        file_name: str,
        file_id: str,
        mime_type: str,
        data: Dict[str, Any],
        html_output: Optional[str] = None
    ) -> bool:
        """
        Insert or update sync data for a tenant

        Args:
            tenant_id: Tenant UUID
            folder_name: Name of the folder
            file_name: Name of the file
            file_id: Google Drive file ID
            mime_type: MIME type of the file
            data: Parsed data as dict
            html_output: Generated HTML output

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                        INSERT INTO sync_data (
                            tenant_id, folder_name, file_name, file_id, mime_type, data, html_output, status
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'active')
                        ON CONFLICT (tenant_id, folder_name, file_id)
                        DO UPDATE SET
                            file_name = EXCLUDED.file_name,
                            data = EXCLUDED.data,
                            html_output = EXCLUDED.html_output,
                            mime_type = EXCLUDED.mime_type,
                            last_synced = CURRENT_TIMESTAMP,
                            status = 'active',
                            error_message = NULL,
                            retry_count = 0
                        RETURNING id;
                    """
                    cur.execute(query, (
                        tenant_id,
                        folder_name,
                        file_name,
                        file_id,
                        mime_type,
                        json.dumps(data),
                        html_output
                    ))
                    result = cur.fetchone()
                    logger.info(f"Inserted/updated sync data for tenant {tenant_id}, file: {file_name}")
                    return True
        except Exception as e:
            logger.error(f"Failed to insert sync data for {file_name}: {e}")
            return False

    def mark_file_deleted(self, file_id: str, tenant_id: Optional[str] = None) -> bool:
        """Mark a file as deleted"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    if tenant_id:
                        query = """
                            UPDATE sync_data
                            SET status = 'deleted', last_synced = CURRENT_TIMESTAMP
                            WHERE file_id = %s AND tenant_id = %s
                        """
                        cur.execute(query, (file_id, tenant_id))
                    else:
                        query = """
                            UPDATE sync_data
                            SET status = 'deleted', last_synced = CURRENT_TIMESTAMP
                            WHERE file_id = %s
                        """
                        cur.execute(query, (file_id,))
                    logger.info(f"Marked file as deleted: {file_id}")
                    return True
        except Exception as e:
            logger.error(f"Failed to mark file as deleted {file_id}: {e}")
            return False

    def mark_file_error(
        self,
        file_id: str,
        error_message: str,
        increment_retry: bool = True,
        tenant_id: Optional[str] = None
    ) -> bool:
        """Mark a file as having an error"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    if increment_retry:
                        query = """
                            UPDATE sync_data
                            SET status = 'error',
                                error_message = %s,
                                retry_count = retry_count + 1,
                                last_synced = CURRENT_TIMESTAMP
                            WHERE file_id = %s
                        """
                        if tenant_id:
                            query += " AND tenant_id = %s"
                            cur.execute(query, (error_message, file_id, tenant_id))
                        else:
                            cur.execute(query, (error_message, file_id))
                    else:
                        query = """
                            UPDATE sync_data
                            SET status = 'error',
                                error_message = %s,
                                last_synced = CURRENT_TIMESTAMP
                            WHERE file_id = %s
                        """
                        if tenant_id:
                            query += " AND tenant_id = %s"
                            cur.execute(query, (error_message, file_id, tenant_id))
                        else:
                            cur.execute(query, (error_message, file_id))

                    logger.warning(f"Marked file as error: {file_id} - {error_message}")
                    return True
        except Exception as e:
            logger.error(f"Failed to mark file as error {file_id}: {e}")
            return False

    def get_files_by_folder(
        self,
        tenant_id: str,
        folder_name: str,
        status: str = 'active'
    ) -> List[Dict[str, Any]]:
        """Get all files for a specific tenant and folder"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    query = """
                        SELECT *
                        FROM sync_data
                        WHERE tenant_id = %s AND folder_name = %s AND status = %s
                        ORDER BY last_updated DESC
                    """
                    cur.execute(query, (tenant_id, folder_name, status))
                    results = cur.fetchall()
                    return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Failed to get files for tenant {tenant_id}, folder {folder_name}: {e}")
            return []

    def get_file_by_id(self, file_id: str, tenant_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a specific file by its ID"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    if tenant_id:
                        query = "SELECT * FROM sync_data WHERE file_id = %s AND tenant_id = %s"
                        cur.execute(query, (file_id, tenant_id))
                    else:
                        query = "SELECT * FROM sync_data WHERE file_id = %s"
                        cur.execute(query, (file_id,))
                    result = cur.fetchone()
                    return dict(result) if result else None
        except Exception as e:
            logger.error(f"Failed to get file {file_id}: {e}")
            return None

    def get_files_needing_retry(
        self,
        max_retries: int = 3,
        tenant_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get files with errors that haven't exceeded max retries"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    if tenant_id:
                        query = """
                            SELECT *
                            FROM sync_data
                            WHERE tenant_id = %s AND status = 'error' AND retry_count < %s
                            ORDER BY last_synced ASC
                        """
                        cur.execute(query, (tenant_id, max_retries))
                    else:
                        query = """
                            SELECT *
                            FROM sync_data
                            WHERE status = 'error' AND retry_count < %s
                            ORDER BY last_synced ASC
                        """
                        cur.execute(query, (max_retries,))
                    results = cur.fetchall()
                    return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Failed to get files needing retry: {e}")
            return []

    # ==================== FOLDER CONFIGURATION ====================

    def get_folder_configs(
        self,
        tenant_id: str,
        enabled_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get folder configurations for a tenant"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    if enabled_only:
                        query = """
                            SELECT * FROM folder_config
                            WHERE tenant_id = %s AND enabled = TRUE
                            ORDER BY folder_name
                        """
                        cur.execute(query, (tenant_id,))
                    else:
                        query = """
                            SELECT * FROM folder_config
                            WHERE tenant_id = %s
                            ORDER BY folder_name
                        """
                        cur.execute(query, (tenant_id,))
                    results = cur.fetchall()
                    return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Failed to get folder configs for tenant {tenant_id}: {e}")
            return []

    def update_folder_check_time(self, tenant_id: str, folder_name: str) -> bool:
        """Update the last_check timestamp for a folder"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                        UPDATE folder_config
                        SET last_check = CURRENT_TIMESTAMP
                        WHERE tenant_id = %s AND folder_name = %s
                    """
                    cur.execute(query, (tenant_id, folder_name))
                    return True
        except Exception as e:
            logger.error(f"Failed to update folder check time: {e}")
            return False

    # ==================== LOGGING ====================

    def log_operation(
        self,
        operation: str,
        status: str,
        message: str,
        tenant_id: Optional[str] = None,
        folder_name: Optional[str] = None,
        file_name: Optional[str] = None,
        file_id: Optional[str] = None,
        error_details: Optional[str] = None,
        duration_ms: Optional[int] = None
    ) -> bool:
        """Log a sync operation"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                        INSERT INTO sync_log (
                            tenant_id, operation, folder_name, file_name, file_id,
                            status, message, error_details, duration_ms
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cur.execute(query, (
                        tenant_id,
                        operation,
                        folder_name,
                        file_name,
                        file_id,
                        status,
                        message,
                        error_details,
                        duration_ms
                    ))
                    return True
        except Exception as e:
            logger.error(f"Failed to log operation: {e}")
            return False

    def close(self):
        """Close all database connections"""
        if self.pool:
            self.pool.closeall()
            logger.info("Database connection pool closed")

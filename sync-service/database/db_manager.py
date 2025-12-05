"""
Database Manager for Government Portal Sync Service
Handles all PostgreSQL database operations
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


class DatabaseManager:
    """Manages database connections and operations"""

    def __init__(self, config: Dict[str, str], min_conn=1, max_conn=10):
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
            logger.info("Database connection pool created successfully")
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

    def insert_sync_data(
        self,
        folder_name: str,
        file_name: str,
        file_id: str,
        mime_type: str,
        data: Dict[str, Any],
        html_output: Optional[str] = None
    ) -> bool:
        """
        Insert or update sync data

        Args:
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
                            folder_name, file_name, file_id, mime_type, data, html_output, status
                        ) VALUES (%s, %s, %s, %s, %s, %s, 'active')
                        ON CONFLICT (file_id)
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
                        folder_name,
                        file_name,
                        file_id,
                        mime_type,
                        json.dumps(data),
                        html_output
                    ))
                    result = cur.fetchone()
                    logger.info(f"Inserted/updated sync data for file: {file_name} (ID: {file_id})")
                    return True
        except Exception as e:
            logger.error(f"Failed to insert sync data for {file_name}: {e}")
            return False

    def mark_file_deleted(self, file_id: str) -> bool:
        """Mark a file as deleted"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
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
        increment_retry: bool = True
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
                    else:
                        query = """
                            UPDATE sync_data
                            SET status = 'error',
                                error_message = %s,
                                last_synced = CURRENT_TIMESTAMP
                            WHERE file_id = %s
                        """
                    cur.execute(query, (error_message, file_id))
                    logger.warning(f"Marked file as error: {file_id} - {error_message}")
                    return True
        except Exception as e:
            logger.error(f"Failed to mark file as error {file_id}: {e}")
            return False

    def get_files_by_folder(
        self,
        folder_name: str,
        status: str = 'active'
    ) -> List[Dict[str, Any]]:
        """Get all files for a specific folder"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    query = """
                        SELECT *
                        FROM sync_data
                        WHERE folder_name = %s AND status = %s
                        ORDER BY last_updated DESC
                    """
                    cur.execute(query, (folder_name, status))
                    results = cur.fetchall()
                    return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Failed to get files for folder {folder_name}: {e}")
            return []

    def get_file_by_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific file by its ID"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    query = "SELECT * FROM sync_data WHERE file_id = %s"
                    cur.execute(query, (file_id,))
                    result = cur.fetchone()
                    return dict(result) if result else None
        except Exception as e:
            logger.error(f"Failed to get file {file_id}: {e}")
            return None

    def log_operation(
        self,
        operation: str,
        status: str,
        message: str,
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
                            operation, folder_name, file_name, file_id,
                            status, message, error_details, duration_ms
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cur.execute(query, (
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

    def get_folder_configs(self, enabled_only: bool = True) -> List[Dict[str, Any]]:
        """Get folder configurations"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    if enabled_only:
                        query = "SELECT * FROM folder_config WHERE enabled = TRUE"
                        cur.execute(query)
                    else:
                        query = "SELECT * FROM folder_config"
                        cur.execute(query)
                    results = cur.fetchall()
                    return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Failed to get folder configs: {e}")
            return []

    def update_folder_check_time(self, folder_name: str) -> bool:
        """Update the last_check timestamp for a folder"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                        UPDATE folder_config
                        SET last_check = CURRENT_TIMESTAMP
                        WHERE folder_name = %s
                    """
                    cur.execute(query, (folder_name,))
                    return True
        except Exception as e:
            logger.error(f"Failed to update folder check time for {folder_name}: {e}")
            return False

    def get_files_needing_retry(self, max_retries: int = 3) -> List[Dict[str, Any]]:
        """Get files with errors that haven't exceeded max retries"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
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

    def close(self):
        """Close all database connections"""
        if self.pool:
            self.pool.closeall()
            logger.info("Database connection pool closed")

#!/usr/bin/env python3
"""
Sync Service Monitor
Quick status dashboard for the sync service
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor

sys.path.insert(0, str(Path(__file__).parent))
import config


def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        host=config.DATABASE['host'],
        port=config.DATABASE['port'],
        database=config.DATABASE['database'],
        user=config.DATABASE['user'],
        password=config.DATABASE['password']
    )


def print_header(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def check_sync_status():
    """Check overall sync status"""
    print_header("SYNC SERVICE STATUS")

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Get folder stats
        cur.execute("""
            SELECT
                folder_name,
                COUNT(*) as file_count,
                MAX(last_synced) as last_sync,
                SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_count
            FROM sync_data
            WHERE status IN ('active', 'error')
            GROUP BY folder_name
            ORDER BY folder_name
        """)

        folders = cur.fetchall()

        if folders:
            print(f"{'Folder':<25} {'Files':<10} {'Errors':<10} {'Last Sync'}")
            print("-" * 70)
            for folder in folders:
                last_sync = folder['last_sync']
                if last_sync:
                    if isinstance(last_sync, str):
                        last_sync_str = last_sync[:16]
                    else:
                        last_sync_str = last_sync.strftime('%Y-%m-%d %H:%M')
                else:
                    last_sync_str = 'Never'

                print(f"{folder['folder_name']:<25} {folder['file_count']:<10} "
                      f"{folder['error_count']:<10} {last_sync_str}")
        else:
            print("No sync data found.")

        # Get total stats
        cur.execute("""
            SELECT
                COUNT(*) as total_files,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_files,
                SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_files,
                SUM(CASE WHEN status = 'deleted' THEN 1 ELSE 0 END) as deleted_files
            FROM sync_data
        """)

        stats = cur.fetchone()

        print("\n" + "-" * 70)
        print(f"TOTAL: {stats['total_files']} files | "
              f"Active: {stats['active_files']} | "
              f"Errors: {stats['error_files']} | "
              f"Deleted: {stats['deleted_files']}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error connecting to database: {e}")


def check_recent_activity():
    """Check recent sync activity"""
    print_header("RECENT ACTIVITY (Last 10)")

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT
                timestamp,
                operation,
                folder_name,
                file_name,
                status,
                message,
                duration_ms
            FROM sync_log
            ORDER BY timestamp DESC
            LIMIT 10
        """)

        logs = cur.fetchall()

        if logs:
            for log in logs:
                timestamp = log['timestamp']
                if isinstance(timestamp, str):
                    ts_str = timestamp[:19]
                else:
                    ts_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')

                status_icon = "✓" if log['status'] == 'success' else "✗"
                folder = log['folder_name'] or 'N/A'
                msg = log['message'] or ''

                print(f"{status_icon} {ts_str} | {log['operation']:<15} | "
                      f"{folder:<20} | {msg[:30]}")
        else:
            print("No recent activity.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")


def check_errors():
    """Check for error files"""
    print_header("FILES WITH ERRORS")

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT
                folder_name,
                file_name,
                error_message,
                retry_count,
                last_synced
            FROM sync_data
            WHERE status = 'error'
            ORDER BY last_synced DESC
            LIMIT 10
        """)

        errors = cur.fetchall()

        if errors:
            print(f"Found {cur.rowcount} files with errors:\n")
            for error in errors:
                print(f"📁 {error['folder_name']} / {error['file_name']}")
                print(f"   Error: {error['error_message']}")
                print(f"   Retries: {error['retry_count']}")
                print(f"   Last attempt: {error['last_synced']}")
                print()
        else:
            print("✓ No error files found.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")


def check_logs():
    """Check log files"""
    print_header("LOG FILES")

    log_dir = Path(__file__).parent / 'logs'

    if log_dir.exists():
        log_files = list(log_dir.glob('*.log'))

        if log_files:
            print(f"{'File':<25} {'Size':<15} {'Last Modified'}")
            print("-" * 70)

            for log_file in sorted(log_files):
                size = log_file.stat().st_size
                size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.1f} MB"
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)

                print(f"{log_file.name:<25} {size_str:<15} {mtime.strftime('%Y-%m-%d %H:%M')}")

            # Show last 5 lines of main log
            main_log = log_dir / 'sync.log'
            if main_log.exists():
                print("\nLast 5 lines from sync.log:")
                print("-" * 70)
                with open(main_log, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-5:]:
                        print(line.rstrip())
        else:
            print("No log files found.")
    else:
        print("❌ Log directory not found.")


def main():
    """Main dashboard"""
    print("\n" + "=" * 70)
    print("  GOVERNMENT PORTAL SYNC SERVICE - MONITORING DASHBOARD")
    print("  " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 70)

    check_sync_status()
    check_recent_activity()
    check_errors()
    check_logs()

    print("\n" + "=" * 70 + "\n")


if __name__ == '__main__':
    main()

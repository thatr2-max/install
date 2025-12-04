#!/usr/bin/env python3
"""
Tenant Management Script for Multi-Tenant Sync Service

This script helps you add new municipalities/tenants to the sync service.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager_multitenant import MultiTenantDatabaseManager
from config import DATABASE


def add_tenant():
    """Interactive script to add a new tenant"""

    print("\n" + "="*60)
    print("Multi-Tenant Sync Service - Add New Municipality")
    print("="*60 + "\n")

    # Gather tenant information
    tenant_key = input("Enter tenant key (e.g., 'springfield', 'riverside'): ").strip().lower()
    if not tenant_key:
        print("Error: Tenant key is required")
        return

    name = input("Enter municipality name (e.g., 'City of Springfield'): ").strip()
    if not name:
        print("Error: Municipality name is required")
        return

    domain = input("Enter website domain (optional, e.g., 'springfield.gov'): ").strip() or None

    output_path = input("Enter output path for HTML files (e.g., '/var/www/springfield'): ").strip()
    if not output_path:
        print("Error: Output path is required")
        return

    service_account_file = input("Enter path to Google service account JSON file: ").strip()
    if not service_account_file:
        print("Error: Service account file is required")
        return

    # Verify service account file exists
    if not os.path.exists(service_account_file):
        print(f"Warning: Service account file not found at {service_account_file}")
        confirm = input("Continue anyway? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Aborted")
            return

    # Verify or create output directory
    if not os.path.exists(output_path):
        confirm = input(f"Output path {output_path} does not exist. Create it? (y/N): ").strip().lower()
        if confirm == 'y':
            try:
                os.makedirs(output_path, exist_ok=True)
                print(f"Created directory: {output_path}")
            except Exception as e:
                print(f"Error creating directory: {e}")
                return
        else:
            print("Aborted")
            return

    # Confirm
    print("\n" + "-"*60)
    print("Tenant Configuration Summary:")
    print("-"*60)
    print(f"Tenant Key: {tenant_key}")
    print(f"Name: {name}")
    print(f"Domain: {domain or '(none)'}")
    print(f"Output Path: {output_path}")
    print(f"Service Account: {service_account_file}")
    print("-"*60 + "\n")

    confirm = input("Create this tenant? (y/N): ").strip().lower()
    if confirm != 'y':
        print("Aborted")
        return

    # Create tenant in database
    try:
        db = MultiTenantDatabaseManager(DATABASE)
        tenant_id = db.create_tenant(
            tenant_key=tenant_key,
            name=name,
            output_path=output_path,
            domain=domain,
            service_account_file=service_account_file
        )

        if tenant_id:
            print(f"\n✓ Tenant created successfully!")
            print(f"  Tenant ID: {tenant_id}")
            print(f"  Default folders have been initialized")
            print(f"\nNext steps:")
            print(f"  1. Configure Google Drive folder IDs in the folder_config table")
            print(f"  2. Ensure the service account has access to the Drive folders")
            print(f"  3. Run the sync worker to start syncing")
        else:
            print("\n✗ Failed to create tenant (may already exist)")

    except Exception as e:
        print(f"\n✗ Error creating tenant: {e}")
        import traceback
        traceback.print_exc()


def list_tenants():
    """List all tenants in the system"""

    try:
        db = MultiTenantDatabaseManager(DATABASE)
        tenants = db.get_all_tenants(enabled_only=False)

        if not tenants:
            print("\nNo tenants found")
            return

        print("\n" + "="*60)
        print(f"Tenants in System ({len(tenants)} total)")
        print("="*60 + "\n")

        for tenant in tenants:
            status = "✓ Enabled" if tenant['sync_enabled'] else "✗ Disabled"
            print(f"{tenant['tenant_key']} - {tenant['name']}")
            print(f"  Status: {status}")
            print(f"  Domain: {tenant.get('domain') or '(none)'}")
            print(f"  Output: {tenant['output_path']}")
            print(f"  Last Synced: {tenant.get('last_synced') or 'Never'}")
            print()

    except Exception as e:
        print(f"Error listing tenants: {e}")


def main():
    """Main entry point"""

    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        list_tenants()
    else:
        add_tenant()


if __name__ == '__main__':
    main()

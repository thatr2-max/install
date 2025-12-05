# Municipality Setup Guide

Automated setup process for creating new municipal government websites from a filled questionnaire.

## Overview

The `setup_municipality.py` script automates the entire process of creating a new municipal website by:

1. **Parsing** a filled-out questionnaire
2. **Creating** a new tenant in the multi-tenant database
3. **Copying** website template files to a tenant-specific directory
4. **Customizing** the website with municipality-specific data
5. **Configuring** Google Drive sync for document management

## Quick Start

### 1. Fill Out the Questionnaire

Start with the template questionnaire:

```bash
cp GOVERNMENT_QUESTIONNAIRE.md municipalities/springfield-questionnaire.md
```

Edit the file and replace all `___________________________________` with actual information.

**Important:**
- Fill in all relevant fields
- Leave fields blank if not applicable (don't leave underscores)
- For Google Drive folders, provide either the folder ID or full URL

### 2. Run the Setup Script

```bash
python setup_municipality.py municipalities/springfield-questionnaire.md
```

The script will:
- Parse the questionnaire
- Create tenant "springfield" in the database
- Copy website files to `/var/www/springfield/`
- Customize pages with questionnaire data
- Configure Google Drive folder mappings

### 3. Configure Web Server

Set up nginx/apache to serve the new municipality:

```nginx
# /etc/nginx/sites-available/springfield.gov
server {
    listen 80;
    server_name springfield.gov www.springfield.gov;
    root /var/www/springfield;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/springfield.gov /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Set Up Google Drive Sync

If using Google Drive for documents:

1. Create a Google Cloud service account for this municipality
2. Download the service account JSON file
3. Update the tenant in the database:

```sql
UPDATE tenants
SET google_service_account_file = '/path/to/springfield-service-account.json'
WHERE tenant_key = 'springfield';
```

4. Share Google Drive folders with the service account email
5. The sync service will automatically sync this tenant's folders

### 5. Start/Restart Sync Service

If the multi-tenant sync service is running, it will automatically pick up the new tenant:

```bash
sudo systemctl restart gov-portal-sync
```

Check logs to verify:
```bash
sudo journalctl -u gov-portal-sync -f | grep springfield
```

## Questionnaire Format

### Required Fields

These fields are **required** for setup to work:

- **General Information**
  - Municipality Name (used to generate tenant key)
  - Main Contact Information (address, phone, email)

### Optional Fields

All other fields are optional. The script will skip unfilled fields (those with only underscores).

### Repeating Items

For items like departments, council members, parks, etc., use the format:

```markdown
**Department 1:**
- Name: Public Works
- Phone: (555) 123-4567
- Email: publicworks@example.gov
- Location: City Hall, Room 101
- Hours: Mon-Fri 8AM-5PM

**Department 2:**
- Name: Parks & Recreation
- Phone: (555) 123-4568
- Email: parks@example.gov
- Location: Community Center
- Hours: Mon-Fri 9AM-6PM
```

The script will automatically parse all numbered items.

### Google Drive Folders

For Google Drive folder IDs, you can provide:

1. **Just the folder ID:** `1a2b3c4d5e6f7g8h9i0j`
2. **Full URL:** `https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j`

The script will extract the ID automatically.

## Directory Structure

After setup, each municipality has this structure:

```
/var/www/{tenant-key}/
├── index.html
├── pages/
│   ├── report-issue.html
│   ├── news.html
│   ├── contact.html
│   ├── staff-directory.html
│   ├── city-council.html
│   ├── boards-commissions.html
│   ├── public-records.html
│   ├── permits.html
│   ├── forms.html
│   ├── events.html
│   ├── voting-elections.html
│   ├── faqs.html
│   ├── parks-recreation.html
│   └── generated/           # Auto-generated from Google Drive
├── assets/
│   ├── css/
│   ├── js/
│   └── images/
├── components/
│   ├── header-home.html
│   ├── header-page.html
│   └── footer.html
└── config/
    ├── staff.json           # Staff directory data
    ├── polling-locations.json
    └── parks.json
```

## Customization

### Generated Configuration Files

The script generates JSON configuration files in `/var/www/{tenant-key}/config/`:

**staff.json** - Staff directory data
```json
{
  "council_members": [...],
  "department_heads": [...]
}
```

**polling-locations.json** - Voting locations
```json
[
  {
    "location_name": "City Hall",
    "address": "123 Main St",
    "hours": "7AM-7PM",
    "accessibility": "ADA accessible"
  }
]
```

**parks.json** - Parks and recreation
```json
{
  "parks": [...],
  "trails": [...]
}
```

These files can be loaded dynamically by JavaScript to populate pages.

### Manual Customization

After automated setup, you may want to manually customize:

1. **Colors/Branding**: Edit `/var/www/{tenant-key}/assets/css/styles.css`
2. **Logo**: Replace `/var/www/{tenant-key}/assets/images/logo.png`
3. **Component Templates**: Edit files in `/var/www/{tenant-key}/components/`

## Database Management

### View Tenant Information

```sql
-- List all tenants
SELECT tenant_key, name, sync_enabled, last_synced FROM tenants;

-- View specific tenant
SELECT * FROM tenants WHERE tenant_key = 'springfield';

-- View tenant's Google Drive folders
SELECT fc.folder_name, fc.drive_folder_id, fc.enabled
FROM folder_config fc
JOIN tenants t ON fc.tenant_id = t.id
WHERE t.tenant_key = 'springfield';
```

### Enable/Disable Sync

```sql
-- Disable sync for a tenant
UPDATE tenants SET sync_enabled = FALSE WHERE tenant_key = 'springfield';

-- Re-enable
UPDATE tenants SET sync_enabled = TRUE WHERE tenant_key = 'springfield';
```

### Update Configuration

```sql
-- Update output path
UPDATE tenants
SET output_path = '/var/www/new-path'
WHERE tenant_key = 'springfield';

-- Update service account
UPDATE tenants
SET google_service_account_file = '/path/to/new-sa.json'
WHERE tenant_key = 'springfield';
```

## Troubleshooting

### Script Fails to Parse Questionnaire

**Error:** "Municipality name not found in questionnaire"

**Solution:** Ensure the Municipality Name field is filled in:
```markdown
- **Municipality Name:** City of Springfield
```

### Tenant Already Exists

**Error:** "Failed to create tenant (may already exist)"

**Solution:** The tenant key is generated from the municipality name. Either:
1. Use a different municipality name
2. Manually delete the existing tenant from database
3. Choose a custom tenant key

### Files Not Copying

**Error:** Permission denied

**Solution:** Ensure you have write permissions:
```bash
sudo chown -R $USER:$USER /var/www
```

Or run with sudo:
```bash
sudo python setup_municipality.py questionnaire.md
```

### Google Drive Folders Not Syncing

**Checklist:**
1. Service account file path is correct in database
2. Folders are shared with service account email
3. Folder IDs are correct in `folder_config` table
4. Tenant is enabled: `sync_enabled = TRUE`
5. Sync service is running: `sudo systemctl status gov-portal-sync`

## Example Workflow

### Complete Setup Example

```bash
# 1. Create questionnaire from template
mkdir -p municipalities
cp GOVERNMENT_QUESTIONNAIRE.md municipalities/springfield.md

# 2. Fill out questionnaire
nano municipalities/springfield.md

# 3. Run setup
python setup_municipality.py municipalities/springfield.md

# 4. Set up service account
# Download springfield-sa.json from Google Cloud Console

# 5. Update database
psql -U sync_user -d gov_portal_sync << EOF
UPDATE tenants
SET google_service_account_file = '/home/user/install/sync-service/credentials/springfield-sa.json'
WHERE tenant_key = 'springfield';
EOF

# 6. Share folders with service account and update folder IDs
psql -U sync_user -d gov_portal_sync << EOF
UPDATE folder_config
SET drive_folder_id = '1a2b3c4d5e6f7g8h9i0j'
WHERE tenant_id = (SELECT id FROM tenants WHERE tenant_key = 'springfield')
  AND folder_name = 'meeting_agendas';
EOF

# 7. Configure web server
sudo nano /etc/nginx/sites-available/springfield.gov
sudo ln -s /etc/nginx/sites-available/springfield.gov /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 8. Restart sync service
sudo systemctl restart gov-portal-sync

# 9. Verify
curl http://springfield.gov
sudo journalctl -u gov-portal-sync -f | grep springfield
```

## Advanced Usage

### Custom Tenant Keys

By default, tenant keys are generated from municipality names. To use a custom key:

```python
# Edit setup_municipality.py, line ~200
def _generate_tenant_key(self, name: str) -> str:
    return "custom-key"  # Your custom key
```

### Multiple Environments

Set up development/staging/production:

```bash
# Development
python setup_municipality.py questionnaire.md --env dev
# Creates /var/www/dev-springfield/

# Production
python setup_municipality.py questionnaire.md --env prod
# Creates /var/www/springfield/
```

(This would require modifying the script)

### Batch Setup

Process multiple municipalities:

```bash
for questionnaire in municipalities/*.md; do
    python setup_municipality.py "$questionnaire"
done
```

## Support

For issues:
1. Check script output for error messages
2. Verify database connection: `psql -U sync_user -d gov_portal_sync`
3. Check logs: `tail -f sync-service/logs/sync.log`
4. Review tenant in database: `SELECT * FROM tenants WHERE tenant_key = 'your-key';`

## Related Documentation

- **GOVERNMENT_QUESTIONNAIRE.md**: Blank questionnaire template
- **sync-service/SETUP_INSTRUCTIONS.md**: Multi-tenant sync service setup
- **sync-service/README.md**: Sync service overview

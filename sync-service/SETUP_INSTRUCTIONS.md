# Government Portal Sync Service - Setup Instructions

Complete setup guide for the sync service that monitors Google Drive and auto-generates static HTML files.

## Multi-Tenant vs Single-Tenant

This sync service comes in two flavors:

- **Single-Tenant**: One database for one municipality (use `schema.sql`, `db_manager.py`, `sync_worker.py`)
- **Multi-Tenant**: One database managing multiple municipalities (use `schema_multitenant.sql`, `db_manager_multitenant.py`, `sync_worker_multitenant.py`)

**Choose Multi-Tenant if**:
- You're managing websites for multiple municipalities
- You want to reduce infrastructure overhead
- You need centralized management and monitoring

**Choose Single-Tenant if**:
- You're only managing one municipality
- You need complete database isolation per client

This guide covers both setups. Multi-tenant specific instructions are marked with **[MULTI-TENANT]**.

---

## Prerequisites

- Ubuntu Server 20.04+ (or similar Linux distribution)
- Python 3.10 or higher
- PostgreSQL 13 or higher
- Google Cloud Platform account with Drive API enabled
- Service account credentials for Google Drive API (one per municipality)

---

## Step 1: Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+
sudo apt install python3.10 python3.10-venv python3-pip -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

---

## Step 2: Set Up PostgreSQL Database

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL prompt, run:
CREATE DATABASE gov_portal_sync;
CREATE USER sync_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE gov_portal_sync TO sync_user;
\q
```

### Single-Tenant Schema

```bash
# Initialize single-tenant database schema
cd /home/user/install/sync-service
sudo -u postgres psql -d gov_portal_sync -f database/schema.sql
```

### Multi-Tenant Schema **[MULTI-TENANT]**

```bash
# Initialize multi-tenant database schema
cd /home/user/install/sync-service
sudo -u postgres psql -d gov_portal_sync -f database/schema_multitenant.sql
```

The multi-tenant schema includes:
- `tenants` table for storing municipality configurations
- All tables have `tenant_id` foreign keys for isolation
- Built-in views for monitoring per-tenant sync status
- Automatic initialization of default folders for new tenants

---

## Step 3: Set Up Google Drive API

### Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable Google Drive API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click "Enable"

4. Create service account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Name: `gov-portal-sync`
   - Click "Create and Continue"
   - Skip optional steps, click "Done"

5. Create service account key:
   - Click on the service account you just created
   - Go to "Keys" tab
   - Click "Add Key" > "Create New Key"
   - Choose JSON format
   - Download the JSON file

6. Save credentials:
   ```bash
   mkdir -p /home/user/install/sync-service/credentials
   # Upload your downloaded JSON file to this location:
   # /home/user/install/sync-service/credentials/service-account.json
   chmod 600 /home/user/install/sync-service/credentials/service-account.json
   ```

### Share Google Drive Folders with Service Account

1. Get the service account email from the JSON file:
   ```bash
   grep client_email credentials/service-account.json
   # Example: gov-portal-sync@project-name.iam.gserviceaccount.com
   ```

2. Share each Google Drive folder with this email:
   - Open Google Drive
   - Right-click each folder you want to sync
   - Click "Share"
   - Add the service account email
   - Give "Viewer" permissions
   - Uncheck "Notify people"
   - Click "Share"

3. Get folder IDs:
   - Open each folder in Google Drive
   - Copy the folder ID from the URL:
     ```
     https://drive.google.com/drive/folders/FOLDER_ID_HERE
     ```
   - Save these IDs for the next step

---

## Step 4: Add Municipalities (Tenants) **[MULTI-TENANT]**

**Skip this step if using single-tenant setup.**

For multi-tenant setups, use the provided script to add municipalities:

```bash
cd /home/user/install/sync-service
source venv/bin/activate

# Add your first municipality
python add_tenant.py

# Follow the interactive prompts:
# - Tenant key: e.g., 'springfield'
# - Name: e.g., 'City of Springfield'
# - Domain: e.g., 'springfield.gov' (optional)
# - Output path: e.g., '/var/www/springfield'
# - Service account file: path to Google credentials JSON

# Add additional municipalities
python add_tenant.py  # Run again for each municipality

# List all tenants
python add_tenant.py list
```

The script will:
1. Create the tenant in the database
2. Initialize default folders (meeting_agendas, meeting_minutes, etc.)
3. Configure output paths and service accounts

**Each municipality should have**:
- Its own Google service account credentials file
- Its own output directory for generated HTML
- Unique tenant key (used as identifier)

---

## Step 5: Configure Folder IDs in Database

### Single-Tenant

```bash
# Connect to database
psql -U sync_user -d gov_portal_sync

# Update folder IDs (replace YOUR_FOLDER_ID with actual IDs)
UPDATE folder_config SET drive_folder_id = 'YOUR_FOLDER_ID' WHERE folder_name = 'meeting_agendas';
UPDATE folder_config SET drive_folder_id = 'YOUR_FOLDER_ID' WHERE folder_name = 'meeting_minutes';
UPDATE folder_config SET drive_folder_id = 'YOUR_FOLDER_ID' WHERE folder_name = 'job_postings';
-- Repeat for all folders you want to sync

# Disable folders you don't want to sync
UPDATE folder_config SET enabled = FALSE WHERE folder_name = 'some_folder';

# View all folder configurations
SELECT folder_name, drive_folder_id, enabled FROM folder_config;

\q
```

### Multi-Tenant **[MULTI-TENANT]**

```bash
# Connect to database
psql -U sync_user -d gov_portal_sync

# First, find your tenant ID
SELECT id, tenant_key, name FROM tenants;

# Update folder IDs for a specific tenant (replace TENANT_ID and YOUR_FOLDER_ID)
UPDATE folder_config
SET drive_folder_id = 'YOUR_FOLDER_ID'
WHERE tenant_id = 'TENANT_ID' AND folder_name = 'meeting_agendas';

UPDATE folder_config
SET drive_folder_id = 'YOUR_FOLDER_ID'
WHERE tenant_id = 'TENANT_ID' AND folder_name = 'meeting_minutes';

-- Repeat for all folders for this tenant

# Disable folders you don't want to sync
UPDATE folder_config
SET enabled = FALSE
WHERE tenant_id = 'TENANT_ID' AND folder_name = 'some_folder';

# View folder configurations for a tenant
SELECT folder_name, drive_folder_id, enabled
FROM folder_config
WHERE tenant_id = 'TENANT_ID';

# Or view for all tenants
SELECT t.tenant_key, fc.folder_name, fc.drive_folder_id, fc.enabled
FROM folder_config fc
JOIN tenants t ON fc.tenant_id = t.id
ORDER BY t.tenant_key, fc.folder_name;

\q
```

---

## Step 6: Install Python Dependencies

```bash
cd /home/user/install/sync-service

# Create virtual environment
python3.10 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Make add_tenant.py executable (multi-tenant only)
chmod +x add_tenant.py
```

---

## Step 7: Configure Environment Variables

```bash
cd /home/user/install/sync-service

# Create .env file
cat > .env << 'EOF'
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gov_portal_sync
DB_USER=sync_user
DB_PASSWORD=your_secure_password_here

# Google Drive Configuration
GOOGLE_SERVICE_ACCOUNT=/home/user/install/sync-service/credentials/service-account.json
DRIVE_ROOT_FOLDER_ID=

# Sync Configuration
SYNC_POLL_INTERVAL=300
MAX_RETRIES=3
RETRY_DELAY=60
BATCH_SIZE=50

# Optional: Email Notifications
NOTIFICATIONS_ENABLED=false
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
FROM_EMAIL=
TO_EMAILS=admin@example.com
EOF

# Secure the .env file
chmod 600 .env
```

---

## Step 8: Test the Sync Service

```bash
# Activate virtual environment
source venv/bin/activate

# Run a test sync
# For single-tenant:
python sync_worker.py

# For multi-tenant:
python sync_worker_multitenant.py

# Check logs
tail -f logs/sync.log

# Press Ctrl+C to stop
```

Verify the test worked:
- Check that files were fetched from Google Drive
- Check that database records were created
- Check that HTML files were generated in the output path(s)

---

## Step 9: Set Up as System Service

### Single-Tenant Service

```bash
# Create systemd service file
sudo tee /etc/systemd/system/gov-portal-sync.service > /dev/null << 'EOF'
[Unit]
Description=Government Portal Sync Service
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/home/user/install/sync-service
Environment="PATH=/home/user/install/sync-service/venv/bin"
ExecStart=/home/user/install/sync-service/venv/bin/python sync_worker.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Set ownership
sudo chown -R www-data:www-data /home/user/install/sync-service

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable gov-portal-sync

# Start the service
sudo systemctl start gov-portal-sync

# Check status
sudo systemctl status gov-portal-sync

# View logs
sudo journalctl -u gov-portal-sync -f
```

### Multi-Tenant Service **[MULTI-TENANT]**

```bash
# Create systemd service file for multi-tenant sync
sudo tee /etc/systemd/system/gov-portal-sync.service > /dev/null << 'EOF'
[Unit]
Description=Government Portal Multi-Tenant Sync Service
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/home/user/install/sync-service
Environment="PATH=/home/user/install/sync-service/venv/bin"
ExecStart=/home/user/install/sync-service/venv/bin/python sync_worker_multitenant.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Set ownership for all tenant output directories
sudo chown -R www-data:www-data /home/user/install/sync-service
# Also ensure www-data can write to each tenant's output path
# Example for multiple tenants:
# sudo chown -R www-data:www-data /var/www/springfield
# sudo chown -R www-data:www-data /var/www/riverside

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable gov-portal-sync

# Start the service
sudo systemctl start gov-portal-sync

# Check status
sudo systemctl status gov-portal-sync

# View logs (you'll see entries prefixed with tenant keys)
sudo journalctl -u gov-portal-sync -f
```

---

## Step 10: Verify Setup

### Check Database - Single-Tenant

```bash
psql -U sync_user -d gov_portal_sync

-- View sync status
SELECT folder_name, COUNT(*) as file_count, MAX(last_updated) as last_sync
FROM sync_data
WHERE status = 'active'
GROUP BY folder_name
ORDER BY folder_name;

-- View recent logs
SELECT timestamp, operation, folder_name, status, message
FROM sync_log
ORDER BY timestamp DESC
LIMIT 20;

-- Check for errors
SELECT * FROM error_files;

\q
```

### Check Database - Multi-Tenant **[MULTI-TENANT]**

```bash
psql -U sync_user -d gov_portal_sync

-- View all tenants and their sync status
SELECT * FROM tenant_sync_status;

-- View sync status per tenant
SELECT tenant_key, folder_name, COUNT(*) as file_count, MAX(last_updated) as last_sync
FROM sync_data sd
JOIN tenants t ON sd.tenant_id = t.id
WHERE status = 'active'
GROUP BY tenant_key, folder_name
ORDER BY tenant_key, folder_name;

-- View recent logs with tenant info
SELECT t.tenant_key, sl.timestamp, sl.operation, sl.folder_name, sl.status, sl.message
FROM sync_log sl
JOIN tenants t ON sl.tenant_id = t.id
ORDER BY sl.timestamp DESC
LIMIT 20;

-- Check for errors per tenant
SELECT t.tenant_key, ef.*
FROM error_files ef
JOIN tenants t ON ef.tenant_id = t.id
ORDER BY t.tenant_key, ef.last_attempt;

-- View files synced per tenant
SELECT * FROM active_files_by_tenant;

\q
```

### Check Generated HTML Files

```bash
# List generated files
ls -lh /home/user/install/pages/generated/

# View a generated file
cat /home/user/install/pages/generated/meeting_agendas.html
```

### Check Logs

```bash
# Application logs
tail -n 100 /home/user/install/sync-service/logs/sync.log

# Error logs
tail -n 50 /home/user/install/sync-service/logs/error.log

# System logs
sudo journalctl -u gov-portal-sync --since "1 hour ago"
```

---

## Step 10: Integrate with Web Server

### Update Web Pages to Use Generated HTML

The sync service generates HTML files in `/pages/generated/`. Update your existing pages to include these:

```html
<!-- Example: pages/council-meetings.html -->
<section class="card">
    <h2>Meeting Agendas</h2>
    <div id="meeting-agendas">
        <p>Loading agendas...</p>
    </div>
</section>

<script>
// Load generated HTML
fetch('generated/meeting_agendas.html')
    .then(response => response.text())
    .then(html => {
        // Extract just the cards from the generated HTML
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const grid = doc.querySelector('.grid');
        document.getElementById('meeting-agendas').innerHTML = grid.innerHTML;
    });
</script>
```

---

## Monitoring & Maintenance

### Daily Health Checks

```bash
# Check service status
sudo systemctl status gov-portal-sync

# Check recent sync activity
tail -n 50 /home/user/install/sync-service/logs/sync.log | grep "Sync cycle complete"

# Check for errors
grep -i error /home/user/install/sync-service/logs/sync.log | tail -n 20
```

### Database Maintenance

```bash
# Vacuum database monthly
psql -U sync_user -d gov_portal_sync -c "VACUUM ANALYZE sync_data;"

# Archive old logs quarterly
psql -U sync_user -d gov_portal_sync << EOF
DELETE FROM sync_log WHERE timestamp < NOW() - INTERVAL '90 days';
EOF
```

### Log Rotation

Logs are automatically rotated at 10MB. Old logs are kept for 5 rotations.

---

## Troubleshooting

### Service Won't Start

```bash
# Check service status and errors
sudo systemctl status gov-portal-sync
sudo journalctl -u gov-portal-sync -n 50

# Check permissions
ls -la /home/user/install/sync-service/
sudo chown -R www-data:www-data /home/user/install/sync-service/

# Check Python environment
source /home/user/install/sync-service/venv/bin/activate
python -c "import google.oauth2.service_account; print('OK')"
```

### Database Connection Errors

```bash
# Test database connection
psql -U sync_user -d gov_portal_sync -c "SELECT version();"

# Check PostgreSQL is running
sudo systemctl status postgresql

# Check .env file has correct password
cat /home/user/install/sync-service/.env | grep DB_PASSWORD
```

### Google Drive API Errors

```bash
# Verify service account file exists
ls -la /home/user/install/sync-service/credentials/service-account.json

# Test API access
python << 'EOF'
from google.oauth2 import service_account
from googleapiclient.discovery import build

creds = service_account.Credentials.from_service_account_file(
    '/home/user/install/sync-service/credentials/service-account.json'
)
service = build('drive', 'v3', credentials=creds)
print("Drive API connection successful")
EOF
```

### No Files Syncing

```bash
# Check folder IDs are configured
psql -U sync_user -d gov_portal_sync -c "SELECT folder_name, drive_folder_id, enabled FROM folder_config WHERE enabled = TRUE;"

# Check folders are shared with service account
# Verify in Google Drive that folders are shared

# Check sync logs for errors
grep -A 5 "Starting sync" /home/user/install/sync-service/logs/sync.log
```

---

## Performance Tuning

### Adjust Sync Interval

Edit `.env` file:
```bash
# Sync every 5 minutes (300 seconds)
SYNC_POLL_INTERVAL=300

# Or sync every 15 minutes
SYNC_POLL_INTERVAL=900
```

Restart service:
```bash
sudo systemctl restart gov-portal-sync
```

### Database Connection Pooling

For high traffic, adjust connection pool in `database/db_manager.py`:
```python
self.pool = psycopg2.pool.ThreadedConnectionPool(
    5,   # min connections
    20,  # max connections
    ...
)
```

---

## Security Best Practices

1. **Secure Credentials**
   ```bash
   chmod 600 /home/user/install/sync-service/credentials/service-account.json
   chmod 600 /home/user/install/sync-service/.env
   ```

2. **Use Strong Database Password**
   - Minimum 16 characters
   - Mix of letters, numbers, symbols

3. **Limit Service Account Permissions**
   - Only grant "Viewer" access to Drive folders
   - Don't use personal Google account

4. **Regular Updates**
   ```bash
   cd /home/user/install/sync-service
   source venv/bin/activate
   pip list --outdated
   pip install --upgrade package-name
   ```

5. **Firewall Configuration**
   ```bash
   # PostgreSQL should only be accessible locally
   sudo ufw deny 5432
   ```

---

## Backup & Recovery

### Backup Database

```bash
# Create backup
pg_dump -U sync_user gov_portal_sync > backup_$(date +%Y%m%d).sql

# Compress backup
gzip backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
# Stop sync service
sudo systemctl stop gov-portal-sync

# Restore from backup
gunzip backup_20250101.sql.gz
psql -U sync_user -d gov_portal_sync < backup_20250101.sql

# Restart service
sudo systemctl start gov-portal-sync
```

---

## Support

For issues or questions:
- Check logs: `/home/user/install/sync-service/logs/`
- Review database: `psql -U sync_user gov_portal_sync`
- Test service: `python sync_worker.py` (manual run)

---

## Multi-Tenant Management **[MULTI-TENANT]**

### Adding New Municipalities

```bash
cd /home/user/install/sync-service
source venv/bin/activate
python add_tenant.py
```

### Disabling a Tenant Temporarily

```bash
psql -U sync_user -d gov_portal_sync

-- Disable sync for a tenant
UPDATE tenants SET sync_enabled = FALSE WHERE tenant_key = 'springfield';

-- Re-enable later
UPDATE tenants SET sync_enabled = TRUE WHERE tenant_key = 'springfield';
```

### Viewing Tenant Statistics

```bash
psql -U sync_user -d gov_portal_sync

-- Overall tenant status
SELECT tenant_key, name, sync_enabled, last_synced,
       (SELECT COUNT(*) FROM sync_data WHERE tenant_id = t.id) as total_files
FROM tenants t
ORDER BY tenant_key;

-- Use the built-in view
SELECT * FROM tenant_sync_status;
```

### Managing Tenant Folders

```bash
# Each tenant has isolated folders
# To add a custom folder for a specific tenant:

psql -U sync_user -d gov_portal_sync

INSERT INTO folder_config (tenant_id, folder_name, drive_folder_id, html_template)
VALUES (
    (SELECT id FROM tenants WHERE tenant_key = 'springfield'),
    'custom_folder_name',
    'GOOGLE_DRIVE_FOLDER_ID',
    'document_card'
);
```

---

## Summary of Key Files

### Single-Tenant Files
- **Service Code**: `/home/user/install/sync-service/sync_worker.py`
- **Database Manager**: `/home/user/install/sync-service/database/db_manager.py`
- **Schema**: `/home/user/install/sync-service/database/schema.sql`

### Multi-Tenant Files
- **Service Code**: `/home/user/install/sync-service/sync_worker_multitenant.py`
- **Database Manager**: `/home/user/install/sync-service/database/db_manager_multitenant.py`
- **Schema**: `/home/user/install/sync-service/database/schema_multitenant.sql`
- **Tenant Management**: `/home/user/install/sync-service/add_tenant.py`

### Shared Files
- **Configuration**: `/home/user/install/sync-service/.env`
- **Credentials**: `/home/user/install/sync-service/credentials/service-account.json` (single-tenant) or per-tenant paths (multi-tenant)
- **Logs**: `/home/user/install/sync-service/logs/sync.log`
- **Generated HTML**: `/home/user/install/pages/generated/` (single-tenant) or per-tenant output paths (multi-tenant)
- **Systemd Service**: `/etc/systemd/system/gov-portal-sync.service`

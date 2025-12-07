# Google Service Account Setup Guide

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a Project" → "New Project"
3. Name it something like "City Portal Sync"
4. Click "Create"

## Step 2: Enable Google Sheets API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API"
3. Click on it and click "Enable"

## Step 3: Create Service Account

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Name: "Portal Sync Service"
4. Click "Create and Continue"
5. Skip optional steps, click "Done"

## Step 4: Download Service Account Key

1. Click on the service account you just created
2. Go to "Keys" tab
3. Click "Add Key" → "Create New Key"
4. Choose "JSON" format
5. Click "Create"
6. **Save this JSON file** - you'll need it!
7. Move it to your sync-service directory: `sync-service/service-account.json`

## Step 5: Share Sheets with Service Account

1. Open the JSON file you downloaded
2. Find the `client_email` field - it looks like:
   `portal-sync-service@your-project.iam.gserviceaccount.com`
3. Copy this email address
4. For EACH Google Sheet you created:
   - Click "Share" button
   - Paste the service account email
   - Set permission to "Viewer"
   - Uncheck "Notify people"
   - Click "Share"

## Step 6: Get Sheet IDs

For each Google Sheet, get the ID from the URL:
```
https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
                                        ^^^^^^^^^^^
                                        Copy this part
```

## Step 7: Configure Sync Service

Edit `sync-service/simple_sync_config.json`:
```json
{
  "service_account_file": "service-account.json",
  "output_dir": "../components",
  "config_output_dir": "../assets/js",
  "sheets": {
    "municipality_config": "PASTE_SHEET_ID_HERE",
    "staff_directory": "PASTE_SHEET_ID_HERE",
    "events": "PASTE_SHEET_ID_HERE",
    "public_notices": "PASTE_SHEET_ID_HERE",
    "job_postings": "PASTE_SHEET_ID_HERE",
    "boards_commissions": "PASTE_SHEET_ID_HERE",
    "news": "PASTE_SHEET_ID_HERE"
  }
}
```

## Step 8: Test the Connection

```bash
cd sync-service
python simple_sync.py --config simple_sync_config.json --once
```

You should see output like:
```
✓ Municipality config synced (15 config values)
✓ Staff directory synced (5 employees)
✓ Events synced (3 events)
...
```

## Troubleshooting

**Error: "Failed to get sheet"**
- Make sure you shared the sheet with the service account email
- Check that the sheet ID is correct

**Error: "No data found"**
- Make sure sheet has the correct tab name (e.g., "Municipality Config")
- Check that column headers are in row 1

**Error: "Permission denied"**
- Service account needs "Viewer" permission on each sheet
- Make sure Google Sheets API is enabled in your project

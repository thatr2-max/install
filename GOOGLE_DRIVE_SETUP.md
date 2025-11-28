# Google Drive Integration Setup

This guide shows you how to set up automatic file loading from Google Drive folders.

## What This Does

Staff can drag and drop PDFs/documents into Google Drive folders, and they'll automatically appear on your website - no manual uploading needed!

## Step 1: Get a Google API Key

1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing one)
3. Click "Enable APIs and Services"
4. Search for "Google Drive API" and enable it
5. Go to "Credentials" (left sidebar)
6. Click "Create Credentials" → "API Key"
7. Copy the API key
8. **IMPORTANT**: Click "Restrict Key" and:
   - Under "API restrictions", select "Restrict key"
   - Choose only "Google Drive API"
   - Under "Website restrictions", add your domain
9. Save the restricted key

## Step 2: Create Google Drive Folders

1. Go to Google Drive (drive.google.com)
2. Create a main folder like "City Website Files"
3. Inside it, create folders for each category you need:
   - Meeting Minutes
   - Meeting Agendas
   - Budgets
   - Job Postings
   - etc.

## Step 3: Make Folders Public

For each folder you want to use:

1. Right-click the folder → "Share"
2. Click "Change" next to "Restricted"
3. Select "Anyone with the link" → "Viewer"
4. Click "Done"

## Step 4: Get Folder IDs

For each public folder:

1. Open the folder in Google Drive
2. Look at the URL in your browser
3. The folder ID is the long string after `/folders/`

   Example URL:
   ```
   https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j
                                          ^^^^^^^^^^^^^^^^^^^
                                          This is the folder ID
   ```
4. Copy this ID

## Step 5: Configure user-setup.json

Edit `user-setup.json` and add your configuration:

```json
{
  "google_drive": {
    "api_key": "YOUR_API_KEY_HERE",
    "enabled": true,
    "folders": {
      "meeting_minutes": "1a2b3c4d5e6f7g8h9i0j",
      "meeting_agendas": "9j0i8h7g6f5e4d3c2b1a",
      "budgets": "2b3c4d5e6f7g8h9i0j1a2b",
      "job_postings": "3c4d5e6f7g8h9i0j1a2b3c"
    }
  }
}
```

**Available folder categories:**
- `meeting_agendas` - Council/committee meeting agendas
- `meeting_minutes` - Official meeting minutes
- `meeting_packets` - Meeting packets and supporting docs
- `meeting_recordings` - Audio/video recordings
- `voting_records` - Voting records and tallies
- `budgets` - Annual budgets
- `financial_reports` - Quarterly/annual financial reports
- `audit_reports` - Audit reports
- `ordinances` - City ordinances
- `resolutions` - City resolutions
- `municipal_codes` - Code updates
- `public_notices` - Legal/public notices
- `rfps_bids` - RFPs and bid documents
- `zoning_maps` - Zoning maps
- `comprehensive_plans` - Planning documents
- `building_permits_public` - Public permit records
- `street_closures` - Street closure notices
- `construction_updates` - Construction project updates
- `utility_interruptions` - Utility service alerts
- `event_flyers` - Event flyers and announcements
- `recreation_schedules` - Parks & rec schedules
- `newsletters` - City newsletters
- `job_postings` - Job openings
- `emergency_alerts` - Emergency alerts
- `weather_advisories` - Weather advisories

## Step 6: Add File Display to Pages

On any page where you want to display files, add this HTML:

```html
<section class="card">
    <h2>Meeting Minutes</h2>
    <div data-drive-folder="meeting_minutes"></div>
</section>
```

The `data-drive-folder` attribute should match a key from your `user-setup.json` folders.

## Step 7: Include the Script

Make sure the page includes the Google Drive loader script:

```html
<script src="../assets/js/google-drive-loader.js"></script>
```

(Add before the closing `</body>` tag)

## Usage for Staff

Once configured, staff simply:

1. Open the Google Drive folder
2. Drag and drop the PDF/document
3. File appears on the website automatically (within seconds!)

## Troubleshooting

**Files not showing up?**
- Check that the folder is set to "Anyone with the link"
- Verify the folder ID is correct
- Check browser console for errors
- Make sure API key is configured correctly

**"API key not configured" message?**
- Make sure you replaced `YOUR_GOOGLE_API_KEY_HERE` in user-setup.json

**"Folder not configured" message?**
- Add the folder ID to user-setup.json for that category

**401/403 errors?**
- API key may not be properly restricted to Google Drive API
- Check API key settings in Google Cloud Console

## Security Notes

- Use API key restrictions (domains + Drive API only)
- Never commit API keys to public repositories
- Folders must be public or "anyone with link" for this to work
- Consider using a dedicated Google account for city files

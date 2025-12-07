# Database-less Setup Guide

This guide explains how to use the **simple sync service** that reads directly from Google Sheets instead of using PostgreSQL.

## Why Database-less?

The original sync service used PostgreSQL to store parsed file data. But for most government portals, this adds unnecessary complexity:

- ❌ Database to install and maintain
- ❌ Backup and migration complexity
- ❌ Two sources of truth (Google Drive + Database)
- ❌ Sync lag and cache issues

**With the simple sync service:**
- ✅ Google Sheets ARE the database
- ✅ Clerks use familiar spreadsheet interface
- ✅ Simple architecture: Sheets → HTML
- ✅ No PostgreSQL installation needed
- ✅ Easy to set up for new municipalities

## Architecture

```
Google Sheets (your data)
     ↓
Simple Sync Service (reads sheets)
     ↓
HTML Components (generated files)
     ↓
Website Pages (fetch components)
```

## Setup Instructions

### 1. Create Google Sheets

Create one Google Sheet per data type with the following columns:

#### Municipality Config Sheet
**This is the most important sheet** - it generates your `config.js` file with all municipality-specific data like phone numbers, addresses, etc.

Columns: `Key`, `Value`, `Category`, `Description`

**Sheet Name:** Must be exactly `Municipality Config`

Example:
| Key | Value | Category | Description |
|-----|-------|----------|-------------|
| municipality_name | City of Springfield | basic | Full municipality name |
| municipality_type | City | basic | City, Town, Village, etc. |
| state | Illinois | basic | State name |
| clerk_name | Jane Smith | contact | City clerk name |
| clerk_phone | 222-222-2222 | contact | Clerk phone number |
| clerk_email | clerk@springfield.gov | contact | Clerk email |
| main_phone | 222-222-2200 | contact | Main city hall phone |
| main_email | info@springfield.gov | contact | Main email |
| street_address | 123 Main Street | address | Street address |
| city | Springfield | address | City name |
| state_abbr | IL | address | State abbreviation |
| zip_code | 62701 | address | ZIP code |
| office_hours | Monday - Friday: 8:00 AM - 4:30 PM | hours | Office hours |
| mayor_name | John Doe | officials | Mayor name |
| mayor_email | mayor@springfield.gov | officials | Mayor email |
| mayor_phone | 222-222-2201 | officials | Mayor phone |
| police_phone | 911 | emergency | Police emergency |
| police_non_emergency | 222-222-2300 | emergency | Police non-emergency |
| fire_phone | 911 | emergency | Fire emergency |
| staff_directory | 1abc...xyz | google_sheet | Sheet ID for staff directory |
| events | 1def...uvw | google_sheet | Sheet ID for events |

**Categories:**
- `basic` - Basic municipality info
- `contact` - Contact information
- `address` - Physical address
- `hours` - Office hours
- `officials` - Elected officials and department heads
- `emergency` - Emergency contact numbers
- `google_sheet` - Google Sheet IDs (automatically added to `google_sheets` object)
- `google_drive_folder` - Google Drive folder IDs (automatically added to `google_drive_folders` object)
- Leave blank for general config values

This sheet will auto-generate `/assets/js/config.js` which is used throughout the site.

#### Staff Directory Sheet
Columns: `Name`, `Title`, `Department`, `Email`, `Phone`, `Photo`

Example:
| Name | Title | Department | Email | Phone | Photo |
|------|-------|------------|-------|-------|-------|
| Jane Smith | City Clerk | Administration | clerk@city.gov | 222-222-2222 | |
| John Doe | Mayor | Executive | mayor@city.gov | 222-222-2201 | |

#### Events Sheet
Columns: `Event Name`, `Date`, `Time`, `Location`, `Description`, `Link`

Example:
| Event Name | Date | Time | Location | Description | Link |
|------------|------|------|----------|-------------|------|
| City Council Meeting | 2025-12-15 | 7:00 PM | City Hall | Monthly meeting | |
| Community Cleanup | 2025-12-20 | 9:00 AM | Main Street Park | Join us! | |

#### Public Notices Sheet
Columns: `Title`, `Date Posted`, `Description`, `Link`, `Category`

Example:
| Title | Date Posted | Description | Link | Category |
|-------|-------------|-------------|------|----------|
| Public Hearing Notice | 2025-12-10 | Zoning change... | | Zoning |
| Road Closure | 2025-12-12 | Main St closed... | | Public Works |

#### Job Postings Sheet
Columns: `Job Title`, `Department`, `Type`, `Salary Range`, `Posted Date`, `Deadline`, `Description`, `Link`

Example:
| Job Title | Department | Type | Salary Range | Posted Date | Deadline | Description | Link |
|-----------|------------|------|--------------|-------------|----------|-------------|------|
| Police Officer | Police | Full-time | $45,000-$60,000 | 2025-12-01 | 2025-12-31 | Join our team | |

#### Boards & Commissions Sheet
Columns: `Name`, `Description`, `Meeting Schedule`, `Contact`, `Link`

Example:
| Name | Description | Meeting Schedule | Contact | Link |
|------|-------------|------------------|---------|------|
| Planning Commission | Reviews zoning | 2nd Tuesday, 6PM | planning@city.gov | |

#### News Sheet
Columns: `Title`, `Date`, `Summary`, `Link`, `Category`

Example:
| Title | Date | Summary | Link | Category |
|-------|------|---------|------|----------|
| New Park Opens | 2025-12-01 | Main Street Park... | | Parks |

### 2. Share Sheets with Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a service account (or use existing)
3. Download service account JSON key file
4. For each Google Sheet:
   - Click "Share"
   - Add service account email
   - Give "Viewer" access

### 3. Get Sheet IDs

For each sheet, the ID is in the URL:
```
https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
                                        ^^^^^^^^^^^^^
```

### 4. Configure Simple Sync Service

Copy the example config:
```bash
cd sync-service
cp simple_sync_config.example.json simple_sync_config.json
```

Edit `simple_sync_config.json`:
```json
{
  "service_account_file": "/path/to/service-account.json",
  "output_dir": "../components",
  "config_output_dir": "../assets/js",
  "sheets": {
    "municipality_config": "YOUR_CONFIG_SHEET_ID_HERE",
    "staff_directory": "YOUR_SHEET_ID_HERE",
    "events": "YOUR_SHEET_ID_HERE",
    "public_notices": "YOUR_SHEET_ID_HERE",
    "job_postings": "YOUR_SHEET_ID_HERE",
    "boards_commissions": "YOUR_SHEET_ID_HERE",
    "news": "YOUR_SHEET_ID_HERE"
  }
}
```

### 5. Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 6. Run Sync Service

Run once:
```bash
python simple_sync.py --config simple_sync_config.json --once
```

Run continuously (syncs every 5 minutes):
```bash
python simple_sync.py --config simple_sync_config.json
```

### 7. Set up Cron Job (Optional)

Run sync every hour:
```bash
0 * * * * cd /path/to/sync-service && python simple_sync.py --config simple_sync_config.json --once
```

## Municipality-Specific Data (Config File)

The `/assets/js/config.js` file contains all municipality-specific data (phone numbers, addresses, clerk info, etc.).

**This file is AUTO-GENERATED from your Municipality Config Google Sheet.**

DO NOT edit `config.js` manually - your changes will be overwritten on the next sync!

Instead, edit the **Municipality Config** sheet and run the sync service to regenerate config.js.

### Using Config in HTML

Add `data-config` attributes to elements:

```html
<!-- Simple text replacement -->
<p>Call us: <span data-config="clerk_phone"></span></p>

<!-- With formatting -->
<p>Phone: <span data-config="clerk_phone" data-config-format="phone"></span></p>

<!-- As link href -->
<a href="tel:" data-config="clerk_phone" data-config-attr="href" data-config-prefix="tel:">
  Call Clerk
</a>

<!-- With fallback -->
<span data-config="fax_number" data-config-fallback="N/A"></span>
```

The config is automatically loaded on every page by including:
```html
<script src="../assets/js/config.js"></script>
<script src="../assets/js/municipality-config.js"></script>
```

## Output Files

The sync service generates files in two directories:

**`/assets/js/`:**
- `config.js` - Municipality configuration (auto-generated from Municipality Config sheet)
- `config.json` - Same data as JSON (for debugging)

**`/components/`:**
- `staff_directory.html` - Staff cards
- `staff_directory_table.html` - Staff table
- `events.html` - Event cards
- `public_notices.html` - Notice cards
- `job_postings.html` - Job cards
- `boards_commissions.html` - Board cards
- `news_press_releases.html` - News cards

These are fetched by pages using:
```html
<div id="content">
    <p>Loading...</p>
</div>
<script>
fetch('../components/staff_directory.html')
    .then(r => r.text())
    .then(html => document.getElementById('content').innerHTML = html);
</script>
```

## Maintenance

As a clerk, you only need to:

1. **Update Google Sheets** with current data
2. **Wait for sync** (or run manual sync)
3. **That's it!** HTML is automatically regenerated

No database knowledge required!

## Troubleshooting

**Sheet not syncing:**
- Check service account has access to sheet
- Verify sheet ID in config
- Check column names match exactly

**Component not showing:**
- Check browser console for errors
- Verify component file exists in `/components/`
- Check fetch URL is correct

**Permission errors:**
- Service account needs "Viewer" access to sheets
- Service account JSON file path must be correct

## Migration from Database Version

If you're currently using the PostgreSQL version:

1. Set up Google Sheets with your current data
2. Configure and test `simple_sync.py`
3. Verify HTML components are generated correctly
4. Switch sync service from database version to simple version
5. (Optional) Remove PostgreSQL and old sync code

## Support

For issues or questions, check the logs:
```bash
tail -f sync-service/simple_sync.log
```
